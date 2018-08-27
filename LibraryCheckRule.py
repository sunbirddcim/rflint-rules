from rflint.common import ResourceRule, GeneralRule, ERROR, WARNING
from rflint.parser import SettingTable, TestcaseTable
from rflint import RobotFactory, Keyword, Testcase, SuiteFile
from pathlib import PureWindowsPath
import glob
import os
import re

def extract_name(statement):
    """
    >>> extract_name([''])
    ''
    >>> extract_name(['', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '\\\\', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '${x}', 'Get X'])
    'Get X'
    >>> extract_name(['', '${x}', '${y} =', 'Get Position'])
    'Get Position'
    >>> extract_name(['# Hello'])
    '# Hello'
    >>> extract_name(['Given An Apple'])
    'An Apple'
    >>> extract_name(['When Snow White Eat'])
    'Snow White Eat'
    >>> extract_name(['Then She Is Happy'])
    'She Is Happy'
    """
    for token in statement:
        if token in ['', '\\']:
            continue
        if not re.match(r'[@$&]\{[^\}]+\}.*', token):
            for bdd_token in ['given', 'when', 'then']:
                if token.lower().startswith(bdd_token):
                    return token[len(bdd_token):].strip()
            return token
    return statement[0]

def extract_max_same_path(files):
    dirs = [os.path.dirname(f) for f in files]
    if dirs == []:
        return ''
    chars = []
    for i in range(min([len(d) for d in dirs])):
        c = list(set([d[i] for d in dirs]))
        if len(c) == 1:
            chars.append(c[0])
        else:
            break
    return ''.join(chars)

def all_robot_files(path):
    ret = []
    p = PureWindowsPath(path)
    for root, _, files in os.walk(p.parents[0]):
        for f in files:
            if f.endswith('.txt') or f.endswith('.robot'):
                ret.append(os.path.join(root, f))
    return ret

def get_project_folder_files_def_keywords_map(path):
    def is_root_folder(path):
        try:
            if '.project' in [f.encode('cp950').decode() for f in os.listdir(path)]:
                return True
        except:
            if '.project' in [f.encode('utf-8').decode() for f in os.listdir(path)]:
                return True
    def project_file(path):
        if is_root_folder(path):
            return '%s/.project' % path
        return project_file(PureWindowsPath(path).parent)
    return get_subfolder_files_def_keywords_map(project_file(PureWindowsPath(path).parent))

def get_subfolder_files_def_keywords_map(path):
    files = all_robot_files(path)
    file_keywords = dict()
    for f in files:
        file_keywords.setdefault(f, keywords(f))
    return file_keywords

def get_subfolder_files_used_keywords_map(path):
    files = all_robot_files(path)
    file_keywords = dict()
    for f in files:
        def_keywords = []
        for statement in statements(f):
            def_keywords.extend(extract_used_keywords(statement))
        file_keywords.setdefault(f, def_keywords)
    return file_keywords

def extract_used_keywords(tokens):
    """
    >>> extract_used_keywords([''])
    []
    >>> extract_used_keywords(['Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['When', 'Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['When Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['', 'Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['', '${x}', 'Get X'])
    ['Get X']
    >>> extract_used_keywords(['', '${x}', '${y} =', 'Get Position'])
    ['Get Position']
    >>> extract_used_keywords(['', '\\\\', 'Get Position'])
    ['Get Position']
    >>> extract_used_keywords(['', 'Run Keyword', 'Get Position'])
    ['Run Keyword', 'Get Position']
    >>> extract_used_keywords(['', 'Run Keyword If',"'${item}'=='Items List'", 'Wait Until Items List Page Is Visible'])
    ['Run Keyword If', 'Wait Until Items List Page Is Visible']
    >>> extract_used_keywords(['', 'Run Keywords', 'Action A', 'arg1', 'AND', 'Action B', 'AND', 'Action C', 'arg2'])
    ['Run Keywords', 'Action A', 'Action B', 'Action C']
    >>> extract_used_keywords(['[Teardown]', 'Run Keywords', 'Action A', 'arg1', 'AND', 'Action B', 'AND', 'Action C', 'arg2'])
    ['Run Keywords', 'Action A', 'Action B', 'Action C']
    >>> extract_used_keywords(['', 'Wait Until Keyword Succeeds', '1min', '1s', 'Action'])
    ['Wait Until Keyword Succeeds', 'Action']
    """
    ret = []
    i = 0
    while i < len(tokens):
        if not re.match(r'[@$&]\{[^\}]+\}.*', tokens[i]) and tokens[i].lower() not in ['\\', '', '[teardown]', 'given', 'when', 'then']:
            ret.append(extract_name([tokens[i]]))
            if tokens[i].lower() in ['run keyword',
                                     'run keyword and continue on failure',
                                     'run keyword and ignore error',
                                     'run keyword and return',
                                     'run keyword and return status',
                                     'run keyword if all critical tests passed',
                                     'run keyword if all tests passed',
                                     'run keyword if any critical tests failed',
                                     'run keyword if any tests failed',
                                     'run keyword if test failed',
                                     'run keyword if test passed',
                                     'run keyword if timeout occurred']:
                # TODO ELSE
                pass
            elif tokens[i].lower() in ['run keyword and return if',
                                       'run keyword and expect error',
                                       'run keyword if',
                                       'run keyword unless',
                                       'keyword should succeed within a period']:
                i = i + 1
            elif tokens[i].lower() in ['wait until keyword succeeds']:
                i = i + 2
            elif tokens[i].lower() in ['run keywords']:
                i = i + 1
                action = []
                while i < len(tokens):
                    if tokens[i] == 'AND':
                        ret.extend(extract_used_keywords(action))
                        action = []
                    else:
                        action.append(tokens[i])
                    i = i + 1
                ret.extend(extract_used_keywords(action))
                return ret
            else:
                return ret
        i = i + 1
    return ret

def normalize_name(string):
    return string.replace(" ", "").replace("_", "").lower()

def statements(file):
    suite = RobotFactory(file)
    ret = []
    for keyword in suite.walk(Keyword):
        for statement in keyword.statements:
            ret.append(statement)
    for table in suite.tables:
        if isinstance(table, SettingTable):
            for statement in table.statements:
                if statement[0].lower() in ['test setup', 'test teardown', 'suite setup', 'suite teardown', 'test template']:
                    ret.append(statement[1:])
        elif isinstance(table, TestcaseTable):
            for testcase in table.testcases:
                for statement in testcase.statements:
                    ret.append(statement)
    return ret

def keywords(file):
    rbfile = RobotFactory(file)
    ret = []
    for keyword in rbfile.walk(Keyword):
        ret.append(keyword)
    return ret

def same(keyword_def, keyword_use):
    """
    >>> same('Get Position', 'Get Position 1')
    False
    >>> same('Get Position', 'Get Position')
    True
    >>> same('Use Variable ${var1}', 'Use Variable 123')
    True
    >>> same('Use Variable 123', 'Use Variable ${var1}')
    True
    >>> same('Use Variable ${var1}', 'Use Variable ${var2}')
    True
    >>> same('Use Variable ${var1} hi', 'Use Variable 132')
    False
    >>> same('The Column ${customField} Was Set To Be Visible', 'The Column ${customField.fieldName} Was Set To Be Visible')
    True
    >>> same('The Column ${customField.fieldName} Was Set To Be Visible', 'The Column ${customField} Was Set To Be Visible')
    True
    >>> same('Action', '"*+,-./:;<="()')
    False
    >>> same('Action', '(')
    False
    >>> same('.', '.')
    True
    """
    try:
        ndef = normalize_name(keyword_def)
        nuse = normalize_name(keyword_use)
        return re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(ndef)), nuse) != None or re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(nuse)), ndef) != None
    except:
        raise Exception((keyword_def, keyword_use))

def keyword_in_keywordslist(keyword, keywords):
    for k in keywords:
        if same(keyword, k):
            return True
    return False

class MoveKeyword(ResourceRule):

    severity = WARNING

    def apply(self, resource):
        file_keywords = get_subfolder_files_used_keywords_map(resource.path)
        for keyword in resource.keywords:
            self_usage = keyword_in_keywordslist(keyword.name, file_keywords[resource.path])
            fk_used_keyword = [(f, use_keywords) for f, use_keywords in file_keywords.items() if keyword_in_keywordslist(keyword.name, use_keywords)]

            # Move the keyword to a file
            if len(fk_used_keyword) == 1 and not(self_usage):
                self.report(keyword, 'Move the keyword to file `%s`' % (os.path.relpath(fk_used_keyword[0][0], os.path.dirname(resource.path))), keyword.linenumber)

            # Move the keyword to a folder
            common_path = extract_max_same_path([f for f, use_keywords in fk_used_keyword])
            if len(fk_used_keyword) > 1 and os.path.normpath(common_path) != os.path.normpath(os.path.dirname(resource.path)) and os.path.isdir(common_path) and not(self_usage):
                self.report(keyword, 'Move the keyword to folder `%s`' % (os.path.relpath(common_path,  os.path.dirname(resource.path))), keyword.linenumber)

class UnusedKeyword(GeneralRule):

    severity = WARNING

    def apply(self, resource):
        file_keywords = get_subfolder_files_used_keywords_map(resource.path)
        for keyword in resource.keywords:
            self_usage = keyword_in_keywordslist(keyword.name, file_keywords[resource.path])
            fk_used_keyword = [(f, use_keywords) for f, use_keywords in file_keywords.items() if keyword_in_keywordslist(keyword.name, use_keywords)]
            if (isinstance(resource, SuiteFile) and not(self_usage)) or len(fk_used_keyword) == 0:
                self.report(keyword, 'Unused Keyword', keyword.linenumber)

class DuplicatedKeyword(GeneralRule):

    severity = WARNING

    def same_statements(self, statements1, statements2):
        while [''] in statements1:
            statements1.remove([''])
        while [''] in statements2:
            statements2.remove([''])
        if len(statements1) != len(statements2):
            return False
        for i, s in enumerate(statements1):
            if len(statements2[i]) != len(s):
                return False
            for j, t in enumerate(s):
                if t != statements2[i][j]:
                    return False
        return True

    def apply(self, rbfile):
        file_keywords = get_project_folder_files_def_keywords_map(rbfile.path)  # TODO: refile.path -> project.path
        for keyword in rbfile.keywords:
            for f, ks in file_keywords.items():
                if f.endswith('\\test_automation\\Keywords.txt') or '\\PageObjects\\' in f or '\\DCT-extra issues\\' in f:
                    continue
                if f == rbfile.path:
                    continue
                for k in ks:
                    if same(k.name, keyword.name):
                        if self.same_statements(k.statements, keyword.statements):
                            self.report(keyword, 'Duplicated Keyword (name and impl): %s:%d' % (os.path.relpath(f, os.path.dirname(rbfile.path)), k.linenumber), keyword.linenumber)
                        else:
                            self.report(keyword, 'Duplicated Keyword (name): %s:%d' % (os.path.relpath(f, os.path.dirname(rbfile.path)), k.linenumber), keyword.linenumber)
                    elif self.same_statements(k.statements, keyword.statements):
                        self.report(keyword, 'Duplicated Keyword (impl): %s:%d' % (os.path.relpath(f, os.path.dirname(rbfile.path)), k.linenumber), keyword.linenumber)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
from rflint.common import ResourceRule, GeneralRule, ERROR, WARNING
from rflint.parser import SettingTable, TestcaseTable
from rflint import RobotFactory, Keyword, Testcase, SuiteFile
from pathlib import PureWindowsPath
import glob
import os
import re

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

def get_subfolder_files_used_keywords_map(path):
    files = all_robot_files(path)
    file_keywords = dict()
    for f in files:
        used_keywords = []
        for statement in statements(f):
            used_keywords.extend(extract_used_keywords(statement))
        file_keywords.setdefault(f, used_keywords)
    return file_keywords

def extract_used_keywords(tokens):
    """
    >>> extract_used_keywords([''])
    []
    >>> extract_used_keywords(['Click Element'])
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
    """
    ret = []
    i = 0
    while i < len(tokens):
        if not re.match(r'[@$&]\{[^\}]+\}.*', tokens[i]) and tokens[i] not in ['\\', '']:
            ret.append(tokens[i])
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

def same(keyword_def, keyword_use):
    """
    >>> same('Get Position', 'Get Position 1')
    False
    >>> same('Get Position', 'Get Position')
    True
    >>> same('Use Variable ${var1}', 'Use Variable 123')
    True
    >>> same('Use Variable ${var1}', 'Use Variable ${var2}')
    True
    >>> same('Use Variable ${var1} hi', 'Use Variable 132')
    False
    >>> same('The Column ${customField} Was Set To Be Visible', 'The Column ${customField.fieldName} Was Set To Be Visible')
    True
    >>> same('The Column ${customField.fieldName} Was Set To Be Visible', 'The Column ${customField} Was Set To Be Visible')
    True
    """
    return re.match("^%s$" % re.sub(r'[@$&]\{[^\}]+\}', r'.+', normalize_name(keyword_def)), normalize_name(keyword_use)) != None

class MoveKeyword(ResourceRule):

    severity = WARNING

    def apply(self, resource):
        file_keywords = get_subfolder_files_used_keywords_map(resource.path)
        for keyword in resource.keywords:
            self_usage = keyword.name in file_keywords[resource.path]
            fk_used_keyword = [(f, use_keywords) for f, use_keywords in file_keywords.items() if keyword.name in use_keywords]

            # Move the keyword to a file
            if len(fk_used_keyword) == 1 and not(self_usage):
                self.report(keyword, 'Move keyword `%s` to file `%s`' % (keyword.name, os.path.relpath(fk_used_keyword[0][0])), keyword.linenumber)

            # Move the keyword to a folder
            common_path = extract_max_same_path([f for f, use_keywords in fk_used_keyword])
            if len(fk_used_keyword) > 1 and os.path.normpath(common_path) != os.path.normpath(os.path.dirname(resource.path)) and os.path.isdir(common_path) and not(self_usage):
                self.report(keyword, 'Move keyword `%s` to folder `%s`' % (keyword.name, os.path.relpath(common_path)), keyword.linenumber)

class UnusedKeyword(GeneralRule):

    severity = WARNING

    def keyword_in_keywordslist(self, keyword, keywords):
        for k in keywords:
            if same(normalize_name(keyword), normalize_name(k)):
                return True
        return False

    def apply(self, resource):
        file_keywords = get_subfolder_files_used_keywords_map(resource.path)
        for keyword in resource.keywords:
            self_usage = self.keyword_in_keywordslist(keyword.name, file_keywords[resource.path])
            fk_used_keyword = [(f, use_keywords) for f, use_keywords in file_keywords.items() if self.keyword_in_keywordslist(keyword.name, use_keywords)]
            if (isinstance(resource, SuiteFile) and not(self_usage)) or len(fk_used_keyword) == 0:
                self.report(keyword, 'Unused Keyword', keyword.linenumber)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
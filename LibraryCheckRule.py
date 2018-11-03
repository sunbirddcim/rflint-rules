from rflint.common import GeneralRule, WARNING, ERROR
from rflint.parser import SettingTable, TestcaseTable
from rflint import RobotFactory, Keyword
from pathlib import PureWindowsPath
import re
import os
import sys
sys.path.append(os.path.dirname(__file__))
from utility import project_meta


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


def is_root_folder(path):
    try:
        if not os.path.isdir(path):
            return False
        if '.project' in [f.encode('cp950').decode() for f in os.listdir(path)]:
            return True
    except:
        if '.project' in [f.encode('utf-8').decode() for f in os.listdir(path)]:
            return True


def project_file(path):
    return '%s/.project' % project_root(path)


def project_root(path):
    if is_root_folder(path):
        return path
    return project_root(PureWindowsPath(path).parent)


def get_project_folder_files_def_keywords_map(path):
    return get_subfolder_files_def_keywords_map(project_file(PureWindowsPath(path).parent))


def get_subfolder_files_def_keywords_map(path):
    files = all_robot_files(path)
    file_keywords = dict()
    for f in files:
        file_keywords.setdefault(f, keywords(f))
    return file_keywords


def normalize_name(string):
    return string.replace(" ", "").replace("_", "").lower()


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
    >>> same('Action', None)
    False
    """
    try:
        if keyword_def != keyword_use and (keyword_def == None or keyword_use == None):
            return False
        ndef = normalize_name(keyword_def)
        nuse = normalize_name(keyword_use)
        if ('{' in ndef and '}' in ndef) or ('{' in nuse and '}' in nuse):
            return re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(ndef)), nuse) != None or re.match("^%s$" % re.sub(r'\\?[@$&]\\{[^\}]+\\}', r'.+', re.escape(nuse)), ndef) != None
        return ndef == nuse
    except:
        raise Exception((keyword_def, keyword_use))


metas = None
def get_metas(path):
    global metas
    if metas == None:
        metas = project_meta(path)
    return metas


class MoveKeyword(GeneralRule):

    severity = ERROR

    def apply(self, rf_file):
        metas = get_metas(rf_file.path)
        current = next(filter(lambda x: x.source == rf_file.path, metas))
        for keyword, values in current.defs.items():
            used_metas = [meta for meta in metas if keyword in meta.uses.keys()]
            self_usage = any(same(keyword, used) for used in current.uses.keys())

            # Move the keyword to a file
            if len(used_metas) == 1 and not self_usage:
                self.report(rf_file, 'Move the keyword to file `%s`' % (os.path.relpath(used_metas[0].source, os.path.dirname(rf_file.path))), values['line'])

            # Move the keyword to a folder
            common_path = extract_max_same_path([meta.source for meta in used_metas])
            if len(used_metas) > 1 and os.path.normpath(common_path) != os.path.normpath(os.path.dirname(rf_file.path)) and os.path.isdir(common_path) and not self_usage:
                move = os.path.relpath(common_path, os.path.dirname(rf_file.path))
                if '..' not in move:
                    self.report(rf_file, 'Move the keyword to folder `%s\\keywords.txt`' % move, values['line'])


class UnusedKeyword(GeneralRule):

    severity = ERROR

    def apply(self, rf_file):
        metas = get_metas(rf_file.path)
        current = next(filter(lambda x: x.source == rf_file.path, metas))
        for keyword, values in current.defs.items():
            if current.is_test_data:
                if self.not_used(keyword, [current]):
                    self.report(rf_file, 'Unused Keyword', values['line'])
            else:
                if self.not_used(keyword, metas):
                    self.report(rf_file, 'Unused Keyword', values['line'])

    def not_used(self, keyword, metas):
        for meta in metas:
            if any(same(keyword, used) for used in meta.uses.keys()):
                return False
        return True


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
        file_keywords = get_project_folder_files_def_keywords_map(rbfile.path)
        for keyword in rbfile.keywords:
            for f, ks in file_keywords.items():
                if f.endswith('\\test_automation\\Keywords.txt') or f.endswith('\\test_automation\\End-to-end test\\Keywords.txt') or '\\PageObjects\\' in f or '\\End-to-end test\\Capacity' in f or '\\End-to-end test\\Plan to decomm' in f or '\\End-to-end test\\Change Management' in f or '\\DCT-extra issues\\' in f or '\\DCT-14884 ' in f or '\\DCT-14886 ' in f:
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

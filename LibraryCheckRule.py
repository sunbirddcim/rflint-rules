from rflint.common import ResourceRule, ERROR, WARNING
from rflint.parser import SettingTable, TestcaseTable
from rflint import RobotFactory, Keyword, Testcase, SuiteFile
from pathlib import PureWindowsPath
import glob
import os

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
                    ret.append(statement)
        elif isinstance(table, TestcaseTable):
            for testcase in table.testcases:
                for statement in testcase.statements:
                    ret.append(statement)
    return ret

def use_keyword(statements, kw):
    nkw = normalize_name(kw)
    for statement in statements:
        if nkw in [normalize_name(token) for token in statement]:
            return True
    return False

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

class LibraryCheck(ResourceRule):

    severity = WARNING

    def apply(self, resource):
        p = PureWindowsPath(resource.path)
        files_statements = []
        for root, dirs, files in os.walk(p.parents[0]):
            for f in files:
                if f.endswith('.txt') or f.endswith('.robot'):
                    filename = os.path.join(root, f)
                    files_statements.append({'statements': statements(filename), 'file': filename})
        for keyword in resource.keywords:
            file_uses_keyword = []
            for file_statements in files_statements:
                if os.path.abspath(file_statements['file']) == os.path.abspath(resource.path):
                    self_usage = use_keyword(file_statements['statements'], keyword.name)
                elif use_keyword(file_statements['statements'], keyword.name):
                    file_uses_keyword.append(file_statements['file'])
            common_path = extract_max_same_path(file_uses_keyword)
            if len(file_uses_keyword) == 1 and not(self_usage):
                self.report(keyword, 'Move keyword `%s` to file `%s`' % (keyword.name, os.path.relpath(file_uses_keyword[0])), keyword.linenumber)
            elif os.path.normpath(common_path) != os.path.normpath(os.path.dirname(resource.path)) and os.path.isdir(common_path) and not(self_usage):
                self.report(keyword, 'Move keyword `%s` to folder `%s`' % (keyword.name, os.path.relpath(common_path)), keyword.linenumber)

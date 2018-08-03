from rflint.common import SuiteRule, KeywordRule, WARNING, ERROR
from rflint.parser import SettingTable, TestcaseTable
import re

def name_check(self, obj, name, line):
    tokens = name.split(' ')
    if any(token[0].isalpha() and not token[0].isupper() for token in tokens):
        self.report(obj, 'Keyword name is not CamelCase', line)

def style_check(self, obj, statement):
    if len(statement) > 1:
        name_check(self, obj, extract_name(statement), statement.startline)
        if re.match(r'[@$&]\{[^\}]+\}.*', statement[1]):
            last_variable = statement[1]
            for token in statement[2:]:
                if re.match(r'[@$&]\{[^\}]+\}.*', token):
                    last_variable = token
                else:
                    break
            if not last_variable.endswith('='):
                self.report(obj, 'Add an assignment operator `=` after the variable', statement.startline)
            if last_variable.endswith('}='):
                self.report(obj, 'Add a apace between the variable and `=`', statement.startline)

def extract_name(statement):
    """
    >>> extract_name([''])
    ''
    >>> extract_name(['', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '${x}', 'Get X'])
    'Get X'
    >>> extract_name(['', '${x}', '${y} =', 'Get Position'])
    'Get Position'
    """
    if len(statement) > 1:
        for token in statement[1:]:
            if not re.match(r'[@$&]\{[^\}]+\}.*', token):
                return token
    return statement[0]

def is_template(suite):
    for table in suite.tables:
        if isinstance(table, SettingTable):
            if any([row[0].lower() == 'test template' for row in table.rows]):
                return True
    return False

class StyleCheck_Test(SuiteRule):

    severity = WARNING

    def apply(self, suite):
        for table in suite.tables:
            if isinstance(table, SettingTable):
                for row in table.rows:
                    print(row)
                    if row[0].lower().endswith('teardown'):
                        if row[1].lower() == 'close browser':
                            self.report(suite, 'Use keyword `Logoff` instead.', row.linenumber)

        if not is_template(suite):
            for table in suite.tables:
                if isinstance(table, TestcaseTable):
                    for testcase in table.testcases:
                        for statement in testcase.statements:
                            style_check(self, testcase, statement)

class StyleCheck_Keyword(KeywordRule):

    severity = WARNING

    def apply(self, keyword):
        name_check(self, keyword, keyword.name, keyword.linenumber)
        for statement in keyword.statements:
            style_check(self, keyword, statement)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
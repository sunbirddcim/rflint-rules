from rflint.common import SuiteRule, KeywordRule, GeneralRule, WARNING, ERROR
from rflint.parser import SettingTable, TestcaseTable, VariableTable, Testcase, Keyword, Row, Statement
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
        if not re.match(r'[@$&]\{[^\}]+\}.*|^\[(Template|template)\]', token):
            for bdd_token in ['given', 'when', 'then']:
                if token.lower().startswith(bdd_token):
                    return token[len(bdd_token):].strip()
            return token
    return statement[0]

def line_number(obj):
    if isinstance(obj, Keyword) or isinstance(obj, Row):
        return obj.linenumber
    if isinstance(obj, Statement):
        return obj.startline

def action_name(obj):
    if isinstance(obj, Keyword):
        return obj.name
    if isinstance(obj, Statement):
        return extract_name(obj)

def last_variable(statement):
    """
    >>> last_variable([''])
    >>> last_variable(['', 'Click Element'])
    >>> last_variable(['', '\\\\', '${x}', 'Get Position'])
    '${x}'
    >>> last_variable(['', '${x}', 'Get X'])
    '${x}'
    >>> last_variable(['', '${x}', '${y} =', 'Get Position'])
    '${y} ='
    """
    variable = None
    for token in statement:
        if token in ['', '\\']:
            continue
        elif re.match(r'[@$&]\{[^\}]+\}.*', token):
            variable = token
        else:
            return variable

def is_test_template(suite):
    for table in suite.tables:
        if isinstance(table, SettingTable):
            if any([row[0].lower() == 'test template' for row in table.rows]):
                return True
    return False

def is_template(testcase):
    if any([statement[1].lower() == '[template]' for statement in testcase.statements if not (len(statement) == 1 and statement[0] == '')]):
        return True
    return False

class UseLogoff(SuiteRule):

    severity = WARNING

    def apply(self, suite):
        for table in suite.tables:
            if isinstance(table, SettingTable):
                for row in table.rows:
                    if row[0].lower().endswith('teardown'):
                        if row[1].lower() == 'close browser':
                            self.report(suite, 'Use keyword `Logoff` instead.', row.linenumber)

class AssignmentStyle(GeneralRule):

    severity = WARNING

    def report_if_should_format_variable(self, obj, statement):
        if all(token == '' for token in statement):
            return
        if isinstance(statement, Statement):
            variable = last_variable(statement)
        elif isinstance(statement, Row): # Variable Table
            variable = statement[0]
        linenumber = line_number(statement)
        if variable != None and not variable.startswith('#') and not variable == '...':
            if not variable.endswith('='):
                self.report(obj, 'Add an assignment operator `=` after the variable', linenumber)
            if variable.endswith('}='):
                self.report(obj, 'Add a space between the variable and `=`', linenumber)

    def apply(self, robotfile):
        for table in robotfile.tables:
            if isinstance(table, TestcaseTable):
                if not is_test_template(robotfile):
                    for testcase in table.testcases:
                        for statement in testcase.statements:
                            self.report_if_should_format_variable(robotfile, statement)
            if isinstance(table, VariableTable):
                for row in table.rows:
                    self.report_if_should_format_variable(robotfile, row)
        for keyword in robotfile.keywords:
            for statement in keyword.statements:
                self.report_if_should_format_variable(robotfile, statement)

class UseCamelCaseKeyword(GeneralRule):

    severity = WARNING

    def report_if_not_camel_case(self, obj, statement):
        tokens = action_name(statement).split(' ')
        linenumber = line_number(statement)
        if tokens[0].startswith('#'):
            return
        if any(len(token) > 0 and token not in ["dcTrack", "eAsset"] and token[0].isalpha() and not token[0].isupper() for token in tokens):
            self.report(obj, 'Keyword name is not Camel Case.', linenumber)

    def apply(self, robotfile):
        for table in robotfile.tables:
            if not is_test_template(robotfile):
                if isinstance(table, TestcaseTable):
                    for testcase in table.testcases:
                        if not is_template(testcase):
                            for statement in testcase.statements:
                                self.report_if_not_camel_case(testcase, statement)
                        else:
                            self.report_if_not_camel_case(testcase, testcase.statements[0])
        for keyword in robotfile.keywords:
            self.report_if_not_camel_case(keyword, keyword)
            for statement in keyword.statements:
                self.report_if_not_camel_case(keyword, statement)

class TrailingWhiteSpaceIgnoreCarriegeReturn(GeneralRule):

    severity = WARNING

    def apply(self, robotfile):
        linenumber = 0
        for line in robotfile.raw_text.splitlines():
            linenumber = linenumber + 1
            if line.endswith((' ', '\t')):
                self.report(robotfile, 'Trailing whiteSpace.', linenumber)

class MoreThanOneBlankLine(GeneralRule):

    severity = WARNING

    def apply(self, robotfile):
        linenumber = 0
        blank_line = False
        for line in robotfile.raw_text.splitlines():
            linenumber = linenumber + 1
            if line.strip() == '':
                if blank_line == True:
                    self.report(robotfile, 'More than one blank line.', linenumber)
                blank_line = True
            else:
                blank_line = False

if __name__ == "__main__":
    import doctest
    doctest.testmod()
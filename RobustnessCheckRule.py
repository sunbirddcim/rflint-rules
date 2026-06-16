from rflint.common import SuiteRule, KeywordRule, WARNING, ERROR
from rflint.parser import SettingTable, TestcaseTable
import re


def extract_checked_keyword_calls(statement):
    if len(statement) <= 1:
        return []

    keyword = statement[1]
    if keyword.lower() != 'if':
        return [(keyword, list(statement[2:]))]

    # Inline IF: IF <cond> <keyword> [args] [ELSE IF <cond> <keyword> [args]] [ELSE <keyword> [args]]
    calls = []
    i = 3
    while i < len(statement):
        token = statement[i]
        lower = token.lower()

        if lower == 'else if':
            i += 2
            continue
        if lower == 'else':
            i += 1
            continue
        if lower == 'end':
            break

        j = i + 1
        while j < len(statement) and statement[j].lower() not in ['else if', 'else', 'end']:
            j += 1

        calls.append((token, list(statement[i + 1:j])))
        i = j

    return calls

def check(self, obj, statement):
    for keyword, args in extract_checked_keyword_calls(statement):
        if keyword.lower() == 'unselect frame':
            self.report(obj, '`Unselect Frame` -> `[Teardown]    Unselect Frame`', statement.startline)
        elif is_wait_until_keyword([keyword]):
            if not any([token.startswith('timeout') for token in args]):
                self.report(obj, 'Missing timeout argument?', statement.startline)
            if not any([token.startswith('error') for token in args]):
                self.report(obj, 'Missing error argument?', statement.startline)
        elif keyword.lower() == 'sleep' and (len(args) == 0 or "reason=" not in args[-1]):
            self.report(obj, 'DO NOT USE SLEEP!', statement.startline)

        xpath = [arg for arg in args if arg.startswith('xpath')]
        if len(xpath) > 0:
            if re.search('@class=.*', xpath[0]):
                self.report(obj, 'use contains(@class, ...)', statement.startline)
            if re.search('text()\\s*=', xpath[0]):
                self.report(obj, 'use normalize-space(text())=', statement.startline)

def check_missing_waiting(self, obj, name, statements):
    previous = ['']
    for statement in statements:
        if is_action_on_element(statement):
            if not is_wait_until_keyword(previous):
                self.report(obj, 'Use keyword `ooo After It Is Visible` instead.', statement.startline)
            elif not name.lower().endswith('after it is visible'):
                self.report(obj, 'Use keyword `ooo After It Is Visible` instead.', statement.startline)
        previous = statement

def is_template(suite):
    for table in suite.tables:
        if isinstance(table, SettingTable):
            if any([row[0].lower() == 'test template' for row in table.rows]):
                return True
    return False

def is_action_on_element(statement):
    for token in statement:
        if token.lower() in [
            'assign id to element',
            'choose file',
            'clear element text',
            'click button',
            'click element',
            'click element at coordinates',
            'click image',
            'click link',
            'double click element',
            'drag and drop',
            'drag and drop by offset',
            'focus',
            'get element attribute',
            'get element count',
            'get element size',
            'get horizontal position',
            'get list items',
            'get selected list label',
            'get selected list labels',
            'get selected list value',
            'get selected list values',
            'get table cell',
            'get text',
            'get value',
            'get vertical position',
            'get webelement',
            'get webelements',
            'input password',
            'input text',
            'mouse down',
            'mouse down on image',
            'mouse down on link',
            'mouse out',
            'mouse over',
            'mouse up',
            'open context menu',
            'press key',
            'select all from list',
            'select checkbox',
            'select frame',
            'select from list',
            'select from list by index',
            'select from list by label',
            'select from list by value',
            'set focus to element',
            'simulate',  # Deprecated
            'simulate event',
            'unselect all from list',
            'unselect checkbox',
            'unselect from list',
            'unselect from list by index',
            'unselect from list by label'
        ]:
            return True
    return False

def is_wait_until_keyword(statement):
    for token in statement:
        if token.lower() in [
            'wait for condition',
            'wait until element contains',
            'wait until element does not contain',
            'wait until element is enabled',
            'wait until element is not visible',
            'wait until element is visible',
            'wait until page contains',
            'wait until page contains element',
            'wait until page does not contain',
            'wait until page does not contain element'
        ]:
            return True
    return False

class RobustnessCheck_Test(SuiteRule):

    severity = WARNING

    def apply(self, suite):
        if not is_template(suite):
            for table in suite.tables:
                if isinstance(table, TestcaseTable):
                    for testcase in table.testcases:
                        # check_missing_waiting(self, testcase, '', testcase.statements)
                        for statement in testcase.statements:
                            check(self, testcase, statement)

class RobustnessCheck_Keyword(KeywordRule):

    severity = WARNING

    def apply(self, keyword):
        # check_missing_waiting(self, keyword, keyword.name, keyword.statements)
        for statement in keyword.statements:
            check(self, keyword, statement)

from rflint import RobotFactory, Keyword
from rflint.parser import SettingTable, TestcaseTable
import platform
from pathlib import PureWindowsPath, PurePosixPath
import os
import time
import re


class RFMeta:

    def __init__(self, source):
        self.source = source
        self.modified = time.ctime(os.path.getmtime(source))
        self.defs = dict()
        self.uses = dict()
        self.is_test_data = False

    def __str__(self):
        return ('source: %s\n' % self.source) +\
               ('  modified: %s\n' % self.modified) +\
               ('  defs: %s\n' % str(self.defs)) + \
               ('  uses: %s\n' % str(self.uses))


def extract_name(tokens):
    """
    No keyword
    >>> extract_name([''])
    >>> extract_name(['# Hello'])
    >>> extract_name(['', '[Documentation]'])
    >>> extract_name(['', '[Arguments]', '${name}', '${age}'])
    >>> extract_name(['', '[Tags]', 'smoke test'])
    >>> extract_name(['', '[Return]', '${age}'])
    >>> extract_name(['', '[Timeout]', '1 min'])
    >>> extract_name(['', ':FOR', '${tabName}', 'IN', '@{tabNames}'])

    >>> extract_name(['', 'Click Element'])
    'Click Element'
    >>> extract_name(['...', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '\\\\', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '[Teardown]', 'Unselect Frame'])
    'Unselect Frame'
    >>> extract_name(['', '[Setup]', 'Open Application', 'App B'])
    'Open Application'
    >>> extract_name(['', '[Template]', 'Example keyword'])
    'Example keyword'

    assign
    >>> extract_name(['', '${x}', 'Get X'])
    'Get X'
    >>> extract_name(['', '@{x} =', 'Get X'])
    'Get X'
    >>> extract_name(['', '${x}', '${y} =', 'Get Position'])
    'Get Position'

    behavior-driven
    >>> extract_name(['Given An Apple'])
    'An Apple'
    >>> extract_name(['When Snow White Eat'])
    'Snow White Eat'
    >>> extract_name(['Then She Is Happy'])
    'She Is Happy'
    """
    if len(tokens) == 0 or tokens[0].startswith('#') or tokens[0] in ['[Documentation]', '[Arguments]', '[Tags]', '[Return]', '[Timeout]', ':FOR']:
        return None
    if tokens[0] in ['', '\\', '...', '[Setup]', '[Teardown]', '[Template]']:
        return extract_name(tokens[1:])
    if re.match(r'[@$&]\{[^\}]+\}.*', tokens[0]):
        return extract_name(tokens[1:])
    for bdd_token in ['given ', 'when ', 'then ', 'and ']:
        if tokens[0].lower().startswith(bdd_token):
            return tokens[0][len(bdd_token):].strip()
    return tokens[0]


def extract_used_keywords(tokens):
    """
    >>> extract_used_keywords([''])
    []
    >>> extract_used_keywords(['# Click Element'])
    []

    behavior-driven
    >>> extract_used_keywords(['Given A Opened Chrome'])
    ['A Opened Chrome']
    >>> extract_used_keywords(['Given', 'A Opened Chrome'])
    ['A Opened Chrome']
    >>> extract_used_keywords(['When', 'Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['When Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['Then User Should Be Happy'])
    ['User Should Be Happy']
    >>> extract_used_keywords(['Then', 'User Should Be Happy'])
    ['User Should Be Happy']

    simple
    >>> extract_used_keywords(['Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['...', 'Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['Click Element'])
    ['Click Element']
    >>> extract_used_keywords(['${x}', 'Get X'])
    ['Get X']
    >>> extract_used_keywords(['${x}', '${y} =', 'Get Position'])
    ['Get Position']
    >>> extract_used_keywords(['\\\\', 'Get Position'])
    ['Get Position']

    run keyword
    >>> extract_used_keywords(['Run Keyword', 'Get Position'])
    ['Run Keyword', 'Get Position']
    >>> extract_used_keywords(['${v}', 'Run Keyword', 'Get Position'])
    ['Run Keyword', 'Get Position']
    >>> extract_used_keywords(['${v} =', 'Run Keyword If', '${cond}', 'Action A'])
    ['Run Keyword If', 'Action A']
    >>> extract_used_keywords(['Run Keyword If',"${cond}", 'Wait Until Items List Page Is Visible'])
    ['Run Keyword If', 'Wait Until Items List Page Is Visible']
    >>> extract_used_keywords(['', 'Wait Until Keyword Succeeds', '1min', '1s', 'Action'])
    ['Wait Until Keyword Succeeds', 'Action']

    if else
    >>> extract_used_keywords(['Run Keyword If', '${cond}', 'Run Keywords', 'Action A', 'arg1', 'arg2', 'AND', 'Action B', 'ELSE IF', '${cond}', 'Run Keywords', 'Action C', 'AND', 'Action D'])
    ['Run Keyword If', 'Run Keywords', 'Action A', 'Action B', 'Run Keywords', 'Action C', 'Action D']
    >>> extract_used_keywords(['...', 'ELSE', 'Run Keywords'])
    ['Run Keywords']
    >>> extract_used_keywords(['...', 'ELSE IF', '${cond}' , 'Action A'])
    ['Action A']
    >>> extract_used_keywords(['...', 'Run Keyword If Test Passed', 'Action A'])
    ['Run Keyword If Test Passed', 'Action A']

    settings
    >>> extract_used_keywords(['[Teardown]', 'Action A'])
    ['Action A']
    >>> extract_used_keywords(['[Template]', 'Action B'])
    ['Action B']
    >>> extract_used_keywords(['', '[Timeout]', '1 min'])
    []

    run keywords
    >>> extract_used_keywords(['Run Keywords', 'Action A', 'Action B', 'Action C'])
    ['Run Keywords', 'Action A', 'Action B', 'Action C']
    >>> extract_used_keywords(['Run Keywords', 'Action A', 'AND', 'Action C'])
    ['Run Keywords', 'Action A', 'Action C']
    >>> extract_used_keywords(['...', 'AND', 'Action B'])
    ['Action B']
    >>> extract_used_keywords(['Run Keywords', 'Action A', 'arg1', 'arg2', 'AND', 'Action B', 'AND', 'Action C', 'arg2'])
    ['Run Keywords', 'Action A', 'Action B', 'Action C']
    >>> extract_used_keywords(['Run Keywords', 'Run Keyword If Test Passed', 'Action A', 'AND', 'Run Keyword If Test Failed', 'Action B', 'AND', 'Action C'])
    ['Run Keywords', 'Run Keyword If Test Passed', 'Action A', 'Run Keyword If Test Failed', 'Action B', 'Action C']
    >>> extract_used_keywords(['Run Keywords', 'Action A', '${arg}'])
    ['Run Keywords', 'Action A']
    """
    ret = []
    if len(tokens) == 0 or tokens[0].startswith('#') or tokens[0] in ['[Documentation]', '[Arguments]', '[Tags]', '[Return]', '[Timeout]', ':FOR']:
        return ret
    if tokens[0].lower() in ['\\', '', '[teardown]', '[template]', '[setup]', 'given', 'when', 'then', 'and'] or re.match(r'[@$&]\{[^\}]+\}.*', tokens[0].lower()):
        return extract_used_keywords(tokens[1:])
    if tokens[:2] == ['...', 'ELSE'] or tokens[:2] == ['...', 'AND']:
        return extract_used_keywords(tokens[2:])
    if tokens[:2] == ['...', 'ELSE IF']:
        return extract_used_keywords(tokens[3:])
    if tokens[0] == 'ELSE':
        return extract_used_keywords(tokens[1:])
    if tokens[0] == 'ELSE IF':
        return extract_used_keywords(tokens[2:])
    if tokens[0] == '...':
        return extract_used_keywords(tokens[1:])
    name = extract_name(tokens)
    if name:
        ret.append(name)
    if tokens[0].lower() in ['run keyword', 'run keyword and continue on failure', 'run keyword and ignore error',
                             'run keyword and return', 'run keyword and return status', 'run keyword if all critical tests passed',
                             'run keyword if all tests passed', 'run keyword if any critical tests failed', 'run keyword if any tests failed',
                             'run keyword if test failed', 'run keyword if test passed', 'run keyword if timeout occurred']:
        ret.extend(extract_used_keywords(tokens[1:]))
    elif tokens[0].lower() in ['run keyword and return if', 'run keyword and expect error', 'run keyword if',
                               'run keyword unless', 'keyword should succeed within a period']:
        indexes = [2] + [i for i, v in enumerate(tokens) if v.lower() in ['else if', 'else']]
        for i in range(len(indexes)-1):
            ret.extend(extract_used_keywords(tokens[indexes[i]:indexes[i+1]]))
        ret.extend(extract_used_keywords(tokens[indexes[-1]:]))
    elif tokens[0].lower() in ['wait until keyword succeeds']:
        ret.extend(extract_used_keywords(tokens[3:]))
    elif tokens[0].lower() in ['run keywords']:
        if 'AND' in tokens:
            itokens = [i for i, v in enumerate(tokens) if v.lower() in ['run keywords', 'and']]
            for i in range(len(itokens)-1):
                ret.extend(extract_used_keywords(tokens[itokens[i]+1:itokens[i+1]]))
            ret.extend(extract_used_keywords(tokens[itokens[-1]+1:]))
        else:
            ret.extend(tokens[1:])
    return [e for e in ret if not (e.startswith("${") and e.endswith("}"))]


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
    return os.path.join(project_root(path), '.project')


def project_root(path):
    if is_root_folder(path):
        return path
    if platform.system() == "Linux":
        return project_root(PurePosixPath(path).parent)
    else:
        return project_root(PureWindowsPath(path).parent)


def all_robot_files(path):
    ret = []
    if platform.system() == "Linux":
        p = PurePosixPath(path)
    else:
        p = PureWindowsPath(path)
    for root, _, files in os.walk(p.parents[0]):
        for f in files:
            if f.endswith('.txt') or f.endswith('.robot'):
                ret.append(os.path.join(root, f))
    return ret


def project_meta(path):
    ret = []
    if platform.system() == "Linux":
        parrentFile = PurePosixPath(path).parent
    else:
        parrentFile = PureWindowsPath(path).parent
    for rfile in all_robot_files(project_file(parrentFile)):
        rf = RobotFactory(rfile)
        rfmeta = RFMeta(rfile)
        for keyword in rf.walk(Keyword):
            rfmeta.defs.setdefault(keyword.name, {'line': keyword.linenumber, 'file': rfile})
            for row in keyword.rows:
                for used_keyword in extract_used_keywords(row.cells):
                    rfmeta.uses.setdefault(used_keyword, []).append({'line': row.linenumber, 'file': rfile})
        for table in rf.tables:
            if isinstance(table, SettingTable):
                for statement in table.statements:
                    if statement[0].lower() in ['test setup', 'test teardown', 'suite setup', 'suite teardown', 'test template']:
                        for used_keyword in extract_used_keywords(statement[1:]):
                            rfmeta.uses.setdefault(used_keyword, []).append({'line': statement.startline, 'file': rfile})
            elif isinstance(table, TestcaseTable):
                rfmeta.is_test_data = True
                for testcase in table.testcases:
                    for statement in testcase.statements:
                        for used_keyword in extract_used_keywords(statement):
                            rfmeta.uses.setdefault(used_keyword, []).append({'line': statement.startline, 'file': rfile})
        ret.append(rfmeta)
    return ret


if __name__ == "__main__":
    import doctest
    doctest.testmod()

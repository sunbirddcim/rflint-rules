*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Suite 1
    ${expected} =    Create List
    ...    W: 3, 0: Add a space between the variable and `=` (AssignmentStyle)
    ...    W: 6, 0: Add a space between the variable and `=` (AssignmentStyle)
    ...    W: 9, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 11, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 12, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 16, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    suite.txt    ${expected}

Resource 1
    ${expected} =    Create List
    ...    W: 16, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 3, 0: Add a space between the variable and `=` (AssignmentStyle)
    ...    W: 6, 0: Add a space between the variable and `=` (AssignmentStyle)
    ...    W: 9, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 11, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ...    W: 12, 0: Add an assignment operator `=` after the variable (AssignmentStyle)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    res.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    python -m rflint --rulefile StyleCheckRule.py --ignore all --no-filenames --warn AssignmentStyle "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
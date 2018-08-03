*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Unselect frame statement not in teardown (Resource)
    Check File    unselect_frame_not_in_teardown.txt    W: 3, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Keyword)

Unselect frame statement in teardown (Resource)
    Check File    unselect_frame_in_teardown.txt    ${EMPTY}

Unselect frame statement in teardown (Suite/Keyword)
    Check File    unselect_frame_not_in_teardown(keyword).robot    W: 7, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Keyword)

Unselect frame statement in teardown (Suite/Test)
    Check File    unselect_frame_not_in_teardown(test).robot    W: 3, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Test)

Wait Until Without Setting Timeout (Keyword)
    ${expected} =    Create List    W: 3, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 4, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 5, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 6, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 7, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 8, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 9, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 10, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 11, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    wait_until_without_setting_timeout(keyword).txt    ${expected}

Wait Until Without Setting Timeout (Test)
    ${expected} =    Create List    W: 3, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 4, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 5, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 6, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 7, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 8, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 9, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 10, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 11, 0: Missing timeout argument? (RobustnessCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    wait_until_without_setting_timeout(test).txt    ${expected}

Missing Wait Befor Action (Keyword)
    Check File    missing_wait_before_action(keyword).txt    W: 3, 0: Require waiting before action (RobustnessCheck_Keyword)

Missing Wait Befor Action (Test)
    Check File    missing_wait_before_action(test).txt    W: 3, 0: Require waiting before action (RobustnessCheck_Test)

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile RobustnessCheckRule.py "RobustnessCheckRule/${file}"
    Should Be Equal    ${output}    ${message}
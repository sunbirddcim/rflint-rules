*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Unselect frame statement not in teardown (Resource)
    Check File    unselect_frame_not_in_teardown.txt    W: 3, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Keyword)

Unselect frame statement in teardown (Resource)
    Check File    unselect_frame_in_teardown.txt    ${EMPTY}

Unselect frame statement in teardown (Suite/Keyword)
    Check File    unselect_frame_not_in_teardown(keyword).txt    W: 7, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Keyword)

Unselect frame statement in teardown (Suite/Test)
    Check File    unselect_frame_not_in_teardown(test).txt    W: 3, 0: `Unselect Frame` -> `[Teardown]\ \ \ \ Unselect Frame` (RobustnessCheck_Test)

Wait Until Without Setting Timeout (Keyword)
    ${expected} =    Create List    W: 3, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 3, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 4, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 4, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 5, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 5, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 6, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 6, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 7, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 7, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 8, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 8, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 9, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 9, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 10, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 10, 0: Missing error argument? (RobustnessCheck_Keyword)
    ...    W: 11, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    ...    W: 11, 0: Missing error argument? (RobustnessCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    wait_until_without_setting_timeout(keyword).txt    ${expected}

Wait Until Without Setting Timeout (Test)
    ${expected} =    Create List    W: 3, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 3, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 4, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 4, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 5, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 5, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 6, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 6, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 7, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 7, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 8, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 8, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 9, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 9, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 10, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 10, 0: Missing error argument? (RobustnessCheck_Test)
    ...    W: 11, 0: Missing timeout argument? (RobustnessCheck_Test)
    ...    W: 11, 0: Missing error argument? (RobustnessCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    wait_until_without_setting_timeout(test).txt    ${expected}

Inline IF Robustness Checks (Keyword)
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile RobustnessCheckRule.py "RobustnessCheckRule/inline_if_robustness(keyword).txt"
    Should Contain    ${output}    W: 3, 0: DO NOT USE SLEEP! (RobustnessCheck_Keyword)
    Should Contain    ${output}    W: 4, 0: Missing timeout argument? (RobustnessCheck_Keyword)
    Should Contain    ${output}    W: 4, 0: Missing error argument? (RobustnessCheck_Keyword)
    Should Contain    ${output}    W: 4, 0: use contains(@class, ...) (RobustnessCheck_Keyword)

Inline IF Robustness Checks (Test)
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile RobustnessCheckRule.py "RobustnessCheckRule/inline_if_robustness(test).txt"
    Should Contain    ${output}    W: 3, 0: DO NOT USE SLEEP! (RobustnessCheck_Test)
    Should Contain    ${output}    W: 4, 0: Missing timeout argument? (RobustnessCheck_Test)
    Should Contain    ${output}    W: 4, 0: Missing error argument? (RobustnessCheck_Test)
    Should Contain    ${output}    W: 4, 0: use contains(@class, ...) (RobustnessCheck_Test)

Missing Wait Befor Action (Keyword)
    [Tags]    deprecated
    Check File    missing_wait_before_action(keyword).txt    W: 3, 0: Use keyword `ooo After Waiting` instead. (RobustnessCheck_Keyword)

Missing Wait Befor Action (Test)
    [Tags]    deprecated
    Check File    missing_wait_before_action(test).txt    W: 3, 0: Use keyword `ooo After Waiting` instead. (RobustnessCheck_Test)

Missing Library Prefix (Keyword)
    ${expected} =    Create List    W: 3, 0: Call `Run Keyword\ \ \ \ \${Library}.Get Text` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Keyword)
    ...    W: 4, 0: Call `Run Keyword\ \ \ \ \${Library}.Press Keys` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Keyword)
    ...    W: 5, 0: Call `Run Keyword\ \ \ \ \${Library}.Close Browser` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    library_prefix_missing(keyword).txt    ${expected}

Missing Library Prefix (Test)
    ${expected} =    Create List    W: 2, 0: Call `Run Keyword\ \ \ \ \${Library}.Delete All Cookies` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Test)
    ...    W: 2, 0: Call `Run Keyword\ \ \ \ \${Library}.Close Browser` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Test)
    ...    W: 6, 0: Call `Run Keyword\ \ \ \ \${Library}.Get Element Count` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Test)
    ...    W: 7, 0: Call `Run Keyword\ \ \ \ \${Library}.Go To` to force the SeleniumLibrary version (ambiguous with Browser library). (LibraryPrefixCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    library_prefix_missing(test).txt    ${expected}

Library Prefix Correctly Used
    Check File    library_prefix_ok.txt    ${EMPTY}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile RobustnessCheckRule.py "RobustnessCheckRule/${file}"
    Should Be Equal    ${output}    ${message}
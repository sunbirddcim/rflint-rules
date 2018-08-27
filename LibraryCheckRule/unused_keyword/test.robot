*** Settings ***
Library    OperatingSystem

*** Test Case ***
Case 1
    ${expected} =    Create List
    ...    W: 2, 0: Unused Keyword (UnusedKeyword)
    ...    W: 15, 0: Unused Keyword (UnusedKeyword)
    ...    W: 19, 0: Unused Keyword (UnusedKeyword)
    ...    W: 32, 0: Unused Keyword (UnusedKeyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    case1_run_keywords/suite.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --rulefile LibraryCheckRule.py --ignore all --no-filenames --warn UnusedKeyword "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
*** Settings ***
Library    OperatingSystem

*** Test Case ***
Case 1
    Check File    case1/keywords.txt    W: 2, 0: Move keyword `Action` to file `LibraryCheckRule\\case1\\testsuite1.robot` (LibraryCheck)

Case 2
    Check File    case2/keywords.txt    ${EMPTY}

Case 3
    Check File    case3/keywords.txt    W: 2, 0: Move keyword `Action` to file `LibraryCheckRule\\case3\\suite1\\testsuite1.robot` (LibraryCheck)

Case 4
    Check File    case4/keywords.txt    ${EMPTY}

Case 5
    Check File    case5/keywords.txt    ${EMPTY}

Case 6
    Check File    case6/keywords.txt    W: 2, 0: Move keyword `Action` to folder `LibraryCheckRule\\case6\\suite1` (LibraryCheck)

Case 7
    Check File    case7/keywords.txt    ${EMPTY}

Case 8
    Check File    case8/keywords.txt    ${EMPTY}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile LibraryCheckRule.py "LibraryCheckRule/${file}"
    Should Be Equal    ${output}    ${message}
*** Settings ***
Library    OperatingSystem

*** Test Case ***
Case 1
    ${expected} =    Create List
    ...    W: 2, 0: Duplicated Keyword (name and impl): res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (impl): res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (name): res2.txt:5 (DuplicatedKeyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    case1_same_folder/res1.txt    ${expected}

Case 2
    ${expected} =    Create List
    ...    W: 2, 0: Duplicated Keyword (name and impl): sub\\res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (impl): sub\\res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (name): sub\\res2.txt:5 (DuplicatedKeyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    case2_sub_folder/res1.txt    ${expected}

Case 3
    ${expected} =    Create List
    ...    W: 2, 0: Duplicated Keyword (name and impl): ..\\sub2\\res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (impl): ..\\sub2\\res2.txt:2 (DuplicatedKeyword)
    ...    W: 5, 0: Duplicated Keyword (name): ..\\sub2\\res2.txt:5 (DuplicatedKeyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    case3_sibling/sub1/res1.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --rulefile LibraryCheckRule.py --ignore all --no-filenames --warn DuplicatedKeyword "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
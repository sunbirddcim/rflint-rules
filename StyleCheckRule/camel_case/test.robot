*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Suite
    ${expected} =    Create List
    ...    W: 4, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 12, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 20, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 21, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 23, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    suite.txt    ${expected}

Resource
    ${expected} =    Create List
    ...    W: 2, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 4, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 10, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 12, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 20, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 21, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ...    W: 23, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)

    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    res.txt    ${expected}

Template
    ${expected} =    Create List    W: 3, 0: Keyword name is not Camel Case. (UseCamelCaseKeyword)
    ${expected} =    Evaluate    ''.join(${expected})
    Check File    template.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    python -m rflint --rulefile StyleCheckRule.py --ignore all --no-filenames --warn UseCamelCaseKeyword "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
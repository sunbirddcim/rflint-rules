*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
No assignment operator (Keyword)
    ${expected} =    Create List
    ...    W: 3, 0: Add an assignment operator `=` after the variable (StyleCheck_Keyword)
    ...    W: 5, 0: Add an assignment operator `=` after the variable (StyleCheck_Keyword)
    ...    W: 6, 0: Add an assignment operator `=` after the variable (StyleCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    no_assignment_operator(keyword).txt    ${expected}

No assignment operator (Test)
    ${expected} =    Create List
    ...    W: 3, 0: Add an assignment operator `=` after the variable (StyleCheck_Test)
    ...    W: 5, 0: Add an assignment operator `=` after the variable (StyleCheck_Test)
    ...    W: 6, 0: Add an assignment operator `=` after the variable (StyleCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    no_assignment_operator(test).txt    ${expected}

Assignment operator without a space (Keyword)
    ${expected} =    Create List
    ...    W: 3, 0: Add a apace between the variable and `=` (StyleCheck_Keyword)
    ...    W: 6, 0: Add a apace between the variable and `=` (StyleCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    assignment_operator_without_a_space(keyword).txt    ${expected}

Assignment operator without a space (Test)
    ${expected} =    Create List
    ...    W: 3, 0: Add a apace between the variable and `=` (StyleCheck_Test)
    ...    W: 6, 0: Add a apace between the variable and `=` (StyleCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    assignment_operator_without_a_space(test).txt    ${expected}

Name Check (Keyword)
    ${expected} =    Create List
    ...    W: 2, 0: Keyword name is not CamelCase (StyleCheck_Keyword)
    ...    W: 8, 0: Keyword name is not CamelCase (StyleCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    name(keyword).txt    ${expected}

Name Check (Test)
    Check File    name(test).txt    ${EMPTY}

Statement camal case (keyword)
    ${expected} =    Create List
    ...    W: 4, 0: Keyword name is not CamelCase (StyleCheck_Keyword)
    ...    W: 5, 0: Keyword name is not CamelCase (StyleCheck_Keyword)
    ...    W: 7, 0: Keyword name is not CamelCase (StyleCheck_Keyword)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    statement_camal_case(keyword).txt    ${expected}

Statement camal case (Test)
    ${expected} =    Create List
    ...    W: 4, 0: Keyword name is not CamelCase (StyleCheck_Test)
    ...    W: 5, 0: Keyword name is not CamelCase (StyleCheck_Test)
    ...    W: 7, 0: Keyword name is not CamelCase (StyleCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    statement_camal_case(test).txt    ${expected}

No using logoff
    ${expected} =    Create List
    ...    W: 2, 0: Use keyword `Logoff` instead. (StyleCheck_Test)
    ...    W: 4, 0: Use keyword `Logoff` instead. (StyleCheck_Test)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    no_using_logoff.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    rflint --ignore all --no-filenames --rulefile StyleCheckRule.py "StyleCheckRule/${file}"
    Should Be Equal    ${output}    ${message}
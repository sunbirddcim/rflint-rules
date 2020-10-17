*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Suite 1
    ${expected} =    Create List
    ...    W: 3, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 4, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 5, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 7, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 8, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 9, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    suite1.txt    ${expected}

Suite 2
    Check File    suite2.txt    W: 1, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)

Resource 1
    ${expected} =    Create List
    ...    W: 1, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 3, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 4, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ...    W: 7, 0: Trailing whiteSpace. (TrailingWhiteSpaceIgnoreCarriegeReturn)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    res1.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    python -m rflint --rulefile StyleCheckRule.py --ignore all --no-filenames --warn TrailingWhiteSpaceIgnoreCarriegeReturn "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
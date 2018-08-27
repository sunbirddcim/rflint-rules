*** Settings ***
Library    OperatingSystem
Library    Collections

*** Test Case ***
Suite
    ${expected} =    Create List
    ...    W: 2, 0: Use keyword `Logoff` instead. (UseLogoff)
    ...    W: 4, 0: Use keyword `Logoff` instead. (UseLogoff)
    ${expected} =    Evaluate    '\\n'.join(${expected})
    Check File    no_using_logoff.txt    ${expected}

*** Keywords ***
Check File
    [Arguments]    ${file}    ${message}
    ${output} =    Run    python -m rflint --rulefile StyleCheckRule.py --ignore all --no-filenames --warn UseLogoff "${CURDIR}/${file}"
    Should Be Equal    ${output}    ${message}
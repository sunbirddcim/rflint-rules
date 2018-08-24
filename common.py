import re

def extract_name(statement):
    """
    >>> extract_name([''])
    ''
    >>> extract_name(['', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '\\\\', 'Click Element'])
    'Click Element'
    >>> extract_name(['', '${x}', 'Get X'])
    'Get X'
    >>> extract_name(['', '${x}', '${y} =', 'Get Position'])
    'Get Position'
    >>> extract_name(['# Hello'])
    '# Hello'
    >>> extract_name(['Given An Apple'])
    'An Apple'
    >>> extract_name(['When Snow White Eat'])
    'Snow White Eat'
    >>> extract_name(['Then She Is Happy'])
    'She Is Happy'
    """
    for token in statement:
        if token in ['', '\\']:
            continue
        if not re.match(r'[@$&]\{[^\}]+\}.*', token):
            for bdd_token in ['given', 'when', 'then']:
                if token.lower().startswith(bdd_token):
                    return token[len(bdd_token):].strip()
            return token
    return statement[0]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
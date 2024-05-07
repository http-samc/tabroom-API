import re

def enum_to_string(string: str | None) -> str:
    if string is None:
        return string
    match = re.findall('[A-Z][^A-Z]*', string)
    return " ".join(match) if match is not None else string
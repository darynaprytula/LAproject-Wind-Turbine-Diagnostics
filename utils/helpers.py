import re

def clean_name(name: str) -> str:
    """
    Clean string for safe file/folder names.

    parameters:
    name - input string

    returns:
    cleaned string
    """

    name = str(name)
    name = re.sub(r'[\\/*?:"<>|]', "_", name)
    name = name.replace(" ", "_")
    return name

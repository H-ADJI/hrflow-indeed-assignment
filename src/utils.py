from dataclasses import dataclass

from dotenv import dotenv_values

__CONFIG = dotenv_values(".env")


@dataclass
class EnvSettings:
    """Class to import environment variables"""

    API_KEY: str
    USER_EMAIL: str
    BOARD_KEY: str


env_settings = EnvSettings(**__CONFIG)


def nested_get(dictionary: dict, query: str):
    """retrieve data from dictionary with jmespath like query syntax

    Args:
        dictionary (dict): data dictionary
        query (str): keys separated by '.'

    Returns:
        Any: data if exists
    """
    keys = query.split(".")
    for key in keys:
        value = dictionary.get(key)
        if isinstance(value, dict):
            dictionary = value
        if not value:
            return None
    return value

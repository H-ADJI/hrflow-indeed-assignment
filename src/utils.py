from dataclasses import dataclass

from dotenv import dotenv_values

__CONFIG = dotenv_values(".env")


@dataclass
class EnvSettings:
    API_KEY: str
    USER_EMAIL: str
    BOARD_KEY: str


env_settings = EnvSettings(**__CONFIG)


def nested_get(dictionary: dict, query: str):
    keys = query.split(".")
    for key in keys:
        value = dictionary.get(key)
        if isinstance(value, dict):
            dictionary = value
        if not value:
            return None
    return value

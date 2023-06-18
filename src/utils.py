def nested_get(dictionary: dict, query: str):
    keys = query.split(".")
    for key in keys:
        value = dictionary.get(key)
        if isinstance(value, dict):
            dictionary = value
        if not value:
            return None
    return value
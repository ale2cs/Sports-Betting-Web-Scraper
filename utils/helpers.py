def add_dec(string):
    if string.isdigit():
        string = f"{string}.0"
    return string


def flatten(list_to_flatten):
    return [item for sub_list in list_to_flatten for item in sub_list]

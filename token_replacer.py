import os
import re
import json


def replace_tokens_in_file(in_file, tokens, out_file=None, delete_after=False):
    if not out_file:
        out_file = in_file
    with open(in_file, "r") as file:
        content = file.read()

    pattern = re.compile(r"\[\[.+\]\]")

    # check if we have values for all of the tokens in the file
    # if not throw an exception
    for match in re.findall(pattern, content):
        key = remove_delimiters_from_key(match)
        if key not in tokens:
            raise Exception("Unknown key: " + key)

    content_replaced = pattern.sub(lambda x: str(tokens[remove_delimiters_from_key(x.group())]), content)

    with open(out_file, "w") as file:
        file.write(content_replaced)

    if delete_after:
        os.remove(in_file)

    return True


def remove_delimiters_from_key(key):
    return key.replace("[[", "").replace("]]", "")

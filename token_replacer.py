import os
import re


TOKEN_REGEX = re.compile(r"\[\[.+?\]\]")


def replace_tokens_in_file(in_file, tokens, out_file=None, delete_after=False):
    if not out_file:
        out_file = in_file
    with open(in_file, "r") as file:
        content = file.read()

    content_replaced = replace_tokens_in_string(content, tokens)

    with open(out_file, "w") as file:
        file.write(content_replaced)

    if delete_after:
        os.remove(in_file)

    return True


def replace_tokens_in_dict(dict, tokens):
    out_dict = dict()

    for key, value in out_dict.items():
        out_dict[key] = replace_tokens_in_string(value, tokens)

    return out_dict


def replace_tokens_in_string(string, tokens):
    for match in re.findall(TOKEN_REGEX, string):
        key = remove_delimiters_from_key(match)
        if key not in tokens:
            raise Exception("Unknown key: " + key)

    return TOKEN_REGEX.sub(lambda x: str(tokens[remove_delimiters_from_key(x.group())]), string)


def remove_delimiters_from_key(key):
    return key.replace("[[", "").replace("]]", "")

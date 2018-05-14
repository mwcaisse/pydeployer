import re
import json


def replace_tokens_in_file(in_file, tokens, out_file=None):
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

    return True


def remove_delimiters_from_key(key):
    return key.replace("[[", "").replace("]]", "")


def test():

    with open("./build_tokens.json", "r") as build_tokens_file:
        tokens = json.load(build_tokens_file)

    replace_tokens_in_file("./buildInformation_repl.pyb", tokens)


if __name__ == "__main__":
    test()



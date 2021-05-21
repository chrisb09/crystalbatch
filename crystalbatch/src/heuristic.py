from . import vocabulary

_REPLACE_SYMBOLS = [
    "^",
    "°",
    "′",
    "!",
    '"',
    "@",
    "§",
    "$",
    "%",
    "&",
    "/",
    "(",
    ")",
    "¬",
    "{",
    "[",
    "]",
    "}",
    "=",
    "?",
    "´",
    "`",
    "+",
    "*",
    "#",
    "|",
    "'",
    "’",
    "–",
    "~",
    "˝",
    "·",
    "…",
    "_",
    "-",
    ".",
    ",",
    "<",
    ">",
]


def rate_name(name, word_set):
    score = 0.0
    temp_name = name.lower()
    for s in _REPLACE_SYMBOLS:
        temp_name = temp_name.replace(s, " ")
    print(temp_name)
    for substring in temp_name.split():
        if substring in word_set:
            print(substring)
            score += len(substring) ** 2
    print(score)
    print(len(temp_name) ** 1.41 + 20)
    score = max(min(score / (len(temp_name) ** 1.41 + 20), 1.0), 0.0)
    return score

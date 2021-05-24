import os

from . import configuration


def list_available_dictionaries():
    dictionaries = {}
    for root, _, files in os.walk(
        os.path.abspath(os.path.join(configuration.root_dir, "res/language/"))
    ):
        for filename in files:
            if filename.endswith(".txt"):
                lines = 0
                for line in open(os.path.join(root, filename), encoding="'iso-8859-1'"):
                    lines += 1
                bare_name, file_extension = os.path.splitext(filename)
                dictionaries[bare_name] = lines
    return dictionaries


def read_words(dictionary_list):
    combined_word_set = set()
    dirname = configuration.root_dir
    for dictionary in dictionary_list:
        text_file = open(
            os.path.join(dirname, "res/language/" + dictionary + ".txt"),
            "r",
            encoding="'iso-8859-1'",
        )
        for line in text_file.readlines():
            combined_word_set.add(line.strip().lower())
        text_file.close()
    return combined_word_set

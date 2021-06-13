# -*- coding: utf-8 -*-
#!/bin/python3

#from crystalbatch.src import old

from crystalbatch.src import vocabulary, language, heuristic, edit_config
from crystalbatch.src.tkinter_helper import tkinter_json_loader
#from crystalbatch.src import selection
import versioneer as versioneer

print("Version: "+versioneer.get_version())

print(vocabulary.list_available_dictionaries())

word_set = vocabulary.read_words(["deutsch", "english"])

print(len(word_set))
#print(language.used_languages)

#print(heuristic.rate_name("test", word_set))

#selection

edit_config.open_window()
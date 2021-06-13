from .tkinter_helper import tkinter_json_loader, popup
from . import language, configuration

import tkinter as tk
from tkinter import *
from functools import partial

widget_tree = None

def callback_folder_select(entry):
    res = popup.get_dir(mustexist=True)
    if str == type(res) and len(res) > 0:
        entry.delete(0, END)
        entry.insert(0, res)

def _callback_remove_from_notebook(child):
    widget_tree.get(["Window","main_section_frame","right_side","pairing_frame","pairing_notebook"]).forget(child)

def _overwrite_entry(entry, text):
    if text is not None:
        entry.delete(0, END)
        entry.insert(0, text)

def _callback_add_to_notebook(notebook, source_dir=None, target_dir=None):
    amount_of_children = int(notebook.index("end"))
    _widget_tree = tkinter_json_loader.add_json_child(notebook, "crystalbatch/res/gui/edit_config.json", configuration.config, language.translation_json, keys=["Notebook"])
    _widget = _widget_tree.get([_widget_tree.name])

    #add command to button
    _source_entry = _widget_tree.get([_widget_tree.name, "source_entry"])
    _source_button = _widget_tree.get([_widget_tree.name, "source_entry_button"])
    _source_button.configure(command=partial(callback_folder_select, _source_entry))
    _overwrite_entry(_source_entry, source_dir)
    
    _target_entry = _widget_tree.get([_widget_tree.name, "target_entry"])
    _target_button = _widget_tree.get([_widget_tree.name, "target_entry_button"])
    _target_button.configure(command=partial(callback_folder_select, _target_entry))
    _overwrite_entry(_target_entry, target_dir)


    #print(notebook.winfo_name())
    #print(l.get([l.name]).winfo_name())
    #print(notebook.winfo_children())

    #add to notebook
    notebook.add(_widget, text=language.translation_json["Content"]["pairing"]+" #"+str(1+amount_of_children))
    
    

    #print(notebook.tabs())
    #print(_widget.winfo_pathname(_widget.winfo_id()))

    #take focus
    notebook.select([_widget.winfo_pathname(_widget.winfo_id())])

def _add_config_pairs(notebook, config):
    
    for general_key in dict(config).keys():
        if general_key.startswith("Pair "):
            source_dir = config.get(general_key, "source")
            target_dir = config.get(general_key, "target")
            #media_module_settings = config.get(pair_section, "settings")
            #selection_regex = config.get(pair_section, "regex")
            #rename_template = config.get(pair_section, "template")
            _callback_add_to_notebook(notebook, source_dir=source_dir, target_dir=target_dir)



def open_window():
    window = tk.Tk()
    window.title("Crystal batch file renamer")

    #window.minsize()
    window.minsize(800, 600)
    window.geometry(str(window.winfo_screenwidth() // 2) + "x" + str(window.winfo_screenheight() // 2))

    window.tk.call(
        "wm", "iconphoto", window._w, tk.PhotoImage(file="logos/vectorgraphic gen 2/black border 5px.png")
    )

    global widget_tree
    widget_tree = tkinter_json_loader.add_json_to_root(window, "crystalbatch/res/gui/edit_config.json", configuration.config, language.translation_json)

    widget_tree.get(["Window","top_text_frame","top_text"]).bind(
        "<Configure>", lambda e: widget_tree.get(["Window","top_text_frame","top_text"]).configure(width=window.winfo_width() - 10)
    )

    tkinter_json_loader.register_callback(["edit_config","add_pair"], _callback_add_to_notebook, widget_tree.get(["Window","main_section_frame","right_side","pairing_frame","pairing_notebook"]))

    s = ttk.Style()
    s.configure('Notebook', foreground='maroon')

    _add_config_pairs(widget_tree.get(["Window","main_section_frame","right_side","pairing_frame","pairing_notebook"]), configuration.config)

    print(tkinter_json_loader._callback_cache)

    window.mainloop()
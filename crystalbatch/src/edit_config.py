from .tkinter_helper import tkinter_json_loader, popup
from . import language, configuration

import tkinter as tk
from tkinter import *
from functools import partial

widget_tree = None

_allowed_chars = [("a","z"),("A","Z"),("0","9"),{"-","_"," ","#","=","/","!","§","$","%","&","(",")",":"}]

_tab_names = {}

def _name_allowed(notebook, tab_id, new_name):
    if new_name is None or not type(new_name) == type(str()) or len(new_name) == 0:
        return False
    for _tab_id in notebook.tabs():
        if not _tab_id == tab_id:
            if _tab_id in _tab_names:
                if _tab_names[_tab_id] == new_name:
                    return False
            else:
                print(str(_tab_id)+" is missing...")
        for c in new_name:
            accepted = False
            for a in _allowed_chars:
                if type(a) == type(tuple()):
                    if a[0] <= c <= a[1]:
                        accepted = TRUE
                        continue
                if type(a) == type(set()):
                    if c in a:
                        accepted = True
                        continue
            if accepted == False:
                return False
    return True
        
def callback_switch_states(state, *widgets):
    if state.get() == 1:
        for w in widgets:
            w.configure(state=tk.NORMAL)
    else:
        for w in widgets:
            w.configure(state=tk.DISABLED)
    for w in widgets:
        #print("P:"+str(w.winfo_children()))
        for c in w.winfo_children():
            #print("C:" +str(c))
            callback_switch_states(state, w.get([w.name,c]))

def callback_change_pairing_name(state, notebook, entry):
    tab_id = notebook.select()
    text = language.translation_json["Content"]["pairing"]+" #"+str(1+(notebook.tabs().index(tab_id)))
    offset = 0
    while not _name_allowed(notebook, tab_id, text):
        offset += 1
        text = language.translation_json["Content"]["pairing"]+" #"+str(offset)
    if state.get() == 1:
        new_name = entry.get()
        if _name_allowed(notebook, tab_id, new_name):
            text = new_name
        else:
            popup.warning(title=language.translation_json["Content"]["pairing_name_wrong_title"],message=language.translation_json["Content"]["pairing_name_wrong_message"]+str(_allowed_chars))
    notebook.tab(tab_id, text=text)
    _tab_names[tab_id] = text


def callback_custom_name_checkbutton(state, notebook, entry, button):
    callback_switch_states(state, entry, button)
    if state.get() == 0:
        callback_change_pairing_name(state, notebook, entry)

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

def _callback_add_to_notebook(notebook, name=None, source_dir=None, target_dir=None):
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

    _custom_name_checkbutton = _widget_tree.get([_widget_tree.name, "custom_pairing_name_checkbutton"])
    _custom_name_checkbutton_variable = IntVar()
    _custom_name_checkbutton.configure(variable=_custom_name_checkbutton_variable)
    _custom_name_entry = _widget_tree.get([_widget_tree.name, "custom_pairing_name_entry"])
    _custom_pairing_name_button = _widget_tree.get([_widget_tree.name, "custom_pairing_name_button"])
    _custom_pairing_name_button.configure(command=partial(callback_change_pairing_name, _custom_name_checkbutton_variable, notebook, _custom_name_entry))
    _custom_name_checkbutton.select()
    #_custom_name_checkbutton.configure(command=partial(callback_switch_states, _custom_name_checkbutton_variable, _custom_name_entry, _custom_pairing_name_button))
    _custom_name_checkbutton.configure(command=partial(callback_custom_name_checkbutton, _custom_name_checkbutton_variable, notebook, _custom_name_entry, _custom_pairing_name_button))


    if name is None:
        offset = 0
        name = ""
        while not _name_allowed(notebook, 0, name):
            offset += 1
            name = language.translation_json["Content"]["pairing"]+" #"+str(offset+amount_of_children)
        _custom_name_entry.delete(0, END)
        _custom_name_entry.insert(0, name)
        notebook.add(_widget, text=name)
        notebook.select([_widget.winfo_pathname(_widget.winfo_id())])
        _tab_names[_widget.winfo_pathname(_widget.winfo_id())] = name
        _custom_name_checkbutton.invoke()
    else:
        notebook.add(_widget, text=name)
        _tab_names[_widget.winfo_pathname(_widget.winfo_id())] = name
        notebook.select([_widget.winfo_pathname(_widget.winfo_id())])
    #print(name)


    #print("Name: "+str(notebook.winfo_name()))
    #print("Id: "+str(notebook.winfo_id()))
    #print("Path:"+str(notebook.winfo_pathname(notebook.winfo_id())))
    #print(notebook.winfo_name())
    #print(l.get([l.name]).winfo_name())
    #print(notebook.winfo_children())

    #add to notebook
    
    

    #print(notebook.tabs())
    #print(_widget.winfo_pathname(_widget.winfo_id()))

    #take focus

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

    #print(tkinter_json_loader._callback_cache)

    window.mainloop()
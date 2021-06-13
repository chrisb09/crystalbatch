# -*- coding: utf-8 -*-

import os, json

import tkinter as tk
from tkinter import *
from tkinter import ttk
from functools import partial

from .tooltip import Tooltip
from .selectionbox import Selectionbox
from . import popup

_config_value_cache = {}
_callback_cache = {}

def _link_config_value(key_general, key_specific, config, value_type):
    if key_general in _config_value_cache:
        if key_specific in _config_value_cache[key_general]:
            return _config_value_cache[key_general][key_specific]
    else:
        if config.get("General","log_level_debug") == "True":
            print("Linked values:")
        _config_value_cache[key_general] = {}
    value = None
    _value = config.get(key_general, key_specific)
    if value_type == "str":
        value = StringVar()
        value.set(str(_value))
    elif value_type == "bool":
        value = BooleanVar()
        value.set(str(_value) == "True")  # ...python ladies and gents...
    elif value_type == "int":
        value = IntVar()
        value.set(int(_value))
    _config_value_cache[key_general][key_specific] = value
    if config.get("General","log_level_debug") == "True":
        print("[" + key_general + "][" + key_specific + "]: " + str(value.get()))
    return value


def _write_back_cache_to_config():
    for key_general in _config_value_cache:
        for key_specific in _config_value_cache[key_general]:
            config.set(
                key_general,
                key_specific,
                str(_config_value_cache[key_general][key_specific]),
            )

def _register_callback(dic, keys, callback, widget):
    if len(keys) == 0:
        return #undefined
    elif len(keys) == 1:
        dic[keys[0]] = (callback, widget)
    else:
        if keys[0] not in dic:
            dic[keys[0]] = {}
        _register_callback(dic[keys[0]], keys[1:], callback, widget)


def register_callback(keys, callback, widget):
    _register_callback(_callback_cache, keys, callback, widget)
    

def _call_callback(keys, dic=_callback_cache):
    if len(keys) == 0:
        return
    elif len(keys) == 1:
        if keys[0] in dic:
            current = dic[keys[0]]
            current[0](current[1])
        else:
            if config.get("General","log_level_debug") == "True":
                print("Key '"+keys[0]+"' not found!")
    else:
        if keys[0] in dic:
            _call_callback(keys[1:], dic[keys[0]])


class WidgetTree:
    name = None
    widget = None
    children = {}

    def __init__(self, name, widget, children):
        self.name = name
        self.widget = widget
        self.children = children

    def get(self, keys):
        if len(keys) == 1:
            if keys[0] == self.name:
                return self.widget
            else:
                print("Key error!")
                exit()
        else:
            if keys[1] in self.children:
                return self.children[keys[1]].get(keys[1:])
            else:
                print("No child matches name '" + keys[1] + "'")

    def print(self, counter=0):
        print(" " * (4 * counter) + self.name + ": " + str(type(self.widget)))
        for k in self.children:
            self.children[k].print(counter + 1)


def _read_in_json(path):
    if os.path.exists(path):
        _opened_file = open(path, "r", encoding="'iso-8859-1'")
        _json = json.loads(_opened_file.read())
        _opened_file.close()
        return _json
    else:
        print("Path '"+_path+"'does not exist!")
        return None

def _get_json_file(keys):
    _json = None
    _dic = _json_cache
    missing = False
    for k in keys:
        if k in _dic:
            _dic = _dic[k]
        else:
            missing = True
            break
    if missing or "" not in _dic:
        _path = _basedir
        return _read_in_json(keys=keys)
    return _dic[""]



def add_to_config(config, path, overwrite=True):
    _json = _read_in_json(path=path)
    has_something_been_changed = False
    if "Configuration" in _json:
        for general_key in _json["Configuration"]:
            for specific_key in _json["Configuration"][general_key]:
                write = True
                if not overwrite:
                    if general_key in dict(config).keys():
                        if specific_key in dict(config[general_key]).keys():
                            write = False
                if write:
                    value = _json["Configuration"][general_key][specific_key]
                    if type(value) == list:
                        value = ",".join(value)
                    config.set(
                        general_key,
                        specific_key,
                        value
                    )
                    has_something_been_changed = True
    return has_something_been_changed


def _typecast(value, typecast):
    if typecast == "int":
        value = int(value)
    elif typecast == "bool":
        value = value == "True"  # python...
    elif typecast == "list":
        value = value.split(",")
    return value


def _forge_new_keylist(keys, key):
    keys = keys.copy()
    keys.append(key)
    return keys


def _get_value_from_dict(_dict_tmp, keys):
    if len(keys) > 0:
        if keys[0] in _dict_tmp:
            return _get_value_from_dict(_dict_tmp[keys[0]], keys[1:])
        else:
            print(str(keys[0])+" not in "+str(_dict_tmp))
            return None
    else:
        return _dict_tmp


def _get_translation_value(_json, keys, config, translation):
    translation_keys = _get_value(_json, keys, config, translation, "keys")
    result =_get_value_from_dict(translation, translation_keys)
    if result is not None:
        return result
    return "Undefined"


def _get_config_link(_json, keys, config, translation):
    return _link_config_value(_get_value(_json, keys, config, translation, "key_general"),
    _get_value(_json, keys, config, translation, "key_specific"),
    config,
    _get_value(_json, keys, config, translation, "typecast"))

def _get_callback(_json, keys, config, translation):
    return lambda: _call_callback(keys=_get_value(_json, keys, config, translation, "keys"))
    

def _get_config_value(_json, keys, config, translation):
    current = _get_value_from_dict(_json, keys)
    value = config.get(_get_value(_json, keys, config, translation, "key_general"),
    _get_value(_json, keys, config, translation, "key_specific"))
    if "typecast" in current:
        value = _typecast(value, _get_value(_json, keys, config, translation, "typecast"))
    return value


def _get_value(_json, keys, config, translation, key=None, disable_type=False):
    if key is not None:
        keys = _forge_new_keylist(keys, key)
    value = _get_value_from_dict(_json, keys)
    if type(value) is dict:
        if "type" in value:
            current = _get_value(_json, keys, config, translation, "type")
            if current == "config":
                return _get_config_value(_json, keys, config, translation)
            elif current == "config_link":
                return _get_config_link(_json, keys, config, translation)
            elif current == "translation":
                return _get_translation_value(_json, keys, config, translation)
            elif current == "callback":
                return _get_callback(_json, keys, config, translation)
            elif current == "function":
                pass
    return value


def _get_params(_json, keys, config, translation, key="parameter"):
    current = _get_value_from_dict(_json, keys)
    params = {}
    _keys = _forge_new_keylist(keys, key)
    if key in current:
        for k in _get_value(_json, keys, config, translation, key):
            params[k] = _get_value(_json, _keys, config, translation, key=k)
    return params


def _create_widget(parent, _json, keys, config, translation):
    widget = None
    widget_params = _get_params(_json, keys, config, translation)
    current = _get_value_from_dict(_json, keys)
    widget_type = _get_value(_json, keys, config, translation, "type")
    #tk widgets
    if widget_type == "Button":
        widget = Button(parent, **widget_params)
    elif widget_type == "Checkbutton":
        widget = Checkbutton(parent, **widget_params)
    elif widget_type == "Combobox":
        widget = ttk.Combobox(parent, **widget_params)
    elif widget_type == "Entry":
        widget = Entry(parent, **widget_params)
    elif widget_type == "Frame":
        widget = Frame(parent, **widget_params)
    elif widget_type == "Label":
        widget = Label(parent, **widget_params)
    elif widget_type == "LabelFrame":
        widget = LabelFrame(parent, **widget_params)
    elif widget_type == "Menubutton":
        widget = Menubutton(parent, **widget_params)
    elif widget_type == "Message":
        widget = Message(parent, **widget_params)
    elif widget_type == "Notebook":
        widget = ttk.Notebook(parent, **widget_params)
    elif widget_type == "PanedWindow":
        widget = PanedWindow(parent, **widget_params)
    elif widget_type == "Progressbar":
        widget = Progressbar(parent, **widget_params)
    elif widget_type == "Radiobutton":
        widget = Radiobutton(parent, **widget_params)
    elif widget_type == "Scale":
        widget = Scale(parent, **widget_params)
    elif widget_type == "Scrollbar":
        widget = Scrollbar(parent, **widget_params)
    elif widget_type == "Seperator":
        widget = Seperator(parent, **widget_params)
    elif widget_type == "Sizegrip":
        widget = Sizegrip(parent, **widget_params)
    elif widget_type == "Tooltip":
        widget = Tooltip(parent, **widget_params)
    elif widget_type == "Treeview":
        widget = Treeview(parent, **widget_params)
    #self defined widgets
    elif widget_type == "Selectionbox": #based on combobox
        widget = Selectionbox(parent, **widget_params)

    return widget


def _setup_grid(widget, _json, keys, config, translation):
    current = _get_value_from_dict(_json, keys)
    if "column_weights" in current:
        for i in range(len(_get_value(_json, keys, config, translation, "column_weights"))):
            weight = _get_value(_json, keys, config, translation, "column_weights") [i]
            widget.grid_columnconfigure(i, weight=weight)
    if "row_weights" in current:
        for i in range(len(_get_value(_json, keys, config, translation, "row_weights"))):
            weight = _get_value(_json, keys, config, translation, "row_weights")[i]
            widget.grid_rowconfigure(i, weight=weight)


def _configure_widget(widget, _json, keys, config, translation):
    current = _get_value_from_dict(_json, keys)
    if "configure" in current:
        values = {}
        _keys = _forge_new_keylist(keys, "configure")
        for k in _get_value(_json, keys, config, translation, "configure"):
            values[k] = _get_value(_json, _keys, config, translation, k)
        widget.configure(values)


def _place_widget(widget, _json, keys, config, translation):
    current = _get_value_from_dict(_json, keys)
    if "display_type" in current:
        display_type = _get_value(_json, keys, config, translation, "display_type")
        display_params = _get_params(
            _json, keys, config, translation, key="display_parameter"
        )
        if display_type == "grid":
            widget.grid(display_params)
        elif display_type == "pack":
            widget.pack(display_params)
        elif display_type == "place":
            widget.place(display_params)


def _create_children(widget, _json, keys, config, translation, key="children"):
    current = _get_value_from_dict(_json, keys)
    _children = {}
    if key in current:
        _keys = _forge_new_keylist(keys, key)
        _keylist = []
        for k in _get_value(_json, keys, config, translation, key):
            _keylist.append(k)
        # sort with the help of optional "priority" number
        _keylist.sort(
            key=lambda k: "priority" in _get_value(_json, keys, config, translation, key)[k] and _get_value(_json, keys, config, translation, key)[k]["priority"],
            reverse=True,
        )
        for k in _keylist:
            _children[k] = add_json_to_widget(
                widget, _json, _forge_new_keylist(_keys, k), config, translation
            )
    return _children


def fill_widget(widget, _json, keys, config, translation):
    _setup_grid(widget, _json, keys, config, translation)
    _configure_widget(widget, _json, keys, config, translation)
    _place_widget(widget, _json, keys, config, translation)
    return WidgetTree(
        keys[-1], widget, _create_children(widget, _json, keys, config, translation)
    )


# parent is the parent widget
# json contains the entirety of the config file
# keys is a list of strings that tells us which section of the config is currently relevant
def add_json_to_widget(parent, _json, keys, config, translation):
    widget = _create_widget(parent, _json, keys, config, translation)
    return fill_widget(widget, _json, keys, config, translation)


def add_json_to_root(root, path, config, translation, keys=["Window"]):
    _json = _read_in_json(path=path)
    if _json is not None:
        widget_tree = fill_widget(root, _json, keys, config, translation)
        if config.get("General","log_level_debug") == "True":
            widget_tree.print()
        return widget_tree
    else:
        popup.error("Problem!", "'" + path + "' does not exist!")
        exit()

def add_json_child(root, path, config, translation, keys):
    _json = _read_in_json(path=path)
    if _json is not None:
        return add_json_to_widget(root, _json, keys, config, translation)
    return None
import configparser, os

from . import language
from .tkinter_helper import tkinter_json_loader

config_path = "config.ini"
configuration = {}
config = None

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
print(root_dir)

def _add_available_languages():
    s = ",".join(language.list_available_translation_names())
    print("S:")
    print(s)
    config.set("General", "available_translation", s)

def _check_if_config_exists():
    return os.path.exists(config_path)


def _write_config():
    global config
    cfgfile = open(config_path, "w")
    if config is None:
        config = configparser.ConfigParser()
    if len(config.sections()) == 0:
        config.add_section("General")
        config.set("General", "log_level_debug", "True")
        config.set(
            "General",
            "selected_translation", language.get_translation_by_locale(language.default_language)[0]
        )
        _add_available_languages()
        tkinter_json_loader.add_to_config(config, os.path.join(root_dir, "res/gui/edit_config.json"))

    config.write(cfgfile)
    cfgfile.close()


def _update_from_config():
    if "General" in config.sections():
        if "root_path" in dict(config["General"]).keys():
            global root_dir
            root_dir = config.get("General", "root_path")
        if "selected_translation" in dict(config["General"]).keys():
            language.load_translation_by_keyword(
                config.get("General", "selected_translation")
            )
            print(
                "Language '"
                + config.get("General", "selected_translation")
                + "' loaded successfully!"
            )
        _add_available_languages()
        if tkinter_json_loader.add_to_config(config, os.path.join(root_dir, "res/gui/edit_config.json"), overwrite=False):
            _write_config()


def read_config():
    global config, configuration
    if not _check_if_config_exists():
        print("Create config file '" + os.path.abspath(config_path) + "'")
        _write_config()
    else:
        config = configparser.ConfigParser()
        config.read(config_path)
        print("Read in config file: '" + os.path.abspath(config_path) + "'")
        for section in config.sections():
            configuration[section] = dict(config[section])
            print(section)
            print(dict(config[section]))
        _update_from_config()


def add_pair(
    pair_name,
    source_dir,
    target_dir,
    media_module_settings,
    selection_regex,
    rename_template,
):
    global config
    pair_section = "Pair " + pair_name
    config.add_section(pair_section)
    config.set(pair_section, "source", source_dir)
    config.set(pair_section, "target", target_dir)
    config.set(pair_section, "settings", media_module_settings)
    config.set(pair_section, "regex", selection_regex)
    config.set(pair_section, "template", rename_template)
    _write_config()


read_config()

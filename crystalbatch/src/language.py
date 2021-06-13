"""Used to get a set 'used_languages' that contains default language selections for a source-target folder pairs wordlists.
Can also provide a default value for the interface language."""
import platform, os, locale, json

from .tkinter_helper import popup


def _check_locale(loc, used_languages):
    if loc is not None:
        for locale_prefix in _locale_language_map:
            if loc.startswith(locale_prefix):
                used_languages.add(_locale_language_map[locale_prefix])
                global default_language
                if default_language is None:
                    default_language = loc[:5]
                break
    return used_languages

def list_available_translation_names():
    return [name for name,_,_ in list_available_translations()]

def list_available_translations():
    translations = []
    for root, _, files in os.walk(
        os.path.abspath(os.path.join(root_dir, "res/gui/language/"))
    ):
        for filename in files:
            if filename.endswith(".json"):
                try:
                    _opened_file = open(
                        os.path.join(root, filename), "r", encoding="'iso-8859-1'"
                    )
                    _translation_json = json.loads(_opened_file.read())
                    translation_name = _translation_json["General"]["language"]
                    translation_locale = _translation_json["General"]["locale"]
                    _opened_file.close()
                    translations.append(
                        (
                            translation_name,
                            translation_locale,
                            os.path.join(root, filename),
                        )
                    )  # (name, locale, path)
                except:
                    print("Failed to open '" + filename + "'.")
    return translations


def get_translation_by_locale(locale):
    if locale is None:
        return

    translations = list_available_translations()

    print(locale)

    selected_translation = None
    # 1. check for exact locale matchings
    for translation in translations:
        _, loc, _ = translation
        if locale == loc:
            selected_translation = translation
            break

    # 2 check for prefix matching
    if selected_translation is None:
        for translation in translations:
            _, loc, _ = translation
            if locale.startswith(loc):
                selected_translation = translation
                break

    # 3 fall back to english if nothing found
    if selected_translation is None:
        for translation in translations:
            _, loc, _ = translation
            if loc.startswith("en"):
                selected_translation = translation
                break

    # 4 get first translation in list
    if selected_translation is None and len(translations) > 0:
        popup.warning(
            "Attention!",
            "Language configuration is broken. Language was selected at random!",
        )
        selected_translation = translations[0]

    # 5 show error and exit if still no translation available
    if selected_translation is None:
        popup.error(
            "Critical error!",
            "There are no language/translation json files available. The GUI cannot be run without text to be displayed!",
        )
        exit()

    load_translation(selected_translation[2])  # path

    return selected_translation


def load_translation_by_keyword(
    keyword,
):  # load a language, keyword could be 'English' or 'Deutsch' etc.
    for (name, _, path) in list_available_translations():
        if name == keyword:
            print("Load '"+path+"'")
            load_translation(path)
            break


def load_translation(path):
    global translation_json
    _opened_file = open(path, "r", encoding="'iso-8859-1'")
    translation_json = json.loads(_opened_file.read())
    _opened_file.close()


translation_json = None

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

operating_system = platform.system()

used_languages = set()
default_language = None

_opened_file = open(os.path.join(root_dir, "res/language/language_locale.json"), "r")
_locale_language_map = json.loads(_opened_file.read())
_opened_file.close()

# Check for user language, somewhat os dependent
if operating_system == "Windows":
    import ctypes

    loc = locale.windows_locale[ctypes.windll.kernel32.GetUserDefaultUILanguage()]
    used_languages = _check_locale(loc, used_languages)
elif operating_system == "Linux" or operating_system == "Darwin":
    loc = os.getenv("LANG")
    used_languages = _check_locale(loc, used_languages)


# Throw in system language for good measure
for loc in locale.getdefaultlocale():
    used_languages = _check_locale(loc, used_languages)

# If there's no suitable locale to be found default to english
if len(used_languages) == 0:
    used_languages.add("english")

if default_language is None:
    default_language = "en_US"

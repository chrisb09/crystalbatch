"""Used to get a set 'used_languages' that contains default language selections for a source-target folder pairs wordlists.
Can also provide a default value for the interface language."""
import platform, os, locale, json


def _check_locale(loc, used_languages):
    if loc is not None:
        for locale_prefix in locale_language_map:
            if loc.startswith(locale_prefix):
                used_languages.add(locale_language_map[locale_prefix])
                global default_language
                if default_language is None:
                    default_language = loc[:5]
                break
    return used_languages


root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))

operating_system = platform.system()

used_languages = set()
default_language = None

opened_file = open(os.path.join(root_dir, "res/language/language_locale.json"), "r")
locale_language_map = json.loads(opened_file.read())
opened_file.close()

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

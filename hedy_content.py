import copy
import attr
import os
from babel import Locale
from website.yaml_file import YamlFile
import iso3166

# Define and load all countries
COUNTRIES = {k: v.name for k, v in iso3166.countries_by_alpha2.items()}

# Define dictionary for available languages. Fill dynamically later.
ALL_LANGUAGES = {}

# Languages that have a keyword grammar file
ALL_KEYWORD_LANGUAGES = {
    'en': 'EN',
    'es': 'ES',
    'fr': 'FR',
    'nl': 'NL',
    'nb_NO': 'NB',
    'tr': 'TR',
    'ar': 'AR',
    'hi': 'HI',
    'id': 'ID'
}

ADVENTURE_ORDER = [
    'default',
    'story',
    'parrot',
    'songs',
    'turtle',
    'dishes',
    'dice',
    'rock',
    'calculator',
    'fortune',
    'restaurant',
    'haunted',
    'piggybank',
    'quizmaster',
    'language',
    'secret',
    'next',
    'end'
]

def fill_all_languages(babel):
    # load all available languages in dict
    # list_translations of babel does about the same, but without territories.
    languages = {}
    for dirname in babel.translation_directories:
        if not os.path.isdir(dirname):
            continue

        for folder in os.listdir(dirname):
            locale_dir = os.path.join(dirname, folder, 'LC_MESSAGES')
            if not os.path.isdir(locale_dir):
                continue

            if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
                locale = Locale.parse(folder)
                languages[folder] = locale.display_name.title()

    for l in sorted(languages):
        ALL_LANGUAGES[l] = languages[l]


class Commands:
    def __init__(self, language):
        self.language = language
        self.keyword_lang = "en"
        self.keywords = YamlFile.for_file(
            f'content/keywords/{self.keyword_lang}.yaml').to_dict()
        self.levels = YamlFile.for_file(
            f'content/commands/{self.language}.yaml')

    def set_keyword_language(self, language):
        if language != self.keyword_lang:
            self.keyword_lang = language
            self.keywords = YamlFile.for_file(
                f'content/keywords/{self.keyword_lang}.yaml')

    def get_commands_for_level(self, level):
        # Commands are stored as a list of dicts, so iterate like a list, then get the dict values
        level_commands = copy.deepcopy(self.levels.get(int(level), []))
        for command in level_commands:
            for k, v in command.items():
                command[k] = v.format(**self.keywords)
        return level_commands

    def get_defaults(self, level):
        return copy.deepcopy(self.levels.get(int(level), {}))


class NoSuchCommand:
    def get_commands(self):
        return {}


class Adventures:
    def __init__(self, language):
        self.language = language
        self.keyword_lang = "en"
        self.keywords = YamlFile.for_file(
            f'content/keywords/{self.keyword_lang}.yaml').to_dict()
        self.adventures_file = YamlFile.for_file(
            f'content/adventures/{self.language}.yaml')

    def set_keyword_language(self, language):
        if language != self.keyword_lang:
            self.keyword_lang = language
            self.keywords = YamlFile.for_file(
                f'content/keywords/{self.keyword_lang}.yaml')

        # When customizing classes we only want to retrieve the name, (id) and level of each adventure
    def get_adventure_keyname_name_levels(self):
        adventures = self.adventures_file['adventures']
        adventures_dict = {}
        for adventure in adventures.items():
            adventures_dict[adventure[0]] = {
                adventure[1]['name']: list(adventure[1]['levels'].keys())}
        return adventures_dict

    def has_adventures(self):
        return self.adventures_file.exists() and self.adventures_file.get('adventures')


class NoSuchAdventure:
    def get_adventure(self):
        return {}

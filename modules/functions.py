
from os import path, makedirs
from glob import glob
import json

from modules.classes import Language, IDE
from modules.create_template import create_defaults


def get_language(language_name:str, project:bool = False) -> Language | str:
    """
    Checks if a language is supported or not, and then returns the Language object for said language.

    Will throw an error if language is not supported.
    Arguments:
        language_name (str): The name of the language to check.
        project (bool, optional): Use csproj for C#. Defaults to False.
    """
    for value in Language.languages.values():
        if not value.language.lower() == language_name.lower():
            continue
        value_name = value.language.lower()

        if project and value_name != "c#":
            print("codeforge.py: error: language chosen is not C#, and thus does not support project toggle")
            exit()
        
        if value_name == "c#" and project:
            return Language.languages["cs_project"]
        
        return value
    
    # If still in function, then language is not in LANGUAGES
    print(f"codeforge.py: error: language '{language_name}' not supported.")
    print("for a list of supported languages, use 'codeforge.py --languages'")
    exit()


def get_languages(show:bool = False) -> list:
    """
    Returns a list of supported languages.

    Arguments:
        show (bool, optional): Display output. Defaults to False.
    """
    if show: print("Supported languages:")
    languages = []
    for language in Language.languages.values():
        name = language.language

        languages.append(name)
        if show: print(f"{name.capitalize()} ({language.name})")
    return languages


def get_ides(show:bool = False) -> list:
    """
    Returns a list of supported IDEs.

    Arguments:
        show (bool, optional): Display output. Defaults to False.
    """
    if show: print("Supported IDEs:")
    ides = []
    for ide in IDE.ides.values():
        name = ide.name
        if name in ides:
            continue

        ides.append(name)
        if show: 
            print(ide.display_name)
    return ides


def get_templates(language_input: str, show: bool = False) -> dict:
    """
    Returns a dictionary of all found template names for a given language in the form {name: path}.

    Arguments:
        language_input (str): The language to find templates for.
        show (bool, optional): Display output. Defaults to False.
    """
    language = get_language(language_input).language
    
    folder_path = path.abspath(path.join(".", "templates", language))
    if not path.exists(folder_path):
        makedirs(folder_path)
        create_defaults(language, False)

    if show:
        print(f"{language} templates:")
    templates = {}
    for template in glob(path.join(folder_path, "*.txt")):
        filename = template[len(folder_path) + 1 : -4].lower()
        templates[filename] = template
        if show:
            with open(template, "r") as file:
                desc = file.readlines()[1][2:]
                file.close()
            print(f"{filename}:    {desc}")

    if show and len(templates) == 0:
        print(f"No templates found for {language}")
    return templates


def get_defaults(language_input:str, show:bool = False) -> dict:
    """
    Returns a dictionary of all default fields for a given langauge in the form {field: value}.

    Arguments:
        language (str): The language to get the default fields for.
        show (bool, optional): Display output. Defaults to False.
    """
    if not path.exists('config.json'):
        print("codeforge.py: error: cannot find 'config.json'.")
        print("please run 'codeforge.py -generate_json' to re-generate the config file.")
        return
    
    language = language_input.lower()
    if language not in Language.languages.keys():
        print(f"codeforge.py: error: Config for language '{language}' not found.")
        print("for a list of configurable languages, use 'codeforge.py --languages'.")
        print("note: when modifying configs, ensure that you use the name INSIDE of the brackets as the <language>.")
        exit()
    
    with open('config.json', 'r') as file:
        data = json.load(file)
        defaults_data = data["defaults"]
        language_defaults = defaults_data[language]
        
    if show:
        print(f"Default {language} fields:")
        for key, value in language_defaults.items():
            print(f"{key}: '{value}'")
    return language_defaults


def update_defaults(language:str, field:str, value:str, show:str = False) -> None:
    """
    Updates a default field in the config.json file for a specified language.

    Arguments:
        language_input (str): The language to change a field of.
        field (str): The name of the field to update.
        value (str): The new value of the field.
        show (bool, optional): Display output. Defaults to False.
    """
    with open("config.json", 'r') as file:
        data = json.load(file)
    default_data = data["defaults"]
    language_data = default_data[language]
    language_data[field] = value

    with open('config.json', 'w+') as file:
        json.dump(data, file, indent=4)

    if show:
        print(f"Successfully updated field '{field}'")
    return


def generate_defaults(language_input:str, show:bool = False) -> None:
    """
    Generates the default config files for a specified language

    Arguments:
        language (str): The language to generate default configs for.
        show (bool, optional): Display output. Defaults to False.
    """
    with open("config.json", 'r') as file:
        data = json.load(file)
    default_data = data["defaults"]

    if default_data.get(language_input, False):
        print(f"All default configs already exist for '{language_input}'")
        return
    
    for language, value in Language.languages.items():
        default_data[language_input] = {'output_path': path.join('.', 'projects', language), 'ide': "vscode"}
    
    with open('config.json', 'w+') as file:
        json.dump(data, file, indent=4)
    if show:
        print(f"Successfully generated default configs for {language_input}")
    return


def generate_json(show:bool = False) -> None:
    """
    Creates the config.json file if not present, otherwise it will overwrite.

    Arguments:
        show (bool, optional): Display output. Defaults to False.
    """
    json_data = {}

    # Create the language database
    languages = {}
    languages["python"] = {"language": "python", "extension": "py", "shebang": "#!/usr/bin/env python3", "gitignore": "# Ignore __pycache__\n__pycache__/"}
    languages["cs_script"] = {"language": "c#", "extension": "csx", "shebang": "/usr/bin/env/ dotnet-script"}
    languages["cs_project"] = {"language": "c#", "extension": "cs"}

    # Create the IDE database
    ides = {}
    ides["VS Code"] = {"name": "vscode", "open_command": "code %PATH%"}

    # Generate the defaults database
    defaults = {}
    for language, value in languages.items():
        defaults[language] = {'output_path': path.join('.', 'projects', value["language"]), 'ide': "vscode"}

    # Compile into single dictionary
    json_data["languages"] = languages
    json_data["ides"] = ides
    json_data["defaults"] = defaults

    with open('config.json', 'w+') as file:
        json.dump(json_data, file, indent=4)

    if show:
        print("Successfully created config file.")
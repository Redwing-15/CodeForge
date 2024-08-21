#!/usr/bin/env python3
from sys import argv
from os import path, makedirs
from glob import glob
import argparse
import json

from modules.create_project import create_project
from modules.create_template import create_template, create_defaults


LANGUAGES = ["python", "c#"]
IDES = ["vscode"]

def show_help():
    """
    Displays the help message
    """
    print("""usage: codeforge.py [options] <project_name> <language> [args]

options:
    -h, --help      Shows this help message and exit
    -l, --languages 
                    Shows the supported languages and exit
    -i, --ides      
                    Shows the supported IDEs and exit
    -p, --templates <language>  
                    Shows the templates for a chosen language
    -d, --defaults  
                    Show the configurable default fields for a chosen language and exit
    -g, --generate_templates <language>
                    Generates the default template files for a given language

commands:
    create          Creates a project
        usage: codeforge.py create <name> <language> [options]
        optional arguments:
            -t, --template <name>       Use a custom template. Default is 'hello world'
            -p, --project               If using C#, creates a .csproj instead of a .csx
            -n, --nullable              If using C#, enables nullable error checking
            -r, --repository            Initializes a git repository in the project folder
            -c, --code:                 Opens the project folder via VS Code once created
            -o, --output:               Specifies the output path for the project

    template        Creates a template
        usage: codeforge.py template <name> <language> [description]

    default         Configures default fields
        usage: codeforge.py default <field> <value>

examples: 
    codeforge.py create "my project" c# -p -n -t "my template"
    codeforge.py template "my template" python "A custom description"
    codeforge.py default ide "vscode"
""")


def handle_args() -> None:
    """
    Handles provided arguments, then runs create_project
    """
    parser = argparse.ArgumentParser(add_help=False)

    # Define optional flags
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit")
    parser.add_argument("-l", "--languages", action="store_true", help="Show the supported languages and exit")
    parser.add_argument("-i", "--ides", action="store_true", help="Show the supported IDEs and exit")
    parser.add_argument("-p", "--templates", type=str, help="Show the templates for a chosen language and exit")
    parser.add_argument("-d", "--defaults", type=str, help="Show the configurable default fields for a chosen language and exit")
    parser.add_argument("-g", "--generate_templates", type=str, help="Generate the default template files for a given language and exit")

    subparsers = parser.add_subparsers(dest="command")

    # Define create subcommand
    create_parser = subparsers.add_parser("create", help="Creates a project")
    create_parser.add_argument("name", type=str, help="The name of the project")
    create_parser.add_argument("language", type=str, help="The programming language for the project")
    create_parser.add_argument("-t", "--template", type=str, default="hello world", help="Use a custom template. Default is 'hello world'")
    create_parser.add_argument("-p", "--project", action='store_true', help="If using C#, creates a .csproj instead of a .csx")
    create_parser.add_argument("-n", "--nullable", action="store_true", help="If using C#, enables nullable error checking")
    create_parser.add_argument("-r", "--repository", action="store_true", help="Initializes a git repository of in the project folder")
    create_parser.add_argument("-c", "--code", action="store_true", help="Opens the project folder via VS Code once created")
    create_parser.add_argument("-o", "--output", type=str, default = None, help="Specifies the output path for the project")

    # Define template subcommand
    template_parser = subparsers.add_parser("template", help="Creates a template")
    template_parser.add_argument("name", type=str, help="The name of the template")
    template_parser.add_argument("language", type=str, help="The programming language for the template")
    template_parser.add_argument("description", type=str, nargs="?", default="A custom template",
                                 help="A description for the template. Default is 'A custom template'")
    
    # Define default subcommand
    default_parser = subparsers.add_parser("default", help="Configures default fields")
    default_parser.add_argument("language", type=str, help="The language to change a field of")
    default_parser.add_argument("field", type=str, help="The field to be changed e.g output path")
    default_parser.add_argument("value", type=str, help="The new value")

    args = parser.parse_args()

    if args.help:
        show_help()
        return

    if args.languages:
        get_languages(True)
        return
    
    if args.ides:
        get_ides(True)
        return
    
    if args.templates:
        get_templates(args.templates, True)
        return
    
    if args.defaults:
        get_defaults(args.defaults, True)
        return

    if args.generate_templates:
        create_defaults(args.generate_templates.lower())
        return

    # Handle 'template' command
    if args.command == "template":
        language = args.language.lower()
        if language not in LANGUAGES:
            languageError(language)
        
        filename = args.name.lower()
        if path.exists(path.abspath(path.join(".", "templates", language, filename))):
            print(f"codeforge.py: error: template '{filename}' already exists.")
            print("for a list of templates, use 'codeforge.py --templates'")
            return

        create_template(args.name, language, args.description)
        return
    
    # Handle 'default' command
    elif args.command == "default":
        language = args.language.lower()
        if language not in LANGUAGES:
            languageError(language)
        
        defaults = get_defaults(language)
        field = args.field.lower()
        if not field in defaults.keys():
            print(f"codeforge.py: error: field '{field}' does not exist.")
            print("for a list of fields, use 'codeforge.py --defaults'")
            return
        value = args.value
        if field == "output":
            if not path.exists(value):
                print(f"codeforge.py: error: path '{value}' does not exist.")
                return
        elif field == "ide":
            if not value in IDES:
                print(f"codeforge.py: error: IDE '{value}' is not supported!")
                print("for a list of supported IDEs, use 'codeforge.py --ides'")
                return
        update_defaults(language, field, value, True)
        return
    
    # Else, handle create function
    project_name = args.name.lower()
    language = args.language.lower()

    if not language in LANGUAGES:
        languageError(language)
    
    defaults = get_defaults(language)
    if args.template is None:
        print(f"codeforge.py create: error: the following arguments are required: template")
        print(f"for a list of templates, use 'codeforge.py --templates {language}'")
        return
    if args.project:
        if language != "c#":
            print("codeforge.py: error: language chosen is not C#, and thus does not need a project toggle")
            return
    if args.template:
        template = args.template.lower()
        templates = get_templates(language)
        if not template in templates:
            print(f"codeforge.py: error: template '{template}' not found for {language}.")
            print(f"for a list of templates, use 'codeforge.py --templates {language}'")
            return

    if args.nullable:
        if language != "c#":
            print("codeforge.py: error: language chosen is not C#, and thus does not support enabling nullable error checking")
            return
        elif not args.project:
            print("codeforge.py: error: cannot enable nullable error checking for csx file")
            return

    if args.output:
        output_path = args.output
        if not path.exists(output_path):
            print(f"codeforge.py: error: cannot find path '{output_path}'")
            return
    else:
        if not path.exists(defaults['output_path']):
            output_path = path.join('.', 'projects', language)
            update_defaults(language, 'output_path', output_path)
        else:
            output_path = defaults['output_path']
    create_project(project_name, language, args.template.lower(), args.project, args.nullable, args.repository, args.code, output_path)


def languageError(value: str) -> None:
    """
    Displays a custom error message for languageErrors.

    Args:
        value (str): The value that caused the error
    """
    print(f"codeforge.py: error: language '{value}' not supported.")
    print("for a list of supported languages, use 'codeforge.py --languages'")
    exit()


def ask_inputs() -> None:
    """
    Asks user for argument inputs, then runs create_project()
    """
    project_name = input("What will the project be called?\nName: ").lower()

    get_languages(True)
    language = input("\nWhat language will the project use?\nLanguage: ").lower()
    if language not in LANGUAGES:
        print(f"Error: language '{language}' is not supported.")
        input("Press enter to exit!")
        return

    defaults = get_defaults(language)
    project = False
    if not language == "c#":
        project = False
    elif (input("\nDo you want to create a csproject instead of a .csx?\n(Y) Y/N: ").lower() == "y"):
        project = True

    nullable = False
    if not language == "c#":
        nullable = False
    elif (input("\nDo you want to enable nullable error checking?\n(Y) Y/N: ").lower() == "y"):
        nullable = True

    print("")
    templates = get_templates(language, True)
    template = input("Do you want to use a template? Leave blank to use default ('blank')\nTemplate: ").lower()

    if template == "":
        template = "blank"
    if template not in templates:
        print(f"Error: template '{template}' not found.")
        input("Press enter to exit!")
        return

    create_repo = False
    if (input("Do you want to initialize a git repository for the project?\n(N) Y/N: ") == "y"):
        create_repo = True

    open_project = False
    if input("Do you want to open the project in VS Code?\n(N) Y/N: ") == "y":
        open_project = True
    create_project(project_name, language, template, project, nullable, create_repo, open_project, defaults['output'])


def get_languages(show:bool = False) -> list:
    """
    Returns a list of supported languages.

    Can optionally output all supported languages if 'show' is True.

    Args:
        show (bool): Will output all default languages if True. Default is False
    """
    if show:
        print("Supported languages:")
        for item in LANGUAGES:
            print(item)
    return LANGUAGES


def get_ides(show:bool = False) -> list:
    """
    Returns a list of supported IDEs.

    Can optionally output all supported IDEs if 'show' is True.

    Args:
        show (bool): Will output all supported IDEs if True. Default is False
    """
    if show:
        print("Supported IDEs:")
        for ide in IDES:
            print(ide)
    return IDES


def get_defaults(language:str, show:bool = False) -> dict:
    """
    Returns a dictionary of all default fields for a given langauge in the form {field: value}.

    Can optionally output all found templates if 'show' is True.

    Args:
        language (str): The language to get the default fields for
        show (bool): Will output all default fields with their value if True. Default is False
    """
    if not language in LANGUAGES:
        languageError(language)
    
    exists = False
    if not path.exists('defaults.json'):
        data = {}
        for entry in LANGUAGES:
            data[entry] = {'output_path': path.join('.', 'projects', entry), 'ide': "vscode"}
        with open('defaults.json', 'w+') as file:
            json.dump(data, file, indent=4)
        data = data[language]
    else:
        exists = True
        with open("defaults.json", 'r') as file:
            data = json.load(file)
            data = data[language]
        
    if show:
        if not exists:
            print("Successfully generated default fields")
        else:
            print(f"Default {language} fields:")
            for field in data:
                print(f"{field}: '{data[field]}'")
    return data


def update_defaults(language:str, field:str, value:str, show:str = False) -> None:
    """
    Updates a field in the defaults.json file.

    Can optionally output a complete message if 'show' is True.
    Args:
        language (str): The language to change a field of
        field (str): The name of the field to update
        value (str): The new value of the field
        show (bool): Will output a completion message when done if True. Default is False
    """
    with open("defaults.json", 'r') as file:
        data = json.load(file)
    defaults = data[language]
    defaults[field] = value

    with open('defaults.json', 'w+') as file:
        json.dump(data, file, indent=4)

    if show:
        print(f"Successfully updated field '{field}'")
    return


def get_templates(language: str, show: bool = False) -> dict:
    """
    Returns a dictionary of all found template names for a given language in the form {name: path}.

    Can optionally output all found templates if 'show' is True.

    Args:
        language (str): The language to find templates for.
        show (bool, optional): Will output all found templates. Default is False
    """
    if not language in LANGUAGES:
        languageError(language)
    
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


if __name__ == "__main__":
    # Check if arguments have been given
    # if not, ask for inputs manually
    if len(argv) >= 2:
        handle_args()
    else:
        ask_inputs()
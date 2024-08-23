#!/usr/bin/env python3
from sys import argv
from os import path, makedirs
from glob import glob
import argparse
import json

from modules.classes import Language, IDE
from modules.create_project import create_project
from modules.create_template import create_template, create_defaults


def show_help():
    """
    Displays the help message
    """
    print("""usage: codeforge.py [options] <project_name> <language> [args]

options:
    -h, --help      Show this help message and exit
    -l, --languages 
                    Show the supported languages and exit
    -i, --ides      
                    Show the supported IDEs and exit
    -p, --templates <language>  
                    Show the templates for a chosen language and exit
    -d, --defaults  
                    Show the configurable default fields for a chosen language and exit
    -g, --generate_templates <language>
                    Generates the default template files for a given language and exit
    -j, --generate_json
                    "Generate the config.json file and exit"

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
    parser.add_argument("-j", "--generate_json", action="store_true", help="Generate the config.json file and exit")

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
    
    if args.generate_json:
        generate_json(True)
        return

    # Handle 'template' command
    if args.command == "template":
        language = get_language(args.language)
        
        filename = args.name.lower()
        if path.exists(path.abspath(path.join(".", "templates", language.language, filename))):
            print(f"codeforge.py: error: template '{filename}' already exists.")
            print("for a list of templates, use 'codeforge.py --templates'")
            return

        create_template(args.name, language, args.description)
        return
    
    # Handle 'default' command
    elif args.command == "default":
        language = get_language(args.language)
        
        defaults = get_defaults(language.lname)
        field = args.field.lower()
        if not field in defaults.keys():
            print(f"codeforge.py: error: field '{field}' does not exist.")
            print("for a list of fields, use 'codeforge.py --defaults'")
            return
        value = args.value
        if field == "output":
            if not path.exists(value):
                print(f"codeforge.py: error: directory '{value}' does not exist.")
                print("note: some operating systems have case-sensitive directories, and thus might throw an error if mis-typed")
                return
        elif field == "ide":
            if not value in get_ides():
                print(f"codeforge.py: error: IDE '{value}' is not supported!")
                print("for a list of supported IDEs, use 'codeforge.py --ides'")
                return
        update_defaults(language.name, field, value, True)
        return
    
    # Else, handle create function
    project_name = args.name.lower()
    language = get_language(args.language, args.project)

    defaults = get_defaults(language.name)
    if args.template is None:
        print(f"codeforge.py create: error: the following arguments are required: template")
        print(f"for a list of templates, use 'codeforge.py --templates {language.language}'")
        return

    if args.template:
        template = args.template.lower()
        templates = get_templates(language.language)
        if not template in templates:
            print(f"codeforge.py: error: template '{template}' not found for {language.language}.")
            print(f"for a list of templates, use 'codeforge.py --templates {language.language}'")
            return

    if args.nullable:
        if language.language != "c#":
            print("codeforge.py: error: language chosen is not C#, and thus does not support enabling nullable error checking")
            return
        elif not args.project:
            print("codeforge.py: error: cannot enable nullable error checking for csx file")
            return

    if args.output:
        output_path = args.output
        if not path.exists(output_path):
            print(f"codeforge.py: error: cannot find directory '{output_path}'")
            print("note: some operating systems have case-sensitive directories, and thus might throw an error if mis-typed")
            return
    else:
        if not path.exists(defaults['output_path']):
            output_path = path.join('.', 'projects', language.language)
            update_defaults(language.name, 'output_path', output_path)
        else:
            output_path = defaults['output_path']
    
    create_project(project_name, language, args.template.lower(), args.nullable, args.repository, args.code, output_path)


def ask_inputs() -> None:
    """
    Asks user for argument inputs, then runs create_project()
    """
    project_name = input("What will the project be called?\nName: ").lower()

    get_languages(True)
    language_input = input("\nWhat language will the project use?\nLanguage: ").lower()
    if not language_input in get_languages():
        print(f"Error: language '{language_input}' not supported.")
        input("Press enter to exit!")
        return
    
    project = False
    if language_input.lower() == "c#" and (input("\nDo you want to create a csproject instead of a .csx?\n(Y) Y/N: ").lower() == "y"):
        project = True
    language = get_language(language_input, project)

    defaults = get_defaults(language.name)

    nullable = False
    if not language.language == "c#":
        nullable = False
    elif (input("\nDo you want to enable nullable error checking?\n(Y) Y/N: ").lower() == "y"):
        nullable = True

    templates = get_templates(language.language, True)
    template = input("\nDo you want to use a template? Leave blank to use default ('blank')\nTemplate: ").lower()

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
    create_project(project_name, language, template, nullable, create_repo, open_project, defaults['output'])


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

    Can optionally output all supported languages if 'show' is True.

    Args:
        show (bool): Will output all default languages if True. Default is False
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

    Can optionally output all supported IDEs if 'show' is True.

    Args:
        show (bool): Will output all supported IDEs if True. Default is False
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


def initialize() -> None:
    """
    Initializes languages, IDEs, and other files/folders.
    """
    if not path.exists('config.json'):
        generate_json()
    
    with open('config.json', 'r') as file:
        data = json.load(file)

    # Initialize languages
    languages = data["languages"]
    for key, value in languages.items():
        # Handle cases where JSON does not provide values for "shebang" or "gitignore"
        shebang = value.get("shebang", None)
        gitignore = value.get("gitignore", "")
        Language(name=key, language=value["language"], extension=value["extension"], shebang=shebang, gitignore=gitignore)
    
    # Initialize IDEs
    ides = data["ides"]
    for key, value in ides.items():
        # Handle cases where JSON does not provide values for "open_command"
        open_command = getattr(value, "open_command", None)
        IDE(display_name=key, name=value["name"], open_command=open_command)


def generate_json(show:bool = False) -> None:
    """
    Creates the config.json file if not present, otherwise it will overwrite.

    Can optionally provide output message when complete.

    Args:
        show (bool, optional): Show output message when done. Defaults to False.
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


def get_defaults(language_input:str, show:bool = False) -> dict:
    """
    Returns a dictionary of all default fields for a given langauge in the form {field: value}.

    Can optionally output all found fields if 'show' is True.

    Args:
        language (str): The language to get the default fields for
        show (bool): Will output all default fields with their value if True. Default is False
    """
    if not path.exists('config.json'):
        # If no config.json, then classes may not be loaded.
        # This should never happen, but just to be safe, re-initialize.
        initialize()
    
    language = language_input.lower()
    if language not in Language.languages.keys():
        print(f"codeforge.py: error: Config for language '{language}' not found.")
        print("for a list of configurable languages, use 'codeforge.py --languages'.")
        print("note: when modifying configs, ensure that you use the name INSIDE of the brackets as the <language>.")
        exit()
    
    with open("config.json", 'r') as file:
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
    Updates a default field in the config.json file.

    Can optionally output a complete message if 'show' is True.
    Args:
        language_input (str): The language to change a field of
        field (str): The name of the field to update
        value (str): The new value of the field
        show (bool): Will output a completion message when done if True. Default is False
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


def get_templates(language_input: str, show: bool = False) -> dict:
    """
    Returns a dictionary of all found template names for a given language in the form {name: path}.

    Can optionally output all found templates if 'show' is True.

    Args:
        language_input (str): The language to find templates for.
        show (bool, optional): Will output all found templates. Default is False
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


if __name__ == "__main__":
    initialize()
    # Check if arguments have been given
    # if not, ask for inputs manually
    if len(argv) >= 2:
        handle_args()
    else:
        ask_inputs()
#!/usr/bin/env python3

from sys import argv
from os import path, makedirs
from glob import glob
import argparse

from create_project import create_project
from create_template import create_template, create_defaults


LANGUAGES = ["python", "c#"]


def show_help():
    """
    Displays the help message
    """
    print("""usage: codeforge.py [options] <project_name> <language> [args]

options:
    -h, --help      Shows this help message and exit
    -l, --languages 
                    Shows the supported languages and exit
    -p, --templates <language>  
                    Shows the templates for a chosen language
    -g, --generate_defaults <language>
                    Generates the default template files for a given language

commands:
    create          Creates a project
        usage: codeforge.py create <name> <language> [options]
        optional arguments:
            -t, --template <name>       Use a custom template. Default is 'hello world'
            -p, --project               If using C#, creates a .csproj instead of a .csx
            -n, --nullable              If using C#, enables nullable error checking
            -r, --repository            Initializes a git repository in the project folder
            -o, --open:                 Opens the project folder via VS Code

    template        Creates a template
        usage: codeforge.py template <name> <language> [description]

examples: 
    codeforge.py create "my project" c# -n -t "my template"
    codeforge.py template "my template" python "A custom description"
""")


def show_languages():
    """
    Displays the supported languages
    """
    print("supported languages:")
    for item in LANGUAGES:
        print(item)


def handle_args() -> None:
    """
    Handles provided arguments, then runs create_project
    """
    parser = argparse.ArgumentParser(add_help=False)

    # Define optional flags
    parser.add_argument("-h", "--help", action="store_true", help="Shows this help message and exit")
    parser.add_argument("-l", "--languages", action="store_true", help="Show the supported languages and exit")
    parser.add_argument("-p", "--templates", type=str, help="Show the templates for a chosen language")
    parser.add_argument("-g", "--generate_defaults", type=str, help="Generates the default template files for a given language")

    subparsers = parser.add_subparsers(dest="command")

    # Define create subcommand
    create_parser = subparsers.add_parser("create", help="Creates a project")
    create_parser.add_argument("name", type=str, help="The name of the project")
    create_parser.add_argument("language", type=str, help="The programming language for the project")
    create_parser.add_argument("-t", "--template", type=str, default="hello world", help="Use a custom template. Default is 'blank'")
    create_parser.add_argument("-p", "--project", action='store_true', help="If using C#, creates a .csproj instead of a .csx")
    create_parser.add_argument("-n", "--nullable", action="store_true", help="If using C#, enables nullable error checking")
    create_parser.add_argument("-r", "--repository", action="store_true", help="Initializes a git repository of in the project folder")
    create_parser.add_argument("-o", "--open", action="store_true", help="Opens the project folder via VS Code")
    # Might possibly add ability to add a custom name for the repository

    # Define template subcommand
    template_parser = subparsers.add_parser("template", help="Creates a template")
    template_parser.add_argument("name", type=str, help="The name of the template")
    template_parser.add_argument("language", type=str, help="The programming language for the template")
    template_parser.add_argument("description", type=str, nargs="?", default="A custom template",
                                 help="A description for the template. Default is 'A custom template'")

    args = parser.parse_args()

    if args.languages:
        show_languages()
        return

    if args.help:
        show_help()
        return

    if args.templates:
        get_templates(args.templates, True)
        return

    if args.generate_defaults:
        create_defaults(args.generate_defaults.lower())
        return

    if args.command == "template":
        language = args.language.lower()
        if language not in LANGUAGES:
            print(f"codeforge.py: error: language '{language}' not supported.")
            print("for a list of supported languages, use 'codeforge.py --languages'")
            return

        filename = args.name.lower()
        if path.exists(path.abspath(path.join(".", "templates", language, filename))):
            print(f"codeforge.py: error: template '{filename}' already exists.")
            print("for a list of templates, use 'codeforge.py --templates'")
            return

        create_template(args.name, language, args.description)
        return

    # Else, handle create function
    project_name = args.name.lower()
    language = args.language.lower()

    if not language in LANGUAGES:
        print(f"codeforge.py: error: language '{language}' not supported.")
        print("for a list of supported languages, use 'codeforge.py --languages'")
        return
    
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

    create_project(project_name, language, args.template.lower(), args.project, args.nullable, args.repository, args.open)


def ask_inputs() -> None:
    """
    Asks user for argument inputs, then runs create_project()
    """
    project_name = input("What will the project be called?\nName: ").lower()

    show_languages()
    language = input("\nWhat language will the project use?\nLanguage: ").lower()
    if language not in LANGUAGES:
        print(f"Error: language '{language}' is not supported.")
        input("Press enter to exit!")
        return

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
    create_project(project_name, language, template, project, nullable, create_repo, open_project)


def get_templates(language: str, show: bool = False) -> dict:
    """
    Returns a dictionary of all found template names for a given language .

    Can optionally output all found templates if \'show\' is True.

    Args:
        language (str): The language to find templates for.
        show (bool, optional): Will output all found templates. Default is False
    """
    if not language in LANGUAGES:
        print(f"codeforge.py: error: language '{language}' not supported.")
        print("for a list of supported languages, use 'codeforge.py -languages'")
        return

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
#!/usr/bin/env/ python3

# Note:
# Currently developing in linux, and thus do not have access to dotnet.
# This means that C# support will come later when it is easier to implement
# due to dotnet having built-in commands for creating projects and using templates.

from sys import argv
from os import path, mkdir
from glob import glob
import argparse

from create_project import create_project
from create_template import create_template, create_defaults


LANGUAGES = ["python"]


def show_help():
    """
    Displays the help message
    """
    print(
        """usage: codeforge.py [options] <language> [args]

options:
    -h, --help                  Shows this help message and exit
    -l, --languages             Show the supported languages and exit
    -p, --templates <language>  Show the templates for a chosen language
    -g, --generate_defaults <language>
                                Generates the default template files for a given language

commands:
    create                      Creates a project
        usage: codeforge.py create <language> [options]
        optional arguments:
            -t, --template <name>       Use a custom template. Default is 'blank'
            -n, --disable_nullable      If using C#, disable nullable error checking

    template                    Creates a template
        usage: codeforge.py template <language> <name> [description]

examples: 
    codeforge.py create c# -n -t "my template"
    codeforge.py template python "my template" "A custom description"
"""""
    )


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
    parser = argparse.ArgumentParser(description="CodeForge CLI", add_help=False)

    # Define optional flags
    parser.add_argument("-h", "--help", action="store_true", help="Shows this help message and exit")
    parser.add_argument("-l", "--languages", action="store_true", help="Show the supported languages and exit")
    parser.add_argument("-p", "--templates", type=str, help="Show the templates for a chosen language")
    parser.add_argument("-g", "--generate_defaults", type=str, help="Generates the default template files for a given language")

    subparsers = parser.add_subparsers(dest="command")

    # Define create subcommand
    create_parser = subparsers.add_parser("create", help="Creates a project")
    create_parser.add_argument("language", type=str, help="The programming language for the project")
    create_parser.add_argument("-n", "--disable_nullable", action='store_true', help="If using C#, disable nullable error checking")
    create_parser.add_argument("-t", "--template", type=str, default="blank", help="Use a custom template. Default is 'blank'")

    # Define template subcommand
    template_parser = subparsers.add_parser("template", help="Creates a template")
    template_parser.add_argument("language", type=str, help="The programming language for the template")
    template_parser.add_argument("name", type=str, help="The name of the template")
    template_parser.add_argument("description", type=str, nargs='?', default="A custom template", help="A description for the template. Default is 'A custom template'")

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
        
        create_template(language, args.name, args.description)
        return
    
    elif args.command == "create":
        language = args.language.lower()

        if not language in LANGUAGES:
            print(f"codeforge.py: error: language \'{language}\' not supported.")
            print("for a list of supported languages, use \'codeforge.py --languages\'")
            return
        
        if args.template is None:
            print(f"codeforge.py create: error: the following arguments are required: template")
            print(f"for a list of templates, use \'codeforge.py --templates {language}\'")
            return
        elif args.template:
            print("Template:", args.template)
            template = args.template.lower()
            templates = get_templates(language)
            if not template in templates:
                print(f"codeforge.py: error: template \'{template}\' not found for {language}.")
                print(f"for a list of templates, use \'codeforge.py --templates {language}\'")
                return
            
        if args.disable_nullable:
            if language != "c#":
                print("codeforge.py: error: language chosen is not C#, and thus does not support disabling of nullable error checking!")
                return

        create_project(language, template, args.disable_nullable)


def ask_inputs() -> None:
    """
    Asks user for argument inputs, then runs create_project()
    """
    show_languages()
    language = input("\nWhat language will the project use?\nLanguage: ").lower()
    if language not in LANGUAGES:
        print(f"Error: language \'{language}\' is not supported.")
        input("Press enter to exit!")
        return
    
    disable_nullable = True
    if not language == 'c#':
        disable_nullable = False
    elif input("\nDo you want to disable nullable error checking?\n(Y) Y/N: ").lower() == "y":
        disable_nullable = False
    
    print("")
    templates = get_templates(language, True)
    template = input("Do you want to use a template? Leave blank to use default (\'blank\')\nTemplate: ")
    
    if template == '': template = "blank"
    if template not in templates:
        print(f"Error: template \'{template}\' not found.")
        input("Press enter to exit!")
        return

    create_project(language, template, disable_nullable)


def get_templates(language: str, show: bool = False) -> dict:
    """
    Returns a dictionary of all found template names for a given language .

    Can optionally output all found templates if \'show\' is True.

    Args:
        language (str): The language to find templates for.
        show (bool, optional): Will output all found templates. Default is False
    """
    if not language in LANGUAGES:
        print(f"codeforge.py: error: language \'{language}\' not supported.")
        print("for a list of supported languages, use \'codeforge.py -languages\'")
        return
    
    templates_folder = path.abspath(path.join(".", "templates"))
    if not path.exists(templates_folder):
        mkdir(templates_folder)
    
    path_to_folder = path.abspath(path.join(".", "templates", language))
    if not path.exists(path_to_folder):
        mkdir(path_to_folder)
        create_defaults(language, False)

    if show: print(f"{language} templates:")
    templates = {}
    for template in glob(path.join(path_to_folder, "*.txt")):
        filename = template[len(path_to_folder)+1:-4].lower()
        templates[filename] = template
        if show:
            with open(template, 'r') as file:
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

from sys import argv, exit
import argparse

LANGUAGES = ["python", "c#"]


def handle_args() -> None:
    """
    Handles provided arguments, then runs main()
    """
    # Check for --languages
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("-l", "--languages", action="store_true")

    parser.add_argument("-h", "--help", action="store_true")

    args, remaining_args = parser.parse_known_args()

    if args.languages:
        show_languages()
        return

    if args.help:
        show_help()
        return

    # Continue checking other arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("language",type=str)

    parser.add_argument("-n", "--disable_nullable", action="store_false")
    args = parser.parse_args(remaining_args)

    language = args.language.lower()

    if args.disable_nullable:
        if language != "c#":
            print("Error: Language chosen is not C#, and thus does not support disabling of nullable error checking!")
            input("Press enter to exit!")
            exit()

    main(language, args.disable_nullable)


def ask_inputs() -> None:
    """
    Asks user for argument inputs, then runs main()
    """
    show_languages()
    language = input("\nWhat language will the project use?\nLanguage: ").lower()

    disable_nullable = True
    if language == "c#" and input("\nDo you want to disable nullable error checking? Default is Yes\nY/N: ").lower() == "y":
        disable_nullable = False

    main(language, disable_nullable)


def show_help():
    """
    Displays the help message
    """
    print(
        """usage: codeforge.py [options] <language> [args]

options:
    -h, --help              Shows this help message and exit
    -l, --languages         Show the supported languages and exit

positional arguments:
    language                The language that the project will use

optional arguments:
    -n, --disable_nullable  If using C#, disable nullable error checking
    

example: codeforge.py C# -n"""
    )


def show_languages():
    """
    Displays the supported languages
    """
    print("Supported languages:")
    for item in LANGUAGES:
        print(item.capitalize())


def main(language: str, disable_nullable: bool) -> None:
    """
    Creates a project folder for a specified langauge with optional flags.

    Can also create a github repository or clone a specified repository.

    Args:
        language (str): The language that the project will use.
        disable_nullable (bool): If using C#, disables nullable error checking when true.
    """

    print(f"\nChosen language: {language}")
    if language not in LANGUAGES:
        print("Error: Language not supported!")
        input("Press enter to exit!")
        exit()

    if language == "c#":
        print(f"Disable nullable error checking: {str(disable_nullable)}")


if __name__ == "__main__":
    # Check if arguments have been given
    # if not, ask for inputs manually
    if not len(argv) < 2:
        handle_args()
    else:
        ask_inputs()

#!/usr/bin/env/ python3

from os import path
from subprocess import run

def get_file_path(filename: str, language:str, ) -> str:
    """
    Returns the path of a txt file, depending on the language it is in.

    Args:
        filename (str): The name of the file
        language (str): The language of the file
    """
    return path.abspath(path.join(".", "templates", language, filename) + '.txt')

def create_template(filename: str, language:str, desc: str, show: bool = True) -> None:
    """
    Creates a blank template for a given language with a custom name and description.
    
    Will provide an output message when successful. Can be disabled by setting \'show\' to false.

    Args:
        filename (str): The name of the template
        language (str): The language that the template is for.
        desc (str, optional): The description of the template.
        show (bool, optional): Will show an output message when successful. Default is True
    """
    file_path = get_file_path(language, filename)
    with open(file_path, "w") as template:
        template.write(f"# Description:\n# {desc}\n")
        template.close()

    if show: print(f"Successfully created \'{filename}\' at \'{file_path}\'")

    return

def create_defaults(language:str, show: bool = True) -> None:
    """
    Will create a set of default templates for the chosen language.

    Will provide an output message when successful. Can be disabled by setting \'show\' to false.

    Args:
        language (str): The language that the template is for.
        show (bool, optional): Will show an output message when successful. Default is True
    """
    if language == "python":
        file_path = get_file_path("blank", "python")
        if not path.exists(file_path):
            with open(file_path, 'w+') as template:
                template.write(f"# Description:\n# A blank file\n")
                template.close()
            if show: print(f"Successfully created \'blank\' at \'{file_path}\'")

        file_path = get_file_path("hello world", "python")
        if not path.exists(file_path):
            with open (file_path, 'w+') as template:
                template.write(f"# Description:\n# A simple \'hello world\' file.\n")
                template.write("print(\"Hello, World!\")\n")
                template.close()
            if show: print(f"Successfully created \'hello, world!\' at \'{file_path}\'")

        file_path = get_file_path("if name main", "python")
        if not path.exists(file_path):
            with open (file_path, 'w+') as template:
                template.write(f"# Description:\n# A file with the \'if name main\' boilerplate code.\n")
                template.write("""def main():
    print(\"Hello, World!\")


if __name__ == \'__main__\':
    main()
""")
                template.close()
            if show: print(f"Successfully created \'if name main\' at \'{file_path}\'")
    
    # Due to a lack of dotnet on linux, the only available template is a blank file
    elif language == "c#":
        file_path = get_file_path("blank", "c#")
        if not path.exists(file_path):
            with open(file_path, 'w+') as template:
                template.write(f"# Description:\n# A blank file\n")
                template.close()
            if show: print(f"Successfully created \'blank\' at \'{file_path}\'")
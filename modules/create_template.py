from os import path, makedirs


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
    
    Will provide an output message when successful. Can be disabled by setting 'show' to false.

    Args:
        filename (str): The name of the template
        language (str): The language that the template is for.
        desc (str, optional): The description of the template.
        show (bool, optional): Will show an output message when successful. Default is True
    """
    if not path.exists(path.join("templates", language)):
        create_defaults(language, False)

    file_path = get_file_path(filename, language)
    with open(file_path, "w+") as template:
        template.write(f"# Description:\n# {desc}\n")

    if show: print(f"Successfully created '{filename}' at '{file_path}'")

    return


def create_defaults(language:str, show: bool = True) -> None:
    """
    Will create a set of default templates for the chosen language.

    Will provide an output message when successful. Can be disabled by setting 'show' to false.

    Args:
        language (str): The language that the template is for.
        show (bool, optional): Will show an output message when successful. Default is True
    """
    makedirs(path.join("templates", language), exist_ok=True)

    created = 0
    # Create python templates
    if language == "python":
        # Create 'hello world'
        file_path = get_file_path("hello world", "python")
        if not path.exists(file_path):
            created += 1
            with open (file_path, 'w+') as template:
                template.write(f"# Description:\n# A simple 'hello world' file.\n")
                template.write("print(\"Hello, World!\")\n")
            if show: print(f"Successfully created 'hello, world!' at '{file_path}'")

        # Create 'if name main'
        file_path = get_file_path("if name main", "python")
        if not path.exists(file_path):
            created += 1
            with open (file_path, 'w+') as template:
                template.write(f"# Description:\n# A file with the 'if name main' boilerplate code.\n")
                template.write("""def main():
    print("Hello, World!")


if __name__ == '__main__':
    main()
""")
            if show: print(f"Successfully created 'if name main' at '{file_path}'")
    
    # Create C# templates
    elif language == "c#":    
        # Create 'hello world'
        file_path = get_file_path("hello world", "c#")
        if not path.exists(file_path):
            created += 1
            with open(file_path, "w+") as template:
                template.write(f"# Description:\n# A simple 'hello world' file.\n")
                template.write("""namespace project;

class Program
{
    static void Main(string[] args)
    {
        Console.WriteLine("Hello, World!");                 
    }
}
""")
            if show: print(f"Successfully created 'hello world' at '{file_path}'")
    
    # Create global 'blank' template
    file_path = get_file_path("blank", language)
    if not path.exists(file_path):
        created += 1
        with open(file_path, 'w+') as template:
            template.write(f"# Description:\n# A blank file\n")
        if show: print(f"Successfully created 'blank' at '{file_path}'")


    if not show: return
    if created > 0:
        print(f"Successfully created all missing default templates for '{language}'")
        return
    print(f"All default templates already exist for '{language}'")
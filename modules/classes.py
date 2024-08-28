class Language():
    """
    A class representing a language with its associated programming language, file extension, optional shebang, and optional gitignore.

    Attributes:
        name (str): The name of the language (e.g., "cs_project").
        language (str): The name of the programming language it uses (e.g., "C#")
        extension (str): The file extension used for files in this language (e.g., "py").
        shebang (str, optional): The shebang line (e.g., "#!/usr/bin/env python3") to be used at the beginning of a script.
        gitignore (str, optional): The contents of the .gitignore file if creating a git repo.
    """
    languages = {}
    def __init__(self, *, name:str, language:str, extension:str, shebang:str = None, gitignore:str = "") -> None:
        """
        Initializes a Language object with the provided name, extension, and optional shebang.

        Arguments:
            name (str): The name of the language variable.
            language (str): The name of the programming language.
            extension (str): The file extension used for files in this language.
            shebang (str, optional): The shebang line for the language, if applicable. Defaults to None.
            gitignore (str, optional): The contents of the .gitignore file if creating a git repo. Defaults to an empty string
        """
        self.name = name.lower()
        self.language = language.lower()
        self.extension = extension.lower()
        self.shebang = shebang
        self.gitignore = gitignore
        Language.languages[self.name] = self

        if self.shebang is not None and not self.shebang.startswith("#!"):
            self.shebang = f"#!{self.shebang}"
        
    def __str__(self) -> str:
        return(f"{self.name.capitalize()}: .{self.extension}\nShebang: '{self.shebang}'\n.gitignore:\n{self.gitignore}")


class IDE():
    """
    A class representing an IDE, optionally with its associated command to open a directory.

    Attributes:
        name (str): The name of the programming language (e.g., "python").
        open_command (str, optional): The command to open the directory with the IDE (e.g., "code 'path/to/directory'" for VS Code).
    """
    ides = {}
    def __init__(self, *, display_name: str, name:str, open_command:str = None) -> None:
        """
        Initializes an IDE object with the provided name, and optional open command.

        Arguments:
            display_name (str): The display name for the IDE
            name (str): The name of the IDE.
            open_command (str): The command to open the directory with the IDE, with the path identifier being denoted by %PATH%. Defaults to None.
        """
        self.display_name = display_name
        self.name = name.lower()
        self.open_command = open_command
        IDE.ides[display_name] = self
        
    def __str__(self) -> str:
        return(f"{self.name.capitalize()}: {self.open_command}")
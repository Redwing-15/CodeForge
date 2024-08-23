class Language():
    """
    A class representing a programming language with its associated file extension, optional shebang, and optional gitignore.

    Attributes:
        name (str): The name of the programming language (e.g., "python").
        extension (str): The file extension used for files in this language (e.g., "py").
        shebang (str, optional): The shebang line (e.g., "#!/usr/bin/env python3") to be used at the beginning of a script.
        gitignore (str, optional): The contents of the .gitignore file if creating a git repo.
    """
    def __init__(self, *, name:str, extension:str, shebang:str = None, gitignore:str = ""):
        """
        Initializes a Language object with the provided name, extension, and optional shebang.

        Arguments:
            name (str): The name of the programming language.
            extension (str): The file extension used for files in this language.
            shebang (str, optional): The shebang line for the language, if applicable. Defaults to None.
            gitignore (str, optional): The contents of the .gitignore file if creating a git repo. Defaults to an empty string
        """
        self.name = name.lower()
        self.extension = extension.lower()
        self.shebang = shebang
        self.gitignore = gitignore
        
    def __str__(self) -> str:
        return(f"{self.name.capitalize()}: .{self.extension}\nShebang: '{self.shebang}'\n.gitignore:\n{self.gitignore}")
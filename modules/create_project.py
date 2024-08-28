from os import path, system as os_system, makedirs, remove
from platform import system as platform_system
from shutil import rmtree

# Need to use modules.classes as this script is intended to be called
# from codeforge.py, which is in a parent directory and thus imports must
# also be called from the parent directory
from modules.classes import Language, IDE
from modules.functions import get_defaults

def create_project(project_name:str,
                   language: Language,
                   template: str,
                   nullable: bool,
                   create_repo: bool,
                   open_project: bool,
                   output: str) -> None:
    """
    Creates a project folder for a specified langauge with optional flags

    Can also create a github repository for the project

    Args:
        project_name (str): The name of the project
        language (Language): The language object that the project will use
        template (str): The template to use for the project
        nullable (bool): If using C#, enables nullable error checking if True
        create_repo (bool): Will initialize a git repository
        open_project (bool): Will open the project in VS Code once created if True
        output (str): Specifies the output path for the project
    """
    project_path = path.abspath(path.join(output, project_name))

    if path.exists(project_path):
        if input("Folder already exists. Do you want to overwrite it's contents?\n(Y) Y/N: ").lower() == 'n':
            print("Exiting program")
            return
        rmtree(project_path)

    makedirs(project_path)
    if language.extension == "cs":
        os_system(f'dotnet new console -n {project_name} -o "{project_path}"')
        remove(path.join(project_path, f"Program.cs"))

    template_path = f"{path.join("templates", language.language, template)}.txt"
    with open(template_path, "r") as file:
        template_lines = file.readlines()
    # Remove first two lines as they only include template description
    template_lines = template_lines[2:len(template_lines)]
        
    if language.shebang:
        template_lines.insert(0, f"{language.shebang}\n")
    with open(path.join(project_path, f"{project_name}.{language.extension}"), "w+") as file:
        file.writelines(template_lines)

    if not nullable and language.extension == "cs":
        with open(path.join(project_path, f"{project_name}.csproj"), 'r') as file:
            content = file.read()
        content = content.replace("<Nullable>enable</Nullable>", "<Nullable>disable</Nullable>")
        with open(path.join(project_path, f"{project_name}.csproj"), 'w') as file:
            content = file.write(content)

    print(f"Successfully created project at '{project_path}'")

    operating_system = platform_system()
    # Provide execute permissions for the file if on linux
    if operating_system == "Linux":
        if language.language != "c#": # C# uses 'dotnet new' which already provides permissions
            os_system(f'chmod +x "{path.join(project_path, f"{project_name}.{language.extension}")}"')
    
    if create_repo: 
        if operating_system == "Windows":
            next_command = "&&"
        elif operating_system == "Linux":
            next_command = ";"
        else:
            print(f"Error: Unsupported operating system {operating_system}")
        os_system(f'cd "{project_path}" {next_command} git init')

        with open(path.join(project_path, ".gitignore"), 'w+') as file:
            file.write(language.gitignore)
    
    if open_project:
        ide_dict = get_defaults(language.name)["ide"]
        ide = IDE.ides[ide_dict]
        ide_command = ide.open_command

        if ide_command is None:
            print(f"codeforge.py: error: IDE '{ide.name}' does not have an open directory command.")
            return

        # Remove ide.open_command path identifier with actual path
        command = ide_command.replace("%PATH%", f'"{path.abspath(project_path)}"')
        os_system(command)
    
    return
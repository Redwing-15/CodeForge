from os import path, system as os_system, makedirs, remove
from platform import system as platform_system
from shutil import rmtree

LANGUAGES = ["python", "c#"]


def create_project(project_name:str,
                   language: str,
                   template: str,
                   project: bool,
                   nullable: bool,
                   create_repo: bool,
                   open_project: bool,
                   output: str) -> None:
    """
    Creates a project folder for a specified langauge with optional flags

    Can also create a github repository for the project

    Args:
        project_name (str): The name of the project
        language (str): The language that the project will use
        template (str): The template to use for the project
        project (bool): If using C#, creates a .csproj instead of a .csx if True
        nullable (bool): If using C#, enables nullable error checking if True
        create_repo (bool): Will initialize a git repository
        open_project (bool): Will open the project in VS Code once created if True
        output (str): Specifies the output path for the project
    """
    project_path = path.join(output, project_name)

    print(f"output: {output}, project: {project_path}")
    if path.exists(project_path):
        if input("Folder already exists. Do you want to overwrite it's contents?\n(Y) Y/N: ").lower() == 'n':
            print("Exiting program")
            return
        rmtree(project_path)

    makedirs(project_path)
    if language == "c#":
        if project:
            os_system(f"dotnet new console -n {project_name} -o {project_path}")
        else:
            extension = "csx"
            shebang = "/usr/bin/env/ dotnet-script"
            

    template_path = f"{path.join("templates", language, template)}.txt"
    with open(template_path, "r") as file:
        template_lines = file.readlines()
    # Remove first two lines as they are just the template description
    template_lines = template_lines[2:len(template_lines)]

    if language == "python":
        extension = "py"
        shebang = "/usr/bin/env python3"
    elif language == "c#" and project == True:
        extension = "cs"
        shebang = False
        remove(path.join(project_path, f"Program.cs"))
    elif not language in LANGUAGES:
        print(f"Error: Unsupported language {language}")
        return
        
    if shebang:
        template_lines.insert(0, f"#!{shebang}\n")
    with open(path.join(project_path, f"{project_name}.{extension}"), "w+") as file:
        file.writelines(template_lines)

    if not nullable and language == "c#":
        with open(path.join(project_path, f"{project_name}.csproj"), 'r') as file:
            content = file.read()
        content = content.replace("<Nullable>enable</Nullable>", "<Nullable>disable</Nullable>")
        with open(path.join(project_path, f"{project_name}.csproj"), 'w') as file:
            content = file.write(content)

    print(f"Successfully created project at '{project_path}'")

    operating_system = platform_system()
    # Provide execute permissions for the file if on linux
    if operating_system == "Linux":
        if language != "c#": # C# uses 'dotnet new' which already provides permissions
            os_system(f'chmod +x "{path.join(project_path, f"{project_name}.{extension}")}"')
    
    if create_repo: 
        if operating_system == "Windows":
            next_command = "&&"
        elif operating_system == "Linux":
            next_command = ";"
        else:
            print(f"Error: Unsupported operating system {operating_system}")
        os_system(f'cd "{project_path}" {next_command} git init')

        if language == "python":
            with open(path.join(project_path, ".gitignore"), 'w+') as file:
                file.write("# Ignore __pycache__\n__pycache__/")
    
    if open_project:
        os_system(f'code "{path.abspath(project_path)}"')
    
    return
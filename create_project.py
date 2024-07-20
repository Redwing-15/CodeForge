from os import path, system as os_system, makedirs
from platform import system as platform_system
from shutil import rmtree


def create_project(project_name:str, language: str, template: str, disable_nullable: bool, create_repo: bool, open_project: bool) -> None:
    """
    Creates a project folder for a specified langauge with optional flags

    Can also create a github repository for the project

    Args:
        project_name (str): The name of the project
        language (str): The language that the project will use
        template (str): The template to use for the project
        disable_nullable (bool): If using C#, disables nullable error checking when true
        create_repo (bool): Will initialize a git repository
        open_project (bool): Will open the project in VS Code if True
    """
    project_path = path.join("projects", language, project_name)
    if path.exists(project_path):
        if input("Folder already exists. Do you want to overwrite it's contents?\n(Y) Y/N: ").lower() == 'n':
            print("Exiting program")
            return
        rmtree(project_path)
    makedirs(project_path)

    template_path = f"{path.join("templates", language, template)}.txt"
    with open(template_path, "r") as file:
        template_lines = file.readlines()
        file.close()
    # Remove first two lines as they are just the template description
    template_lines = template_lines[2:len(template_lines)]

    with open(path.join(project_path, f"{project_name}.py"), "w+") as file:
        file.writelines(template_lines)
        file.close()

    if create_repo: 
        operating_system = platform_system()
        if operating_system == "Windows":
            next_command = "&&"
        elif operating_system == "Linux":
            next_command = ";"
        else:
            print(f"Error: Unsupported operating system {operating_system}")

        os_system(f"cd {project_path} {next_command} git init")
    
    if open_project:
        os_system(f"code \"{path.abspath(project_path)}\"")
    
    print(f"Successfully created project")
    return
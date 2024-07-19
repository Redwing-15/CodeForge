#!/usr/bin/env/ python3
from os import path, system as os_system, mkdir
from platform import system as platform_system

def create_project(project_name:str, language: str, template: str, disable_nullable: bool, create_repo: bool) -> None:
    """
    Creates a project folder for a specified langauge with optional flags

    Can also create a github repository for the project

    Args:
        project_name (str): The name of the project
        language (str): The language that the project will use
        template (str): The template to use for the project
        disable_nullable (bool): If using C#, disables nullable error checking when true
        create_repo (bool): Will initialize a git repository
    """

    print(f"Project name: {project_name}")
    print(f"\nChosen language: {language}")

    if language == "c#":
        print(f"\nDisable nullable error checking: {str(disable_nullable)}")

    print(f"\nTemplate: {template}")

    if create_repo: 
        print(f"\nCreating git repository")
        operating_system = platform_system()
        if operating_system == "Windows":
            next_command = "&&"
        elif operating_system == "Linux":
            next_command = ";"
        else:
            print(f"Error: Unsupported operating system {operating_system}")

        print(f"cd {path.join(language, project_name)} {next_command} git init")
        # Will allow git init when project creation is implemented
        # os_system(f"cd {path.join(language, project_name)} {next_command} git init")
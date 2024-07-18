#!/usr/bin/env/ python3

def create_project(language: str, template: str, disable_nullable: bool) -> None:
    """
    Creates a project folder for a specified langauge with optional flags.

    Can also create a github repository or clone a specified repository. (TBD)

    Args:
        language (str): The language that the project will use.
        template (str): The template to use for the project.
        disable_nullable (bool): If using C#, disables nullable error checking when true.
    """

    print(f"\nChosen language: {language}")

    if language == "c#":
        print(f"Disable nullable error checking: {str(disable_nullable)}")

    print(f"Template: {template}")
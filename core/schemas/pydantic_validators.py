"""
    Extra Functions

    Description:
        This module contains extra functions that are used in the application ecosystem at multiple
    places.

"""

# Importing Python packages
import re

# Importing FastAPI packages

# Importing from project files


# --------------------------------------------------------------------------------------------------


def lowercase_email_username(string: str) -> str:
    """
        Lowercase String

        Description:
            This method is used to lowercase the email or username passed to the API.

        Parameters:
        - **string**: String to be lowercased. (STR) *--Required*

        Returns:
        - **string**: Lowercased string.

    """
    print("Calling lowercase_email_username method")

    return string.strip().lower()


def username_validator(username: str) -> str:
    """
        Username Validator

        Description:
            This method is used to validate the username data passed to the API.

        Parameters:
        - **username**: Username to be validated. (STR) *--Required*

        Returns:
        - **username**: Validated username with lower.

    """
    print("Calling username_validator method")

    if not re.search(r"^[a-zA-Z0-9_.-]+$", username):
        raise ValueError(
            'Username can only contains alphabets, numbers, underscore, dot and hyphen')
    return username.lower()


def names_validator(name: str) -> str:
    """
        Name Validator

        Description:
            This method is used to validate the name data passed to the API.

        Parameters:
        - **value**: Name to be validated. (STR) *--Required*

        Returns:
        - **value**: Validated name.

    """
    print("Calling names_validator method")

    if not re.search(r"^[a-zA-Z]*$", name):
        raise ValueError('Only alphabets are allowed')
    return name


def password_validator(password: str) -> str:
    """
        Password Validator

        Description:
            This method is used to validate the password data passed to the API.

        Parameters:
        - **value**: Password to be validated. (STR) *--Required*

        Returns:
        - **value**: Validated password.

    """
    print("Calling password_validator method")

    if not re.search(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#^()_+-/])"
                     r"[A-Za-z\d@$!%*?&#^()_+-/]{8,}$", password):
        raise ValueError("Password should contain at least one uppercase, "
                         "one lowercase and special character")
    return password


def contact_validator(contact):
    """
        Contact Number Validator

        Description:
            This method is used to validate the contact number passed to the API.
    """
    print("Calling contact_validator method")

    if not re.search(r"\d{3}[-. ]\d{3}[-. ]\d{4}|"
                     r"\(\d{2,3}\)[-. ]\d{3,4}[-. ]\d{4}|"
                     r"\+\d{1,2}[-. ]\(\d{3}\)[-. ]\d{3}[-. ]\d{4}|"
                     r"\+\d{1,2}\(\d{3}\)[-. ]\d{3}[-. ]\d{4}|"
                     r"\+\d{1,2}[-. ]\d{3}[-. ]\d{3}[-. ]\d{4}|\+\d{1,2}\d{10}", contact):
        raise ValueError('Contact number should be in proper format')
    return contact


def general_validator(value):
    """
        General String Validator

        Description:
            This method is used to validate the other string passed to the API.

        Parameters:
        - **value**: String to be validated. (STR) *--Required*

        Returns:
        - **value**: Validated string.

    """
    print("Calling general_validator method")

    if not re.search(r"^[^\s].+[^\s]$", value):
        raise ValueError(f"{value} should not start or end with space")
    return value

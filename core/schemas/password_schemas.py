"""
    Password Pydantic Schemas

    Description:
        This module contains all the password schemas used by the API.
        Schemas are used to validate the data passed to the API.

"""

# Importing Python packages
from pydantic import (BaseModel, EmailStr, Field, validator)

# Importing FastAPI packages

# Importing from project files
from core.schemas.pydantic_validators import (lowercase_email_username, password_validator)


# --------------------------------------------------------------------------------------------------


class PasswordSchema(BaseModel):
    """
        Password Schema

        Description:
            This schema is used to validate the password data passed to the API.

    """
    password: str = Field(min_length=8, max_length=3_0, example="Abc12345#")
    password_validator = validator("password", allow_reuse=True)(password_validator)
    token: str = Field(example="123456")


class ChangePasswordSchema(BaseModel):
    """
        Change Password Schema

        Description:
            This schema is used to validate the password data passed to change password API.

    """

    old_password: str = Field(min_length=8, max_length=3_0, example="Abc12345#")
    old_password_validator = validator("old_password", allow_reuse=True)(password_validator)
    new_password: str = Field(min_length=8, max_length=3_0, example="Abc12345#")
    new_password_validator = validator("new_password", allow_reuse=True)(password_validator)


class RequestResetPasswordSchema(BaseModel):
    """
        Request Reset Password Schema

        Description:
            This schema is used to validate the email to reset password passed to the API.

    """
    email: EmailStr = Field(example="johndoe@email.com")
    lowercase_email = validator("email", allow_reuse=True)(lowercase_email_username)


class ResetPasswordSchema(BaseModel):
    """
        Reset Password Schema

        Description:
            This schema is used to validate the password data passed to reset password API.

    """
    password: str = Field(min_length=8, max_length=3_0, example="Abc12345#")
    password_validator = validator("password", allow_reuse=True)(password_validator)
    token: str = Field(example="123456")

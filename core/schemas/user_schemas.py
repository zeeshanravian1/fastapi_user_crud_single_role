"""
    User Pydantic Schemas

    Description:
        This module contains all the user schemas used by the API.
        Schemas are used to validate the data passed to the API.

"""

# Importing Python packages
from datetime import datetime
from pydantic import (BaseModel, EmailStr, Field, validator)

# Importing FastAPI packages

# Importing from project files
from core.schemas.pydantic_validators import (lowercase_email_username, username_validator,
                                              names_validator, contact_validator, general_validator)


# --------------------------------------------------------------------------------------------------


class UserCreateSchema(BaseModel):
    """
        User In Schema

        Description:
            This schema is used to validate the user creation data passed to the API.

    """
    email: EmailStr = Field(example="johndoe@email.com")
    lowercase_email = validator("email", allow_reuse=True)(lowercase_email_username)


class UserReadSchema(BaseModel):
    """
        User Out Schema

        Description:
            This schema is used to validate the user data returned from the API.

    """
    id: int
    first_name: str | None = Field(None, min_length=1, max_length=3_0, example="John")
    first_name_validator = validator("first_name", allow_reuse=True)(names_validator)
    last_name: str | None = Field(None, min_length=1, max_length=3_0, example="Doe")
    last_name_validator = validator("last_name", allow_reuse=True)(names_validator)
    contact: str | None = Field(None, min_length=1, max_length=3_0, example="(02) 123-4567")
    contact_validator = validator("contact", allow_reuse=True)(contact_validator)
    username: str = Field(None, min_length=1, max_length=3_0, example="johndoe")
    username_validator = validator("username", allow_reuse=True)(username_validator)
    email: EmailStr = Field(example="johndoe@email.com")
    company_name: str | None = Field(None, min_length=1, max_length=3_0, example="Company Name")
    company_name_validator = validator("company_name", allow_reuse=True)(general_validator)
    address: str | None = Field(None, min_length=1, max_length=1_00, example="Address")
    address_validator = validator("address", allow_reuse=True)(general_validator)
    city: str | None = Field(None, min_length=1, max_length=3_0, example="City")
    city_validator = validator("city", allow_reuse=True)(general_validator)
    country: str | None = Field(None, min_length=1, max_length=3_0, example="Country")
    country_validator = validator("country", allow_reuse=True)(general_validator)
    postal_code: str | None = Field(None, min_length=1, max_length=6, example="12345")
    postal_code_validator = validator("postal_code", allow_reuse=True)(general_validator)
    profile_image: str | None = Field(None, min_length=1, max_length=1_00, example="Address")
    is_active: bool
    role_id: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserRoleCreateSchema(BaseModel):
    """
        Set User Role Schema

        Description:
            This schema is used to validate the user role data passed to the API.

    """
    user_id: int
    role_id: int


class UserUpdateSchema(BaseModel):
    """
        User Update Schema

        Description:
            This schema is used to validate the user update data passed to the API.

    """
    first_name: str = Field(min_length=1, max_length=3_0, example="John")
    first_name_validator = validator("first_name", allow_reuse=True)(names_validator)
    last_name: str = Field(min_length=1, max_length=3_0, example="Doe")
    last_name_validator = validator("last_name", allow_reuse=True)(names_validator)
    contact: str | None = Field(None, min_length=1, max_length=3_0, example="(02) 123-4567")
    contact_validator = validator("contact", allow_reuse=True)(contact_validator)
    username: str | None = Field(None, min_length=1, max_length=3_0, example="johndoe")
    username_validator = validator("username", allow_reuse=True)(username_validator)
    company_name: str | None = Field(None, min_length=1, max_length=3_0, example="Company Name")
    company_name_validator = validator("company_name", allow_reuse=True)(general_validator)
    address: str | None = Field(None, min_length=1, max_length=1_00, example="Address")
    address_validator = validator("address", allow_reuse=True)(general_validator)
    city: str | None = Field(None, min_length=1, max_length=3_0, example="City")
    city_validator = validator("city", allow_reuse=True)(general_validator)
    country: str | None = Field(None, min_length=1, max_length=3_0, example="Country")
    country_validator = validator("country", allow_reuse=True)(general_validator)
    postal_code: str | None = Field(None, min_length=1, max_length=3_0, example="12345")
    postal_code_validator = validator("postal_code", allow_reuse=True)(general_validator)
    profile_image: str | None = None


class UserPatchSchema(BaseModel):
    """
        User Partially Update Schema

        Description:
            This schema is used to validate the user patch data passed to the API.

    """
    first_name: str | None = Field(None, min_length=1, max_length=3_0, example="John")
    first_name_validator = validator("first_name", allow_reuse=True)(names_validator)
    last_name: str | None = Field(None, min_length=1, max_length=3_0, example="Doe")
    last_name_validator = validator("last_name", allow_reuse=True)(names_validator)
    contact: str | None = Field(None, min_length=1, max_length=3_0, example="(02) 123-4567")
    contact_validator = validator("contact", allow_reuse=True)(contact_validator)
    username: str | None = Field(None, min_length=1, max_length=3_0, example="johndoe")
    username_validator = validator("username", allow_reuse=True)(username_validator)
    company_name: str | None = Field(None, min_length=1, max_length=3_0, example="Company Name")
    company_name_validator = validator("company_name", allow_reuse=True)(general_validator)
    address: str | None = Field(None, min_length=1, max_length=1_00, example="Address")
    address_validator = validator("address", allow_reuse=True)(general_validator)
    city: str | None = Field(None, min_length=1, max_length=3_0, example="City")
    city_validator = validator("city", allow_reuse=True)(general_validator)
    country: str | None = Field(None, min_length=1, max_length=3_0, example="Country")
    country_validator = validator("country", allow_reuse=True)(general_validator)
    postal_code: str | None = Field(None, min_length=1, max_length=3_0, example="12345")
    postal_code_validator = validator("postal_code", allow_reuse=True)(general_validator)
    profile_image: str | None = None

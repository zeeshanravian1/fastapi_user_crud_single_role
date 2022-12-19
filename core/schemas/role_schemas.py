"""
    Role Pydantic Schemas

    Description:
        This module contains all the role schemas used by the API.
        Schemas are used to validate the data passed to the API.

"""

# Importing Python packages
from datetime import datetime
from typing import Literal
from pydantic import (BaseModel, Field)

# Importing FastAPI packages

# Importing from project files


# --------------------------------------------------------------------------------------------------


class RoleCreateSchema(BaseModel):
    """
        Role In Schema

        Description:
            This schema is used to validate the role creation data passed to the API.

    """
    role_name: Literal["super_admin", "admin", "manager", "user", "reporting_user"]
    role_description: str = Field(min_length=1, max_length=3_0)


class RoleReadSchema(RoleCreateSchema):
    """
        Role Out Schema

        Description:
            This schema is used to validate the role data returned from the API.

    """
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None


class RoleUpdateSchema(BaseModel):
    """
        Role Update Schema

        Description:
            This schema is used to validate the role update data passed to the API.

    """
    role_name: Literal["super_admin", "admin", "manager", "user", "reporting_user"]
    role_description: str = Field(min_length=1, max_length=3_0)


class RolePatchSchema(BaseModel):
    """
        Role Partially Update Schema

        Description:
            This schema is used to validate the role patch data passed to the API.

    """
    role_name: Literal["super_admin", "admin", "manager",
                       "user", "reporting_user"] | None = None
    role_description: str | None = Field(None, min_length=1, max_length=3_0)

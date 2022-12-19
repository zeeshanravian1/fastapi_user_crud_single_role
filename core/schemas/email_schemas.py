"""
    Email Pydantic Schemas

    Description:
        This module contains all the email schemas used by the API.
        Schemas are used to validate the data passed to the API.

"""

# Importing Python packages
from typing import (Any, Dict, List)
from pydantic import (BaseModel, EmailStr, Field, validator)

# Importing FastAPI packages

# Importing from project files
from core.schemas.pydantic_validators import lowercase_email_username


# --------------------------------------------------------------------------------------------------


class EmailSchema(BaseModel):
    """
        Email Schema

        Description:
            This schema is used to validate the email data passed to send email.

    """
    email: List[EmailStr] = Field(example="johndoe@email.com")
    lowercase_email = validator("email", allow_reuse=True)(lowercase_email_username)
    body: Dict[str, Any]

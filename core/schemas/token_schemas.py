"""
    Token Pydantic Schemas

    Description:
        This module contains all the token schemas used by the API.
        Schemas are used to validate the data passed to the API.

"""

# Importing Python packages
from typing import List
from pydantic import BaseModel

# Importing FastAPI packages

# Importing from project files


# --------------------------------------------------------------------------------------------------


class TokenData(BaseModel):
    """
        Token Data Schema

        Description:
            This schema is used to validate the token data passed to the API.

    """
    name: str | None = None
    scopes: List[str] = []

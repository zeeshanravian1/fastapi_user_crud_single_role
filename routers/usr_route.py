"""
    Route module

    Description:
        This module is used to create a route.

"""

# Importing FastAPI packages
from fastapi import APIRouter

# Importing from project files
from routers import (usr_auth, usr_role, usr_user)

# Router Object to Create Routes
router = APIRouter()


# --------------------------------------------------------------------------------------------------


# Include all file routes
router.include_router(usr_role.router)
router.include_router(usr_user.router)
router.include_router(usr_auth.router)

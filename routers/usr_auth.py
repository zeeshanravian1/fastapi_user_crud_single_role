"""
    Login Authentication

    Description:
        This module is responsible for handling the login authentication.
        It is used to verify the user's credentials and create a JWT token.

"""

# Importing Python packages
import traceback
from passlib.hash import pbkdf2_sha256

# Importing FastAPI packages
from fastapi import (APIRouter, Depends, HTTPException, status)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

# Importing from project files
from core.models.database import (database, UserTable)
from internal.token import create_access_token


# Router Object to Create Routes
router = APIRouter(
    tags=["Log In"]
)


# --------------------------------------------------------------------------------------------------


# Login Route
@router.post('/login/', summary="Performs authentication")
async def log_in(request: OAuth2PasswordRequestForm = Depends()):
    """
        Performs authentication and returns the authentication token to keep the user
        logged in for longer time.

        Provide **Username** and **Password** to log in.

    """
    print("Calling log_in method")

    try:
        query = UserTable.select().where(UserTable.c.username == request.username.lower())
        user_result = await database.fetch_one(query=query)

        if not user_result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        if not pbkdf2_sha256.verify(request.password, user_result['password']):
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"detail": "Password is incorrect"})

        access_token = create_access_token(data={"sub": user_result["username"],
                                                 "scopes": request.scopes,
                                                 "id": user_result["id"]},
                                           token_type="access")

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error in authorizing credentials, Please try again") from err

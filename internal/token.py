"""
    Token, Scopes, and Security

    Description:
        This module is used to create a token for the user and get the current user to assign scopes
        The scopes are used to determine what the user can do in the application.

"""

# Importing Python packages
import traceback
from datetime import (datetime, timedelta)
from typing import (Dict, List)
from jose import (jwt, JWTError)
from pydantic import ValidationError

# Importing FastAPI packages
from fastapi import (Depends, HTTPException, Security, status)
from fastapi.security import (OAuth2PasswordBearer, SecurityScopes)

# Importing from project files
from dependencies import (ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES)
from core.models.database import (database, RoleTable, UserTable)
from core.schemas.user_schemas import UserReadSchema
from core.schemas.token_schemas import TokenData
from core.scopes.set_scope import Role


# --------------------------------------------------------------------------------------------------


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict, token_type: str) -> str:
    """
        Create an access token from a user id and scopes

        Description:
            This function is used to create an access token from a user id and scopes.

        Parameters:
            data (dict): The data to be used to create the token.
            token_type (str): The type of token to be created.

        Returns:
            str: The access token.

    """
    print("Calling create_access_token method")

    try:
        to_encode = data.copy()

        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        if token_type == "refresh":
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES * 2)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong while creating token") from err


def assign_scopes(scopes) -> List[str]:
    """
        Assign scopes to a user

        Description:
            This function is used to assign scopes to a user.

        Parameters:
            scopes (list): The scopes to be assigned to the user.

        Returns:
            list: The scopes assigned to the user.

    """
    print("Calling assign_scopes method")

    try:
        if Role.SUPER_ADMIN["name"] in scopes:
            return [Role.SUPER_ADMIN["name"], Role.ADMIN["name"],
                    Role.MANAGER["name"], Role.USER["name"], Role.REPORTING_USER["name"]]

        if Role.ADMIN["name"] in scopes:
            return [Role.ADMIN["name"], Role.MANAGER["name"],
                    Role.USER["name"], Role.REPORTING_USER["name"]]

        if Role.MANAGER["name"] in scopes:
            return [Role.MANAGER["name"], Role.USER["name"], Role.REPORTING_USER["name"]]

        if Role.USER["name"] in scopes:
            return [Role.USER["name"], Role.REPORTING_USER["name"]]

        if Role.REPORTING_USER["name"] in scopes:
            return [Role.REPORTING_USER["name"]]

        return []

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong while assigning scopes") from err


async def get_current_user(security_scopes: SecurityScopes,
                           token: str = Depends(oauth2_scheme)) -> Dict:
    """
        Get the current user

        Description:
            This function is used to get the current user.

        Parameters:
            security_scopes (SecurityScopes): The scopes to be assigned to the user.
            token (str): The token to be used to get the user.

        Returns:
            dict: The user.

    """
    print("Calling get_current_user method")

    if security_scopes.scopes:
        authenticate_value = f"Brearer scope='{security_scopes.scope_str}'"
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        userid: str = payload.get("id")

        if username is None:
            raise credentials_exception

    except (JWTError, ValidationError) as err:
        raise credentials_exception from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong while getting current user") from err

    query = UserTable.join(RoleTable, RoleTable.c.id == UserTable.c.role_id). \
        select().with_only_columns([UserTable, RoleTable.c.role_name]). \
        where(UserTable.c.id == userid)
    result = await database.fetch_one(query=query)

    if not result:
        raise credentials_exception

    token_scopes = [result.role_name.upper()]
    token_scopes = assign_scopes(token_scopes)

    token_data = TokenData(scopes=token_scopes, name=username)

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return result


async def get_current_active_user(current_user: UserReadSchema = Security(get_current_user)
                                  ) -> Dict:
    """
        Get the current active user

        Description:
            This function is used to get the current active user.

        Parameters:
            current_user (UserSchema): The user to be checked.

        Returns:
            dict: The user.

    """
    print("Calling get_current_active_user method")

    try:
        current_user = UserReadSchema.parse_obj(current_user)

        return current_user

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong while getting current active user") \
            from err

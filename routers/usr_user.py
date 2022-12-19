"""
    User APIs Module

    Description:
        This module is responsible for handling the user APIs.
        It is used to create, update, delete and get the user details.

"""

# Importing Python packages
import traceback
from datetime import (datetime, timedelta)
from jose import (jwt, JWTError)
from passlib.hash import pbkdf2_sha256
from asyncpg import exceptions

# Importing FastAPI packages
from fastapi import (APIRouter, HTTPException, Security, status)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page, paginate)

# Importing from project files
from dependencies import (ALGORITHM, SECRET_KEY, COMPANY_NAME, OTP_CODE_EXPIRY_MINUTES,
                          FRONTEND_URL)
from core.models.database import (database, UserTable)
from core.scopes.set_scope import Role
from core.schemas.user_schemas import (UserCreateSchema, UserReadSchema, UserRoleCreateSchema,
                                       UserUpdateSchema, UserPatchSchema)
from core.schemas.password_schemas import (PasswordSchema, ChangePasswordSchema,
                                           RequestResetPasswordSchema, ResetPasswordSchema)
from internal.token import get_current_active_user
from internal.helper import generate_otp_code
from internal.send_email import send_email
from routers.usr_role import get_role

# Router Object to Create Routes
router = APIRouter(
    prefix='/user',
    tags=["User"]
)


# --------------------------------------------------------------------------------------------------


# Create a single user route
@router.post('/create/', summary="Create a single user",
             responses={
                 201: {
                     "description": "User created successfully",
                     "content": {
                         "application/json": {
                             "example": {"detail": "User created successfully"}
                         }
                     },
                 },
                 200: {
                     "description": "Email sent at given email address",
                     "content": {
                         "application/json": {
                             "example": {"detail": "Email sent at given email address"}
                         }
                     },
                 }
             })
async def create_user(record: UserCreateSchema) -> dict:
    """
        Creates a single user.

        Description:
        - This method is used to create a single user.

        Parameters:
        User details to be created with following fields:
        - **email**: Email address of user. (STR) *--Required*

        Returns:
        - **JSON**: Email sent status.

    """
    print("Calling create_user method")

    try:
        username = record.email.split("@")[0]

        # Check if email already exists
        email_query = UserTable.select().where(UserTable.c.email == record.email)
        email_result = await database.fetch_one(query=email_query)

        if email_result:
            if email_result.email_verified:
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                    content={"detail": "Email already verified"})

            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                content={"detail": "Email already exists"})

        # Check if username already exists
        username_query = UserTable.select().where(UserTable.c.username == username)
        username_result = await database.fetch_one(query=username_query)

        if username_result:
            username = f"{username}_{str(datetime.now().microsecond)}"

        # Generate OTP Code
        otp_code = await generate_otp_code()
        otp_expiry_time = datetime.now() + timedelta(minutes=OTP_CODE_EXPIRY_MINUTES)

        # Encode the OTP Code
        encoded_jwt = jwt.encode({
            "email": record.email,
            "token": str(otp_code),
            "expiry": otp_expiry_time.strftime("%Y-%m-%d %H:%M:%S")
        }, SECRET_KEY, algorithm=ALGORITHM)

        email_payload = {
            "email": [record.email],
            "body": {
                "url": f"{FRONTEND_URL}/confirm_email/{encoded_jwt}",
                "first_name": "Test User",
                "msg_purpose": "Confirm Email",
                "company_name": COMPANY_NAME,
                "base_url": FRONTEND_URL
            }
        }

        # Send email
        email_otp_response = await send_email(email_payload)

        if email_otp_response.status_code == 200:
            query = UserTable.insert().values(email=record.email, username=username,
                                              email_otp=otp_code, email_verified=False)
            await database.execute(query=query)

            return JSONResponse(status_code=status.HTTP_201_CREATED,
                                content={"detail": "User created successfully"})

    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token") from err

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Set password route for single user
@router.post('/set_password/', status_code=status.HTTP_200_OK,
             summary="Set password for user",
             response_description="Password set successfully")
async def set_password(record: PasswordSchema) -> dict:
    """
        Sets password for user.

        Description:
        - This method is used to set password for user.

        Parameters:
        - **password**: Password for user. (STR) *--Required*
        - **token**: Token for user. (STR) *--Required*

        Returns:
        - **JSON**: Password set status.

    """
    print("Calling set_password method")

    try:
        token_data = jwt.decode(record.token, SECRET_KEY, algorithms=[ALGORITHM])

        if token_data["expiry"] < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "Token expired"})

        # Check if email exists
        email_query = UserTable.select().where(UserTable.c.email == token_data["email"])
        email_result = await database.fetch_one(query=email_query)

        if not email_result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        # Check if email is already verified
        if email_result.email_verified:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                content={"detail": "Email already verified"})

        # Check if OTP Code is correct
        if email_result.email_otp != token_data["token"]:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "OTP Code is incorrect"})

        # Update password
        query = UserTable.update().where(UserTable.c.email == token_data["email"]).values(
            password=pbkdf2_sha256.hash(record.password), email_otp=None, email_verified=True)
        await database.execute(query=query)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"detail": "Password set successfully"})

    except JWTError as err:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid token") from err

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Set Role of single user by super admin route
@router.post('/set_role/', status_code=status.HTTP_200_OK,
             summary="Set role of user",
             response_description="Role set successfully")
async def set_role(record: UserRoleCreateSchema,
                   current_user: UserReadSchema = Security(get_current_active_user,
                                                           scopes=[Role.SUPER_ADMIN['name']])
                   ) -> dict:
    """
        Sets role of user.

        Description:
        - This method is used to set role of user by Super Admin.

        Parameters:
        - **role_id**: Role ID of user. (INT) *--Required*
        - **user_id**: User ID of user to assign role. (INT) *--Required*

        Returns:
        - **JSON**: Role set status.

    """
    print("Calling set_role method")

    try:
        # Check if role exists
        role_result = await get_role(role_id=record.role_id)

        if role_result.status_code == 404:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Role does not exist"})

        # Update role
        query = UserTable.update().where(UserTable.c.id == record.user_id). \
            values(role_id=record.role_id)

        await database.execute(query=query)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"detail": "Role set successfully"})

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Get a single user route
@ router.get('/{user_id}/', status_code=status.HTTP_200_OK,
             summary="Get a single user by providing id",
             response_model=UserReadSchema,
             response_description="User details fetched successfully")
async def get_user(user_id: int,
                   current_user: UserReadSchema = Security(get_current_active_user,
                                                           scopes=[Role.REPORTING_USER['name']])
                   ) -> dict:
    """
        Get a single user.

        Description:
        - This method is used to get a single user by providing id.

        Parameters:
        - **user_id**: Id of user to be fetched. (INT) *--Required*

        Returns:
        Get a single user with following information:
        - **id**: Id of user. (INT)
        - **first_name**: First name of user. (STR)
        - **last_name**: Last name of user. (STR)
        - **contact**: Contact number of user. (STR)
        - **username**: Username of user. (STR)
        - **email**: Email address of user. (STR)
        - **company_name**: Company name of user. (STR)
        - **address**: Address of user. (STR)
        - **city**: City of user. (STR)
        - **country**: Country of user. (STR)
        - **postal_code**: Postal code of user. (STR)
        - **profile_image**: Profile image of user. (STR)
        - **is_active**: Status of user. (BOOL)
        - **role_id**: Role id of user. (INT)
        - **created_at**: Datetime of user creation. (DATETIME)
        - **updated_at**: Datetime of user updation. (DATETIME)

    """
    print("Calling get_user method")

    try:
        query = UserTable.select().where(UserTable.c.id == user_id)
        result = await database.fetch_one(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        return result

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Get all users route
@ router.get('/', status_code=status.HTTP_200_OK,
             summary="Get all users",
             response_model=Page[UserReadSchema],
             response_description="Users fetched successfully")
async def get_all_users(current_user: UserReadSchema = Security(get_current_active_user,
                                                                scopes=[Role.SUPER_ADMIN['name']])
                        ) -> dict:
    """
        Get all users.

        Description:
        - This method is used to get all users.

        Parameters:
        - **page**: Page number. (INT) *--Optional*
        - **size**: Page size. (INT) *--Optional*

        Returns:
        Get all users with following information:
        - **id**: Id of user. (INT)
        - **first_name**: First name of user. (STR)
        - **last_name**: Last name of user. (STR)
        - **contact**: Contact number of user. (STR)
        - **username**: Username of user. (STR)
        - **email**: Email address of user. (STR)
        - **company_name**: Company name of user. (STR)
        - **address**: Address of user. (STR)
        - **city**: City of user. (STR)
        - **country**: Country of user. (STR)
        - **postal_code**: Postal code of user. (STR)
        - **profile_image**: Profile image of user. (STR)
        - **is_active**: Status of user. (BOOL)
        - **role_id**: Role id of user. (INT)
        - **created_at**: Datetime of user creation. (DATETIME)
        - **updated_at**: Datetime of user updation. (DATETIME)

    """
    print("Calling get_all_users method")

    try:
        query = UserTable.select()
        result = await database.fetch_all(query=query)

        return paginate(result)

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Update a single user route
@ router.put('/{user_id}/', status_code=status.HTTP_200_OK,
             summary="Update a single user by providing id",
             response_model=UserUpdateSchema,
             response_description="User updated successfully")
async def update_user(user_id: int, record: UserUpdateSchema,
                      current_user: UserReadSchema = Security(get_current_active_user,
                                                              scopes=[Role.REPORTING_USER['name']])
                      ) -> dict:
    """
        Update a single user.

        Description:
        - This method is used to update a single user by providing id.
        - If any field is not provided, it will be updated with null value.

        Parameters:
        - **user_id**: Id of user to be updated. (INT) *--Required*

        Update a single user with following information:
        - **first_name**: First name of user. (STR) *--Required*
        - **last_name**: Last name of user. (STR) *--Required*
        - **contact**: Contact number of user. (STR) *--Optional*
        - **username**: Username of user. (STR) *--Optional*
        - **company_name**: Company name of user. (STR) *--Optional*
        - **address**: Address of user. (STR) *--Optional*
        - **city**: City of user. (STR) *--Optional*
        - **country**: Country of user. (STR) *--Optional*
        - **postal_code**: Postal code of user. (STR) *--Optional*
        - **profile_image**: Profile image of user. (STR) *--Optional*

        Returns:
        - **JSON**: Updated user details.

    """
    print("Calling update_user method")

    try:
        # Check if user exists
        user_result = await get_user(user_id)

        if user_result.status_code == 404:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        if record.username:
            record.username = record.username

            # Check if username already exists
            username_query = UserTable.select().where(UserTable.c.username == record.username)
            username_result = await database.fetch_one(query=username_query)

            if username_result:
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                    content={"detail": "Username already exists"})

        query = UserTable.update().where(UserTable.c.id == user_id). \
            values({**record.dict(), "is_active": True})
        await database.execute(query=query)

        return record

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Partially update a single user route
@ router.patch('/{user_id}/', status_code=status.HTTP_200_OK,
               summary="Partially update a single user by providing id",
               response_model=UserPatchSchema,
               response_model_exclude_none=True,
               response_description="User partially updated successfully")
async def patch_user(user_id: int, record: UserPatchSchema,
                     current_user: UserReadSchema = Security(get_current_active_user,
                                                             scopes=[Role.REPORTING_USER['name']])
                     ) -> dict:
    """
        Partially update a single user.

        Description:
        - This method is used to partially update a single user by providing id.
        - If any field is not provided, it will not be updated.

        Parameters:
        - **user_id**: Id of user to be updated. (INT) *--Required*

        Partially update a single user with following information:
        - **first_name**: First name of user. (STR) *--Optional*
        - **last_name**: Last name of user. (STR) *--Optional*
        - **contact**: Contact number of user. (STR) *--Optional*
        - **username**: Username of user. (STR) *--Optional*
        - **company_name**: Company name of user. (STR) *--Optional*
        - **address**: Address of user. (STR) *--Optional*
        - **city**: City of user. (STR) *--Optional*
        - **country**: Country of user. (STR) *--Optional*
        - **postal_code**: Postal code of user. (STR) *--Optional*
        - **profile_image**: Profile image of user. (STR) *--Optional*

        Returns:
        - **JSON**: Partially updated user details.

    """
    print("Calling patch_user method")

    try:
        # Check if user exists
        result = await get_user(user_id)

        if result.status_code == 404:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        if record.username:
            record.username = record.username

            # Check if username already exists
            username_query = UserTable.select().where(UserTable.c.username == record.username)
            username_result = await database.fetch_one(query=username_query)

            if username_result:
                return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                    content={"detail": "Username already exists"})

        record = UserReadSchema(**result).copy(update=record.dict(exclude_unset=True))

        query = UserTable.update().where(UserTable.c.id == user_id). \
            values({**record.dict(), "is_active": True})
        await database.execute(query=query)

        return record

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Delete a single user route
@ router.delete('/{user_id}/', status_code=status.HTTP_200_OK,
                summary="Delete a single user by providing id",
                response_description="User deleted successfully")
async def delete_user(user_id: int,
                      current_user: UserReadSchema = Security(get_current_active_user,
                                                              scopes=[Role.REPORTING_USER['name']])
                      ) -> dict:
    """
        Delete a single user.

        Description:
        - This method is used to delete a single user by providing id.

        Parameters:
        - **user_id**: Id of user to be deleted. (INT) *--Required*

        Returns:
        - **JSON**: Deleted user details.

    """
    print("Calling delete_user method")

    try:
        query = UserTable.delete().where(UserTable.c.id == user_id).returning(UserTable)
        result = await database.execute(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Change password route
@router.post('/change_password/{user_id}/', status_code=status.HTTP_200_OK,
             summary="Change password of a single user by providing id",
             response_description="Password changed successfully")
async def change_password(user_id: int, record: ChangePasswordSchema,
                          current_user: UserReadSchema = Security(get_current_active_user,
                                                                  scopes=[Role.REPORTING_USER[
                                                                      'name']])) -> dict:
    """
        Change password of a single user.

        Description:
        - This method is used to change password of a single user by providing id.

        Parameters:
        - **user_id**: Id of user to be updated. (INT) *--Required*
        - **old_password**: Old password of user. (STR) *--Required*
        - **new_password**: New password of user. (STR) *--Required*

        Returns:
        - **JSON**: Password changed message.

    """
    print("Calling change_password method")

    try:
        query = UserTable.select().where(UserTable.c.id == user_id)
        result = await database.fetch_one(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        if result:
            if not pbkdf2_sha256.verify(record.old_password, result['password']):
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Incorrect password")

            query = UserTable.update().where(UserTable.c.id == user_id). \
                values(password=pbkdf2_sha256.hash(record.new_password))
            await database.execute(query=query)

            return {"detail": "Password changed successfully"}

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Request Reset password route
@router.post('/request/reset_password/', status_code=status.HTTP_200_OK,
             summary="Reset password of a single user by providing email",
             response_description="Email sent successfully")
async def request_reset_password(record: RequestResetPasswordSchema) -> dict:
    """
        Send email to reset password of a single user.

        Description:
        - This method is used to send email to reset password of a single user by providing email.

        Parameters:
        - **email**: Email of user. (STR) *--Required*

        Returns:
        - **JSON**: Email sent message.

    """
    print("Calling request_reset_password method")

    try:
        # Check if email already exists
        email_query = UserTable.select().where(UserTable.c.email == record.email)
        email_result = await database.fetch_one(query=email_query)

        if not email_result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "User not found"})

        # Generate OTP Code
        otp_code = await generate_otp_code()
        otp_expiry_time = datetime.now() + timedelta(minutes=OTP_CODE_EXPIRY_MINUTES)

        # Encode the OTP Code
        encoded_jwt = jwt.encode({
            "email": record.email,
            "token": str(otp_code),
            "expiry": otp_expiry_time.strftime("%Y-%m-%d %H:%M:%S")
        }, SECRET_KEY, algorithm=ALGORITHM)

        email_payload = {
            "email": [record.email],
            "body": {
                "url": f"{FRONTEND_URL}/reset_password/{encoded_jwt}",
                "first_name": "Test User",
                "msg_purpose": "Confirm Email",
                "company_name": COMPANY_NAME,
                "base_url": FRONTEND_URL
            }
        }

        # Send email
        email_otp_response = await send_email(email_payload)

        if email_otp_response.status_code == 200:
            query = UserTable.update().where(UserTable.c.email == record.email). \
                values(password_otp=otp_code, password_verified=False).returning(UserTable)
            await database.execute(query=query)

            return email_otp_response.json()

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Reset password route
@router.post('/reset_password/', status_code=status.HTTP_200_OK,
             summary="Reset password of a single user by providing email and OTP Code",
             response_description="Password reset successfully")
async def reset_password(record: ResetPasswordSchema) -> dict:
    """
        Reset password of a single user.

        Description:
        - This method is used to reset password of a single user by providing OTP Code.

        Parameters:
        - **token**: OTP of user. (STR) *--Required*
        - **password**: Password of user. (STR) *--Required*

        Returns:
        - **JSON**: OTP verified message.

    """
    print("Calling reset_password method")

    try:
        token_data = jwt.decode(record.token, SECRET_KEY, algorithms=[ALGORITHM])

        if token_data["expiry"] < datetime.now().strftime("%Y-%m-%d %H:%M:%S"):
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "Token expired"})

        # Check if email exists
        email_query = UserTable.select().where(UserTable.c.email == token_data["email"])
        email_result = await database.fetch_one(query=email_query)

        if not email_result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Email does not exist"})

        # Check if password is already verified
        if email_result.password_verified:
            return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                                content={"detail": "Password already verified"})

        # Check if OTP Code is correct
        if email_result.password_otp != token_data["token"]:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content={"detail": "OTP Code is incorrect"})

        # Update password
        query = UserTable.update().where(UserTable.c.email == token_data["email"]).values(
            password=pbkdf2_sha256.hash(record.password), password_otp=None, password_verified=True)
        await database.execute(query=query)

        return JSONResponse(status_code=status.HTTP_200_OK,
                            content={"detail": "Password set successfully"})

    except exceptions.UniqueViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Unique key constraint fails with {err_message}") from err

    except exceptions.ForeignKeyViolationError as err:
        err_message = str(err).split("DETAIL:")[1].strip()

        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Foreign key constraint fails with {err_message}") from err

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err

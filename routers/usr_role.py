"""
    Role APIs Module

    Description:
        This module is responsible for handling the role APIs.
        It is used to create, get, update, delete the role details.

"""

# Importing Python packages
import traceback
from asyncpg import exceptions

# Importing FastAPI packages
from fastapi import (APIRouter, HTTPException, Security, status)
from fastapi.responses import JSONResponse
from fastapi_pagination import (Page, paginate)

# Importing from project files
from core.models.database import (database, RoleTable)
from core.schemas.user_schemas import UserReadSchema
from core.schemas.role_schemas import (RoleCreateSchema, RoleReadSchema, RoleUpdateSchema,
                                       RolePatchSchema)
from core.scopes.set_scope import Role
from internal.token import get_current_active_user

# Router Object to Create Routes
router = APIRouter(
    prefix='/role',
    tags=["Role"]
)


# --------------------------------------------------------------------------------------------------


# Create a single role route
@router.post('/create/', status_code=status.HTTP_201_CREATED,
             summary="Create a single role",
             response_model=RoleReadSchema,
             response_description="Role created successfully")
async def create_role(record: RoleCreateSchema,
                      current_user: UserReadSchema = Security(get_current_active_user,
                                                              scopes=[Role.SUPER_ADMIN['name']])
                      ) -> dict:
    """
        Creates a single role.

        Description:
        - This method is used to create a single role.

        Parameters:
        Role details to be created with following fields:
        - **role_name**: Name of role. (STR) *--Required*
            - **Allowed values:** "super_admin", "admin", "manager", "user", "reporting_user"
        - **role_description**: Description of role. (STR) *--Required*

        Returns:
        - **JSON**: Role details along with id.

    """
    print("Calling create_role method")

    try:
        query = RoleTable.insert().values(**record.dict())
        record_id = await database.execute(query=query)

        return {**record.dict(), "id": record_id}

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


# Get a single role route
@router.get('/{role_id}/', status_code=status.HTTP_200_OK,
            summary="Get a single role by providing id",
            response_model=RoleReadSchema,
            response_description="Role details fetched successfully")
async def get_role(role_id: int,
                   current_user: UserReadSchema = Security(get_current_active_user,
                                                           scopes=[Role.SUPER_ADMIN['name']])
                   ) -> dict:
    """
        Get a single role.

        Description:
        - This method is used to get a single role by providing id.

        Parameters:
        - **role_id**: ID of role to be fetched. (INT) *--Required*

        Returns:
        Get a single role with following information:
        - **id**: Id of role. (INT)
        - **role_name**: Name of role. (STR)
        - **role_description**: Description of role. (STR)
        - **created_at**: Datetime of role creation. (DATETIME)
        - **updated_at**: Datetime of role updation. (DATETIME)

    """
    print("Calling get_role method")

    try:
        query = RoleTable.select().where(RoleTable.c.id == role_id)
        result = await database.fetch_one(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Role not found"})

        return result

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Get all roles route
@router.get('/', status_code=status.HTTP_200_OK,
            summary="Get all roles",
            response_model=Page[RoleReadSchema],
            response_description="Roles details fetched successfully")
async def get_all_roles(current_user: UserReadSchema = Security(get_current_active_user,
                                                                scopes=[Role.SUPER_ADMIN['name']])
                        ) -> dict:
    """
        Get all roles.

        Description:
        - This method is used to get all roles.

        Parameters:
        - **page**: Page number. (INT) *--Optional*
        - **size**: Page size. (INT) *--Optional*

        Returns:
        Get all roles with following information:
        - **id**: Id of role. (INT)
        - **role_name**: Name of role. (STR)
        - **role_description**: Description of role. (STR)
        - **created_at**: Datetime of role creation. (DATETIME)
        - **updated_at**: Datetime of role updation. (DATETIME)

    """
    print("Calling get_all_roles method")

    try:
        query = RoleTable.select()
        result = await database.fetch_all(query=query)

        return paginate(result)

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err


# Update a single role route
@router.put('/{role_id}/', status_code=status.HTTP_202_ACCEPTED,
            summary="Update a single role by providing id",
            response_model=RoleUpdateSchema,
            response_description="Role updated successfully")
async def update_role(role_id: int, record: RoleUpdateSchema,
                      current_user: UserReadSchema = Security(get_current_active_user,
                                                              scopes=[Role.SUPER_ADMIN['name']])
                      ) -> dict:
    """
        Update a single role.

        Description:
        - This method is used to update a single role by providing id.
        - If any field is not provided, it will be updated with null value.

        Parameters:
        - **role_id**: ID of role to be updated. (INT) *--Required*
        - **role_name**: Name of role. (STR) *--Required*
            - **Allowed values:** "super_admin", "admin", "manager", "user", "reporting_user"
        - **role_description**: Description of role. (STR) *--Required*

        Returns:
        - **JSON**: Role details.

    """
    print("Calling update_role method")

    try:
        query = RoleTable.update().where(RoleTable.c.id == role_id).values(**record.dict()). \
            returning(RoleTable)
        result = await database.execute(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Role not found"})

        return record.dict()

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


# Partially update a single role route
@router.patch('/{role_id}/', status_code=status.HTTP_202_ACCEPTED,
              summary="Partially update a single role by providing id",
              response_model=RolePatchSchema,
              response_model_exclude_none=True,
              response_description="Role partially updated successfully")
async def patch_role(role_id: int, record: RolePatchSchema,
                     current_user: UserReadSchema = Security(get_current_active_user,
                                                             scopes=[Role.SUPER_ADMIN['name']])
                     ) -> dict:
    """
        Partially update a single role.

        Description:
        - This method is used to partially update a single role by providing id.
        - If any field is not provided, it will be updated with the previous value.

        Parameters:
        - **role_id**: ID of role to be updated. (INT) *--Required*
        - **role_name**: Name of role. (STR) *--Optional*
            - **Allowed values:** "super_admin", "admin", "manager", "user", "reporting_user"
        - **role_description**: Description of role. (STR) *--Optional*

        Returns:
        - **JSON**: Role details.

    """
    print("Calling patch_role method")

    try:
        # Check if role exists
        result = await get_role(role_id)

        if result.status_code == 404:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Role not found"})

        record = RoleReadSchema(**result).copy(update=record.dict(exclude_unset=True))

        query = RoleTable.update().where(RoleTable.c.id == role_id).values(**record.dict())
        await database.execute(query=query)

        return record.dict()

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


# Delete a single role route
@router.delete('/{role_id}/', status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete a single role by providing id",
               response_description="Role deleted successfully")
async def delete_role(role_id: int,
                      current_user: UserReadSchema = Security(get_current_active_user,
                                                              scopes=[Role.SUPER_ADMIN['name']])
                      ) -> None:
    """
        Delete a single role.

        Description:
        - This method is used to delete a single role by providing id.

        Parameters:
        - **role_id**: Id of role to be deleted. (INT) *--Required*

        Returns:
        - **None**

    """
    print("Calling delete_role method")

    try:
        query = RoleTable.delete().where(RoleTable.c.id == role_id).returning(RoleTable)
        result = await database.execute(query=query)

        if not result:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                                content={"detail": "Role not found"})

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong") from err

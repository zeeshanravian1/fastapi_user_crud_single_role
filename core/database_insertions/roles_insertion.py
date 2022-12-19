"""
    Insert roles in the database

    Description:
        This module is responsible for inserting roles in the database.

"""

# Importing Python packages
from environs import Env
from databases import Database
from sqlalchemy import (create_engine, Column, DateTime, Enum, Integer, MetaData, String, Table,
                        sql)

# Importing FastAPI packages

# Importing from project files


# --------------------------------------------------------------------------------------------------


# Env Object to read from env file
env = Env()
env.read_env()


# Database connection
DATABASE = env("DATABASE")
DB_USERNAME = env("DB_USERNAME")
DB_PASSWORD = env("DB_PASSWORD")
DB_HOST = env("DB_HOST")
DB_PORT = env("DB_PORT")
DB_NAME = env("DB_NAME")

# Database connection
SQLALCHEMY_DATABASE_URL = f"{DATABASE}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
metadata = MetaData(schema="usr_crud_db")
database = Database(SQLALCHEMY_DATABASE_URL)


# Role table
RoleTable = Table(
    "usr_role",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, unique=True),
    Column("role_name", Enum('super_admin', 'admin', 'manager', 'user', 'reporting_user',
                             name="usr_role_type"), unique=True, nullable=False),
    Column("role_description", String(1_00), nullable=False),
    Column("created_at", DateTime, server_default=sql.func.now()),
    Column("updated_at", DateTime, server_default=sql.func.now(), onupdate=sql.func.now())
)


# Insert Roles in the database
async def insert_roles() -> None:
    """Insert roles in the database"""

    # Connecting to the database
    await database.connect()

    # Making roles list
    roles = [{"role_name": "super_admin", "role_description": "Super Admin Description"},
             {"role_name": "admin", "role_description": "Admin Description"},
             {"role_name": "manager", "role_description": "Manager Description"},
             {"role_name": "user", "role_description": "User Description"},
             {"role_name": "reporting_user", "role_description": "Reporting User Description"}]

    # Inserting roles in the database
    query = RoleTable.insert().values(roles)
    await database.execute(query)

    # Disconnecting from the database
    await database.disconnect()


# Calling the function
if __name__ == "__main__":
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(insert_roles())

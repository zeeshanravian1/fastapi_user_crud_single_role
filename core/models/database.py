"""
    Database Models

    Description:
        Models are used to create the database and map the database to the models.

"""

# Importing Python packages
from databases import Database
from sqlalchemy import (create_engine, Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        MetaData, String, Table, sql)

# Importing FastAPI packages

# Importing from project files
from dependencies import (DATABASE, DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)


# --------------------------------------------------------------------------------------------------


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


# User table
UserTable = Table(
    "usr_user",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True, unique=True),
    Column("first_name", String(3_0), nullable=True, default=None),
    Column("last_name", String(3_0), nullable=True, default=None),
    Column("contact", String(3_0), nullable=True, default=None),
    Column("username", String(3_0), unique=True, nullable=False),
    Column("email", String(1_00), unique=True, nullable=False),
    Column("password", String(1_00), nullable=True, default=None),
    Column("company_name", String(3_0), nullable=True, default=None),
    Column("address", String(1_00), nullable=True, default=None),
    Column("city", String(3_0), nullable=True, default=None),
    Column("country", String(3_0), nullable=True, default=None),
    Column("postal_code", String(6), nullable=True, default=None),
    Column("profile_image", String(1_00), nullable=True, default=None),
    Column("email_otp", String(6), nullable=True, default=None),
    Column("email_verified", Boolean, nullable=False),
    Column("password_otp", String(6), nullable=True, default=None),
    Column("password_verified", Boolean, nullable=False),
    Column("is_active", Boolean, nullable=False),
    Column("role_id", Integer, ForeignKey("usr_role.id"), nullable=False),
    Column("created_at", DateTime, server_default=sql.func.now()),
    Column("updated_at", DateTime, server_default=sql.func.now(), onupdate=sql.func.now())
)

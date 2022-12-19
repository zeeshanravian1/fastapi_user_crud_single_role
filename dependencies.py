"""
    User Parameters Module

    Description:
        This module is responsible for defining constants and read values from environment file.
"""

# Importing Python packages
from environs import Env


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


# Cors configuration
CORS_ALLOW_ORIGINS = env("CORS_ALLOW_ORIGINS")
CORS_ALLOW_METHODS = env("CORS_ALLOW_METHODS")
CORS_ALLOW_HEADERS = env("CORS_ALLOW_HEADERS")


# JWT Constants
ALGORITHM = env("ALGORITHM")
SECRET_KEY = env("SECRET_KEY")


# Access Token Expire Time
ACCESS_TOKEN_EXPIRE_MINUTES = 1440


# Email Configuration
EMAIL_HOST=env("EMAIL_HOST")
EMAIL_PORT=env("EMAIL_PORT")
EMAIL_USERNAME=env("EMAIL_USERNAME")
EMAIL_PASSWORD=env("EMAIL_PASSWORD")
EMAIL_FROM=env("EMAIL_FROM")
EMAIL_FROM_NAME=env("EMAIL_FROM_NAME")


# OTP Code Expiry Time
OTP_CODE_EXPIRY_MINUTES = 5


# Company Details
COMPANY_NAME = env("COMPANY_NAME")


# Frontend
FRONTEND_URL = env("FRONTEND_URL")

"""
    Main file for the project

    Description:
        This program is the main file for the project.
        It is the entry point for the program.
        It is the file that is run when the program is started.

"""

# Importing Python packages
import logging

# Importing FastAPI packages
from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html)
from fastapi_pagination import add_pagination


# Importing from project files
from core.models.database import database
from dependencies import (CORS_ALLOW_ORIGINS, CORS_ALLOW_METHODS, CORS_ALLOW_HEADERS)
from routers import usr_route


# Router Object to Create Routes
app = FastAPI(
    docs_url=None, redoc_url=None,
    title="User CRUD Project",
    description="User CRUD Project Documentation",
    version="0.1a",
)


# --------------------------------------------------------------------------------------------------


logger = logging.getLogger('main-logger')

app.mount("/static", StaticFiles(directory="static"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGINS],
    allow_credentials=True,
    allow_methods=[CORS_ALLOW_METHODS],
    allow_headers=[CORS_ALLOW_HEADERS],
)


@app.on_event("startup")
async def startup():
    """
        Startup event

        Description:
            This function is called when the program starts.
            It is used to connect to the database.

        Parameters:
            None

        Returns:
            None

    """

    await database.connect()
    logger.info("Server Startup")


@app.on_event("shutdown")
async def shutdown():
    """
        Shutdown event

            Description:
                This function is called when the program is closed.
                It is used to disconnect from the database.

            Parameters:
                None

            Returns:
                None

    """

    await database.disconnect()
    logger.info("Server Shutdown")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
        Custom Swagger UI HTML

        Description:
            This function is used to create a custom swagger UI HTML page.

        Parameters:
            None

        Returns:
            None

    """

    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " ",
        swagger_favicon_url='',
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc_ui_html():
    """
        Custom Redoc UI HTML

        Description:
            This function is used to create a custom redoc UI HTML page.

        Parameters:
            None

        Returns:
            None

    """

    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js"
    )


# Add all file routes to app
app.include_router(usr_route.router)


# Pagination
add_pagination(app)

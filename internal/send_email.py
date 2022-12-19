"""
    Extra Functions

    Description:
        This module contains extra functions that are used in the application ecosystem at multiple
    places.

"""

# Importing Python packages
import traceback

# Importing FastAPI packages
from fastapi import (HTTPException, status)
from fastapi.responses import JSONResponse
from fastapi_mail import (ConnectionConfig, FastMail,
                          MessageSchema, MessageType)

# Importing from project files
from core.schemas.email_schemas import EmailSchema
from dependencies import (COMPANY_NAME, EMAIL_FROM, EMAIL_FROM_NAME, EMAIL_HOST, EMAIL_PASSWORD,
                          EMAIL_PORT, EMAIL_USERNAME)

# --------------------------------------------------------------------------------------------------


# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD,
    MAIL_FROM=EMAIL_FROM,
    MAIL_PORT=EMAIL_PORT,
    MAIL_SERVER=EMAIL_HOST,
    MAIL_FROM_NAME=EMAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER="static/email",
)


# Sending OTP Code
async def send_email(email: EmailSchema) -> dict:
    """
        Sends an OTP code to the user's email.

        Description:
        - This method is used to send an OTP code to the user's email.

        Parameters:
        - **email**: Email of the user. (STR) *--Required*

        Returns:
        - **JSON**: Email sent status.

    """
    print("Calling send_otp_code method")

    try:
        message = MessageSchema(
            subject=f"Welcome to {COMPANY_NAME}",
            recipients=email["email"],
            template_body=email["body"],
            subtype=MessageType.html
        )

        fastapi_mail = FastMail(conf)
        await fastapi_mail.send_message(message, template_name="email.html")

        return JSONResponse(status_code=200,
                            content={"detail": "Email sent at given email address"})

    except Exception as err:
        err_message = f"{traceback.format_exc()}\n\n{str(err)}"
        print("err_message --> ", err_message)

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Something went wrong while sending email") from err

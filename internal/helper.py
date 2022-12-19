"""
    Extra Functions

    Description:
        This module contains extra functions that are used in the application ecosystem at multiple
    places.

"""

# Importing Python packages
import random

# Importing FastAPI packages

# Importing from project files

# --------------------------------------------------------------------------------------------------


# OTP Code Generator
async def generate_otp_code() -> str:
    """
        Generates a 6 digit OTP code.

        Description:
        - This method is used to generate a 6 digit OTP for a single user.

        Parameters:
        - **None**

        Returns:
        - **STR**: 6 digit OTP code.

    """
    print("Calling generate_otp_code method")

    return str(random.randint(100000, 999999))

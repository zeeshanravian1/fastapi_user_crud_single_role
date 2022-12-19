"""
    This module is used to set the scope of the user.

    Description:
        This module is used to set the scope of the user. The scope is used to determine the
        permissions of the user.

"""

# Importing Python packages
from dataclasses import dataclass


# --------------------------------------------------------------------------------------------------


@dataclass
class Role:
    """
    Constants for the various roles scoped in the application ecosystem
    """

    REPORTING_USER = {
        "name": "REPORTING_USER",
        "description": "Can only view reporting page for each listing."
                       "Can only view listings assigned to them by Admin Users and Manger Users."
                       "This user class will ultimately become while labeled reporting.",
    }

    USER = {
        "name": "USER",
        "description": "Can add new listings to system."
                       "Can setup new campaigns but not start."
                       "Can edit campaigns but edits will need to approved by Admin Users."
                       "New campaigns will need to be approved and started by Admin Users."
                       "Can view accounts they created and those assigned to them by Admin User"
                       "and Manager Users.",
    }

    MANAGER = {
        "name": "MANAGER",
        "description": "Have all the functionality of Users."
                       "Can approve campaigns and start campaigns."
                       "Can add new users."
                       "Assign campaigns that are assigned to them by managers to users",
    }

    ADMIN = {
        "name": "ADMIN",
        "description": "Have all privileges of lower accounts."
                       "Have the ability to create admin and user accounts."
                       "Have access to aggregated performance reporting."
                       "Can bulk upload new listings.",
    }

    SUPER_ADMIN = {
        "name": "SUPER_ADMIN",
        "description": "Super Administrator of Application Ecosystem."
                       "Have all privileges."
                       "Can add Manager Users."
                       "Can add new clients to the system – all user accounts need to be assigned"
                       "to a Brand Signals client.",
    }

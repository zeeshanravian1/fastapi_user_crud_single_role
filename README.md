# FastAPI_User_CRUD_Single_Role



## Name
FastAPI User CRUD with a single role for each user.

## Description
This project is built in [FastAPI](https://fastapi.tiangolo.com/) (The most popular framework of python) using python 3.11.0.
You can also use [Alembic](https://alembic.sqlalchemy.org/en/latest/) for database migrations for this project.

This project contains all the routes relating to users such as:
- Register a single user with email verification.
- Super Admin can assign a single role to the user.
- Get a single user.
- Get all users with pagination.
- Update a single user.
- Partially update a single user.
- Delete a single user.
- Change user password.
- Reset the user password.

## Badges
On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals
Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation
- Python Installation:
To install project dependencies you must have python 3.11.0 installed on your system.
If python 3.11.0 is not installed you can download it from the [python website](https://www.python.org/downloads/) or you can configure your system to handle multiple python versions using [pyenv](https://realpython.com/intro-to-pyenv/).

Verify your python installation by typing this command in your terminal:
```
python --version
```

- Pipenv installation:
After that, you need to install pipenv to handle the virtual environments, you can install it by typing this command in your terminal:
```
pip install pipenv or
pip3 install pipenv
```

Verify your pipenv installation by typing this command in your terminal:
```
pipenv
```

- Creating a Virtual Environment
Go to the project directory and type the following command in the terminal.
```
pipenv sync
```

This will create a virtual environment for your project along with dependencies.

- Activate Virtual Environment
To active virtual environment type the following command in the terminal.
```
pipenv shell
```

You can verify your environment dependencies by running:
```
pip list
```

## Configure [Alembic](https://alembic.sqlalchemy.org/en/latest/) for Database Migrations.
First, create your schema in the database. It is mandatory otherwise alembic will give you an error.

- Type the following command to initialize migrations
```
alembic init migrations
```

- Edit env.py in the migrations folder to set the path for your database:
```
from core.models.database import (metadata, SQLALCHEMY_DATABASE_URL)
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
target_metadata = metadata
```

- Your first migrations
```
alembic revision --autogenerate -m "<Migration Name>"
```

- Apply Migrations
```
alembic upgrade heads
```

## Usage
- Pre Defined Roles:
Run roles_insertion.py from core/database_insertions to insert pre-defined roles

- Run FastAPI Server:
To run the FastAPI server run this command
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

- Access Swagger UI:
http://0.0.0.0:8000/docs

- Access Redoc UI:
http://0.0.0.0:8000/redoc

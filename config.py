#!/usr/bin/python3
import os

# Statement for enabling the development environment 5000
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database
HOST = "192.168.0.10"
USER = "ponduser"
PASSD = "e8262ad87bde192dc6840b3caf1957b42282f6f8d20589e5e21949bb73ac5725"
DB = "xiap"
SQLALCHEMY_DATABASE_URI = "postgresql://{user}:{password}@{host}/{db}".format(
    user=USER, password=PASSD, host=HOST, db=DB
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
DATABASE_CONNECT_OPTIONS = {}

# Application threads.
# A common general assumption is using 2 per available processor cores
# to handle incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for signing the data.
CSRF_SESSION_KEY = "secret"

# Secret key for signing cookies
SECRET_KEY = "secret"

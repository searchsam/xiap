#!/usr/bin/python3
# Import flask
import click
from flask import Flask

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)

# Configurations
app.config.from_object("config")

# Define the database object which is imported by modules and controllers
db = SQLAlchemy(app)

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return "404", 404


# Import a module / component using its blueprint handler variable (pool)
from app.pond.controllers import pond as pond_module
from app.pond.oauth2 import config_oauth


config_oauth(app)
# Register blueprint(s)
app.register_blueprint(pond_module)


# Build the database:
# This will create the database file using SQLAlchemy
@app.cli.command()
def initdb():
    db.create_all()

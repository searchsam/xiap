# Import flask dependencies
from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for

# Import password / encryption helper tools
from werkzeug import check_password_hash, generate_password_hash

# Import the database object from the main app module
from app import db

# Import module models (i.e. User)
from app.pool.models import User

# Define the blueprint: 'auth', set its url prefix: app.url/auth
pool = Blueprint('auth', __name__, url_prefix='/auth')

# Set the route and accepted methods
@pool.route('/signin/', methods=['GET', 'POST'])
def signin():
    return 'Hola Mundo!'

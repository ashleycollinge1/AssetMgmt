from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash
from app import db

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_frontend = Blueprint('frontend', __name__, url_prefix='/frontend')

# Set the route and accepted methods
@mod_frontend.route('/', methods=['GET'])
def default():
    return "Hello"

@mod_frontend.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Returns the dashboard view
    """
    return render_template("mod_frontend/dashboard.html")

@mod_frontend.route('/assets', methods=['GET'])
def assets():
    """
    Returns the view for assets
    """
    return "assets testing"
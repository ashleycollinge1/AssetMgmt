from flask import Blueprint, render_template

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_frontend = Blueprint('frontend', __name__, url_prefix='/frontend')


# Set the route and accepted methods
@mod_frontend.route('/dashboard', methods=['GET'])
@mod_frontend.route('/', methods=['GET'])
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
    return render_template("mod_frontend/assets.html")

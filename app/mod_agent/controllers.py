# Import flask dependencies
from flask import Blueprint

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_agent = Blueprint('agent', __name__, url_prefix='/agent')


# Set the route and accepted methods
@mod_agent.route('/register', methods=['POST'])
def signin():
    return "Hello"


@mod_agent.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    Heartbeat from asset agent
    """
    return "Thanks"


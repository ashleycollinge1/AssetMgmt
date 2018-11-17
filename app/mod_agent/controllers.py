# Import flask dependencies
from flask import Blueprint, request, jsonify, url_for

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_agent = Blueprint('agent', __name__, url_prefix='/agent')


@mod_agent.route('/configuration', methods=['GET'])
def get_configuration():
    """
    allows agent to get the latest configuration that they
    need to adhere too
    """
    return jsonify({"configuration": {"heartbeat_interval": 2,
                                      "heartbeat_uri": "http://127.0.0.1:5000/agent/heartbeat"}})


# Set the route and accepted methods
@mod_agent.route('/register', methods=['POST'])
def signin():
    """
    Takes in serial number of the machine and it's ip address,
    and name
    creates a new asset record from that infomration and creates
    an agent record tied to that asset.
    returns an id, api token, uri to pull down agent config
    """
    if request.method == 'POST':
        if request.get_json():
            json_data = request.get_json()
            if 'serialnumber' in json_data.keys() and 'ipaddress' in json_data.keys():
                # create new asset here, create new agent here and attach agent to asset
                # also return the id and the uri to pick up the config
                return jsonify({"asset_id": "nf3f28hf892", "config_uri": "{}".format(url_for('.get_configuration'))})
    return "Hello"


@mod_agent.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    recieves id, api token an 'ok' message
    logs heartbeat to db and return 'ok' message
    """
    if request.get_json():
        json_data = request.get_json()
        if 'asset_id' in json_data.keys():
            return jsonify({"message": "Heartbeat recieved from: {}".format(json_data['asset_id'])})


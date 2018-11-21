# Import flask dependencies
from flask import Blueprint, request, jsonify, url_for
from app import db
from sqlalchemy.exc import IntegrityError
import datetime

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_agent = Blueprint('agent', __name__, url_prefix='/agent')

from app.mod_api.models import Asset, AssetPC, WindowsAgent


@mod_agent.route('/configuration', methods=['GET'])
def get_configuration():
    """
    allows agent to get the latest configuration that they
    need to adhere too
    """
    return jsonify({"configuration": {"heartbeat_interval": 15,
                                      "heartbeat_uri": "https://assetmgmt.ashleycollinge.co.uk/agent/heartbeat",
                                      "information_reload": 300}})


@mod_agent.route('/push/client_data', methods=['POST'])
def push_client_data():
    """
    Recieve a json dict with all of the information for the assetpc
    """
    if request.method == 'POST':
        if request.get_json():
            json_data = request.get_json()
            if 'data' in json_data.keys():
                pass


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
            if 'serialnumber' in json_data.keys():
                # create new asset here, create new agent here and attach agent to asset
                # also return the id and the uri to pick up the config
                results = db.session.query(Asset).filter_by(serialnumber=json_data['serialnumber']).first()
                if results:
                    return jsonify({"asset_id": results.id, "config_uri": "{}".format(url_for('.get_configuration'))})
                new_asset = Asset(serialnumber=json_data['serialnumber'],
                                  asset_type="windowspc",
                                  status="Live")
                new_assetpc = AssetPC(hostname=json_data['hostname'],
                                      domain=json_data['domain'],
                                      operating_system=json_data['operating_system'],
                                      service_pack_version = json_data['servicepackversion'])
                new_windows_agent = WindowsAgent(agent_version=1)
                new_assetpc.windows_agent.append(new_windows_agent)
                new_asset.assetpcrecord.append(new_assetpc)
                try:
                    db.session.add(new_asset)
                    db.session.commit()
                except IntegrityError:
                    db.session.rollback()
                    return "500"
                return jsonify({"asset_id": new_asset.id, "config_uri": "{}".format(url_for('.get_configuration'))})
    return "Hello"


@mod_agent.route('/heartbeat', methods=['POST'])
def heartbeat():
    """
    recieves id, api token an 'ok' message
    updates last_seen variable in assetpc
    logs heartbeat to db and return 'ok' message
    """
    if request.get_json():
        json_data = request.get_json()
        if 'asset_id' in json_data.keys():
            asset = db.session.query(Asset).filter_by(id = json_data['asset_id']).first()
            print(asset.id)
            asset.assetpcrecord[0].last_seen = db.func.current_timestamp()
            db.session.add(asset)
            db.session.commit()
            return jsonify({"message": "Heartbeat recieved from: {}".format(json_data['asset_id'])})

@mod_agent.route('/information_upload', methods=['POST'])
def information_upload():
    if request.get_json():
        json_data = request.get_json()
        if 'asset_id' in json_data.keys():
            # need to add asset_id to initial dict
            asset = db.session.query(Asset).filter_by(id = json_data['asset_id']).first()
            print(asset.id)
            print(json_data)
            asset.assetpcrecord[0].hostname = json_data['generic']['hostname']
            asset.assetpcrecord[0].service_pack_version = json_data['generic']['servicepackversion']
            asset.assetpcrecord[0].manufacturer = json_data['generic']['manufacturer']
            asset.assetpcrecord[0].operating_system = json_data['generic']['operatingsystem']
            asset.assetpcrecord[0].model = json_data['generic']['model']
            asset.assetpcrecord[0].cpu_model = json_data['generic']['cpu_model']
            asset.assetpcrecord[0].logicalcorecount = str(json_data['generic']['logicalcorecount'])
            asset.assetpcrecord[0].physicalcorecount = json_data['generic']['physicalcorecount']
            asset.assetpcrecord[0].maxclockspeed = json_data['generic']['maxclockspeed']
            asset.assetpcrecord[0].memcapingb = json_data['generic']['memcapingb']
            db.session.add(asset)
            db.session.commit()
            return jsonify({"thanks": "success"})

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from app import db
from app.mod_api.models import Asset

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_api = Blueprint('api', __name__, url_prefix='/api')


# Set the route and accepted methods
@mod_api.route('/assets', methods=['GET', 'POST'])
def get_assets():
    """
    Gets assets and returns them in JSON format.
    POST Can post data to this endpoint and will add it
    into SQL. Must include a serial number to use as
    unique id within the app.
    Filtering, allows searching through the assets based
    on search values: serialnumber, id
    """
    if request.method == 'GET':
        json_results = []
        if request.args.get('serialnumber'):
            results = db.session.query(Asset).filter_by(
                serialnumber=request.args.get('serialnumber')).all()
        elif request.args.get('id'):
            results = db.session.query(Asset).filter_by(
                id=request.args.get('id')).all()
        elif request.args.get('purchaseordernumber'):
            results = db.session.query(Asset).filter_by(
                purchaseordernumber=request.args.get('purchaseordernumber')
                ).all()
        elif request.args.get('asset_type'):
            results = db.session.query(Asset).filter_by(
                asset_type=request.args.get('asset_type')).all()
        elif request.args.get('status'):
            results = db.session.query(Asset).filter_by(
                status=request.args.get('status')).all()
        else:
            results = db.session.query(Asset).all()
        for asset in results:
            new_asset = {}
            new_asset['id'] = asset.id
            new_asset['date_created'] = asset.date_created
            new_asset['date_modified'] = asset.date_modified
            new_asset['status'] = asset.status
            new_asset['serialnumber'] = asset.serialnumber
            new_asset['purchaseordernumber'] = asset.purchaseordernumber
            new_asset['asset_type'] = asset.asset_type
            new_asset['last_seen'] = asset.assetpcrecord[0].last_seen
            json_results.append(new_asset)
        if not json_results:
            return jsonify({"Error": "No results found."})
        return jsonify(json_results)
    if request.method == 'POST':
        if request.get_json():
            json_data = request.get_json()
            new_asset = Asset()
            if json_data['serialnumber']:
                query = db.session.query(Asset).filter_by(
                    serialnumber=json_data['serialnumber']).first()
                if query:
                    return jsonify({"error":
                                    "serialnumber must be unique, already"
                                    "found in db."})
                else:
                    new_asset.serialnumber = json_data['serialnumber']
            else:
                return jsonify({'error': 'missing serialnumber'})
            if 'hostname' in json_data.keys():
                new_asset.hostname = json_data['hostname']
            db.session.add(new_asset)
            try:
                db.session.commit()
                return jsonify({"success": {"id": new_asset.id,
                                            "serialnumber":
                                            new_asset.serialnumber,
                                            "date_created":
                                            new_asset.date_created}})
            except SQLAlchemyError:
                db.session.rollback()
                return jsonify({'error': 'failed for sql reason'})


@mod_api.route('/assets/<asset_Id>/extendedinfo', methods=['GET'])
def get_extended_info(asset_Id):
    """
    gets extended info for asset and return in json format
    """
    json_results = []
    asset = db.session.query(Asset).filter_by(id=asset_Id).first()
    new_asset = {}
    new_asset['id'] = asset.id
    new_asset['serialnumber'] = asset.serialnumber
    new_asset['asset_type'] = asset.asset_type
    extended_info = {}
    extended_info['hostname'] = asset.assetpcrecord[0].hostname
    extended_info['domain'] = asset.assetpcrecord[0].domain
    extended_info['operating_system'] = asset.assetpcrecord[0].operating_system
    extended_info['service_pack_version'] = asset.assetpcrecord[0].service_pack_version
    extended_info['last_bootup_time'] = asset.assetpcrecord[0].last_bootup_time
    extended_info['last_seen'] = asset.assetpcrecord[0].last_seen
    extended_info['manufacturer'] = asset.assetpcrecord[0].manufacturer
    extended_info['model'] = asset.assetpcrecord[0].model
    extended_info['memorygb'] = asset.assetpcrecord[0].memorygb
    extended_info['cpu_maxclockspeed'] = asset.assetpcrecord[0].cpu_maxclockspeed
    extended_info['cpu_logicalcorecount'] = asset.assetpcrecord[0].cpu_logicalcorecount
    extended_info['cpu_physicalcorecount'] = asset.assetpcrecord[0].cpu_physicalcorecount
    extended_info['cpu_model'] = asset.assetpcrecord[0].cpu_model
    extended_info['physical_arch'] = asset.assetpcrecord[0].physical_arch
    new_asset['extended_info'] = extended_info
    json_results.append(new_asset)
    return jsonify(json_results)


@mod_api.route('/assets/<serialnumber>/delete', methods=['GET'])
def delete_asset(serialnumber):
    """
    Takes the var serialnumber from the URL and performs the delete
    operation on the asset, removing it from the DB.
    """
    asset = db.session.query(Asset).filter_by(
            serialnumber=serialnumber).first()
    if asset:
        db.session.delete(asset)
        try:
            db.session.commit()
            return jsonify({"record deleted": {"id": asset.id,
                                               "serialnumber":
                                               asset.serialnumber}})
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({"Error": "something went wrong with sql"})
    else:
        return jsonify({"Error": "record does not exist"})


@mod_api.route('/assets/<asset_id>/decommission', methods=['GET'])
def decommission_asset(asset_id):
    """
    Take AssetID from the url and perform the decommission
    on the asset.
    """
    asset = db.session.query(Asset).filter_by(id=asset_id).first()
    asset.status = "Decommissioned"
    try:
        db.session.commit()
        return jsonify({"asset decommissioned": "success"})
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({"sql error": "success"})

@mod_api.errorhandler(404)
def not_found_error(error):
    return 404

@mod_api.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return 500

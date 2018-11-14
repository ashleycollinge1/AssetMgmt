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

from flask import Blueprint, request, render_template, \
                  flash, g, session, redirect, url_for, jsonify
from werkzeug import check_password_hash, generate_password_hash
from app import db
from app.mod_api.models import Asset

# Define the blueprint: 'auth', set its url prefix: app.url/auth
mod_api = Blueprint('api', __name__, url_prefix='/api')

# Set the route and accepted methods
@mod_api.route('/assets', methods=['GET', 'POST'])
def get_assets():
    """
    Gets assets and returns them in JSON format.
    """
    if request.method == 'GET':
        json_results = []
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
        return jsonify(json_results)
    if request.method == 'POST':
        if request.get_json():
            json_data = request.get_json()
            new_asset = Asset()
            if json_data['serialnumber']:
                if db.session.query(Asset).filter_by(serialnumber = json_data['serialnumber']).first():
                    return jsonify({"error": "serialnumber must be unique, already found in db."})
                else:
                    new_asset.serialnumber = json_data['serialnumber']
            else:
                return jsonify({'error':'missing serialnumber'})
            if 'hostname' in json_data.keys():
                new_asset.hostname = json_data['hostname']
            db.session.add(new_asset)
            try:
                db.session.commit()
                return jsonify({"success": {"id": new_asset.id,
                "serialnumber": new_asset.serialnumber,
                "date_created": new_asset.date_created}})
            except:
                db.session.rollback()
                return jsonify({'error':'failed for sql reason'})

@mod_api.route('/assets/<serialnumber>/delete', methods=['GET'])
def delete_asset(serialnumber):
    """
    Takes the var serialnumber from the URL and performs the delete
    operation on the asset, removing it from the DB.
    """
    asset = db.session.query(Asset).filter_by(serialnumber = serialnumber).first()
    if asset:
        db.session.delete(asset)
        try:
            db.session.commit()
            return jsonify({"record deleted": {"id": asset.id,
                                                "serialnumber": asset.serialnumber}})
        except:
            db.session.rollback()
            return jsonify({"Error": "something went wrong with sql"})
    else:
        return jsonify({"Error": "record does not exist"})
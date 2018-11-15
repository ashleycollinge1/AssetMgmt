from flask import Blueprint, render_template, redirect, request, url_for
from app import db
from app.mod_api.models import Asset

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

@mod_frontend.route('/assets/extended_information', methods=['GET'])
def assets_extendedinfo():
    """
    Return the extendedinfo page using the asset_id
    in the url filter
    """
    if request.method == 'GET':
        json_results = []
        if request.args.get('asset_id'):
            results = db.session.query(Asset).filter_by(
                id=request.args.get('asset_id')).first()
            asset_information = {}
            asset_information['id'] = results.id
            asset_information['date_created'] = results.date_created
            asset_information['date_modified'] = results.date_modified
            return render_template('mod_frontend/assets_extendedinfo.html', asset_information=asset_information)
        return redirect(url_for('.assets'))

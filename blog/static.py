from flask import Blueprint, send_from_directory

static = Blueprint('static_blueprint', __name__, static_folder = '.', static_url_path = '/static')

@static.route('/file/<path:file_path>')
def static_return(file_path):
    return send_from_directory(static.static_folder, file_path)
from flask import Flask, session
from flask_session import Session
from pymongo import MongoClient
from .auth import auth
from .views import views
from .static import static;

def create_app():
    app = Flask(__name__)
    # MongoDB implementation
    app.secret_key = "mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.4"
    client = MongoClient('localhost', 27017)
    db = client['Charoite']
    users_collection = db['users']

    # Register blueprints
    app.register_blueprint(views(db), url_prefix="/")
    app.register_blueprint(auth(db), url_prefix="/")
    app.register_blueprint(static, url_prefix="/")

    #Session implementaion
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_TYPE"] = "filesystem"
    Session(app)

    return app


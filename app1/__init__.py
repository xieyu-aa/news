from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from flask import Flask
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    Session(app)
    CsrfProtect(app)

    from .main import main
    app.register_blueprint(main)
    return app
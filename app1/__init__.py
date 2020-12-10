from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask_script import Manager
from flask_migrate import MigrateCommand, Migrate
from flask import Flask
from config import config_dict

db = SQLAlchemy()


def create_app(name):
    app = Flask(__name__)
    config = config_dict.get(name)
    app.config.from_object(config)
    db.init_app(app)
    Session(app)
    CsrfProtect(app)

    from .main import main
    app.register_blueprint(main)  # 注册蓝图

    from .admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    return app
import logging
from logging.handlers import RotatingFileHandler

from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CsrfProtect
from flask import Flask
from config import config_dict
from redis import StrictRedis

db = SQLAlchemy()
redis_store = None

def create_app(name):
    file_log()
    app = Flask(__name__)
    config = config_dict.get(name)
    app.config.from_object(config)
    db.init_app(app)
    Session(app)
    CsrfProtect(app)

    global redis_store
    redis_store = StrictRedis()  # 创建redis对象

    from .news import main   # 解决循环导包
    app.register_blueprint(main)  # 注册蓝图

    from .admin import admin
    app.register_blueprint(admin, url_prefix='/admin')

    from .passport import passport
    app.register_blueprint(passport, url_prefix='/passport')

    return app


def file_log():
    # 设置日志的记录等级
    logging.basicConfig(level=logging.DEBUG)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)
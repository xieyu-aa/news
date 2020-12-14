from redis import Redis
from datetime import timedelta
import logging

class Config:
    #调试信息
    DEBUG = True
    SECRET_KEY = "fdfdjfkdjfkdf"

    #数据库配置信息
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/new"
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    #redis配置信息
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置信息
    SESSION_TYPE = "redis" #设置session存储类型
    SESSION_REDIS = Redis(host=REDIS_HOST,port=REDIS_PORT) #指定session存储的redis服务器
    SESSION_USE_SIGNER = True #设置签名存储
    PERMANENT_SESSION_LIFETIME = timedelta(days=2) #设置session有效期,两天时间

    # 默认日志级别
    LEVEL_NAME = logging.DEBUG
    

class DevelopConfig(Config):
    '''开发环境'''
    pass


class ProductConfig(Config):
    '''线上环境'''
    DEBUG = False


class   TestConfig(Config):
    '''测试环境'''
    pass


# 访问统一入口字典
config_dict = {'develop': DevelopConfig, 'product': ProductConfig, 'test': TestConfig}

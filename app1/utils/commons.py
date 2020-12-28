
from flask import session, current_app, g

from functools import wraps
# 自定义过滤器
def color_hot_new(index):
    if index ==1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index == 3:
        return 'third'
    else:
        return ''


# 自定义装饰器获取用户登录信息
def login_user(func):
    @wraps(func)
    def call_func(*args, **kwargs):
    # 获取用户登录信息
        user_id = session.get('user_id')
        # 获取用户名
        user = None
        if user_id:
            try:
                from app1.models import User
                user = User.query.filter_by(id=user_id).first()
            except Exception as e:
                current_app.logger.error(e)
        #将user数据存到g对象中
        g.user = user

        return func(*args, **kwargs)
    return call_func

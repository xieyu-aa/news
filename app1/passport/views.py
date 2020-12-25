from datetime import datetime

from . import passport
from app1.utils.captcha.captcha import captcha
from app1 import redis_store, db
from flask import request, current_app, make_response, jsonify, session
from app1 import constants
import re
# from app1.libs.yuntongxun.sms import CCP
import random
from app1.utils.response_code import RET
from app1.models import User



"""
#功能：图片验证码
请求路径：/passport/sms_code
请求方式：POST
参数：moblie， image_code, image_code_id
返回值：发送状态
"""
@passport.route('/image_code')
def image_code():
    print(request.url)
    cur_id = request.args.get('cur_id')
    pre_id = request.args.get('pre_id')

    name, text, image_data = captcha.generate_captcha()

    try:
        redis_store.set('img_code:%s'%cur_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        if pre_id:
            redis_store.delete('img_code:%s' % pre_id)
    except Exception as e:
        current_app.logger.error(e)
    response = make_response(image_data)
    response.headers['Content-Type'] = 'image/png'
    return response


"""
#功能：发短信
请求路径：/passport/sms_code
请求方式：POST
参数：mobile， image_code, image_code_id
返回值：发送状态
"""
@passport.route('/sms_code', methods=['POST'])
def sms_code():
    # 获取json数据转为字典
    json_dict = request.get_json()  # 等价于request.json, 也可以传统json方法

    mobile = json_dict.get('mobile')
    img_code = json_dict.get('image_code')
    img_code_id = json_dict.get('image_code_id')
    # 验证参数是否为空
    if not all([mobile, img_code, img_code_id]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')

    # 判断手机号格式
    if not re.match('1[34578]\d{9}', mobile):
        return jsonify(errno=RET.DATAERR, errmsg='手机号格式错误')
    # 取真实图片验证码

    try:
        img_id = redis_store.get('img_code:%s'%img_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='操作数据库失败')
    # 判断图片验证码过期

    if not img_id:
        return jsonify(errno=RET.NODATA, errmsg='验证码过期')
    # 判断图片验证码

    if img_code.upper() != img_id.upper():
        return jsonify(errno=RET.DATAERR, errmsg='验证码错误')
    # 删除图片验证码
    try:
        redis_store.delete('img_code:%s'%img_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='删验证码失败')
    # 发送短信
    sms_data = '%04s' % random.randint(0, 9999)
    print(sms_data)
    # ccp = CCP()
    # result = ccp.send_template_sms(mobile, [sms_data, constants.IMAGE_CODE_REDIS_EXPIRES/60], 1)
    # # 判断发送成功
    # if result == -1:
    #     return jsonify(errno=RET.DATAERR, errmsg='发送失败')
    # 保存短信验证码到redis
    try:
        redis_store.set('sms_code:%s'%mobile, sms_data, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        return jsonify(errno=RET.DBERR, errmsg='短信验证码保存失败')

    return jsonify(errno=RET.OK, errmsg='发送成功')


"""
#功能：创建新用户
请求路径：/passport/register
请求方式：POST
参数：mobile, sms_code, password
返回值：注册状态
"""
@passport.route('/register', methods=['POST'])
def register():
    json_data = request.get_json()

    mobile = json_data.get('mobile')
    sms_code = json_data.get('sms_code')
    password = json_data.get('password')

    if not all([mobile, sms_code, password]):
        return jsonify(errno=RET.NODATA, errmsg='参数不全')
    try:
        redis_sms_code = redis_store.get('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='数据库操作失败')
    # 验证验证码过期
    if not redis_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg='短信验证码已过期')
    # 验证验证码正确
    if redis_sms_code != sms_code:
        return jsonify(errno=RET.NODATA, errmsg='短信验证码错误')

    # 创建用户对象
    user = User(mobile=mobile)
    user.nick_name = '用户' + mobile
    # user.password_hash =
    user.signature = '该用户什么都没有留下'
    user.password = password
    # 储存用户信息
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='注册失败')
    # 删除验证码
    try:
        redis_store.delete('sms_code:%s'%mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='短信验证码删除失败')
    return jsonify(errno=RET.OK, errmsg='注册成功')


"""
#功能：登录
请求路径：/passport/login
请求方式：POST
参数：moblie， password
返回值：登录状态
"""
@passport.route('/login', methods=['POST'])
def login():
    # 获取参数
    json_data = request.json
    mobile = json_data.get('mobile')
    password = json_data.get('password')
    # 为空校验
    if not all([mobile, password]):
        return jsonify(errno=RET.NODATA, errmsg='参数不全')
    #查询用户对象
    try:
        user = User.query.filter_by(mobile=mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='查询数据库失败')
    # 判断对象存在
    if not user:
        return jsonify(errno=RET.NODATA, errmsg='用户不存在')
    # 校验密码
    if not user.check_password(password):
        return jsonify(errno=RET.DATAERR, errmsg='密码错误')
    # 保存session
    session['user_id'] = user.id

    # 保存最后一次登录时间
    user.last_login = datetime.now()
    # try:
    #
    #     db.session.commit()
    # except Exception as e:
    #     current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg='登录成功')


"""
#功能：退出登录
请求路径：/passport/logout
请求方式：POST
参数：无
返回值：无登录状态
"""
@passport.route('/logout', methods=['POST'])
def logout():

    # 删除session
    try:
        session.pop('user_id')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='退出失败')

    return jsonify(errno=RET.OK, errmsg='退出成功')
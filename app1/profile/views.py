from . import profile
from flask import render_template, g, jsonify, redirect
from app1.utils.commons import login_user
#功能：个人中心首页
#请求方式：get
#请求路径：/user/info
#参数：g.user
#返回值：用户个人信息
from ..utils.response_code import RET


@profile.route('/info')
@login_user
def profile_index():
    # 用户登录
    if not g.user:
        return redirect('/')
    data = {
        'user_info':g.user.to_dict()
    }
    return render_template('news/user.html', data=data)
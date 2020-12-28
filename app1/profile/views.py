from . import profile
from flask import render_template, g, jsonify, redirect, request, current_app
from app1.utils.commons import login_user
from .. import constants, db
from ..models import News, User, Category

from ..utils.response_code import RET
from  app1.utils.image_url import image_url

#功能：个人中心首页
#请求方式：get
#请求路径：/user/info
#参数：g.user
#返回值：用户个人信息
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

#功能：用户基本资料
#请求方式：get， post
#请求路径：/user/base_info
#参数：nick_name, signature, gender
#返回值：模板
@profile.route('/base_info', methods=['POST', 'GET'])
@login_user
def base_info():
    # GET请求
    if request.method == 'GET':
        return render_template('news/user_base_info.html', user_info=g.user.to_dict())
    # POST请求
    #获取参数
    nick_name = request.json.get('nick_name')
    signature = request.json.get('signature')
    gender = request.json.get('gender')
    # 校验参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    if not  gender in ['MAN', 'WOMAN']:
        return jsonify(errno=RET.DATAERR, errmsg='参数错误')
    # 修改数据
    g.user.nick_name = nick_name
    g.user.signature = signature
    g.user.gender = gender
    #返回响应
    return jsonify(errno=RET.OK, errmsg='保存成功')

#功能：用户头像
#请求方式：get， post
#请求路径：/user/pic_info
#参数：nick_name, signature, gender
#返回值：模板
@profile.route('/pic_info', methods=['POST', 'GET'])
@login_user
def pic_info():
    # get请求
    if request.method == 'GET':
        return render_template('news/user_pic_info.html', user_info=g.user.to_dict())
    # post请求取参数
    avatar = request.files.get('avatar')
    if not avatar:
        return jsonify(errno=RET.PARAMERR, errmsg='图片为空')
    # 上传处理
    try:
        # 将获取的图片转成二进制，不要写成image_name = image_url(avatar.read())
        image_data = avatar.read()
        image_name = image_url(image_data)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')
    # 返回响应
    if not image_name:
        return jsonify(errno=RET.DATAERR, errmsg='上传失败')
    # 保存数据库
    g.user.avatar_url = image_name

    data = {'avatar_url': constants.QINIU_DOMIN_PREFIX + image_name}
    print(data.get('avatar_url'))
    return jsonify(errno=RET.OK, errmsg='上传成功', data=data)


#功能：修改密码
#请求方式：get， post
#请求路径：/user/pass_info
#参数：old_password, new_password, new_password2
#返回值：模板
@profile.route('/pass_info', methods=['POST', 'GET'])
@login_user
def pass_info():
    # get请求
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    # post请求
    # 取参数
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    new_password2 = request.json.get('new_password2')
    # 验证参数
    if not all([old_password, new_password, new_password2]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    if not g.user.check_password(old_password):
        return jsonify(errno=RET.DATAERR, errmsg='原密码错误')
    if new_password2 != new_password:
        return jsonify(errno=RET.DATAERR, errmsg='两次密码不一致')
    # 保存到数据库
    try:
        g.user.password = new_password
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='修改失败')
    # 返回响应
    return jsonify(errno=RET.OK, errmsg='修改成功')


#功能：用户收藏
#请求方式：get
#请求路径：/user/collection
#参数：page
#返回值：模板
@profile.route('/collection', methods=['GET'])
@login_user
def collection():
    # 获取参数
    page = request.args.get('page',1,int)
    # 获取收藏新闻列表
    try:
        paginate = g.user.collection_news.order_by(News.create_time.desc()).paginate(page,2,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')
    # 获取新闻列表，总页数，当前页
    news_list = paginate.items
    totalPage = paginate.pages
    currentPage = paginate.page
    # 将新闻列表转成新闻字典列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    # 携带数据
    data = {
        'currentPage' : currentPage,
        'totalPage':totalPage,
        'news_dict_list':news_dict_list
    }
    return render_template('news/user_collection.html', data=data)


#功能：新闻发布
#请求方式：get，post
#请求路径：/user/news_release
#参数：
#返回值：模板
@profile.route('/news_release', methods=['GET', 'POST'])
@login_user
def news_release():
    # get请求
    if request.method == 'GET':
        try:
            categories = Category.query.offset(1).all()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取新闻分类失败')
        categories_list = []
        for categoriy in categories:
            categories_list.append(categoriy.to_dict())

        data = {'categories_list': categories_list}
        return render_template('news/user_news_release.html', data=data)
    # post请求
    # 取参数
    title = request.form.get('title')
    category_id = request.form.get('category_id')
    digest = request.form.get('digest')
    index_image = request.files.get('index_image')
    content = request.form.get('content')
    # 校验参数
    if not all([title, category_id, digest, index_image, content]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    # 上传图片处理
    try:
        index_image = index_image.read()
        image_name = image_url(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg='七牛云异常')
    if not image_name:
        return jsonify(errno=RET.DATAERR, errmsg='图片上传失败')
    # 保存数据库
    news = News()
    news.title = title
    news.source = g.user.nick_name
    news.digest = digest
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + image_name
    news.user_id = g.user.id
    news.category_id = category_id
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='发布失败')
    # 返回响应
    return jsonify(errno=RET.OK, errmsg='发布成功')


#功能：新闻列表
#请求方式：get
#请求路径：/user/news_list
#参数：page
#返回值：模板
@profile.route('/news_list')
@login_user
def news_list():
    # 取参数
    page = request.args.get('page', 1, int)
    # 查出分页内容对象列表
    try:
        paginate = News.query.filter(News.user_id==g.user.id).order_by(News.create_time.desc()).paginate(page,4,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')
    # 携带数据返回响应
    user_news_list = paginate.items
    totalPage = paginate.pages
    currentPage = paginate.page
    news_dict_list = []
    for news in user_news_list:
        news_dict_list.append(news.to_review_dict())
    data = {
        'news_dict_list':news_dict_list,
        'totalPage':totalPage,
        'currentPage':currentPage
    }
    return render_template('news/user_news_list.html', data=data)


# 功能：关注列表
# 请求方式：get, post
# 请求路径：/news/follow
# 参数：user_id
# 返回值：渲染关注列表模板
@profile.route('/follow', methods=['GET'])
@login_user
def follow():
    # 取参数
    page = request.args.get('page', 1, int)
    # 查询数据库得出分页对象
    paginate = g.user.followed.paginate(page,2,False)
    # 取出当前页关注人对象列表，当前页，总页数
    user_list = paginate.items
    totalPage = paginate.pages
    currentPage = paginate.page

    # 携带数据返回响应
    user_dict_list = []
    for aurhor in user_list:
        user_dict_list.append(aurhor.to_dict())
    data = {
        'user_dict_list':user_dict_list,
        'totalPage':totalPage,
        'currentPage':currentPage
    }
    return render_template('news/user_follow.html',data=data)
from . import index_blue
from flask import render_template, current_app, session, jsonify, request, g
from app1.utils.commons import color_hot_new
from ..models import User, News, Category
from ..utils.response_code import RET
from app1.utils.commons import login_user

# 功能：首页框架
@index_blue.route('/', methods=['POST', 'GET'])
@login_user
def new_index(*args):
    # 获取热门新闻列表
    try:
        news = News.query.order_by(News.clicks.desc()).limit(10).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='热门新闻获取失败')

    # 将新闻对象列表转成字典列表
    new_list = list()
    for i in news:
        new_list.append(i.to_dict())

    # 获取新闻分类对象列表
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='获取新闻分类失败')
    # 将新闻分类对象列表转成字典列表
    categorie_list = list()
    for item in categories:
        categorie_list.append(item.to_dict())

    data = {
        'user_info': g.user.to_dict() if g.user else '',  # 用户信息
        'news_list':new_list,   # 热门新闻信息字典列表
        'category':categorie_list  # 新闻分类列表
    }
    # 返回响应
    return render_template('news/index.html', data=data)


# 功能：展示新闻数据
# 请求路径：/newlist
# 请求方式：GET（ajax）
# 请求参数：page，per_page, cid
# 返回值：新闻数据
@index_blue.route('/newslist')
def newlist():
    # 1.获取参数
    cid = request.args.get('cid', 1, type=int)
    print(type(cid))
    print(cid)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # 2.分页查询数据

    try:
        """
        if cid == 1:
            paginate = News.query.order_by(News.create_time.desc()).paginate(page, per_page, False)
        else:
            paginate = News.query.filter(News.category_id==cid).order_by(News.create_time.desc()).paginate(page, per_page, False)
        """

        filters = []
        if cid != 1:
            filters.append(News.category_id == cid)
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page,per_page,False)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg='获取新闻失败')

    # 3.得到将返回的数据
    items = paginate.items
    totalPage = paginate.pages
    news_list = list()
    for item in  items:
        news_list.append(item.to_dict())
        print(item.to_dict().get('title'))
    #4.返回数据
    return jsonify(errno=RET.OK, errmsg='获取新闻成功', newsList=news_list, totalPage=totalPage)



# 功能：网页logo
@index_blue.route('/favicon.ico')
def get_img_logo():
    return current_app.send_static_file('news/favicon.ico')

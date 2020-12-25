
from flask import current_app, render_template, session, abort, jsonify, g, request
from . import news
from .. import db
from ..models import News, User, Comment, CommentLike
from ..utils.commons import login_user
from ..utils.response_code import RET

# 功能：展示新闻详情页
# 请求方式：get
# 请求路径：/news/id
# 参数：id
# 返回值：新闻详情夜模板
@news.route('/<int:id>')
@login_user
def news_detail(id):
    # 1.取出id对应的新闻对象
    try:
        new = News.query.get(id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻数据失败')
    # 2.判断新闻对象存在否则抛出异常
    if not new:
        abort(404)
    # 3.获取热门新闻对象列表
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(6).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg='获取热门新闻失败')
    # 4.判断用户是否有收藏这篇新闻
    is_collected = False
    if g.user:
        if new in g.user.collection_news:
            is_collected = True
    # 5.取出该新闻的所有评论对象
    try:
        comments = Comment.query.filter(Comment.news_id==id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取评论失败')
    # 6.1 该用户的所有点赞对象
    mylikes_comment_id = []
    if g.user:
        try:
            commentlikes = CommentLike.query.filter(CommentLike.user_id==g.user.id).all()
            mylikes_comment_id = []
            for commentlike in commentlikes:
                mylikes_comment_id.append(commentlike.comment_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg='获取点赞失败')
    # 6.将评论对象列表转成字典列表
    comments_list = []
    for item in comments:
        comment_dict = item.to_dict()
        comment_dict['is_like'] = False
        if g.user and item.id in mylikes_comment_id:
            comment_dict['is_like'] = True
        comments_list.append(comment_dict)
    # 渲染需要的数据
    data = {
        'user_info':g.user.to_dict() if g.user else '',  # 用户信息字典
        'news_dateil_dict':new.to_dict(),   # 新闻详情字典
        'news_list':news_list,  # 热门新闻对象列表
        'is_collected':is_collected,  # 判断收藏信息
        'comments':comments_list    # 评论信息字典列表
    }
    return render_template('news/detail.html',data=data)



# 功能：收藏/取消收藏
# 请求方式：post
# 请求路径：/news/news_collect
# 参数：news_id, action
# 返回值：收藏的状态
@news.route('/news_collect', methods=['POST'])
@login_user
def collect():
    # 用户是否登录
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='未登录')
    # 获取参数
    data_dict =request.json
    news_id = data_dict.get('news_id')
    action = data_dict.get('action')
    # 校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    # 取出新闻对象
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')
    # 判断新闻存在
    if not new:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')
    # 判断action参数
    if not action in ['collect', 'cancel_collect']:
        return jsonify(errno=RET.NODATA, errmsg='操作有误')
    if action == 'collect':
        if new not in g.user.collection_news:
            g.user.collection_news.append(new)

    else:
        if new not in g.user.collection_news:
            g.user.collection_news.remove(new)

    return jsonify(errno=RET.OK, errmsg='操作成功')

# 功能：评论
# 请求方式：post
# 请求路径：/news/news_collect
# 参数：news_id,content，parent_id
# 返回值：content
@news.route('/news_comment', methods=['POST'])
@login_user
def news_comments():
    # 用户登录
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')
    # 获取参数
    news_id = request.json.get('news_id')
    news_comment = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    # 校验参数
    if not all([news_id, news_comment]):
        return jsonify(errno=RET.PARAMERR, errmsg='参数不全')
    # 取出新闻对象
    try:
        new = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='获取新闻失败')
    # 判断新闻存在
    if not new:
        return jsonify(errno=RET.NODATA, errmsg='新闻不存在')
    # 创建评论对象
    comment = Comment(user_id=g.user.id, news_id=news_id, content=news_comment)
    if parent_id:
        comment.parent_id = parent_id
    # 保存评论到数据库
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='评论失败')
    # 返回响应
    return jsonify(errno=RET.OK, errmsg='评论成功', data=comment.to_dict())

# 功能：评论点赞
# 请求方式：post
# 请求路径：/news/comment_like
# 参数：comment_id, action
# 返回值：content
@news.route('/comment_like', methods=['POST'])
@login_user
def comment_like():
    print(g.user)
    # 1.用户登录
    if not g.user:
        return jsonify(errno=RET.NODATA, errmsg='用户未登录')
    # 2.获取参数
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')
    print(type(comment_id))
    # 3.校验参数
    if not all([comment_id, action]):
        return jsonify(errno=RET.DBERR, errmsg='参数不全')
    # 4.取出评论对象
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR,errmsg='获取评论失败')
    # 5.判断评论
    if not comment:
        return jsonify(errno=RET.PARAMERR, errmsg='评论不存在')
    # 6.判断action参数
    if not action in ['add', 'remove']:
        return jsonify(errno=RET.DATAERR, errmsg='参数错误')
    # 7.点赞
    try:
        if action == 'add':
            like = CommentLike.query.filter(CommentLike.user_id == g.user.id, CommentLike.comment_id == comment_id).first()
            if  not like:
                my_commentlike = CommentLike()
                my_commentlike.user_id = g.user.id
                my_commentlike.comment_id = comment_id

                db.session.add(my_commentlike)
                comment.like_count += 1
                db.session.commit()
        # 取消点赞
        else:
            my_commentlike = CommentLike.query.filter(CommentLike.user_id == g.user.id, CommentLike.comment_id == comment_id).first()
            print(CommentLike.query.filter_by(user_id = 1, comment_id = 1).first())
            print(CommentLike.query.filter_by(user_id = '1', comment_id = '1').first())
            print(CommentLike.query.filter(CommentLike.user_id == 1, CommentLike.comment_id == 1).first())
            print(CommentLike.query.filter(CommentLike.user_id == '1', CommentLike.comment_id == '1').first())
            print(type(my_commentlike.comment_id))
            if  my_commentlike:
                db.session.delete(my_commentlike)
                if comment.like_count >0:
                    comment.like_count -= 1
                db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg='操作失败')
    return jsonify(errno=RET.OK, errmsg='操作成功')
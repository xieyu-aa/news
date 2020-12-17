from . import main
from flask import render_template, current_app, session

from ..models import User


@main.route('/index')
def index():
    user_id = session.get('user_id')

    user = None
    if user_id:
        try:
            user = User.query.filter_by(id=user_id).first()
        except Exception as e:
            current_app.logger.error(e)
    data = { 'user_info': user.to_dict() if user else ''}
    return render_template('news/index.html', data=data)







@main.route('/favicon.ico')
def get_img_logo():
    return current_app.send_static_file('news/favicon.ico')

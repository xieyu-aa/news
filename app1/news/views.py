from . import main
from flask import render_template, current_app


@main.route('/index')
def index():
    return render_template('news/index.html')


@main.route('/favicon.ico')
def get_img_logo():
    return current_app.send_static_file('news/favicon.ico')

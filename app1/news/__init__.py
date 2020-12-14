from flask import Blueprint


main = Blueprint('news', __name__)

from . import views

from . import admin
from app1 import models

@admin.route('/')
def index():
    return 'hello admin'
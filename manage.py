
from app1 import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app('develop')
manage = Manager(app)  # 插入脚本

Migrate(app, db)  # 数据迁移
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    print(app.url_map)
    manage.run()



from flask import Flask
from app1 import create_app, db
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

app = create_app()
manage = Manager(app)

Migrate(app, db)
manage.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manage.run()


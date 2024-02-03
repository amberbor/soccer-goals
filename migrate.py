import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from database.models import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@127.0.0.1:3315/soccer'
db.init_app(app)
migrate = Migrate(app, db)

def create_app():
    with app.app_context():
        return app


if __name__ == '__main__':
    from flask.cli import FlaskGroup

    migrate.init_app(app, db)
    app_cli = FlaskGroup(create_app=create_app)

    if 'db' in sys.argv:
        app_cli()

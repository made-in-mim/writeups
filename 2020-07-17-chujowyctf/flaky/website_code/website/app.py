import os
import sys
from flask import Flask
from .models import db, User
from .oauth2 import config_oauth
from .routes import bp, csrf
from flask_wtf.csrf import CSRFProtect

def create_app(config=None):
    app = Flask(__name__)
    csrf.init_app(app)

    # load default configuration
    app.config.from_object('website.settings')

    # load environment configuration
    if 'WEBSITE_CONF' in os.environ:
        app.config.from_envvar('WEBSITE_CONF')

    # load app specified configuration
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        elif config.endswith('.py'):
            app.config.from_pyfile(config)

    setup_app(app)
    return app, csrf


def setup_app(app):
    # Create tables if they do not exist already
    @app.before_first_request
    def create_tables():
        db.create_all()
        admin_passwd = os.getenv('ADMINPASSWORD')
        if admin_passwd is None:
            print(os.environ)
            sys.exit('Admin password not set')
        admin = User(username="admin", password=admin_passwd)
        try:
            db.session.add(admin)
            db.session.commit()
        except Exception as e:
            # probably user already exists
            print(e)

    db.init_app(app)
    config_oauth(app)
    app.register_blueprint(bp, url_prefix='')

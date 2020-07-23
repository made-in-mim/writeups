import os
from website.app import create_app


app, csrf = create_app({
    'SECRET_KEY': os.urandom(40).hex(),
    'OAUTH2_REFRESH_TOKEN_GENERATOR': True,
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///db.sqlite',
})

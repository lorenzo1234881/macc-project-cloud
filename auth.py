from flask import Blueprint, request
from google.oauth2 import id_token
from google.auth.transport import requests
from config import conf
from models import User

from flask_login import (
    LoginManager,
    login_user
)

login_manager = LoginManager()

bp = Blueprint('token_signin', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@bp.route('/token-signin', methods=["POST"])
def login():
    request_data = request.get_json()
    token = request_data['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), conf.CLIENT_ID)
        userid = idinfo['sub']
        email = idinfo['email']


        user = User.query.filter_by(email=email).first()
        if(user == None):
            # Registration
            user = User.create(googleid=userid, email=email)
            print('user created')

        login_user(user)

        print('authentication successful')

        return {'auth' : True}

    except ValueError:
        # Invalid token
        pass

    print('authentication failed')

    return {'auth' : False}
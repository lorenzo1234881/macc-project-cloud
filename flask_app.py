from flask import Flask, request, redirect, Response, session
from google.oauth2 import id_token
from google.auth.transport import requests
import json
from flask_login import LoginManager

from config import conf
from models import Restaurant
import upload_restaurant

def create_app():

    app = Flask(__name__)

    from models import db, SQLALCHEMY_DATABASE_URI
    db.init_app(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config['MAX_CONTENT_LENGTH'] = conf.MAX_CONTENT_LENGTH

    app.config['UPLOAD_FOLDER'] = conf.UPLOAD_FOLDER

    app.config['SECRET_KEY'] = conf.SECRET_KEY

    return app


app = create_app()
app.register_blueprint(upload_restaurant.bp)

# login_manager = LoginManager()
# login_manager.init_app(app)


@app.route('/')
def hello_world():
    return 'All working'

@app.route('/token-signin', methods=["POST"])
def login():
    request_data = request.get_json()
    token = request_data['id_token']
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), conf.CLIENT_ID)

        # userid = idinfo['sub']

        print('authentication successful')

        return {'auth' : True}

    except ValueError:
        # Invalid token
        pass

    print('authentication failed')

    return {'auth' : False}

@app.route("/nearby-restaurants", methods=["GET", "POST"])
def nearby_restaurants():

    default_response = {"restaurants":[]}

    if request.method == 'POST':

        request_data = request.get_json()

        user_latitude = request_data['latitude']
        user_longitude = request_data['longitude']


        miles = 100
        max_nresults = 10

        restaurants = Restaurant.near_user(miles, max_nresults, user_latitude, user_longitude)

        response = Response(json.dumps(restaurants) , mimetype='application/json') if restaurants != None else default_response

        return response


    else:
        return default_response


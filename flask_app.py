from flask import Flask, request, Response
import json

from config import conf
from models import Restaurant, User, Reservation
import upload_restaurant
import auth

from flask_login import login_required, current_user

def create_app():

    app = Flask(__name__)

    from models import db, SQLALCHEMY_DATABASE_URI
    db.init_app(app)

    from auth import login_manager
    login_manager.init_app(app)

    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config['MAX_CONTENT_LENGTH'] = conf.MAX_CONTENT_LENGTH

    app.config['UPLOAD_FOLDER'] = conf.UPLOAD_FOLDER

    app.config['SECRET_KEY'] = conf.SECRET_KEY

    return app


app = create_app()
app.register_blueprint(upload_restaurant.bp)
app.register_blueprint(auth.bp)

@app.route('/')
def hello_world():
    return 'All working'

@app.route("/nearby-restaurants", methods=["GET", "POST"])
@login_required
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

@app.route("/make-reservation", methods=["POST"])
@login_required
def make_reservation():
    if request.method == 'POST':
        request_data = request.get_json()

        restaurantid = request_data['restaurantid']
        number_seats = request_data['number_seats']
        userid = current_user.id

        Reservation.create_or_update(userid, restaurantid, number_seats)

        return {'reserved': True}

if __name__ == '__main__':
    from models import db
    with app.app_context():
        db.create_all()



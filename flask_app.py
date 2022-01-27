from flask import Flask, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy

from geopy import Nominatim

import uuid

import os

import json

LOCATOR_USER_AGENT = "macc-project"
UPLOAD_FOLDER = "/home/ll328II/images"
UPLOAD_URL = "https://ll328ii.pythonanywhere.com/images"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ll328II",
    password="b25PEtQuxYh4yzA",
    hostname="ll328II.mysql.pythonanywhere-services.com",
    databasename="ll328II$MACCProject",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config['MAX_CONTENT_LENGTH'] = 512 * 1000 # 512 kb

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['SECRET_KEY'] = 'XmMSjnfM7dhSB8dQazZ'

db = SQLAlchemy(app)
locator = Nominatim(user_agent="macc-project")

class Restaurant(db.Model):

    __tablename__ = "restaurant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    description = db.Column(db.String(4096))
    path_image = db.Column(db.String(128))
    address = db.Column(db.String(128))
    latitude = db.Column(db.Float(10,6))
    longitude = db.Column(db.Float(10,6))

    def as_dict(self):
        return {
            "name" : self.name,
            "description" : self.description,
            "path_image" : self.path_image,
            "address" : self.address,
            "latitude" : self.latitude,
            "longitude" : self.longitude
        }


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_restaurant_to_db(name, description, path_image, address, latitude, longitude):

    restaurant = Restaurant(name=name,
        description=description,
        path_image=path_image,
        address=address,
        latitude=latitude,
        longitude=longitude)

    db.session.add(restaurant)
    db.session.commit()

@app.route('/')
def hello_world():
    return 'Hello from Flask!'

@app.route('/upload-restaurant', methods=["GET", "POST"])
def upload_restaurant():

    if request.method == 'POST':

        if 'restaurant_photo' not in request.files:
            print("upload_restaurant():", "POST request doesn't contain file part")
            return redirect(request.url)

        image = request.files['restaurant_photo']
        name = request.form['name']
        address = request.form['address']
        description = request.form['description']

        location = locator.geocode(address)
        if location == None:
            print("upload_restaurant():", 'Invalid address')
            return redirect(request.url)

        if image.filename == '':
            print("upload_restaurant():", "Didn't select a file")
            return redirect(request.url)

        if image and allowed_file(image.filename):
            print("upload_restaurant():", "Extension not allowed")
            filename = str(uuid.uuid4())
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            add_restaurant_to_db(name,
                description,
                os.path.join(UPLOAD_URL, filename),
                address,
                location.latitude,
                location.longitude)


    return '''
    <!doctype html>
    <title>Upload new Restaurant</title>
    <h1>Upload new Restaurant</h1>

    <form method=post enctype=multipart/form-data>
        <label for="name">Name:</label><br>
        <input type="text" id="name" name="name" value=""><br>
        <br>

        <label for="address">Address:</label><br>
        <input type="text" id="address" name="address" value=""><br>
        <br>

        <label for="restaurant_photo">Restaurant Photo:</label><br>
        <input type=file name=restaurant_photo><br>
        <br>

        <label for="description">Description:</label><br>
        <textarea name="description" placeholder="Enter a description"></textarea><br>
        <br>
        <input type=submit value=Upload>
    </form>
    '''


@app.route("/nearby-restaurants", methods=["GET", "POST"])
def nearby_restaurants():

    default_response = {"restaurants":[]}

    if request.method == 'POST':

        request_data = request.get_json()

        user_latitude = request_data['latitude']
        user_longitude = request_data['longitude']


        miles = 100
        max_nresults = 10

        cursor_result = db.session.execute("""SELECT id, name, path_image, description, address, ( 3959 * acos( cos( radians(:user_latitude) ) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians(:user_longitude) ) + sin( radians(:user_latitude) ) * sin( radians( latitude ) ) ) ) AS distance
        FROM restaurant HAVING distance < :miles ORDER BY distance LIMIT 0 , :max_nresults""",
        {"miles":miles, "max_nresults":max_nresults, "user_latitude":user_latitude, "user_longitude":user_longitude})

        list_row_mapping = cursor_result.mappings().all()

        if len(list_row_mapping) > 0:

            restaurants = {"restaurants": [{k:v for k,v in r.items()} for r in list_row_mapping]} # from list of RowMapping to dict
            return Response(json.dumps(restaurants) , mimetype='application/json')

        else:
            return default_response

    else:
        return default_response


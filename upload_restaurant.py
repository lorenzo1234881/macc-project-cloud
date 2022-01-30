from geopy import Nominatim
import uuid
import os
from config import conf
from flask import Blueprint, request, redirect
from flask import current_app
from models import Restaurant

bp = Blueprint('upload_restaurant', __name__)

locator = Nominatim(user_agent="macc-project")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in conf.ALLOWED_EXTENSIONS

@bp.route('/upload-restaurant', methods=["GET", "POST"])
def upload_restaurant_api():

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
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

            Restaurant.create(name=name,
                description=description,
                path_image=os.path.join(conf.UPLOAD_URL, filename),
                address=address,
                latitude=location.latitude,
                longitude=location.longitude)


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

        <label for="seating_capacity">Seating capacity:</label><br>
        <input type="number" id="seating_capacity" name="seating_capacity" value=><br>
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

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from config import conf

SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ll328II",
    password=conf.PASSWORD_DB,
    hostname="ll328II.mysql.pythonanywhere-services.com",
    databasename="ll328II$MACCProject",
)

db = SQLAlchemy()

class BaseMixin(object):
    @classmethod
    def create(cls, **kw):
        obj = cls(**kw)
        db.session.add(obj)
        db.session.commit()

        return obj

class Restaurant(BaseMixin, db.Model):

    __tablename__ = "restaurant"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(4096))
    path_image = db.Column(db.String(128))
    address = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.Float(10,6))
    longitude = db.Column(db.Float(10,6))


    def near_user(miles, max_nresults, user_latitude, user_longitude):
        """ Find $max_nresults within $miles from user location.

        To search by kilometers instead of miles, replace 3959 with 6371
        Snippet from web.archive.org/web/20170126150533/https://developers.google.com/maps/articles/phpsqlsearch_v3#findnearsql
        """

        cursor_result = db.session.execute("""SELECT id, name, path_image, description, address, ( 3959 * acos( cos( radians(:user_latitude) ) * cos( radians( latitude ) ) * cos( radians( longitude ) - radians(:user_longitude) ) + sin( radians(:user_latitude) ) * sin( radians( latitude ) ) ) ) AS distance
        FROM restaurant HAVING distance < :miles ORDER BY distance LIMIT 0 , :max_nresults""",
        {"miles":miles, "max_nresults":max_nresults, "user_latitude":user_latitude, "user_longitude":user_longitude})

        list_row_mapping = cursor_result.mappings().all()

        if len(list_row_mapping) > 0:

            restaurants = {"restaurants": [{k:v for k,v in r.items()} for r in list_row_mapping]} # from list of RowMapping to dict
            return restaurants

        else:
            return None

class User(UserMixin, BaseMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    googleid = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)


class Reservation(BaseMixin, db.Model):

    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer, nullable=False)
    restaurantid = db.Column(db.Integer, nullable=False)
    number_seats = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    dayOfMonth = db.Column(db.Integer)
    hour = db.Column(db.Integer)
    minute = db.Column(db.Integer)


    @classmethod
    def create_or_update(cls, userid, restaurantid, **kw):

        reservationQuery = cls.query.filter_by(userid=userid, restaurantid=restaurantid)
        reservation = reservationQuery.first()
        if reservation == None:

            print('Create new reservation')

            kw['userid'] = userid
            kw['restaurantid'] = restaurantid

            cls.create(**kw)

        else:
            reservationQuery.update(kw)
            db.session.commit()

            print('Update reservation')

    @classmethod
    def delete(cls, userid, restaurantid):
        Reservation.query.filter_by(userid=userid, restaurantid=restaurantid).delete()
        db.session.commit()


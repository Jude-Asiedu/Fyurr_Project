
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# #----------------------------------------------------------------------------#
# # Models.
# #----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genre = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talents = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    # def __repr__(self) -> str:
    #     return super().__repr__()

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
     
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


shows = db.Table('Shows',
    db.Column('artist_id', db.Integer,db.ForeignKey('Artist.id'),primary_key=True),
    db.Column('venue_id', db.Integer,db.ForeignKey('Venue.id'),primary_key=True),
    db.Column('start_time',db.DateTime)
)

#   # genre ,starting time
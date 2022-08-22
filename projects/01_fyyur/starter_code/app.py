#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from models import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# db = SQLAlchemy(app)
# New Changes made were referenced from StackOverflow
db.init_app(app)
migrate = Migrate(app,db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# class Venue(db.Model):
#     __tablename__ = 'Venue'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     address = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     genre = db.Column(db.String(120))
#     website_link = db.Column(db.String(120))
#     seeking_talents = db.Column(db.Boolean)
#     seeking_description = db.Column(db.String(500))
#     # TODO: implement any missing fields, as a database migration using Flask-Migrate


# class Artist(db.Model):
#     __tablename__ = 'Artist'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String)
#     city = db.Column(db.String(120))
#     state = db.Column(db.String(120))
#     phone = db.Column(db.String(120))
#     genres = db.Column(db.String(120))
#     image_link = db.Column(db.String(500))
#     facebook_link = db.Column(db.String(120))
#     website_link = db.Column(db.String(120))
#     seeking_venue = db.Column(db.Boolean)
#     seeking_description = db.Column(db.String(500))
     
#     # TODO: implement any missing fields, as a database migration using Flask-Migrate


# shows = db.Table('Shows',
#     db.Column('artist_id', db.Integer,db.ForeignKey('Artist.id'),primary_key=True),
#     db.Column('venue_id', db.Integer,db.ForeignKey('Venue.id'),primary_key=True),
#     db.Column('start_time',db.DateTime)
# )

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  # data = []
  # data = Venue.query.group_by(Venue.city).all()\
  # data = Venue.query.filter(Venue.city)

  # showsCount = shows.query.count(shows.query.filter(shows.start_time >= format_datetime(datetime.today())))
  data  = Venue.query.join(shows).with_entities(Venue.city,Venue.state,Venue.id,Venue.name,shows.query.count(shows.query.filter(shows.start_time >= format_datetime(datetime.today()))).label('num_upcoming_shows')).group_by(Venue.city).all()

  # for _ in city:
  #   data.append(_.asdict())

  # venues['num_upcoming_shows'] = showsCount
  
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_Term = request.get_json()['search_term']
  response = Venue.query.all()
  data = Venue.query.filter(Venue.name.like(f'%{search_Term}%')).all()
  show_number =  shows.query.count(Venue.query.filter(shows.start_time >= format_datetime(datetime.today())).all())

  # show_number = shows.query.count(data.filter_by(venue_id))
  data['num_upcoming_shows'] = show_number
  count = len(data)
  response['data'] = data
  response['count'] = count


  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  #  data = Venue.query.all()
  data = Venue.query.filter(Venue.id == venue_id).all()
  past_shows = Venue.query.filter(shows.venue_id == venue_id,shows.start_time <= format_datetime(datetime.today())).all()
  upcoming_shows =  Venue.query.filter(shows.venue_id == venue_id,shows.start_time >= format_datetime(datetime.today())).all()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

 
  # dict_a = {}
  # dict_b = []
  # dict_a["past_shows"] = dict_b
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error = False
  body = {}
  try:
    name  = request.get_json()['name']
    state  = request.get_json()['state']
    city  = request.get_json()['city']
    address  = request.get_json()['address']
    phone  = request.get_json()['phone']
    genres  = request.get_json()['genres']
    image_link  = request.get_json()['image_link']
    website_link = request.get_json()['website_link']
    facebook_link = request.get_json()['facebook_link']
    seeking_talent = request.get_json()['seeking_talent']
    seeking_desciption = request.get_json()['seeking_description']

    data = Venue(name=name)

    db.session.add(data)
    db.session.commit()

    body['name'] = Venue.name

  except:
    db.session.rollback()
    error= True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
   flash('Error in creating venue for ' + request.form['name'])
  else:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # on successful db insert, flash success
  # flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using # SQLAlchemy ORM to delete a record.# 
  # Handle cases where the session commit could fail .

  error = False
  try: 
      data = Venue.query.get(venue_id)
      db.session.delete(data)
      db.session.commit()
  except:
      db.session.rollback()
      error= True
      print(sys.exc_info())
    
  finally:
      db.session.close()
      
  if error:
      flash('Sorry an error occured when deleting venue')
  else:
      flash('Venue was deleted succesfully when deleting venue')
  # return  redirect(url_for('index'))
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))


#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  # data = Artist.query.all()
  # TODO:replace with real data returned from querying the database
  data = Artist.query.with_entities(Artist.id,Artist.name).all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  response = {}
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_Term = request.get_json()['search_term']
  # response = Artist.query.all()
  data = Artist.query.filter(Artist.name.like(f'%{search_Term}%')).all()
  show_number =  shows.query.count(Artist.query.filter(shows.start_time >= format_datetime(datetime.today())).all())

  data['num_upcoming_shows'] = show_number
  count = len(data)
  response['data'] = data
  response['count'] = count

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  data = Artist.query.filter(Artist.id == artist_id).all()
  past_shows = Artist.query.filter(shows.artist_id == artist_id,shows.start_time <= format_datetime(datetime.today())).all()
  upcoming_shows =  Venue.query.filter(shows.artist_id == artist_id,shows.start_time >= format_datetime(datetime.today())).all()
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)






#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.filter(Artist.id == artist_id).all()
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error= False
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    image_link = request.get_json()['imsge_link']
    genres = request.get_json()['genres']
    facebook_link = request.get_json()['facebook_link']
    website_link = request.get_json()['website_link']
    seeking_venue = request.get_json()['seeking_venue']
    seeking_description = request.get_json()['seeking_description']

    data = Artist.query.get(artist_id)
    data.name = name
    data.city = city
    data.state = state
    data.phone = phone
    data.image_link = image_link
    data.genres = genres
    data.facebook_link = facebook_link
    data.website_link = website_link
    data.seeking_venue = seeking_venue
    data.seeking_description = seeking_description
  
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exec_info)
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))
# ...
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.filter(Venue.id == venue_id).first()
  venue = venue._asdict()
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  error = False
  try:

    name  = request.get_json()['name']
    state  = request.get_json()['state']
    city  = request.get_json()['city']
    address  = request.get_json()['address']
    phone  = request.get_json()['phone']
    genres  = request.get_json()['genres']
    image_link  = request.get_json()['image_link']
    website_link = request.get_json()['website_link']
    facebook_link = request.get_json()['facebook_link']
    seeking_talent = request.get_json()['seeking_talent']
    seeking_description = request.get_json()['seeking_description']

    newData = Venue.query.get(venue_id)
    newData.name = name
    newData.city = city
    newData.state = state
    newData.address = address
    newData.phone = phone
    newData.genres = genres
    newData.image_link = image_link
    newData.genres = genres
    newData.facebook_link = facebook_link
    newData.image_link = image_link
    newData.website_link = website_link
    newData.seeking_talent = seeking_talent
    newData.seeking_description = seeking_description

    db.session.commit()

  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()



  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  error= False
  data = {}
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    image_link = request.get_json()['imsge_link']
    genres = request.get_json()['genres']
    facebook_link = request.get_json()['facebook_link']
    website_link = request.get_json()['website_link']
    seeking_venue = request.get_json()['seeking_venue']
    seeking_description = request.get_json()['seeking_description']

    body = Artist(name = name, city = city, state = state, phone = phone, genres = genres, image_link = image_link , website_link = website_link , seeking_venue = seeking_venue, seeking_description = seeking_description, facebook_link = facebook_link)
    db.session.add(body)
    db.session.commit()
    data['name'] = body.name
    data['city'] = body.city
    data['state'] = body.state
    data['phone'] = body.phone
    data['imsge_link'] = body.image_link
    data['genres'] = body.genres
    data['facebook_link'] = body.facebook_link
    data['website_link'] = body.website_link
    data['seeking_venue'] = body.seeking_venue
    data['seeking_description'] = body.seeking_description
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info)
  finally:
    db.session.close()
  if error:
    flash("An error occured.New Artist could not be created")
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return jsonify(data)


  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  result = shows.query.join(Artist,Artist.id == shows.artist_id).join(Venue,Venue.id ==  shows.venue_id).with_entities(shows.venue_id,shows.artist_id, Venue.name.label('venue_name')  ,Artist.name.label('artist_name') , Artist.image_link.label('artist_image_link')).all()
  data = []
  for _ in result:
    data.append(_.asdict())

  # print(data)
  # venueName  = Venue.query.filter(shows.venue_id == Venue.id)
  # artistName  = Artist.query.filter(shows.artist_id == Artist.id)
  # data['venue_name'] = venueName['name']
  # data['artist_name']= artistName['name']
  # data['artist_image_link']= artistName['image_link']


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record  in the db, instead
  error = False
  body = {}
  try:
      artist_id = request.get_json()['artist_id']
      venue_id = request.get_json()['venue_id']
      start_time = request.get_json()['start_time']
      
      newData = shows(artist_id = artist_id, venue_id = venue_id , start_time = start_time)
      db.session.add(newData)
      db.session.commit()
      body['start_time'] = newData.start_time
      body['artist_id'] = newData.artist_id
      body['venue_id'] = newData.venue_id
  except(error):
    db.session.rollback()
    error= True

    print(sys.exc_info)

  finally:  
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
    return jsonify(body)
  
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

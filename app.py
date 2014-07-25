from flask import Flask, request, g, redirect, url_for, render_template, flash
from datetime import datetime
from mongokit import Connection, Document
from urlparse import urlparse, parse_qs
import os

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = "a"


def parse_mongodb_url():
    mongodb_url = os.environ.get(
        'MONGOHQ_URL', 'mongodb://localhost:27017/orgullopr')
    parsed_url = urlparse(mongodb_url)

    return {
        'host': parsed_url.hostname,
        'port': int(parsed_url.port),
        'username': parsed_url.username,
        'password': parsed_url.password,
        'database': parsed_url.path[1:]
    }

parsed_mongodb_url = parse_mongodb_url()

app.config.update(dict(
    DEBUG=True,
))

app.config.from_envvar('ORGULLOPR_SETTINGS', silent=True)


class Testimonial(Document):
    __database__ = parsed_mongodb_url['database']
    __collection__ = 'testimonials'
    structure = {
        'name': unicode,
        'email': unicode,
        'prof': unicode,
        'industry': unicode,
        'industry_other': unicode,
        'town': unicode,
        'pride_in': unicode,
        'metas': list,
        'desafio': unicode,
        'website_url': unicode,
        'twitter_url': unicode,
        'facebook_url': unicode,
        'youtube_url': unicode,
        'picture_url': unicode,
        'created_date': datetime
    }
    required_fields = ['name', 'email', 'prof', 'industry', 'town', 'pride_in', 'desafio', 'picture_url']
    default_values = {'created_date': datetime.utcnow}


class Town(Document):
    __database__ = parsed_mongodb_url['database']
    __collection__ = 'towns'
    structure = {
        'id': int,
        'name': unicode
    }
    required_fields = ['id', 'name']


def dict_factory(cursor, row):
    """
    Used to substitute the sqlite.Row factory. This is done to avoid the tuple
    output from sqlite.Row.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def connect_mongo_db():
    """Connecto to a mongodb database."""
    host = parsed_mongodb_url['host']
    port = parsed_mongodb_url['port']
    database = parsed_mongodb_url['database']
    username = parsed_mongodb_url['username']
    password = parsed_mongodb_url['password']

    connection = Connection(host, port)

    if username and password:
        connection[database].authenticate(username, password)

    return connection


def get_db():
    """
    Opens a new database connection if there is none yet for the current
    application context.
    """
    if not hasattr(g, 'mongo_db'):
        g.db = get_mongo_db()

    return g.db


def get_mongo_db():
    """
    Opens a new mongodb connection if there isn't one for the current
    application context.
    """

    if not hasattr(g, 'mongodb'):
        g.mongodb = connect_mongo_db()

    g.mongodb.register([Testimonial])
    g.mongodb.register([Town])

    return g.mongodb


def run_query(query, bindings=None):
    db = get_db()
    if bindings and len(bindings):
        cur = db.execute(query, bindings)
    else:
        cur = db.execute(query)
    return cur.fetchall()


def get_towns():
    db = get_db()

    return db.Town.find()


def get_town_videos(town=0):
    db = get_db()
    if town:
        return db.Testimonial.find({'town': town})
    else:
        return db.Testimonial.find()


def load_towns():
    """
    Loads into session all towns (municipios) in PR
    """
    if not hasattr(g, 'towns'):
        #g.towns = run_query('select id, name from municipios')
        g.towns = get_towns()
    return g.towns


def video_id(value):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


@app.teardown_appcontext
def close_db(error):
    """
    Closes the database again at the end of the request
    """

    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()


@app.route('/')
def index():
    load_towns()
    return render_template('index.html', towns=g.towns)

@app.route('/subir')
def subir():
    load_towns()
    return render_template('subir.html', towns=g.towns)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')

@app.route('/explora')
def explora():
    """
    Get all videos from all cities and renders them in the videos view.
    """

    towns = get_towns()
    entries = {}

    for town in towns:
        town_entries = get_town_videos(town['name'])
        list_of_entries = []
        for entry in town_entries:
            list_of_entries.append(entry)
        if list_of_entries != []:
            entries[town['name']] = list_of_entries

    if entries:
        return render_template('explora.html', entries=entries)
    else:
        flash('No se encontraron videos.')
        return render_template('explora.html')
    return render_template('explora.html', entries=[])

@app.route('/videos', methods=['GET'])
def show_videos():
    return render_template('videos.html')


@app.route('/videos/<town>', methods=['GET'])
def get_videos(town):
    """
    Get all videos from specified city and renders them in the videos view.
    """

    entries = get_town_videos(town)

    if entries:
        return render_template('videos.html', videos=entries, town=town)
    else:
        flash('No se encontraron videos.')
        return render_template('videos.html', town=town)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()

    testimonials = db.Testimonial()

    testimonials['name'] = request.form.get('name', None)
    testimonials['email'] = request.form.get('email', None)
    testimonials['prof'] = request.form.get('prof', None)
    testimonials['industry'] = request.form.get('industry', None)
    testimonials['industry_other'] = request.form.get('industry_other', None)
    testimonials['town'] = request.form.get('town', None)
    testimonials['pride_in'] = request.form.get('pride_in', None)
    testimonials['metas'] = request.form.getlist('metas[]', None)
    testimonials['desafio'] = request.form.get('desafio', None)
    testimonials['website_url'] = request.form.get('website_url', None)
    testimonials['twitter_url'] = request.form.get('twitter_url', None)
    testimonials['facebook_url'] = request.form.get('facebook_url', None)
    testimonials['youtube_url'] = request.form.get('youtube_url', None).split('=')[-1]
    testimonials['picture_url'] = request.form.get('picture_url', None)
    testimonials['created_date'] = request.form.get('created_date', None)

    testimonials.save()

    flash('New entry was successfully posted')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
    url_for('static', filename='geotiles/pueblos.json')
    url_for('static', filename='geotiles/barrios.json')
    url_for('static', filename='geotiles/barrios+isla.json')
    url_for('static', filename='geotiles/barrios+isla+pueblos.json')
    url_for('static', filename='geotiles/barrios+pueblos.json')
    url_for('static', filename='geotiles/isla.json')
    url_for('static', filename='geotiles/isla+pueblos.json')
    url_for('static', filename='geotiles/pueblos.json')
    url_for('static', filename='geotiles/puertorico-geo.json')

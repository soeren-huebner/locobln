# stdlib
from datetime import datetime as dt
import os
import random
# databases (mongodb for resources and sqlalchemy/sqlite for user data)
from pymongo import MongoClient
#from flask_sqlalchemy import SQLAlchemy
# flask stuff
from flask import Flask, render_template, request, jsonify, redirect, abort, send_file, send_from_directory, url_for, flash, session
from werkzeug.utils import secure_filename
# oauth
from authlib.integrations.flask_client import OAuth, OAuthError
# to prevent cors errors
from flask_cors import CORS

# WTForms
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired

# do I need this?
#from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user

#####################################
######## INIT ######################
####################################

# initialise flask
application = Flask(__name__)
# this is a local configuration containing credentials/secrets (it's included in .gitignore)
application.config.from_object('config.Config')

# set up the user db
#user_db = SQLAlchemy(application)
#lm = LoginManager(application)
# TODO change this to make it work with the webapp
#lm.login_view = 'index'
#user_db.init_app(application)
#user_db.create_all()

CORS(application)

oauth = OAuth(application)
oauth.register(
    name='twitter',
    api_base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
)
oauth.register(
    name='google',
    server_metadata_url=application.config['GOOGLE_CONF_URL'],
    client_kwargs={
        'scope': 'openid email profile'
    }
)
oauth.register(
    name='facebook',
    api_base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=application.config['FACEBOOK_CLIENT_ID'],
    consumer_secret=application.config['FACEBOOK_CLIENT_SECRET'],
    request_token_params={'scope': 'id,email,name'},
    fetch_token=lambda: session.get('token'),  # DON'T DO IT IN PRODUCTION
)

# connect to mongo db
client = MongoClient('mongodb://mongo:27017/')
db = client.resource_database

#####################################
####### USER DB ####################
####################################

#class User(UserMixin, user_db.Model):
#    __tablename__ = 'users'
#    id = user_db.Column(user_db.Integer, primary_key=True)
#    social_id = user_db.Column(user_db.String(64), nullable=False, unique=True)
#    name = user_db.Column(user_db.String(64), nullable=False)
#    email = user_db.Column(user_db.String(64), nullable=True)


#####################################
######## WTForms ###################
####################################
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')




#####################################
######## ROUTES ####################
####################################


@application.errorhandler(OAuthError)
def handle_error(error):
    return render_template('error.html', error=error)


@application.route('/login2')
def login2():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


@application.route('/')
def homepage():
    user = session.get('user')
    return render_template('home.html', user=user)
    #return redirect('http://a82150d.online-server.cloud/login')


@application.route('/login/<provider>')
def login(provider):
    redirect_uri = url_for('auth', provider=provider, _external=True)
    if provider == 'twitter':
        return oauth.twitter.authorize_redirect(redirect_uri)
    elif provider == 'google':
        return oauth.google.authorize_redirect(redirect_uri)
    elif provider == 'facebook':
        return oauth.facebook.authorize_redirect(redirect_uri)
    else:
        # TODO proper error handling (unsupported provider)
        return redirect('/')


@application.route('/auth/<provider>')
def auth(provider):
    if provider == 'twitter':
        token = oauth.twitter.authorize_access_token()
        url = 'account/verify_credentials.json'
        #resp = oauth.twitter.get(url, params={'skip_status': True, 'include_email': True})
        resp = oauth.twitter.get(url, params={'include_email': True})
        user = resp.json()
    elif provider == 'facebook':
        token = oauth.facebook.authorize_access_token()
        resp = oauth.facebook.get('/me')
        user = resp.json()
    elif provider == 'google':
        token = oauth.google.authorize_access_token()
        user = oauth.google.parse_id_token(token)
    else:
        # TODO proper error handling (unsupported provider)
        return redirect('/')
    # DON'T DO IT IN PRODUCTION, SAVE INTO DB IN PRODUCTION
    session['token'] = token
    session['user'] = user
    return redirect('/')


@application.route('/logout')
def logout():
    session.pop('token', None)
    session.pop('user', None)
    return redirect('/')


@application.route('/user', methods=['GET'])
def user():
    user = session.get('user')
    user_info = {
        'id':           None,
        'name':         None,
        'email':        None,
    }
    if user:
        for key in user_info.keys():
            try:
                user_info[key] = user[key]
            except KeyError:
                continue
    response = jsonify(user_info)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


######## OTHER ROUTES
@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@application.route('/upload')
def upload():
    # display the upload web page
    return render_template('upload.html')


@application.route('/uploader', methods=['POST', 'DELETE'])
def upload_resource():
   if request.method == 'POST':
      try:
         # save the uploaded file to the server
         f = request.files['file']
         # add a timestamp to the filename to avoid collisions
         # TODO make sure that this works even if the filename contains seperators
         timestamp = dt.timestamp(dt.now())
         timestamp_str = '%.0f' % timestamp
         new_filename = timestamp_str + '_' + f.filename
         dst = os.path.join(RESOURCE_FOLDER, secure_filename(new_filename))
         f.save(dst)
         # TODO leave out attribute if the html field was empty
         doc = {
            'title': request.form['title'],
            'author': request.form['author'],
            'description': request.form['description'],
            'latitude': float(request.form['latitude']),
            'longitude': float(request.form['longitude']),
            'timestamp': timestamp,
            'path': dst,
            'tags': '',
            'type': request.form['res_type'],           # resource type
            'size': os.stat(dst).st_size,               # filesize in bytes
            }
         db.resource_collection.insert_one(doc)
      except Exception as e:
         raise

   return 'Finished the file upload.'


@application.route('/tags', methods=['GET'])
def get_all_tags():
   return {'data': db.resource_collection.distinct('tags')}


@application.route('/markers', methods=['GET', 'POST'])
def get_markers():
   start_date = request.args.get('start_date')
   end_date = request.args.get('end_date')
   tags = request.args.get('tags')

   if tags:
      query = {
         "timestamp": {
            "$gte": float(start_date),
            "$lte": float(end_date)
         },
         "tags": str(tags)
      }
   else:
         query = {
         "timestamp": {
            "$gte": float(start_date),
            "$lte": float(end_date)
         }
      }


   # read from mongoDB
   cursor = db.resource_collection
   output = []
   for c in cursor.find(query):
      output.append(
         {
            'title'        :  c['title'],
            'author'       :  c['author'],
            'description'  :  c['description'],
            'latitude'     :  c['latitude'],
            'longitude'    :  c['longitude'],
            'timestamp'    :  c['timestamp'],
            'path'         :  c['path'],
            'type'         :  c['type'],
            'size'         :  c['size'],
            'key'          :  str(c['_id']),
            'tags'         :  c['tags'],
         })
   return {'data' : output}

@application.route('/resources/<resource_name>')
def get_resource(resource_name):
   try:
      return send_file(RESOURCE_FOLDER+'/'+resource_name, as_attachment=True)
   except FileNotFoundError:
      abort(404)

#@application.route('/')
#def index():
#   # display the homepage
#   return render_template('index.html')

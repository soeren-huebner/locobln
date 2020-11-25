from datetime import datetime as dt
import os
import random

from pymongo import MongoClient

from flask import Flask, render_template, request, jsonify, redirect, abort, send_file, send_from_directory, url_for
from werkzeug.utils import secure_filename

#####################################
######## INIT ######################
####################################

# initialise flask
application = Flask(__name__)

# connect to mongo db
#client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)
client = MongoClient('mongodb://mongo:27017/')
db = client.resource_database

# setup the folder where uploaded videos are going to be stored
RESOURCE_FOLDER = '/resources'
application.config['RESOURCE_FOLDER'] = RESOURCE_FOLDER
# constrain max size of uploads to 50MB
application.config['MAX_CONTENT_LENGTH'] = 50 * 10**6

#####################################
######## ROUTES ####################
####################################

@application.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(application.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@application.route('/upload')
def upload():
   # display the upload web page
   return render_template('upload.html')

@application.route('/uploader', methods = ['POST', 'DELETE'])
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
   return {'data' : db.resource_collection.distinct('tags')}

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

@application.route('/')
def index():
   # display the homepage
   return render_template('index.html')

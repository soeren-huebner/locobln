from datetime import datetime as dt
import os
import random

from pymongo import MongoClient

from flask import Flask, render_template, request, jsonify, redirect, abort, send_file
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response

# initialise flask
app = Flask(__name__)

@app.route('/upload')
def upload():
   # display the upload web page
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST', 'DELETE'])
def upload_file():
   if request.method == 'POST':
      try:
         # TODO generalise to different types of documents
         # save the uploaded file to the server
         f = request.files['file']
         dst = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
         f.save(dst)
         print('[DIR] SAVED video {} to server'.format(f.filename))
         
         # construct a document for the mongo db
         doc = {
            'title': f.filename,                   # TODO change this to a title
            'author': author,
            'location': location,
            'timestamp': dt.timestamp(dt.now()),
            'type': 'video',                       # resource type
            'url': dst,
            'size': os.stat(dst).st_size,          # filesize in bytes
            }
         print('[MONGO DB] CREATED a new document')
         # insert the document into database
         collection.insert_one(doc)
         print('[MONGO DB] INSERTED the document to the collection')
      except Exception as e:
         print(e)

   elif request.method == 'DELETE':
      f = request.files['file']
      dst = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
      # delete resource from server
      os.remove(dst)
      print('[DIR] DELETED video {} from server'.format(f.filename))

   return '[RETURN] file operation was successful'

@app.route('/markers')
def get_markers():
   # read from mongoDB
   cursor = db.markers
   output = []
   for c in cursor.find():
      output.append(
         {
            'title': c['title'], 
            'description' : c['description'],
            'latitude' : c['latitude'],
            'longitude' : c['longitude'],
            'key' : str(c['_id']),
         })
   return {'data' : output}

@app.route('/video/<video_name>')
def get_video(video_name):
   # TODO get video dst by id
   #dst = os.path.join(UPLOAD_FOLDER, secure_filename('jupiters_auroras.mp4'))
   #f = open(dst)
   #return Response(f, direct_passthrough=True)

   try:
      return send_file('videos/'+video_name, as_attachment=True)
   except FileNotFoundError:
      abort(404)

@app.route('/')
def index():
   # display the homepage
   return render_template('index.html')


if __name__ == '__main__':
   # connect to mongo db
   client = MongoClient('localhost', 27017, username='locobln_mongoroot', password='Start.Mongo!')
   db = client['resource_database']
   collection = db['resource_collection']

   # setup the folder where uploaded videos are going to be stored
   UPLOAD_FOLDER = 'videos'
   app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
   # constrain max size of uploads to 50MB 
   app.config['MAX_CONTENT_LENGTH'] = 50 * 10**6

   # TODO do this via config files or user input
   # set parameters for the upload
   author = 'author'
   location = [52.436244, 13.345781]
   # add a bit of randomness to the location
   location[0] += random.randrange(-100,100,1)/1000
   location[1] += random.randrange(-100,100,1)/1000

   # start flask
   app.run(host='0.0.0.0', debug=True)

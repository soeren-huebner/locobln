from datetime import datetime as dt
import os
import random

from pymongo import MongoClient
import gridfs

from flask import Flask, render_template, request, jsonify, redirect, abort, send_file
from werkzeug.utils import secure_filename
from werkzeug.wrappers import Response

# initialise flask
app = Flask(__name__)

@app.route('/upload')
def upload():
   # display the upload web page
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['POST', 'DELETE'])
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
            'type': request.form['res_type'],           # resource type
            'size': os.stat(dst).st_size,               # filesize in bytes
            }
         db.resource_collection.insert_one(doc)
      except Exception as e:
         print(e)

   return 'Finished the file upload.'

@app.route('/markers', methods=['GET', 'POST'])
def get_markers():
   start_date = request.args.get('start_date')
   end_date = request.args.get('end_date')
   
   print(start_date)
   print(end_date)

   query = {
      "timestamp": {
         "$gte": start_date,
         "$lte": end_date
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
         })
   return {'data' : output}

@app.route('/resources/<resource_name>')
def get_resource(resource_name):
   try:
      return send_file(RESOURCE_FOLDER+'/'+resource_name, as_attachment=True)
   except FileNotFoundError:
      abort(404)

@app.route('/')
def index():
   # display the homepage
   return render_template('index.html')


if __name__ == '__main__':
   # connect to mongo db
   client = MongoClient('localhost', 27017, username='locobln_mongoroot', password='Start.Mongo!')
   db = client.resource_database
   fs = gridfs.GridFS(db)

   # setup the folder where uploaded videos are going to be stored
   RESOURCE_FOLDER = 'resources'
   app.config['RESOURCE_FOLDER'] = RESOURCE_FOLDER
   # constrain max size of uploads to 50MB 
   app.config['MAX_CONTENT_LENGTH'] = 50 * 10**6

   # start flask
   app.run(host='0.0.0.0', debug=True)

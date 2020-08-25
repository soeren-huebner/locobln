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
         # save the uploaded file to the server via gridfs & read out necessary attributes
         # TODO leave out attribute if the html field was empty
         f = request.files['file']
         fs.put(f,
            filename=f.filename,
            title=request.form['title'],
            author=request.form['author'],
            description=request.form['description'],
            latitude=request.form['latitude'],
            longitude=request.form['longitude'],
            type=request.form['res_type'],            # resource type
         )
         print('INSERTED a document to the collection')
      except Exception as e:
         print(e)

   return 'Finished the file upload.'

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
            'video' : c['video'],
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

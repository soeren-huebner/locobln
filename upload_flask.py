import os
from datetime import datetime as dt

from pymongo import MongoClient

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

# initialise flask
app = Flask(__name__)

@app.route('/upload')
def upload():
   # display the upload web page
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      # TODO generalise to different types of documents
      # save the uploaded file to the server
      f = request.files['file']
      dst = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
      f.save(dst)
      print('[DIR] SAVED video {} to server'.format(f.filename))

      # TODO upload video to youtube
      
      # construct a document for the mongo db
      doc = {
         'title': f.filename,
         'author': 'author',
         'location': (33.3, 44.4),
         'timestamp': dt.timestamp(dt.now()),
         'type': 'video',
         'url': 'https://www.youtube.com',
         'size': 10,
         }
      print('[MONGO DB] CREATED a new document')
      # insert the document into database
      collection.insert_one(doc)
      print('[MONGO DB] INSERTED the document to the collection')

      # delete resource from server
      os.remove(dst)
      print('[DIR] DELETED video {} from server'.format(f.filename))
      
      return 'file uploaded successfully'

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
   
   # start flask
   app.run(host='0.0.0.0', debug=True)

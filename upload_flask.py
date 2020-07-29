import os

from pymongo import MongoClient
client = MongoClient('localhost', 27017, username='locobln_mongoroot', password='Start.Mongo!')
db = client.video_database
collection = db.video_collection

from flask import Flask, render_template, request
from werkzeug import secure_filename
app = Flask(__name__)
UPLOAD_FOLDER = 'videos'

@app.route('/upload')
def upload():
   return render_template('upload.html')
	
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      dst = os.path.join(UPLOAD_FOLDER, secure_filename(f.filename))
      f.save(dst)
      print('video saved')
      
      post = {'title': f.filename}
      return 'file uploaded successfully'

@app.route('/')
def index():
   return render_template('index.html')

		
if __name__ == '__main__':
   app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
   app.config['MAX_CONTENT_LENGTH'] = 50 * 10**6
   app.run(host='0.0.0.0', debug=True)


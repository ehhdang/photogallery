#!flask/bin/python
#docker run --name mariadbtest -e MYSQL_ROOT_PASSWORD=mypass -e MYSQL_DATABASE=mydb -p 3306:3306  -d mariadb

from flask import Flask, jsonify, abort, request, make_response, url_for
from flask import render_template, redirect
import os    
import time
import datetime
import exifread
import json
import boto3  
import pymysql
import sys

app = Flask(__name__, static_url_path="")

UPLOAD_FOLDER = os.path.join(app.root_path,'static','media')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

sys.path.append(os.path.abspath(os.path.join("utils")))
from utils.env import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    BUCKET_NAME,
    DB_HOSTNAME,
    DB_USERNAME,
    DB_PORT,
    DB_PASSWORD,
    DB_NAME,
    TABLE_NAME,
    REGION
)
   
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

def getExifData(path_name):
    f = open(path_name, 'rb')
    tags = exifread.process_file(f)
    ExifData={}
    for tag in tags.keys():
        if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'Filename', 'EXIF MakerNote'):
            #print "Key: %s, value %s" % (tag, tags[tag])
            key="%s"%(tag)
            val="%s"%(tags[tag])
            ExifData[key]=val
    return ExifData

def s3uploading(filename, filenameWithPath):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
                       
    bucket = BUCKET_NAME
    path_filename = "photos/" + filename
    #print path_filename
    s3.upload_file(filenameWithPath, bucket, path_filename)  
    return "http://"+BUCKET_NAME+".s3-website."+REGION+".amazonaws.com/"+ path_filename 
    
@app.route('/', methods=['GET', 'POST'])
def home_page():
    conn = pymysql.connect (host = DB_HOSTNAME,
                        user = DB_USERNAME,
                        passwd = DB_PASSWORD,
                        db = DB_NAME, 
            port = DB_PORT)
    cursor = conn.cursor ()

    items=[]
    try:
        cursor.execute("SELECT * FROM "+DB_NAME+"."+TABLE_NAME+";")
        results = cursor.fetchall()
        
        for item in results:
            photo={}
            photo['PhotoID'] = item[0]
            photo['CreationTime'] = item[1]
            photo['Title'] = item[2]
            photo['Description'] = item[3]
            photo['Tags'] = item[4]
            photo['URL'] = item[5]
            items.append(photo)
    except:
        cursor.execute ("CREATE TABLE IF NOT EXISTS "+DB_NAME+"."+TABLE_NAME+" ( \
            PhotoID int PRIMARY KEY NOT NULL AUTO_INCREMENT, \
            CreationTime TEXT NOT NULL, \
            Title TEXT NOT NULL, \
            Description TEXT NOT NULL, \
            Tags TEXT NOT NULL, \
            URL TEXT NOT NULL,\
            EXIF TEXT NOT NULL\
            );")
    
    
    conn.close()        
    print(items)
    return render_template('index.html', photos=items)

@app.route('/add', methods=['GET', 'POST'])
def add_photo():
    if request.method == 'POST':    
        uploadedFileURL=''
        file = request.files['imagefile']
        title = request.form['title']
        tags = request.form['tags']
        description = request.form['description']

        print(title,tags,description)
        if file and allowed_file(file.filename):
            filename = file.filename
            filenameWithPath = os.path.join(UPLOAD_FOLDER, filename)
            print(filenameWithPath)
            file.save(filenameWithPath)            
            uploadedFileURL = s3uploading(filename, filenameWithPath);
            ExifData=getExifData(filenameWithPath)
            print(ExifData)            
            ts=time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

            conn = pymysql.connect (host = DB_HOSTNAME,
                        user = DB_USERNAME,
                        passwd = DB_PASSWORD,
                        db = DB_NAME, 
            port = DB_PORT)
            cursor = conn.cursor ()
            statement = "INSERT INTO "+DB_NAME+"."+TABLE_NAME+" (CreationTime,Title,Description,Tags,URL,EXIF) VALUES ("+\
                    "'"+str(timestamp)+"', '"+\
                    title+"', '"+\
                    description+"', '"+\
                    tags+"', '"+\
                    uploadedFileURL+"', '"+\
                    json.dumps(ExifData)+"');"
            
            print(statement)
            result = cursor.execute(statement)
            conn.commit()
            conn.close()

        return redirect('/')
    else:
        return render_template('form.html')


@app.route('/<int:photoID>', methods=['GET'])
def view_photo(photoID):    
    conn = pymysql.connect (host = DB_HOSTNAME,
                        user = DB_USERNAME,
                        passwd = DB_PASSWORD,
                        db = DB_NAME, 
            port = DB_PORT)
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM "+DB_NAME+"."+TABLE_NAME+" WHERE PhotoID="+str(photoID)+";")
    results = cursor.fetchall()

    items=[]
    for item in results:
        photo={}
        photo['PhotoID'] = item[0]
        photo['CreationTime'] = item[1]
        photo['Title'] = item[2]
        photo['Description'] = item[3]
        photo['Tags'] = item[4]
        photo['URL'] = item[5]
        photo['ExifData']=json.loads(item[6])
        items.append(photo)
    conn.close()        
    tags=items[0]['Tags'].split(',')
    exifdata=items[0]['ExifData']
    
    return render_template('photodetail.html', photo=items[0], tags=tags, exifdata=exifdata)

@app.route('/search', methods=['GET'])
def search_page():
    query = request.args.get('query', None)    
    conn = pymysql.connect (host = DB_HOSTNAME,
                        user = DB_USERNAME,
                        passwd = DB_PASSWORD,
                        db = DB_NAME, 
            port = DB_PORT)
    cursor = conn.cursor ()
    cursor.execute("SELECT * FROM "+DB_NAME+"."+TABLE_NAME+" WHERE Title LIKE '%"+query+ "%' UNION SELECT * FROM "+DB_NAME+"."+TABLE_NAME+" WHERE Description LIKE '%"+query+ "%' UNION SELECT * FROM "+DB_NAME+"."+TABLE_NAME+" WHERE Tags LIKE '%"+query+"%' ;")
    results = cursor.fetchall()

    items=[]
    for item in results:
        photo={}
        photo['PhotoID'] = item[0]
        photo['CreationTime'] = item[1]
        photo['Title'] = item[2]
        photo['Description'] = item[3]
        photo['Tags'] = item[4]
        photo['URL'] = item[5]
        photo['ExifData']=item[6]
        items.append(photo)
    conn.close()        
    print(items)
    return render_template('search.html', photos=items, searchquery=query)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)

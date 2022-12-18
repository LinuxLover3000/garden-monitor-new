from importlib.resources import contents
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import exifread

imagesPath = os.path.relpath("static/images")
imagePrefix = "image"

DATA_INTERVAL = 5 #minutes
IMAGE_INTERVAL = 10 #minutes

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Image():
    images = []
    def __init__(self, path):
        self.path = path
        self.parsePath()
        self.getDateTime()
    def parsePath(self):
        split = os.path.splitext(os.path.split(self.path)[1])
        name = split[0]
        self.ext = split[1]
        i = 0
        while(not name[i:].isdigit()):
            i += 1
        self.number = name[i:]
        self.prefix = name[:i]
    def getDateTime(self):
        tags = exifread.process_file(open(self.path, "rb"))
        self.datetime = datetime.strptime(tags["Image DateTime"].printable, "%Y:%m:%d %H:%M:%S")
    def getImages(path, prefix): #returns array of files if prefix matches
        contents = os.listdir(path)
        Image.images = [Image(os.path.join(path, image)) for image in contents if image[:len(prefix)] == prefix]
    def getMostRecent(): #sort list by datetime
        dates = [image.datetime for image in Image.images]
        mostRecentDate = max(dates)
        mostRecentImage = Image.images[dates.index(mostRecentDate)]
        return mostRecentImage
        #return Image.images[len(Image.images)]

class Data(db.Model):    
    humidity = db.Column(db.Float, nullable = False)
    temperature = db.Column(db.Float, nullable = False)
    time = db.Column(db.DateTime)
    id = db.Column(db.Integer, primary_key = True)

    def __repr__(Self):
        return "<Data " + Self.id + ">"

@app.route("/")
def index():
    Image.getImages(imagesPath, imagePrefix)
    image = Image.getMostRecent()
    d = Data.query.paginate()
    return render_template("index.html", img = image, data=d.query.get(d.total)) #sends most recent record

@app.route("/webcam/")
def webcam():
    Image.getImages(imagesPath, imagePrefix)
    nextDateTime = Image.getMostRecent().datetime + timedelta(minutes = IMAGE_INTERVAL)
    return render_template("webcam.html", imgs = Image.images, nextDT = nextDateTime)

@app.route("/data/")
def data():
    d = Data.query.all()
    nextDateTime = d[len(d) - 1].time + timedelta(minutes = DATA_INTERVAL)
    return render_template("data.html", data = d, nextDT = nextDateTime) #sends all records

if __name__ == "__main__":
    app.run(debug = True)
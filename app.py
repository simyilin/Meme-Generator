from flask import Flask, render_template, request
from flickrapi import FlickrAPI
import urllib.request
import os, shutil, datetime
from PIL import Image, ImageDraw, ImageFont

# To Do: Code cleanup, animations and testing

app = Flask(__name__)

FLICKR_PUBLIC = '58828f5f5d114133ebc1d053cca2028c'
FLICKR_SECRET = '6ab6621d8cc13c54'

@app.route('/')
def index():
    # remove static/images folder
    if os.path.exists("static/images"):
        shutil.rmtree("static/images")
    # re-create static/images folder
    os.makedirs("static/images")
    
    return render_template("index.html")

@app.route('/picture')
def picture():
    # use GET to obtain search keyword and number of pics to load
    keyword = request.args.get('keyword')
    pageNo = (request.args.get('page') or 1)

    # output images that match keyword
    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    extras='url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    fetchData = flickr.photos.search(text=keyword, page=pageNo, per_page=10, extras=extras)
    photos = fetchData['photos']['photo']
    
    data = {
        "keyword": keyword,
        "photos": photos,
        "page": str(pageNo)
    }
    return render_template("picture.html", **data)

@app.route('/text')
def text():
    # check if there is a valid photo id
    if not request.args.get('photoID'):
        return render_template("picture.html")

    keyword = request.args.get('keyword')

    # use GET to obtain photo id
    photoID = request.args.get('photoID')
    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    fetchData = flickr.photos.getSizes(photo_id=photoID)
    # '6' is the Medium photo option
    sourceURL = fetchData["sizes"]["size"][6]["source"]
    # use timeStamp to prevent caching
    timeStamp = str(datetime.datetime.now().microsecond)
    path = 'static/images/' + photoID + timeStamp + '.jpg'
    # download image
    urllib.request.urlretrieve(sourceURL, path)
    # find out size of image and limit text input length
    path = 'static/images/' + photoID + timeStamp + '.jpg'
    image = Image.open(path) 
    width, height = image.size
    limit = int(width/45)

    data = {
        "photoID": photoID,
        "path": path,
        "timeStamp": timeStamp,
        "keyword": keyword, 
        "limit": limit
    }
    return render_template("text.html", **data)

@app.route('/result')
def result():
    # use GET to obtain text and photoID
    photoID = request.args.get('photoID')
    textColor = request.args.get('color')
    textPosition = request.args.get('position')
    text = request.args.get('text')
    timeStamp = request.args.get('timeStamp')

    # add text to the image using python pillow module
    path = 'static/images/' + photoID + timeStamp + '.jpg'
    image = Image.open(path) 
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', size=45)
    
    width, height = image.size
    w, h = draw.textsize(text, font=font)
    # default to position top
    (x, y) = ((width / 2) - (w/2), 25)

    if textPosition == "middle":
        y = (height / 2) - (h/2)
    elif textPosition == "bottom":
        y = height - h - 25
    
    draw.text((x, y), text, fill=textColor, font=font)

    image = image.convert('RGB')
    path = 'static/images/' + photoID + timeStamp + 'edited.jpg'
    image.save(path)

    data = {
        "path": path
    }
    return render_template("result.html", **data)

if __name__ == '__main__':
   app.run(debug=True)
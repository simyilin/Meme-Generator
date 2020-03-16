from flask import Flask, render_template, request
from flickrapi import FlickrAPI
import urllib.request
import os, shutil, datetime
import textwrap
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
port = int(os.environ.get('PORT', 5000))

FLICKR_PUBLIC = '58828f5f5d114133ebc1d053cca2028c'
FLICKR_SECRET = '6ab6621d8cc13c54'

@app.route('/index')
def index():
    # remove static/images folder
    if os.path.exists("static/images"):
        shutil.rmtree("static/images")
    # re-create static/images folder
    os.makedirs("static/images")
    
    return render_template("index.html")

@app.route('/picture')
def picture():
    # use GET to obtain search keyword and page number (if available)
    keyword = request.args.get('keyword')
    pageNo = (request.args.get('page') or 1)

    # output images that match keyword
    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    # fetches data using Flickr API
    fetchData = flickr.photos.search(text=keyword, page=pageNo, per_page=10, extras='url_q')
    photos = fetchData['photos']['photo']
    
    data = {
        "keyword": keyword,
        "photos": photos,
        "page": str(pageNo)
    }
    return render_template("picture.html", **data)

@app.route('/text')
def text():
    # use GET to obtain photo id and keyword
    photoID = request.args.get('photoID')
    keyword = request.args.get('keyword')
    # use Flickr API to obtain image static url
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
    image = Image.open(path) 
    width, height = image.size
    limit = int(width/45)

    data = {
        "photoID": photoID,
        "keyword": keyword,
        "path": path,
        "timeStamp": timeStamp,
        "limit": limit
    }
    return render_template("text.html", **data)

@app.route('/result')
def result():
    # use GET to obtain photoID, keyword and timeStamp
    photoID = request.args.get('photoID')
    keyword = request.args.get('keyword')
    timeStamp = request.args.get('timeStamp')
    # use GET to meme text and text settings
    text = request.args.get('text')
    textColor = request.args.get('color')
    textPosition = request.args.get('position')

    # add text to the image using python pillow module
    path = 'static/images/' + photoID + timeStamp + '.jpg'
    image = Image.open(path) 
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('static/Anton-Regular.ttf', size=45)
    
    width, height = image.size
    w, h = draw.textsize(text, font=font)
    limit = int(width/30)

    # text position settings, default to position of top
    (x, y) = ((width / 2), 25)
    if textPosition == "middle":
        y = (height / 2) - (h/2)
    elif textPosition == "bottom":
        additionalOffset = w / width * h
        y = height - h - additionalOffset - 25    
    
    # wrap text
    for line in textwrap.wrap(text, width=limit):  
        x = (width / 2) - (font.getsize(line)[0]/2 )
        draw.text((x, y), line, font=font, fill=textColor)
        y += font.getsize(line)[1]

    # converts image to 'RGB' format and saves it
    image = image.convert('RGB')
    path = 'static/images/' + photoID + timeStamp + 'edited.jpg'
    image.save(path)

    data = {
        "path": path,
        "keyword": keyword,
        "photoID": photoID
    }
    return render_template("result.html", **data)

if __name__ == '__main__':
   app.run(debug=True)
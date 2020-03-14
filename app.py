from flask import Flask, render_template, request
from flickrapi import FlickrAPI
import urllib.request
import os, shutil
from PIL import Image, ImageDraw, ImageFont

# To Do: Option to select text color in text.html, 
# allow download of edited image, 
# problem with caching of image (works fine when downloading but caching display)

app = Flask(__name__)

FLICKR_PUBLIC = '58828f5f5d114133ebc1d053cca2028c'
FLICKR_SECRET = '6ab6621d8cc13c54'

@app.route('/')
def index():
    # remove static folder
    if os.path.exists("static"):
        shutil.rmtree("static")
    # re-create static folder
    os.makedirs("static")
    # render template with search bar
    return render_template("index.html")

@app.route('/picture')
def picture():
    # use GET to obtain search keyword
    keyword = request.args.get('keyword')

    # output images that match keyword
    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    extras='url_sq,url_t,url_s,url_q,url_m,url_n,url_z,url_c,url_l,url_o'
    fetchData = flickr.photos.search(text=keyword, per_page=10, extras=extras)
    photos = fetchData['photos']['photo']  
    
    data = {
        "keyword": keyword,
        "photos": photos
    }
    return render_template("picture.html", **data)

@app.route('/text')
def text():
    # use GET to obtain image id
    photoID = request.args.get('photoID')
    flickr = FlickrAPI(FLICKR_PUBLIC, FLICKR_SECRET, format='parsed-json')
    fetchData = flickr.photos.getSizes(photo_id=photoID)
    # 6 is the Medium photo option
    sourceURL = fetchData["sizes"]["size"][6]["source"]
    # download image
    path = 'static/' + photoID + '.jpg'
    urllib.request.urlretrieve(sourceURL, path)
    # option to add in text
    data = {
        "photoID": photoID,
        "fetchData": sourceURL
    }
    return render_template("text.html", **data)

@app.route('/result')
def result():
    # use GET to obtain text and photoID
    photoID = request.args.get('photoID')
    text = request.args.get('text')

    path = 'static/' + photoID + '.jpg'
    image = Image.open(path) 
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('arial.ttf', size=45)
    
    # How to check which font color to use - black or white?
    width, height = image.size
    w, h = draw.textsize(text, font=font)
    (x, y) = ((width / 2) - (w/2), 50)
    color = 'rgb(0, 0, 0)'
    
    draw.text((x, y), text, fill=color, font=font)

    image = image.convert('RGB')
    path = 'static/' + photoID + '.jpg'
    image.save(path)

    data = {
        "path": path
    }
    return render_template("result.html", **data)

if __name__ == '__main__':
   app.run(debug=True)
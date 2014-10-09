'''
Server
'''
from main import find_zips, find_zips_v2, read_shp, geo_json_generator
from flask import Flask
# from flask.ext.mako import MakoTemplates, render_template
from flask import render_template
from flask import request
import json
app = Flask(__name__)
# mako = MakoTemplates(app)

zcta_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_zcta510.shp'
state_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_state.shp'
json_file = '/home/homejoy/Desktop/Hardeep/data/by_state/California.json'

FILE_TO_LOAD = state_file

API_KEY = "AIzaSyA-K0HGkMnxBL6PTHcxh5YmZWZmshbfpbQ"

# read once on start...
# zips, polys = read_shp(FILE_TO_LOAD, limit=50)
geopolys = {}

for district, zipcode, raw in geo_json_generator(json_file, limit=None):
    geopolys[district] = zipcode['geometry']

def decode_line(encoded):
    """
    Decodes a polyline that was encoded using the Google Maps method.

    See http://code.google.com/apis/maps/documentation/polylinealgorithm.html

    This is a straightforward Python port of Mark McClure's JavaScript polyline decoder
    (http://facstaff.unca.edu/mcmcclur/GoogleMaps/EncodePolyline/decode.js)
    and Peter Chng's PHP polyline decode
    (http://unitstep.net/blog/2008/08/02/decoding-google-maps-encoded-polylines-using-php/)

    via http://seewah.blogspot.com/2009/11/gpolyline-decoding-in-python.html
    """

    encoded_len = len(encoded)
    index = 0
    array = []
    lat = 0
    lng = 0

    while index < encoded_len:

        b = 0
        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        shift = 0
        result = 0

        while True:
            b = ord(encoded[index]) - 63
            index = index + 1
            result |= (b & 0x1f) << shift
            shift += 5
            if b < 0x20:
                break

        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        # array.append((lat * 1e-5, lng * 1e-5))
        array.append((lng * 1e-5, lat * 1e-5)) # so we get x, y pairs

    return array

@app.route('/')
def hello():
    # zips, polys = read_shp(FILE_TO_LOAD, limit=5)
    # first = polys[polys.keys()[0]][0]
    # sx = first.centroid.x
    # sy = first.centroid.y

    # last = polys[polys.keys()[-1]][0]
    # ex = last.centroid.x
    # ey = last.centroid.y

    first = geopolys[geopolys.keys()[0]][0]
    sx = first.centroid.x
    sy = first.centroid.y

    last = geopolys[geopolys.keys()[-1]][0]
    ex = last.centroid.x
    ey = last.centroid.y

    return render_template('index.html', API_KEY=API_KEY, sx=sx, sy=sy, ex=ex, ey=ey)

@app.route('/query')
def query():
    '''
    Expects query variables:
        float : p1x (longitute)
        float : p1y (latitude)
        float : p2x (longitute)
        float : p2y (latitude)
    '''
    p1x = float(request.args.get("p1x"))
    p1y = float(request.args.get("p1y"))
    p2x = float(request.args.get("p2x"))
    p2y = float(request.args.get("p2y"))

    result = find_zips([p1x, p1y], [p2x, p2y], polys)

    # get a dictionary of zipcode -> exterior shape of matching zipcodes
    matches = {k:v for k,v in polys.iteritems() if k in result}
    asCoords = {}

    for k, v in matches.iteritems():
        asCoords[k] = []
        for shape in v:
            asCoords[k].append(list(shape.exterior.coords))

    return json.dumps(asCoords)

@app.route('/queryv2')
def queryv2():
    polyline = str(request.args.get("polyline"))

    coords = decode_line(polyline)

    print 'decoded:', coords

    result = find_zips_v2(coords, polys)

    # get a dictionary of zipcode -> exterior shape of matching zipcodes
    matches = {k:v for k,v in polys.iteritems() if k in result}
    asCoords = {}

    for k, v in matches.iteritems():
        asCoords[k] = []
        for shape in v:
            asCoords[k].append(list(shape.exterior.coords))

    return json.dumps(asCoords)

@app.route('/queryv3')
def queryv3():
    polyline = str(request.args.get("polyline"))

    coords = decode_line(polyline)

    print 'decoded:', coords

    result = find_zips_v2(coords, geopolys)

    # get a dictionary of zipcode -> exterior shape of matching zipcodes
    matches = {k:v for k,v in geopolys.iteritems() if k in result}
    asCoords = {}

    for k, v in matches.iteritems():
        asCoords[k] = []
        for shape in v:
            try:
                asCoords[k].append(list(shape.exterior.coords))
            except:
                # skipping complex zip codes...
                continue

    return json.dumps(asCoords)

if __name__ == "__main__":
    app.debug = True
    app.template_folder = "templates"
    app.run()
'''
Goal:
Read in shp files of areas, plot (straight?) line from point A to B, find all
intersecting polygons along path.
'''

import fiona
import geojson

from shapely.geometry import asShape, shape, Polygon, LineString
from shapely.ops import cascaded_union

zcta_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_zcta510.shp'
test_file = '/home/homejoy/Desktop/Hardeep/data/test.shp'
json_file = '/home/homejoy/Desktop/Hardeep/data/by_state/California.json'

properties = [
    "ZCTA5CE10",    # "95832"         2010 Census 5-digit ZIP Code Tabulation Area code
    "GEOID10",      # "95832"         2010 Census 5-digit ZIP Code Tabulation Area identifier, 2010 Census 5-digit ZIP Code Tabulation Area code
    "CLASSFP10",    # "B5"            2010 Census Federal Information Processing Standards (FIPS) 55 class code (B5 = Five-digit ZCTA)
    "MTFCC10",      # "G6350"         MAF/TIGER feature class code, (G6350 = ZIP Code Tabulation Area (5-digit))
    "FUNCSTAT10",   # "S"             2010 Census functional status (S = Statistical entity)
    # "ALAND10",      # 21414053.0      2010 Census land area (square meters) (0 to 9,999,999,999,999 = Blank)
    "AWATER10",     # 1511680.0       2010 Census water area (square meters) (0 to 9,999,999,999,999 = Blank)
    "INTPTLAT10",   # "+38.4470502"   2010 Census latitude of the internal point (00 = Blank)
    "INTPTLON10",   # "-121.4961141"  2010 Census latitude of the internal point (00 = Blank)
]

state_properties = [
    "REGION",
    "DIVISION",
    "STATEFP",
    "STATENS",
    "GEOID",
    "STUSPS",
    "NAME",
    "LSAD",
    "MTFCC",
    "FUNCSTAT",
    "ALAND",
    "AWATER",
    "INTPTLAT",
    "INTPTLON"
]

def geo_json_generator(_file, limit=None, is_state_file=False, raw_coords=False):
    with open(_file, 'r') as src:
        gj = geojson.load(src)

        count = 0
        while True:
            if limit is not None and count >= limit:
                break

            if count < len(gj):
                zipcode = gj[count]
            else:
                break

            count += 1
            if count % 500 == 0:
                print count

            temp = None
            if zipcode:
                if not is_state_file:
                    zipcode['id'] = zipcode['properties']['ZCTA5CE10']
                else:
                    zipcode['id'] = zipcode['properties']['NAME']

                district = zipcode['id']

                if temp:
                    continue
                else:
                    if raw_coords:
                        raw = zipcode['geometry']
                    else:
                        raw = []

                    polygon = shape(zipcode['geometry'])
                    zipcode['geometry'] = [polygon.simplify(0.0003, preserve_topology=True)]

                    temp = zipcode

                    yield (district, zipcode, raw)
            else:
                break

def shp_generator(_file, limit=None, is_state_file=False, raw_coords=False):
    global properties

    with fiona.open(_file, 'r') as source:

        count = 0
        while True:
            if limit is not None and count >= limit:
                break

            count += 1
            if count % 500 == 0:
                print count

            zipcode = source.next()
            temp = None
            if zipcode:
                if not is_state_file:
                    zipcode['id'] = zipcode['properties']['ZCTA5CE10']
                else:
                    zipcode['id'] = zipcode['properties']['NAME']

                district = zipcode['id']

                if temp:
                    continue
                else:
                    if raw_coords:
                        raw = zipcode['geometry']
                    else:
                        raw = []

                    polygon = shape(zipcode['geometry'])
                    zipcode['geometry'] = polygon.simplify(0.0003, preserve_topology=True)

                    temp = zipcode

                    yield (district, zipcode, raw)
            else:
                break

def read_shp(_file, limit=None, is_state_file=False):
    '''
    Read in the given SHP file, and return a tuple with two dictionaries.

    The first, mapping coordinate IDs from the file to their zip codes.
    The second, zip codes to shape objects.
    '''
    global properties

    ZIPS = {}
    GEOJSON = {}
    POLYGONS = {}

    with fiona.open(_file, 'r') as source:

        count = 0
        while True:
            if limit is not None and count >= limit:
                break

            count += 1
            if count % 500 == 0:
                print count

            zipcode = source.next()
            temp = None
            if zipcode:
                if not is_state_file:
                    zipcode['id'] = zipcode['properties']['ZCTA5CE10']
                else:
                    zipcode['id'] = zipcode['properties']['NAME']

                district = zipcode['id']
                ZIPS[district] = zipcode['id']

                if temp:
                    if not (district) in GEOJSON:
                        GEOJSON[district] = []
                    GEOJSON[district].append(temp)

                else:
                    if not is_state_file:
                        zipcode['properties']['ZIP'] = zipcode['properties']['ZCTA5CE10']

                        for prop in properties:
                            del zipcode['properties'][prop]
                    else:
                        for prop in state_properties:
                            del zipcode['properties'][prop]

                    polygon = shape(zipcode['geometry'])

                    if not (district) in POLYGONS:
                        POLYGONS[district] = []
                    POLYGONS[district].append(polygon)

                    zipcode['geometry'] = polygon.simplify(0.0003, preserve_topology=True)
                    temp = zipcode

                    if not (district) in GEOJSON:
                        GEOJSON[district] = []
                    GEOJSON[district].append(zipcode)
            else:
                break

    return (ZIPS, POLYGONS)

def find_zips(p1, p2, ZIP_DICT):
    '''
    Given a line from point p1, to point p2, return a list of all zipcodes that
    we encounter along the path. No order gaurantee.

    ZIP_DICT in format:
    {
        'zipcode': [shape1, shape2, ...],
        ...
    }
    '''
    line = [p1, p2]
    s_line = LineString(line)

    o = []

    for zip_, shape_list in ZIP_DICT.iteritems():
        for shape_ in shape_list:

            if shape_.intersects(s_line):
                o.append(zip_)

    return o

def find_zips_v2(coords, ZIP_DICT):
    '''
    Given a list of coordinate pairs representing a line, return a list of all
    zipcodes that we encounter along the path. No order gaurantee.

    ZIP_DICT in format:
    {
        'zipcode': [shape1, shape2, ...],
        ...
    }
    '''
    s_line = LineString(coords)

    o = []

    for zip_, shape_list in ZIP_DICT.iteritems():
        for shape_ in shape_list:

            if shape_.intersects(s_line):
                o.append(zip_)

    return o
"""
zipjoy: Script to generate per district zip code boundary files in geoJSON and topoJSON

On Ubuntu:
1) Install GCC, Python dev extensions, GDAL
    sudo apt-get install gcc python-dev libgdal1-dev

For libgdal1-dev, version has to be >=1.9.2, use ppa if necesarry:
    sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable)

2) Install Python libs:
    pip Install fiona shapely geojson fabric

3) Download Zip-Code Tabulation Area (ZCTA) Shape files from the US Census Bureau.
    ftp://ftp2.census.gov/geo/tiger/TIGER2013/ZCTA5/

"""
from fabric.api import local, puts
import fiona
import geojson
from shapely.geometry import asShape, shape, Polygon
from shapely.ops import cascaded_union
import sys

config_path = '/home/sid/code/homejoy/homejoy'
# zcta_file = '/home/sid/Downloads/tl_2013_us_zcta510/tl_2013_us_zcta510.shp'
# output_path = '/home/sid/code/homejoy/zipjoy'

zcta_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_zcta510.shp'
output_path = '/home/homejoy/Desktop/Hardeep/out'

# sys.path.append(config_path)
# from config import DISTRICT_CONFIGS

# Total zip codes = 33144
# Properties included in ZCTA files
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

# DISTRICT_ZIPS = {}
# DISTRICT_ZIP_GEOJSON = {}
# DISTRICT_POLYGON_GEOJSON = {}

# for key, value in DISTRICT_CONFIGS.iteritems():
#     DISTRICT_ZIPS[key] = set(value['zips'])
#     DISTRICT_ZIP_GEOJSON[key] = []
#     DISTRICT_POLYGON_GEOJSON[key] = []

count = 0
with fiona.open(zcta_file, 'r') as source:
    while (True):
        count += 1
        if count%5000 == 0: print count

        zipcode = next(source, None)
        temp = None
        if zipcode:
            zipcode['id'] = zipcode['properties']['ZCTA5CE10']
            for district, zip_list in DISTRICT_ZIPS.iteritems():

                if zipcode['id'] in zip_list:
                    # This is so that we don't have to calculate the same zip polygon twice
                    if temp:
                        DISTRICT_ZIP_GEOJSON[district].append(temp)
                    else:
                        zipcode['properties']['ZIP'] = zipcode['properties']['ZCTA5CE10']
                        for prop in properties:
                            del zipcode['properties'][prop]

                        polygon = shape(zipcode['geometry'])

                        DISTRICT_POLYGON_GEOJSON[district].append(polygon)
                        zipcode['geometry'] = polygon.simplify(0.0003, preserve_topology=True)
                        temp = zipcode
                        DISTRICT_ZIP_GEOJSON[district].append(zipcode)
        else:
            break


local('mkdir -p {0}/geojson'.format(output_path))
local('mkdir -p {0}/topojson'.format(output_path))


for district, polygons in DISTRICT_POLYGON_GEOJSON.iteritems():

    district_polygon = cascaded_union(polygons)
    filename = 'district_' + district.lower().replace(' ','_')

    with open('{0}/geojson/{1}.geojson'.format(output_path, filename), 'w') as sink:
        geojson.dump(district_polygon, sink, indent=None)

    local ('topojson -o {0}/topojson/{1}.topojson {0}/geojson/{1}.geojson -p'.format(output_path, filename))


for district, zip_geojson in DISTRICT_ZIP_GEOJSON.iteritems():

    zip_code_layer = {
        "type": "FeatureCollection",
        "features": zip_geojson,
    }
    filename = 'zips_' + district.lower().replace(' ','_')

    with open('{0}/geojson/{1}.geojson'.format(output_path, filename), 'w') as sink:
        geojson.dump(zip_code_layer, sink, indent=None)

    local ('topojson -o {0}/topojson/{1}.topojson {0}/geojson/{1}.geojson -p'.format(output_path, filename))

    puts('{0}\t\t...done'.format(filename))


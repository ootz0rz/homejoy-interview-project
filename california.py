'''
Get california zip codes only...
'''
import os
import json
from main import read_shp, shp_generator

zcta_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_zcta510.shp'
state_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_state.shp'

out_folder = '/home/homejoy/Desktop/Hardeep/data/by_state/'

szips, spolys = read_shp(state_file, limit=50, is_state_file=True)

state_filter = ['California']

matching_zips = {}

# If we're going to do multiple states...probably faster to switch around the loops and stop
# after a state matching the zipcode is found. Alternatively, keep a list of matched zipcodes
# and don't re-visit them for each different state...
for state, shape_list in {k:v for k,v in spolys.iteritems() if k in state_filter}.iteritems():
    print 'Finding zipcodes for...', state

    matching_zips[state] = []

    # intersect all the things...
    found = 0
    for cur_shape in shape_list:
        for zip_, zip_data, raw in shp_generator(zcta_file, limit=None, raw_coords=True):
            zip_shape = zip_data['geometry']

            if cur_shape.intersects(zip_shape):
                # print zip_

                # geoJSON Format
                # http://geojson.org/
                matching_zips[state].append({
                    'type': zip_data['type'],
                    'geometry': raw,
                    'properties': dict(zip_data['properties'])
                })
                found += 1
                # break
    print "Found %s matches" % found

print "DONE!"

# finally dump it all to a file...
for state in state_filter:
    full_path = os.path.join(out_folder, state + '.json')

    with open(full_path, 'w') as sink:
        json.dump(matching_zips[state], sink)
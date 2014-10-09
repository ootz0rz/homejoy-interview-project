from main import find_zips, read_shp
from shapely.geometry import asShape, shape, Polygon, LineString

zcta_file = '/home/homejoy/Desktop/Hardeep/data/tl_2013_us_zcta510.shp'

class Tests(object):

    def setup(self):
        po1 = [(1,1), (2,2), (1,3), (1,4), (3,3), (3,1), (1,1)]
        po2 = [(1,4), (1,5), (3,4), (3,3), (1,4)]
        po3 = [(3,1), (3,3), (5,5), (7,3), (5,1), (3,1)]

        ZIPS = {
            '1': [shape({'type': 'polygon', 'coordinates': [po1]})],
            '2': [shape({'type': 'polygon', 'coordinates': [po2]})],
            '3': [shape({'type': 'polygon', 'coordinates': [po3]})]
        }

        self.ZIPS = ZIPS

    def test_no_intersect(self):
        result = find_zips([0, 10], [10, 10], self.ZIPS)
        assert len(result) == 0, "Should not have any intersections"

    def test_intersect_3_1_outside_start(self):
        result = find_zips([10, 5], [0, 0], self.ZIPS)

        assert len(result) == 2, "Should have 2 intersections"
        assert '3' in result, "Should intersect with area 3"
        assert '1' in result, "Should intersect with area 1"

    def test_intersect_3_1_inside_start(self):
        result = find_zips([5, 3], [0, 0], self.ZIPS)

        assert len(result) == 2, "Should have 2 intersections"
        assert '3' in result, "Should intersect with area 3"
        assert '1' in result, "Should intersect with area 1"

    def test_intersect_3_inside_only(self):
        result = find_zips([5, 3], [5, 2], self.ZIPS)

        assert len(result) == 1, "Should have 1 intersections"
        assert '3' in result, "Should intersect with area 3"

    def test_intersect_3_outside_start(self):
        result = find_zips([10, 5], [5, 2], self.ZIPS)

        assert len(result) == 1, "Should have 1 intersections"
        assert '3' in result, "Should intersect with area 3"

    def test_line_along_edge_3(self):
        result = find_zips([5, 5], [7, 3], self.ZIPS)

        assert len(result) == 1, "Should have 1 intersections"
        assert '3' in result, "Should intersect with area 3"

    def test_line_inside_concave_no_intersect(self):
        result = find_zips([1, 2], [1.1, 2], self.ZIPS)

        assert len(result) == 0, "Should have 0 intersections"

    def test_line_inside_concave_1_intersect(self):
        result = find_zips([1, 2], [2, 2], self.ZIPS)

        assert len(result) == 1, "Should have 1 intersections"
        assert '1' in result, "Should intersect with area 1"

    def test_first_few(self):
        zips, polys = read_shp(zcta_file, limit=15)
        first = polys[polys.keys()[0]][0]
        sx = first.centroid.x
        sy = first.centroid.y

        last = polys[polys.keys()[-1]][0]
        ex = last.centroid.x
        ey = last.centroid.y

        result = find_zips([sx, sy], [ex, ey], polys)
        assert len(result) >= 2, "Should intersect at least the two zip codes whose centroids we're using"

        import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    import nose
    nose.main()
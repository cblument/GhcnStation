import unittest
import geojson

from station import GhcnStation

class TestValidGhcnStationLine(unittest.TestCase):
    def setUp(self):
        self.station = GhcnStation()
        self.valid_line_with_newline = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196\n'
        self.valid_line_without_newline = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196'
        self.invalid_line = 'AE000041196  25.3330 55.5170 34.0    SHARJAH INTER. AIRP            GSN     41196\n'
    
    def tearDown(self):
        self.station = None

    def test_valid_line_with_newline(self):
        result = self.station.valid_station_line_length(self.valid_line_with_newline) 
        self.assertTrue(result)

    def test_valid_line_without_newline(self):
        print self.valid_line_without_newline
        result = self.station.valid_station_line_length(self.valid_line_without_newline)
        self.assertTrue(result)

    def test_invalid_line(self):
        result = self.station.valid_station_line_length(self.invalid_line) 
        self.assertFalse(result)

class TestParseLine(unittest.TestCase):
    def setUp(self):
        self.station = GhcnStation()
        self.line_positive_latitude = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196'
        self.line_negative_latitude = 'ZI000067865 -18.9330   29.8330 1215.0    KWEKWE                                 67865'
        self.line_positive_longitude = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196'
        self.line_negative_longitude = 'ACW00011647  17.1333  -61.7833   19.2    ST JOHNS                                    '
        self.line_missing_elevation = 'UZM00038592  40.9000   69.4000 -999.9    TUAYBUGUZ                              38592'
        self.line_with_state = 'USC00410420  30.2833  -97.7333 -999.9 TX AUSTIN                                      '
        self.line_missing_state = 'UZM00038592  40.9000   69.4000 -999.9    TUAYBUGUZ                              38592'

    def tearDown(self):
        self.station = None

    def test_parse_fips_country_code(self):
        result = self.station.parse_fips_country_code(self.line_positive_latitude)
        self.assertEqual(result, 'ae')

    def test_valid_network_code(self):
        valid_codes = ['0', '1', 'c', 'e', 'm', 'n', 'r', 's', 'w']
        result = self.station.parse_network_code(self.line_positive_latitude)
        self.assertIn(result, valid_codes)

    def test_invalid_network_code(self):
        result = self.station.parse_network_code('DDDDDDDD')
        self.assertIsNone(result)

    def test_station_id(self):
        result = self.station.parse_station_id(self.line_positive_latitude)
        self.assertEqual(result, '00041196')

    def test_parse_latitude_postive(self):
        result = self.station.parse_latitude(self.line_positive_latitude)
        self.assertEqual(result, 25.333)

    def test_parse_latitude_negative(self):
        result = self.station.parse_latitude(self.line_negative_latitude)
        self.assertEqual(result, -18.933)

    def test_parse_longitude_positive(self):
        result = self.station.parse_longitude(self.line_positive_longitude)
        self.assertEqual(result, 55.517)

    def test_parse_longitude_negative(self):
        result = self.station.parse_longitude(self.line_negative_longitude)
        self.assertEqual(result, -61.7833)

    def test_parse_elevation(self):
        result = self.station.parse_elevation(self.line_positive_latitude)
        self.assertEqual(result, 34.0)

    def test_parse_missing_elevation(self):
        result = self.station.parse_elevation(self.line_missing_elevation)
        self.assertIsNone(result)

    def test_parse_line_with_state(self):
        result = self.station.parse_state(self.line_with_state)
        self.assertEqual(result, 'TX')

    def test_parse_line_without_state(self):
        result = self.station.parse_state(self.line_missing_state)
        self.assertIsNone(result)

    def test_parse_name(self):
        result = self.station.parse_name(self.line_positive_latitude)
        self.assertEqual(result, 'Sharjah Inter. Airp')

    def test_set_station_data_from_line(self):
        # Does this need to be tested?
        pass

class TestGeoJsonFeature(unittest.TestCase):
    def setUp(self):
        self.station = GhcnStation()
        self.line_positive_latitude = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196'
        self.line_negative_latitude = 'ZI000067865 -18.9330   29.8330 1215.0    KWEKWE                                 67865'
        self.line_positive_longitude = 'AE000041196  25.3330   55.5170   34.0    SHARJAH INTER. AIRP            GSN     41196'
        self.line_negative_longitude = 'ACW00011647  17.1333  -61.7833   19.2    ST JOHNS                                    '
        self.line_missing_elevation = 'UZM00038592  40.9000   69.4000 -999.9    TUAYBUGUZ                              38592'
        self.line_with_state = 'USC00410420  30.2833  -97.7333 -999.9 TX AUSTIN                                      '
        self.line_missing_state = 'UZM00038592  40.9000   69.4000 -999.9    TUAYBUGUZ                              38592'

    def test_feature_has_geometry_without_elevation(self):
        self.station.set_station_data_from_line(self.line_positive_latitude)
        result = self.station.to_geojson_feature()
        self.assertIsInstance(result, geojson.Feature)
        self.assertTrue(result.has_key('geometry'))
        self.assertIsNotNone(result['geometry'])
        self.assertEqual(result.geometry.coordinates, [55.517, 25.333, 34.0])

    def test_feature_has_geometry_with_elevation(self):
        self.station.set_station_data_from_line(self.line_missing_elevation)
        result = self.station.to_geojson_feature()
        self.assertTrue(result.has_key('geometry'))
        self.assertIsNotNone(result['geometry'])
        self.assertEqual(result.geometry.coordinates, [69.4, 40.9])

    def test_feature_has_name(self):
        self.station.set_station_data_from_line(self.line_positive_latitude)
        result = self.station.to_geojson_feature()
        self.assertEqual(result.properties.get('name'), 'Sharjah Inter. Airp')

    def test_feature_has_country(self):
        self.station.set_station_data_from_line(self.line_positive_latitude)
        result = self.station.to_geojson_feature()
        self.assertEqual(result.properties.get('country'), 'ae')

    def test_feature_has_state(self):
        self.station.set_station_data_from_line(self.line_with_state)
        result = self.station.to_geojson_feature()
        self.assertEqual(result.properties.get('state'), 'TX')

    def test_feature_does_not_have_state(self):
        self.station.set_station_data_from_line(self.line_positive_latitude)
        result = self.station.to_geojson_feature()
        self.assertIsNone(result.properties.get('state'))

    def test_feature_has_station_id(self):
        self.station.set_station_data_from_line(self.line_positive_latitude)
        result = self.station.to_geojson_feature()
        self.assertEqual(result.properties.get('station_id'), '00041196')

if __name__ == '__main__':
    unittest.main()

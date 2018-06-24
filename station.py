"""Weather station parser for Global Historical Climatology Network (ghcn)"""
import geojson

class GhcnStation(object):
    """Weather station class for Global Historical Climatology Network (ghcn)

    A class that represents the a row from the Global Historical Climatology
    Network. The station file can be found at:
    ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
    The format of the ghcnd-stations.txt file can be found under section IV at:
    ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt
    """

    def __init__(self):
        self.station_id = None
        self.name = None
        self.latitude = None
        self.longitude = None
        self.elevation = None
        self.state = None
        self.country = None

    def set_station_data_from_line(self, line):
        """Sets station data from line of ghcnd-stations.txt file"""
        if self.valid_station_line_length(line):
            self.station_id = self.parse_station_id(line)
            self.name = self.parse_name(line)
            self.latitude = self.parse_latitude(line)
            self.longitude = self.parse_longitude(line)
            self.elevation = self.parse_elevation(line)
            self.state = self.parse_state(line)
            self.country = self.parse_fips_country_code(line)

    def valid_station_line_length(self, line):
        """Verifies tht the length of the line is correct."""
        length = len(line.rstrip('\n'))
        if length == 85:
            return True
        return False

    def parse_fips_country_code(self, line):
        """Returns the country code from the line."""
        return line[0:2].lower()

    def parse_network_code(self, line):
        """Returns the network code from the line or None if unknown"""
        valid_codes = ['0', '1', 'c', 'e', 'm', 'n', 'r', 's', 'w']
        code = line[2:3].lower()
        if code in valid_codes:
            return code
        return None

    def parse_station_id(self, line):
        """Returns the station id from the line."""
        return line[3:11]

    def parse_latitude(self, line):
        """Returns the latitude from the line."""
        return float(line[12:20])

    def parse_longitude(self, line):
        """Returns the longitude from the line."""
        return float(line[21:30])

    def parse_elevation(self, line):
        """Returns the elevation from the line.

        Returns elevation in meters or None if the value from file is -999.9
        """
        elevation = float(line[31:37])
        if elevation == -999.9:
            return None
        return elevation

    def parse_state(self, line):
        """Returns state if present or None"""
        state = line[38:40].upper()
        if state == '  ':
            return None
        return state

    def parse_name(self, line):
        """Returns station name"""
        name = line[41:71].rstrip().title()
        return name

    def to_geojson_feature(self):
        """Converts object to geojson feature"""
        properties = {}
        if self.elevation is None:
            point = geojson.Point((self.longitude, self.latitude))
        else:
            point = geojson.Point((self.longitude, self.latitude, self.elevation))
        properties['name'] = self.name
        properties['country'] = self.country
        properties['station_id'] = self.station_id
        if self.state:
            properties = {'state': self.state}

        feature = geojson.Feature(geometry=point, properties=properties)
        return feature

if __name__ == '__main__':
    import json
    import argparse
    DESCRIPTION = """
    Convert ghcnd-stations.txt to geojson file.  The ghcnd-stations.txt can be
    downloaded from ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('filename', help='filename to convert.')
    args = parser.parse_args()
    features = []
    with open(args.filename, 'r') as f:
        for station_line in f:
            station = GhcnStation()
            station.set_station_data_from_line(station_line)
            features.append(station.to_geojson_feature())
    feature_collection = geojson.FeatureCollection(features)
    print json.dumps(feature_collection, indent=2)

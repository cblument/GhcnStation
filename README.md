# GhcnStation

### Example Usage

Download an almost 9mb txt file and turn it into a 27mb geojson file
```
curl ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt --output /tmp/ghcnd-stations.txt
python station.py /tmp/ghcnd-stations.txt > /tmp/ghcnd-stations.geojson
```
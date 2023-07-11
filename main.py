import datetime
import httpx
import mercantile
from rasterio.features import bounds as featureBounds

if __name__ == "__main__":
    stac_endpoint = "https://earth-search.aws.element84.com/v0/search"
    # http://localhost:5000/tiles/9/248/193?red_band_index=B04&green_band_index=B03&blue_band_index=B02
    uri = 'http://localhost:5000/tiles/9/249/194?red_band_index=B04&green_band_index=B03&blue_band_index=B02'
    # uri = 'http://localhost:5000/tiles/8/124/96?red_band_index=B04&green_band_index=B03&blue_band_index=B02'
    # uri = 'http://localhost:5000/tiles/8/124/95?red_band_index=B04&green_band_index=B03&blue_band_index=B02'
    tokens = uri.split("/")
    tokens = [token.split("?")[0] for token in tokens]
    x = int(tokens[5])
    y = int(tokens[6])
    z = int(tokens[4])
    # x = int(15)
    # y = int(11)
    # z = int(5)
    bbox = mercantile.bounds(x, y, z)
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [min(bbox.east, bbox.west), min(bbox.north, bbox.south)],
                            [max(bbox.east, bbox.west), min(bbox.north, bbox.south)],
                            [max(bbox.east, bbox.west), max(bbox.north, bbox.south)],
                            [min(bbox.east, bbox.west), max(bbox.north, bbox.south)],
                            [min(bbox.east, bbox.west), min(bbox.north, bbox.south)]
                        ]
                    ]
                }
            }
        ]
    }

    bounds = featureBounds(geojson)

    # Date filter
    date_min = "2023-04-11"
    date_max = "2023-07-11"

    start = datetime.datetime.strptime(date_min, "%Y-%m-%d").strftime("%Y-%m-%dT00:00:00Z")
    end = datetime.datetime.strptime(date_max, "%Y-%m-%d").strftime("%Y-%m-%dT23:59:59Z")

    query = {
        "collections": ['sentinel-s2-l2a-cogs'],
        # "query": {
        #     "eo:cloud_cover": {
        #         "lt": 20
        #     },
        #     "sentinel:data_coverage": {
        #         "gt": 80
        #     }
        # },
        "datetime": f"{start}/{end}",
        "intersects": geojson["features"][0]["geometry"],
        "limit": 100,
        "fields": {
          'include': ['properties.datetime'],  # This will limit the size of returned body
          'exclude': ['links']  # This will limit the size of returned body
        },
        "sortby": [
            {
                "field": "properties.datetime",
                "direction": "desc"
            }
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "Accept": "application/geo+json",
    }

    # print(query)
    data = httpx.post(stac_endpoint, headers=headers, json=query).json()
    print(data["context"])
    f = data["features"][0]
    print(f['collection'] + " " + f['properties']['datetime'])
    f = data["features"][len(data["features"])-1]
    print(f['collection'] + " " + f['properties']['datetime'])

import pymongo
from pymongo import GEOSPHERE


class GeographicMongoDB:
    def __init__(self, db_name, container):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.location_database = self.client[db_name]
        self.container = container

        self.location_database[self.container].create_index([("coordinates", GEOSPHERE)])

    def insert_point(self, long, lat, image_path):
        location = {
            "type": "Point",
            "coordinates": [long, lat],
            "image_path": image_path
        }

        self.location_database[self.container].insert_one(location)

    def retrieve_nearest_point(self, long, lat, max_distance=100):
        query = [{
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [long, lat]},
                "distanceField": "distance",
                "maxDistance": max_distance
            }
        },
            {"$sort": {
                "distance": 1
            }
        },
            {"$limit": 1}
        ]

        try:
            return self.location_database[self.container].aggregate(query).next()
        except StopIteration:
            return None


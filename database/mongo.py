import pymongo
from pymongo import GEOSPHERE


class GeographicMongoDB:
    def __init__(self, db_name):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.location_database = self.client[db_name]

        self.location_database.images.create_index([("coordinates", GEOSPHERE)])

    def insert_point(self, long, lat, image_path):
        location = {
            "type": "Point",
            "coordinates": [long, lat],
            "image_path": image_path
        }

        self.location_database.images.insert_one(location)

    def retrieve_nearest_point(self, long, lat, max_distance=100):
        query = [{
            "$geoNear": {
                "near": {"type": "Point", "coordinates": [long, lat]},
                "distanceField": "dist.calculated",
                "maxDistance": max_distance
            }
        }, {"$limit": 1}]

        try:
            return self.location_database.images.aggregate(query).next()
        except StopIteration:
            return None


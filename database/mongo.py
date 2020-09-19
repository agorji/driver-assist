import pymongo
from pymongo import GEOSPHERE


class GeographicMongoDB:
    def __init__(self, db_name):
        self.client = pymongo.MongoClient("localhost", 27017)
        self.location_database = self.client[db_name]

        self.location_database.create_index([("coordinates", GEOSPHERE)])

    def insert_point(self, long, lat, image_name):
        location = {
            "type": "Point",
            "coordinates": [long, lat],
            "name": "sample1"
        }

        self.location_database.insert_one(location)

    def retrieve_nearest_point(self, long, lat, max_distance=100):
        self.location_database.find_one({"coordinates": {"$geoNear": [long, lat], "$maxDistance": max_distance}})


location = {
    "type": "Point",
    "coordinates": [long, lat],
    "name": "sample1"
}

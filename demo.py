from PIL import Image

from database.mongo import GeographicMongoDB
from main import load_exif_data
import matplotlib.pyplot as plt
import cv2 as cv

import time

def draw_plot(image_1_path, image_2_path):
    # print(image_1_path, image_2_path)
    image_1 = cv.imread(image_1_path)
    image_2 = cv.imread(image_2_path)
    cv.imshow("Bad Weather", image_1)
    cv.imshow("Good Weather", image_2)
    cv.waitKey(1)


def plot_similars(directory_path, mongo_database, mongo_container):
    bad_metadata = load_exif_data(directory_path)

    geographic_db = GeographicMongoDB(mongo_database, mongo_container)
    for bad_entry in bad_metadata:
        nearest_point = geographic_db.retrieve_nearest_point(long=bad_entry["longitude"],
                                                             lat=bad_entry["latitude"])
        # print(nearest_point)
        draw_plot(bad_entry["path"], nearest_point["image_path"])
        time.sleep(0.25)


def plot_similars_from_mongo(mongo_database, bad_container, nice_container):
    geographic_db = GeographicMongoDB(mongo_database, nice_container)

    for bad_entry in geographic_db.location_database[bad_container].find():
        bad_long = bad_entry["coordinates"][0]
        bad_lat = bad_entry["coordinates"][1]
        nearest_point = geographic_db.retrieve_nearest_point(long=bad_long,
                                                             lat=bad_lat)
        if nearest_point is not None:
            print(nearest_point["distance"])
            draw_plot(bad_entry["image_path"], nearest_point["image_path"])
        time.sleep(0.1)


if __name__ == '__main__':
    database_name = "karmanUpdated"
    container_name = "nice_weather_thusis_filisur"
    bad_container_name = "bad_weather_thusis_filisur"
    cv.namedWindow("Good Weather", cv.WINDOW_NORMAL)
    cv.resizeWindow("Good Weather", 640, 480)
    cv.namedWindow("Bad Weather", cv.WINDOW_NORMAL)
    cv.resizeWindow("Bad Weather", 640, 480)
    # plot_similars("data/Trackpictures/bad_weather/bad_weather_thusis_filisur_20200829_pixelated",
    #               database_name,
    #               container_name)
    plot_similars_from_mongo(database_name, bad_container_name, container_name)

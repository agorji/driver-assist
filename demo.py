from PIL import Image

from database.mongo import GeographicMongoDB
from main import load_exif_data
import matplotlib.pyplot as plt

import time


def draw_plot(image_1_path, image_2_path):
    print(image_1_path, image_2_path)
    image_1 = Image.open(image_1_path)
    image_2 = Image.open(image_2_path)

    plt.imshow(image_1)
    plt.imshow(image_2)


def plot_similars(directory_path, mongo_database, mongo_container):
    bad_metadata = load_exif_data(directory_path)

    geographic_db = GeographicMongoDB(mongo_database, mongo_container)
    for bad_entry in bad_metadata:
        nearest_point = geographic_db.retrieve_nearest_point(long=bad_entry["longitude"],
                                                             lat=bad_entry["latitude"])
        print(nearest_point)
        draw_plot(bad_entry["path"], nearest_point["image_path"])
        time.sleep(2)


if __name__ == '__main__':
    database_name = "karmanUpdated"
    container_name = "nice_weather_filisur_thusis"
    plot_similars("data/Trackpictures/bad_weather/bad_weather_thusis_filisur_20200829_pixelated",
                  database_name,
                  container_name)

import sys
import time
from PIL import Image

import cv2 as cv
import gpxpy
import numpy as np
import pygame
import utm
import threading

from database.mongo import GeographicMongoDB
from utils.kalman_filter import KalmanFilter

real_fps = 30
target_fps = 30

near_image = None


def image_load_job(image_path):
    global near_image
    near_image = cv.imread(image_path)


if __name__ == '__main__':
    database_name = "kalmanUpdated"
    container_name = "nice_weather_thusis_filisur"
    gpx_file_address = "data/Trackmovies/Thusis_Filisur_20200828/movie - Copy.gpx"
    video_address = "data/Trackmovies/Thusis_Filisur_20200828/movie.mp4"
    cv.namedWindow("Good Weather", cv.WINDOW_NORMAL)
    cv.resizeWindow("Good Weather", 640, 480)
    cv.namedWindow("Bad Weather", cv.WINDOW_NORMAL)
    cv.resizeWindow("Bad Weather", 640, 480)
    clock = pygame.time.Clock()

    geographic_db = GeographicMongoDB(database_name, container_name)

    with open(gpx_file_address) as gpx_file:
        gpx_data = gpxpy.parse(gpx_file)
    video_kalman = KalmanFilter(location_noise=4, speed_noise=3)
    way_points = gpx_data.waypoints
    utm_data = utm.from_latlon(way_points[0].latitude, way_points[0].longitude)
    print(utm_data)
    video = cv.VideoCapture(video_address)
    fake_timestamp = way_points[0].time.timestamp()
    fake_time_start = fake_timestamp
    start_real_time = time.time()
    prev_time = start_real_time
    video_kalman.initialize(np.array([utm_data[0], utm_data[1], 0, 0]).T, np.array([4, 4, 3, 3]).T, start_real_time)
    index = 1
    video.set(1, 100)
    current_image = ""
    while index < len(way_points):
        if fake_timestamp >= way_points[index].time.timestamp():
            if way_points[index].latitude > 0:
                utm_data = utm.from_latlon(way_points[index].latitude, way_points[index].longitude)
                video_kalman.update_estimations(np.array(utm_data[:2]).T)
            print(way_points[index])
            index += 1

        success, image = video.read()
        if not success:
            print("Error in reading video!", file=sys.stderr)
            break
        cv.imshow("Good Weather", image)
        video_kalman.predict_values()
        zone_num, zone_letter = utm_data[2], utm_data[3]
        lat, long = utm.to_latlon(video_kalman.predicted_data[0], video_kalman.predicted_data[1], zone_num, zone_letter)
        nearest_data = geographic_db.retrieve_nearest_point(long, lat)
        if nearest_data is not None:
            # print(nearest_data["distance"])
            if current_image != nearest_data["image_path"]:
                current_image = nearest_data["image_path"]
                threading.Thread(target=image_load_job, args=(current_image,)).start()
        if near_image is not None:
            cv.imshow("Bad Weather", near_image)
        cv.waitKey(1)
        clock.tick(target_fps)
        new_time = time.time()
        current_diff = new_time - prev_time
        print(f'FPS: {1 / current_diff}')
        prev_time = new_time
        time_diff = new_time - start_real_time
        fake_timestamp = fake_time_start + time_diff * 0.98 - current_diff + (1 / target_fps)

from os import listdir
from os.path import isfile, join

from utils.exif_extractor import export_exif_data
from utils.kalman_filter import KalmanFilter

import numpy as np
import utm


def normalize_vec(a):
    norm = np.linalg.norm(a)
    if norm != 0:
        return a / norm

    return a


def load_exif_data(directory_path):
    files_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith(".jpg")]
    files_list.sort()

    metadata = list()
    for file_path in files_list:
        exif_data = export_exif_data(directory_path + "/" + file_path)
        if exif_data is not None:
            metadata.append(exif_data)

    return metadata


def update_using_kalman(kalman: KalmanFilter, metadata):
    last_point = metadata[0]
    last_utm = utm.from_latlon(last_point.get("latitude", None),
                               last_point.get("longitude", None))
    for i, data in enumerate(metadata[1:]):
        if data["time"] != last_point["time"]:
            data_utm = utm.from_latlon(data.get("latitude", None),
                                       data.get("longitude", None))
            if data["speed"] is not None:
                speed_vec = normalize_vec(np.array(data_utm) - np.array(last_utm)) * data["speed"]
                new_data = np.array([data_utm[0], data_utm[1], speed_vec[0], speed_vec[1]]).T
            else:
                new_data = np.array(data_utm).T

            if data["accuracy"] is not None:
                noise_vec = [data["accuracy"] * 0.71, data["accuracy"] * 0.71]
            else:
                noise_vec = None

            kalman.update_estimations(new_data=new_data,
                                      measurement_noise=noise_vec,
                                      estimate_time=data["time"])



def extrapolate_metadata(directory_path):
    metadata = load_exif_data(directory_path)

    # Kalman
    kalman = KalmanFilter()
    initial_image_metadata = metadata[0]
    initial_utm = utm.from_latlon(initial_image_metadata.get("latitude", None),
                                  initial_image_metadata.get("longitude", None))
    init_data = np.array([initial_utm[0], initial_utm[1], 0, 0]).T
    init_noise_vec = np.array([initial_image_metadata.get("accuracy", None),
                               initial_image_metadata.get("accuracy", None),
                               2,
                               2]).T
    kalman.initialize(init_data=init_data,
                      init_noise_vec=init_noise_vec,
                      start_timestamp=initial_image_metadata.get("time", None))


print(load_exif_data(
    "/Users/agorji/Downloads/Dataset_complete/Trackpictures/bad_weather/bad_weather_thusis_filisur_20200829_pixelated"))

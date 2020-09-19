from os import listdir
from os.path import isfile, join

from database.mongo import GeographicMongoDB
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
            exif_data['path'] = directory_path + "/" + file_path
            metadata.append(exif_data)

    return metadata


def update_using_kalman(kalman: KalmanFilter, metadata):
    output_data = []
    last_point = metadata[0]
    last_utm = utm.from_latlon(last_point.get("latitude", None),
                               last_point.get("longitude", None))
    similar_data_count = 1
    for data in metadata[1:]:
        if data["time"] != last_point["time"]:
            data_utm = utm.from_latlon(data.get("latitude", None),
                                       data.get("longitude", None))
            if data["speed"] is not None:
                speed_vec = normalize_vec(np.array([data_utm[0], data_utm[1]]) - np.array(last_utm)) * data["speed"]
                new_data = np.array([data_utm[0], data_utm[1], speed_vec[0], speed_vec[1]]).T
            else:
                new_data = np.array([data_utm[0], data_utm[1]]).T
            last_utm = data_utm[:2]

            if data["accuracy"] is not None:
                noise_vec = [data["accuracy"] * 0.71, data["accuracy"] * 0.71]
            else:
                noise_vec = None

            kalman.update_estimations(new_data=new_data,
                                      measurement_noise=noise_vec,
                                      estimate_time=data["time"])
            last_point = data
            similar_data_count = 1
            predicted_data = kalman.predicted_data
            predicted_utm = predicted_data[:2]
            predicted_lat_lng = utm.to_latlon(predicted_utm[0], predicted_utm[1], data_utm[2], data_utm[3])
            output_data.append({
                'latitude': predicted_lat_lng[0],
                'longitude': predicted_lat_lng[1],
                'path': data['path']
            })
        else:
            new_time = data['time'] + 0.25 * similar_data_count
            data_utm = utm.from_latlon(data.get("latitude", None),
                                       data.get("longitude", None))
            last_utm = data_utm[:2]
            kalman.predict_values(new_time)
            predicted_data = kalman.predicted_data
            predicted_utm = predicted_data[:2]
            predicted_lat_lng = utm.to_latlon(predicted_utm[0], predicted_utm[1], data_utm[2], data_utm[3])
            output_data.append({
                'latitude': predicted_lat_lng[0],
                'longitude': predicted_lat_lng[1],
                'path': data['path']
            })
            similar_data_count += 1
    return output_data


def insert_data_to_mongo(geographic_db, data):
    for entry in data:
        geographic_db.insert_point(long=entry["longitude"],
                                   lat=entry["latitude"],
                                   image_path=entry["path"])


def extrapolate_metadata(directory_path, database_name, mongo_container):
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

    updated_data = update_using_kalman(kalman, metadata)

    geographic_db = GeographicMongoDB(database_name, mongo_container)

    insert_data_to_mongo(geographic_db, updated_data)


if __name__ == '__main__':
    database_name = "karmanUpdated"
    container_name = "nice_weather_filisur_thusis"
    extrapolate_metadata("data/Trackpictures/nice_weather/nice_weather_filisur_thusis_20200824_pixelated",
                         database_name,
                         container_name)
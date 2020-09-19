from os import listdir
from os.path import isfile, join

from utils.exif_extractor import export_exif_data


def load_exif_data(directory_path):
    files_list = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith(".jpg")]

    metadata = list()
    for file_path in files_list:
        metadata.append(export_exif_data(file_path))

    return metadata


def extrapolate_metadata(directory_path):
    metadata = load_exif_data(directory_path)







import exifread
from datetime import datetime


def export_exif_data(image_address):
    with open(image_address, 'rb') as image_file:
        tags = exifread.process_file(image_file, details=False)

    latitude = float(tags['GPS GPSLatitude'].values[0])
    longitude = float(tags['GPS GPSLongitude'].values[0])
    speed = float(tags['GPS GPSSpeed'].values[0]) / 3.6
    accuracy = float(tags['GPS GPSDOP'].values[0])
    time = datetime.strptime(tags['EXIF DateTimeDigitized'].values, '%Y:%m:%d %H:%M:%S').timestamp()

    return latitude, longitude, speed, accuracy, time


from datetime import datetime

import exifread


def export_exif_data(image_address):
    with open(image_address, 'rb') as image_file:
        tags = exifread.process_file(image_file, details=False)

    if "GPS GPSLatitude" not in tags.keys() or "GPS GPSLongitude" not in tags.keys()\
            or "EXIF DateTimeDigitized" not in tags.keys():
        return None
    else:
        latitude = float(tags['GPS GPSLatitude'].values[0])
        longitude = float(tags['GPS GPSLongitude'].values[0])
        time = datetime.strptime(tags['EXIF DateTimeDigitized'].values, '%Y:%m:%d %H:%M:%S').timestamp()

        if 'GPS GPSSpeed' in tags.keys():
            speed = float(tags['GPS GPSSpeed'].values[0]) / 3.6
        else:
            speed = None

        if 'GPS GPSDOP' in tags.keys():
            accuracy = float(tags['GPS GPSDOP'].values[0])
        else:
            accuracy = None

        return {
            'latitude': latitude,
            'longitude': longitude,
            'speed': speed,
            'accuracy': accuracy,
            'time': time
        }

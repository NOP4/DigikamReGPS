import mariadb
import sys
import piexif
from fractions import Fraction

path_prefix = "/path_to/your/photo/files/"

#mode_test = True     #If you want to test with writing to a test.jpg file before updating your real photo files
mode_test = False

# Connect to MariaDB Platform
try:
    conn = mariadb.connect(
        user="digikam_user",
        password="digikam_password",
        host="database ip address",
        port=3306,
        database="digikam"
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)
cur = conn.cursor()


def to_deg(value, loc):
    # FROM https://gist.github.com/c060604/8a51f8999be12fc2be498e9ca56adc72
    """convert decimal coordinates into degrees, munutes and seconds tuple
    Keyword arguments: value is float gps-value, loc is direction list ["S", "N"] or ["W", "E"]
    return: tuple like (25, 13, 48.343 ,'N')
    """
    if value < 0:
        loc_value = loc[0]
    elif value > 0:
        loc_value = loc[1]
    else:
        loc_value = ""
    abs_value = abs(value)
    deg =  int(abs_value)
    t1 = (abs_value-deg)*60
    min = int(t1)
    sec = round((t1 - min)* 60, 5)
    return (deg, min, sec, loc_value)


def change_to_rational(number):
    # FROM https://gist.github.com/c060604/8a51f8999be12fc2be498e9ca56adc72
    """convert a number to rantional
    Keyword arguments: number
    return: tuple like (1, 2), (numerator, denominator)
    """
    f = Fraction(str(number))
    return (f.numerator, f.denominator)

def updateExif(path, filename, latitude, latitudeNumber, longitude, longitudeNumber):
    print(path + "/" + filename)
    exif_dict = piexif.load(path + "/" + filename)

    try:
        tmp = exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
        print("    GPS data available => skipping")
    except:
        print("    No GPS data => update picture")

        lat_deg = to_deg(latitudeNumber, ["S", "N"])
        lng_deg = to_deg(longitudeNumber, ["W", "E"])
        exiv_lat = (change_to_rational(lat_deg[0]), change_to_rational(lat_deg[1]), change_to_rational(lat_deg[2]))
        exiv_lng = (change_to_rational(lng_deg[0]), change_to_rational(lng_deg[1]), change_to_rational(lng_deg[2]))

        print("    " + repr(exiv_lat))
        print("    " + repr(exiv_lng))
        # Latitude
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef] = latitude[-1].encode('UTF-8')
        exif_dict["GPS"][piexif.GPSIFD.GPSLatitude] = exiv_lat
        # Longitude
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef] = longitude[-1].encode('UTF-8')
        exif_dict["GPS"][piexif.GPSIFD.GPSLongitude] = exiv_lng

        exif_bytes = piexif.dump(exif_dict)
        if (mode_test == True):
            piexif.insert(exif_bytes, "test.jpg")
        else:
            piexif.insert(exif_bytes, path + "/" + filename)

cur.execute("SELECT Images.id, AlbumRoots.label, Albums.relativePath, Images.name, ImagePositions.latitude, ImagePositions.latitudeNumber, ImagePositions.longitude, ImagePositions.longitudeNumber FROM ImagePositions INNER JOIN Images ON ImagePositions.imageid = Images.id LEFT JOIN Albums ON Albums.id = Images.album LEFT JOIN AlbumRoots ON AlbumRoots.id = Albums.albumRoot WHERE Images.album IS NOT NULL")

for (imageid, label, relativepath, name, latitude, latitudeNumber, longitude, longitudeNumber) in cur:
    if (name[-4:].lower() == ".jpg"):
        updateExif(path_prefix + label + relativepath, name, latitude, latitudeNumber, longitude, longitudeNumber)

print("END OF GPS TAGGING")


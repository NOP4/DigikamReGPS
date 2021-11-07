# DigikamReGPS

DigikamReGPS is a Python3 script that extracts GPS data from Digikam MariaDB or MySQL database and add the corresponding GPS coordinates to JPG files.
This is usefull when you use Digikam the GPS correlatating functionality.

If GPS coordinatated are already available in the JPG file, nothing is updated.
JPG picture is not recompressed, not any other Exif data updated.

## Configuration
As of now, there is no config file, you need to directy update the Python script with your information:

```
path_prefix = "/path_to/your/photo/files/"
#mode_test = True  #If you want to test with writing to a test.jpg file before updating your real photo files
mode_test = False

conn = mariadb.connect(
    user="digikam_user",
    password="digikam_password",
    host="database ip address",
    port=3306,
    database="digikam"
)
```
    
## Usage
Just execute the script:
`python3 digikamregps.py`

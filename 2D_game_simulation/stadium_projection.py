import math

Teddy_stadium = (31.75123,35.19078,12)
Sammy_Ofer_stadium_before_Nov = (32.783085,34.965336,0) 
Sammy_Ofer_stadium_after_Nov = (32.783053,34.965294,0)
Green_stadium_before_Nov = (32.6901365,35.311345,0)  
Green_stadium_after_Nov = (32.69006,35.31129,0)  
Acre_stadium = (32.90788,35.086034,345)
Ashdod_stadium = (31.81041417,	34.64833117, 3)
Terner_stadium = (31.27339317, 34.77953383, 354)
Netanya_stadium = (32.29449983,	34.864548, 0)
Moshava_stadium = (32.10424417, 34.86504433, 343)
Doha_stadium = (32.866708, 35.310823, 356)
Bloomfield_stadium = (32.051753, 34.761550, 14)


def coordinatesToAxis(lat_origin, lon_origin, lat, lon):
    earthRadius = 6371000
    lat_origin_rad = math.radians(lat_origin)
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lon_origin_rad = math.radians(lon_origin)

    # Equirectangular approximation
    x = (lon_rad - lon_origin_rad) * math.cos(lat_origin_rad) * earthRadius
    y = (lat_rad - lat_origin_rad) * earthRadius
    return x, y

def project_using_2_corners(playerLat, playerLong,stadium):
    """ deprecated, use project_around_pitch_center instead"""
    # Stadium's corners GPS coordinates taken from Google earth and crosscheck with Maccabi Haifa GPS data + Video footage of the game
    upperLeftCornerLat = 32.78354
    upperLeftCornerLong = 34.964993
    lowerRightCornerLat = 32.782597 
    lowerRightCornerLong = 34.965663
    pitch_width = 68.0
    pitch_length = 105.0 

    # Convert origin and player to local XY
    playerX, playerY = coordinatesToAxis(upperLeftCornerLat, upperLeftCornerLong, playerLat, playerLong)
    maxX, maxY = coordinatesToAxis(upperLeftCornerLat, upperLeftCornerLong, lowerRightCornerLat, lowerRightCornerLong)

    # Scale to pitch dimensions
    scaledX = (playerX / maxX) * pitch_width
    scaledY = (playerY / maxY) * pitch_length

    return scaledX, scaledY

def project_around_pitch_center(playerLat,playerLong,stadium):
    lat0,lon0 = stadium[0:2]
    R = 6371000  # Radius of Earth in meters

    # Convert degrees to radians
    lat_rad = math.radians(playerLat)
    lon_rad = math.radians(playerLong)
    lat0_rad = math.radians(lat0)
    lon0_rad = math.radians(lon0)

    x = R * (lon_rad - lon0_rad) * math.cos((lat_rad + lat0_rad) / 2)
    y = R * (lat_rad - lat0_rad)
    if stadium[2] != 0:
        rad = math.radians(stadium[2])
        # Apply rotation matrix for counter-clockwise rotation
        x = x * math.cos(rad) - y * math.sin(rad)
        y = y * math.cos(rad) + x * math.sin(rad)
    return x, y



import math
import serial
import geomag
import pynmea2
from os import listdir
from os.path import isfile, join


def genNextLogFileId():
    """
    Generate the name of the next log file. Checks for the last id of the current log files.
    """
    mypath = "log/"
    allFiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    nextId = 0
    if len(allFiles) > 0:
        # Get the latest id
        for file in allFiles:
            newId = int(file.split(".")[0].split("-")[-1])
            if newId > nextId:
                nextId = newId

    nextId += 1

    return nextId

    
def checkGPSUpdates(sio, gpsData):
    """
    Check if the GPS module has sent any new messages
  
    :param sio: The text wrapped serial connection.
    :param gpsData: A dictionary containing the gps data to be updated.
    """
    # Read data
    line = "1"

    while len(line) > 0:
        try:
            # Get data
            line = sio.readline()
            if len(line) > 0:
                # Parse Messages
                messageName = line[0:6]
                msg = pynmea2.parse(line)
                if messageName == "$GPGGA":
                    gpsData['orthometricHeight'] = msg.altitude
                    gpsData['geoidSeparation'] = float(msg.geo_sep)

                elif messageName == "$GPRMC":
                    gpsData['gpsDatetime'] = msg.datetime
                    gpsData['gpsDatetimeSec'] = msg.datetime.timestamp()
                    gpsData['gpsLatitude'] = msg.latitude
                    gpsData['gpsLongitude'] = msg.longitude
                    gpsData['gpsSpeedOverGround'] = msg.spd_over_grnd


        except serial.SerialException as e:
            print('Device error: {}'.format(e))
            break
        except pynmea2.ParseError as e:
            print('Parse error: {}'.format(e))
            continue
        except Exception as e:
            print(e)
            continue

    
    return gpsData


def parseAccelMag(mag, accel, lat, lon):
    """
    Parse the accelerometer and magnetometer, calculating a heading.

    :param mag:     The magetometer sensor object.
    :param accel:   The accelerometer sensor object.
    :param lat:     The current latitude, to use to calculate the magnetic declination.
    :param lon:     The current longitude, to use to calculate the magnetic declination.
    """
    # Set magnetometer offset
    magOffset = [14.699999999999996, 26.55, -5.324999999999999]

    # Get sensor data
    accels = accel.acceleration
    mags = mag.magnetic

    accx = accels[0]
    accy = accels[1]
    accz = accels[2]
    magx = mags[0] + magOffset[0]
    magy = mags[1] + magOffset[1]
    magz = mags[2] + magOffset[2]

    # Convert in terms of g
    g = 9.81
    gx = accx/g
    gy = accy/g
    gz = accz/g

    # Calculate roll and pitch from accel data
    if abs(gx) > 1:
        gx = math.copysign(1, gx)
    pitch = math.asin(-gx)
    checkVal = gy / math.cos(pitch)
    if(abs(checkVal) <= 1.0):
        roll = math.asin(checkVal)
    else:
        roll = 0


    # Calculate compass heading - compensate for tilt, require pitch, roll from accel
    magNorm = math.sqrt(magx**2 + magy**2 + magz**2)
    mxn = magx/magNorm
    myn = magy/magNorm
    mzn = magz/magNorm

    # Project onto x-y plane
    mx2 = (mxn*math.cos(pitch)) + (mzn*math.sin(pitch))
    my2 = (mxn*math.sin(roll)*math.sin(pitch)) + (myn*math.cos(roll)) - (mzn*math.sin(roll)*math.cos(pitch))
    mz2 = (-mzn*math.cos(roll)*math.sin(pitch)) + (myn*math.sin(roll)) + (mzn*math.cos(roll)*math.cos(pitch))

    # Calc heading
    heading = 0
    if (mx2 > 0 and my2 > 0):
        heading = math.atan(my2/mx2)
    elif mx2 < 0:
        heading = math.pi + math.atan(my2/mx2)
    elif (mx2 > 0 and my2 <= 0):
        heading = 2*math.pi + math.atan(my2/mx2)
    elif my2 < 0:
        # mx2 == 0
        heading = math.pi/2.0
    elif my2 > 0:
        # mx2 == 0
        heading = 3*math.pi/2.0

    headingMagCompass = (-180.0*heading/math.pi + 180.0) % 360

    # Adjust for magnetic declination
    currDeclination = geomag.declination(lat, lon)
    headingMagTrue = (heading + currDeclination) % 360

    # Convert pitch and roll to degs
    pitch = math.degrees(pitch)
    roll = math.degrees(roll)

    return accx, accy, accz, magx, magy, magz, pitch, roll, headingMagCompass, headingMagTrue


def parseTempPressure(dps310):
    """
    Parse the temperature and pressure from the dps310.

    :param dps310: The dps310 sensor object.
    """
    temperature = dps310.temperature
    pressure = 100*dps310.pressure
    altitude = dps310.altitude

    return temperature, pressure, altitude


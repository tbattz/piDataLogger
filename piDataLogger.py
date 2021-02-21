import io
import sys
import time
import board
import busio
import struct
import serial
import adafruit_dps310
import adafruit_lis2mdl
import adafruit_lsm303_accel

import tools


if __name__ == "__main__":
    # Set mag offsets
    magOffsets = [14.699999999999996, 26.55, -5.324999999999999]

    # Set log files
    nextId = tools.genNextLogFileId()
    logFileAscii = "log/data-ascii-%i.csv" % nextId
    logFileBinary = "log/data-bin-%i.bin" % nextId

    # Open log files for writing
    f = open(logFileAscii, 'w')
    g = open(logFileBinary, 'wb')
    f.write("gpsDatetime,gpsDatetimeSec,gpsLatitude,gpsLongitude,gpsSpeedOverGround,orthometricHeight,geoidSeparation," +
            "accx,accy,accz,magx,magy,magz,pitch,roll,headingMagCompass,headingMagTrue,temperature,pressure,baroAltitude\n")

    # Create serial connection - GPS Module
    ser = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.1)
    sio = io.TextIOWrapper(io.BufferedRWPair(ser,ser))

    # Create i2c connection
    i2c = busio.I2C(board.SCL, board.SDA)

    # Setup mag, accel, pressure sensors
    mag = adafruit_lis2mdl.LIS2MDL(i2c)
    accel = adafruit_lsm303_accel.LSM303_Accel(i2c)
    dps310 = adafruit_dps310.DPS310(i2c)

    # Initialise pressure module
    dps310.initialize()

    # Initialise variables
    accx = 0    # m/s^2
    accy = 0    # m/s^2
    accz = 0    # m/s^2
    magx = 0
    magy = 0
    magz = 0
    pitch = 0   # deg
    roll = 0    # deg
    headingMagCompass = 0   # deg
    headingMagTrue = 0      # deg
    gpsData = {'orthometricHeight': 0,   # m
               'geoidSeparation': 0,     # m
               'gpsDatetime': 0,         # datetime
               'gpsDatetimeSec': 0,      # datetime converted to time since epoch
               'gpsLatitude': 0,         # deg
               'gpsLongitude': 0,        # deg
               'gpsSpeedOverGround': 0}  # m/s
    temperature = 0         # C
    pressure = 0            # Pa
    baroAltitude = 0        # m

    # Setup time
    prevTime = 0
    currTime = time.time()
    diffTime = currTime - prevTime
    minTimePeriod = 0.5 # s


    try:
            while True:

                currTime = time.time()
                diffTime = currTime - prevTime

                #if diffTime > minTimePeriod:
                # Get GPS Updates
                gpsData = tools.checkGPSUpdates(sio, gpsData)

                # Parse mag and accelerometer
                accx, accy, accz, magx, magy, magz, pitch, roll, headingMagCompass, headingMagTrue = tools.parseAccelMag(mag, accel, gpsData['gpsLatitude'], gpsData['gpsLongitude'])

                # Parse temp and pressure
                temperature, pressure, baroAltitude = tools.parseTempPressure(dps310)

                # Setup data
                csvStr = "%s,%i,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f" % (str(gpsData['gpsDatetime']), gpsData['gpsDatetimeSec'], gpsData['gpsLatitude'], gpsData['gpsLongitude'], gpsData['gpsSpeedOverGround'], gpsData['orthometricHeight'], gpsData['geoidSeparation'], accx, accy, accz, magx, magy, magz, pitch, roll, headingMagCompass, headingMagTrue, temperature, pressure, baroAltitude)
                binaryData = struct.pack("sidddfffffffffffffff",
                                    str(gpsData['gpsDatetime']).encode('utf-8'),
                                    int(gpsData['gpsDatetimeSec']),
                                    gpsData['gpsLatitude'],
                                    gpsData['gpsLongitude'],
                                    gpsData['gpsSpeedOverGround'],
                                    gpsData['orthometricHeight'],
                                    gpsData['geoidSeparation'],
                                    accx, accy, accz,
                                    magx, magy, magz,
                                    pitch, roll,
                                    headingMagCompass, headingMagTrue,
                                    temperature, pressure, baroAltitude)

                # Write to file
                f.write(csvStr + "\n")
                g.write(binaryData)

                # Flush data
                f.flush()
                g.flush()

                # Print current data
                print(gpsData['gpsDatetime'], gpsData['gpsDatetimeSec'], gpsData['gpsLatitude'], gpsData['gpsLongitude'], gpsData['gpsSpeedOverGround'], gpsData['orthometricHeight'], gpsData['geoidSeparation'], accx, accy, accz, magx, magy, magz, pitch, roll, headingMagCompass, headingMagTrue, temperature, pressure, baroAltitude)
                print()


                time.sleep(0.5)

                prevTime = currTime

    except KeyboardInterrupt:
        # Close files
        f.close()
        g.close()

        sys.exit()




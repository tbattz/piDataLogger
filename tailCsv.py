import sys
import time
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt



# Get file Id
fileId = int(sys.argv[1])


def followFile(filename):
    """
    Follow the given file, returning an iterator to the lines.
    """
    while True:
        # Read all current lines of the file
        line = filename.readline()

        yield line

        if line is None:
            time.sleep(0.01)
        continue





if __name__ == '__main__':

    # Open log file
    logFile = open("log/data-ascii-%i.csv" % fileId)

    # Get line iterator
    lines = followFile(logFile)

    # Create figure
    fig, axs = plt.subplots(3,3, figsize=(10,8))
    axs[0,0].set_xlabel('Longitude')
    axs[0,0].set_ylabel('Latitude')
    axs[0,1].set_xlabel('Time')
    axs[0,1].set_ylabel('GPS Speed Over Ground')
    axs[0,2].set_xlabel('Time')
    axs[0,2].set_ylabel('Altitude')
    axs[1,0].set_xlabel('Time')
    axs[1,0].set_ylabel('Accelerometer')
    axs[1,1].set_xlabel('Time')
    axs[1,1].set_ylabel('Magnetometer')
    axs[1,2].set_xlabel('Time')
    axs[1,2].set_ylabel('Orientation')
    axs[2,0].set_xlabel('Time')
    axs[2,0].set_ylabel('Heading')
    axs[2,1].set_xlabel('Time')
    axs[2,1].set_ylabel('Temperature')
    axs[2,2].set_xlabel('Time')
    axs[2,2].set_ylabel('Pressure')
    plt.suptitle('Raspberry Pi Sensor Data')

    # Setup data stores
    data = {"gpsDatetime": [], "gpsDatetimeSec": [], "gpsLatitude": [], "gpsLongitude": [], "gpsSpeedOverGround": [], "orthometricHeight": [], "geoidSeparation": [],
            "accx": [], "accy": [], "accz": [], "magx": [], "magy": [], "magz": [], "pitch": [], "roll": [], "headingMagCompass": [], "headingMagTrue": [], "temperature": [], "pressure": [], "baroAltitude": []}

    # Setup lines
    datetimes = matplotlib.dates.date2num(data['gpsDatetime'])
    latLonLine, = axs[0,0].plot(data['gpsLongitude'], data['gpsLatitude'],'b-')
    gpsSpeedLine, = axs[0,1].plot(datetimes, data['gpsSpeedOverGround'], 'b-')
    altOrthoLine, = axs[0,2].plot(datetimes, data['orthometricHeight'], 'b-', label='Ortho Height')
    geoidSepLine, = axs[0,2].plot(datetimes, data['geoidSeparation'], 'r-', label='Geoid Separation')
    baroAltLine, = axs[0,2].plot(datetimes, data['baroAltitude'], 'g-', label='Baro Alt')
    accxLine, = axs[1,0].plot(datetimes, data['accx'], 'r-', label='Accel x')
    accyLine, = axs[1,0].plot(datetimes, data['accy'], 'g-', label='Accel y')
    acczLine, = axs[1,0].plot(datetimes, data['accz'], 'b-', label='Accel z')
    magxLine, = axs[1,1].plot(datetimes, data['magx'], 'r-', label='Mag x')
    magyLine, = axs[1,1].plot(datetimes, data['magy'], 'g-', label='Mag y')
    magzLine, = axs[1,1].plot(datetimes, data['magz'], 'b-', label='Mag z')
    pitchLine, = axs[1,2].plot(datetimes, data['pitch'], 'b-', label='Pitch')
    rollLine, = axs[1,2].plot(datetimes, data['roll'], 'g-', label='Roll')
    headingMagLine, = axs[2,0].plot(datetimes, data['headingMagCompass'], 'b-', label='Compass Heading')
    trueHeadingLine, = axs[2,0].plot(datetimes, data['headingMagTrue'], 'g-', label='True Heading')
    tempLine, = axs[2,1].plot(datetimes, data['temperature'], 'b-')
    pressureLine, = axs[2,2].plot(datetimes, data['pressure'], 'b-')


    # Setup interactive plotting
    plt.ion()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.canvas.draw()
    plt.show(block=False)
    plt.pause(0.1)
    axs[0,2].legend(loc='best')
    axs[1,0].legend(loc='best')
    axs[1,1].legend(loc='best')
    axs[1,2].legend(loc='best')
    axs[2,0].legend(loc='best')

    # Skip header line
    line = next(lines)

    # Record time between plots
    lastPlotTime = time.time()
    newData = False

    # Read data from iterator
    for line in lines:
        if line is not None and len(line) > 0:
            print(line)

            # Update Data
            lineSplit = line.split(",")
            data['gpsDatetime'].append(datetime.strptime(lineSplit[0], '%Y-%m-%d %H:%M:%S'))
            data['gpsDatetimeSec'].append(int(lineSplit[1]))
            data['gpsLatitude'].append(float(lineSplit[2]))
            data['gpsLongitude'].append(float(lineSplit[3]))
            data['gpsSpeedOverGround'].append(float(lineSplit[4]))
            data['orthometricHeight'].append(float(lineSplit[5]))
            data['geoidSeparation'].append(float(lineSplit[6]))
            data['accx'].append(float(lineSplit[7]))
            data['accy'].append(float(lineSplit[8]))
            data['accz'].append(float(lineSplit[9]))
            data['magx'].append(float(lineSplit[10]))
            data['magy'].append(float(lineSplit[11]))
            data['magz'].append(float(lineSplit[12]))
            data['pitch'].append(float(lineSplit[13]))
            data['roll'].append(float(lineSplit[14]))
            data['headingMagCompass'].append(float(lineSplit[15]))
            data['headingMagTrue'].append(float(lineSplit[16]))
            data['temperature'].append(float(lineSplit[17]))
            data['pressure'].append(float(lineSplit[18]))
            data['baroAltitude'].append(float(lineSplit[19]))

            newData = True

        elif time.time() - lastPlotTime > 1.0 and newData:
            # Update plots
            datetimes = matplotlib.dates.date2num(data['gpsDatetime'])
            latLonLine.set_data(data['gpsLongitude'], data['gpsLatitude'])
            gpsSpeedLine.set_data(datetimes, data['gpsSpeedOverGround'])
            altOrthoLine.set_data(datetimes, data['orthometricHeight'])
            geoidSepLine.set_data(datetimes, data['geoidSeparation'])
            baroAltLine.set_data(datetimes, data['baroAltitude'])
            accxLine.set_data(datetimes, data['accx'])
            accyLine.set_data(datetimes, data['accy'])
            acczLine.set_data(datetimes, data['accz'])
            magxLine.set_data(datetimes, data['magx'])
            magyLine.set_data(datetimes, data['magy'])
            magzLine.set_data(datetimes, data['magz'])
            pitchLine.set_data(datetimes, data['pitch'])
            rollLine.set_data(datetimes, data['roll'])
            headingMagLine.set_data(datetimes, data['headingMagCompass'])
            trueHeadingLine.set_data(datetimes, data['headingMagTrue'])
            tempLine.set_data(datetimes, data['temperature'])
            pressureLine.set_data(datetimes, data['pressure'])

            # Update axes
            for row in axs:
                for ax in row:
                    ax.relim()
                    ax.autoscale_view()
            fig.canvas.draw()
            plt.show()

            lastPlotTime = time.time()
            newData = False

            plt.pause(0.1)


    logFile.close()





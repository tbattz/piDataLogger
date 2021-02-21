import sys
import time
import tools
from datetime import datetime
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d



# Get file Id
if len(sys.argv) > 1:
    fileId = int(sys.argv[1])
else:
    # Use last value
    fileId = tools.genNextLogFileId() - 1


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
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    plt.suptitle('Raspberry Pi Path')

    # Setup data stores
    data = {"gpsDatetime": [], "gpsDatetimeSec": [], "gpsLatitude": [], "gpsLongitude": [], "gpsSpeedOverGround": [], "orthometricHeight": [], "geoidSeparation": [],
            "accx": [], "accy": [], "accz": [], "magx": [], "magy": [], "magz": [], "pitch": [], "roll": [], "headingMagCompass": [], "headingMagTrue": [], "temperature": [], "pressure": [], "baroAltitude": []}

    # Setup interactive plotting
    plt.ion()
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.canvas.draw()
    plt.show(block=False)
    plt.pause(0.1)

    # Create line
    pathLine, = ax.plot([], [], [], 'o-')

    # Skip header line
    line = next(lines)

    # Record time between plots
    lastPlotTime = time.time()
    newData = False

    # Read data from iterator
    for line in lines:
        if line is not None and len(line) > 0 and line[0] != '\x00':
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
            pathLine.set_xdata(data['gpsLongitude'])
            pathLine.set_ydata(data['gpsLatitude'])
            pathLine.set_3d_properties(data['orthometricHeight'])

            # Update axes
            #ax.relim()
            xmin = min(data['gpsLongitude'])
            xmax = max(data['gpsLongitude'])
            ymin = min(data['gpsLatitude'])
            ymax = max(data['gpsLatitude'])
            zmin = min(data['orthometricHeight'])
            zmax = max(data['orthometricHeight'])
            ax.set_xlim([xmin, xmax])
            ax.set_ylim([ymin, ymax])
            ax.set_zlim([zmin, zmax])
            ax.autoscale_view()
            fig.canvas.draw()
            plt.show()

            lastPlotTime = time.time()
            newData = False

            plt.pause(0.1)


    logFile.close()





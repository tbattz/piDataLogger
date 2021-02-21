piDataLogger
==============
A simple repository that logs various sensors data using a raspberry pi.

Sensors
--------
U-blox NEO-6M GPS Module
Adafruit DPS310 Precision Barometric Pressure/Altitude Sensor
Adafruit LSM303AGR Accelerometer Magnetometer
2-Pin Toggle Switch

Pin Layout
-----------
- The GPS module should be connected on the serial interface through the TX and RX Pins. This appears as /dev/ttyAMA0
- The pressure sensor and accelerometer should be connected to SDA and SCL though I2C, chained using the Qwiic ports
- The switch is connected specifically to the GPIO 21 pin

Usage
----------
The piDataLogger.py script does the work of communicating with the sensors, and logging the data to .csv and .bin files. But it is kept alive, using the keepAlive.py script, which will kill the piDataLogging script, when the toggle switch is set to off, and start/check that script is running, when the toggle switch is set to on.

The tailCsv.py script will visualise the sensor data in real time, or in playback mode by giving the id of the log file.



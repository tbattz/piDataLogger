import time
import subprocess as sp
import RPi.GPIO as GPIO


# Set script to keep alive
scriptName = "piDataLogger.py"
runDir = "/home/pi/git/piDataLogger"
# Setup switch pin
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pin = 21
GPIO.setup(pin, GPIO.IN, GPIO.PUD_UP)



def getScriptProcs(scriptNamePy):
    """
    Get the process ids of the given script name.
    
    :param scriptNamePy: The name of the script, with the .py extenson.
    :return: A list of process ids for this script.
    """
    # Get output of processes running python
    psOutput = sp.check_output('ps -ef | grep "python %s"' % scriptNamePy, shell=True)
    lines = psOutput.split(b'\n')

    # Get id of process
    scriptProcs = []
    for line in lines:
        if (b'grep' not in line) and (b'.bashrc' not in line) and len(line) > 0:
            lineSplit = [mystr for mystr in line.split(b' ') if len(mystr) > 0]
            procId = int(lineSplit[1])
            scriptProcs.append(procId)

    print(scriptProcs)

    return scriptProcs   

f = open("out.txt", "w")


while True:

    # Get script process ids
    procIds = getScriptProcs(scriptName)

    # Check switch state
    switchState = GPIO.HIGH != GPIO.input(pin)

    print("Switch: ", switchState, "Processes: ", procIds)

    if not switchState:
        # Script should be stopped
        if len(procIds) > 0 and not switchState:
            # Kill all of the script procs
            for procId in procIds:
               print("Killing process %i" % procId)
               sp.run(["kill", "-2", str(procId)])
    else:
        # Only one proc should be running
        if len(procIds) == 0:
            # Start new script
            print("Staring new script %s" % scriptName)
            proc = sp.Popen(". /home/pi/.bashrc && cd %s && python %s" % (runDir, scriptName), shell=True, stdin=sp.PIPE, stdout=f)
        
        elif len(procIds) > 1:
            # Kill all but one script
            for procId in procIds[1:]:
                print("Killing process %i" % procId)
                sp.run(["kill", "-2", str(procId)])



    time.sleep(2.0)


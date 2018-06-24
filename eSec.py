#!/usr/bin/env python
# eSec.py
################
#
# DESCRIPTION
# A security daemon, that is designed to protect sensitive data from onsite attacks.
# Automatically locks your computer based on various configurable state changes. 
# State change monitors available are, bluetooth, USB serial numbers, AC power, and internet connection status.
# Automatically photographs user on lock/unlock & backs up.
# Automatically logs location on lock/unlock & backs up.
# Automatically backs up device once locked
########################
#
# TODO
# Multithread the main program
# Add AC, USB and Net detection.
#
#
###################################
#
# FUTURE FEATURES
# Facial recognition
# Record and analyze system performance to detect degridation
# 2FA frontend for BT and facial authentication.
# Wireless ringfence to detect and wirelessly mask the device from other users.
#
###############################################

# Imports
import os, sys, subprocess, time, readline, thread, re

verbose = False
sound = False
key = ""

# Dependancy installer
def installDeps():
	dependancies = [ "xdotool", "espeak", "nmap" ,"streamer"]
	for dep in dependancies:
		vprint(runProcess("/home/joseph/bin/eSecTools.sh installDeps "+dep))

def wordCount(value):
    # Find all non-whitespace patterns.
    list = re.findall("(\S+)", value)
    # Return length of resulting list.
    return len(list)

# Debug print; shows extra runtime info
def vprint(i, reverse=False, extras=False): 
	global verbose
	if verbose is not None:
		if verbose is not reverse:
			if extras : print("")
			print(i)
			if extras : print("> ")

# Audio print: Speaks and prints the get_line_buffer
def sprint(line):
	global sound
	print(line)
	if sound is True:
		for item in line.split(): 
			runProcess("espeak -s230 -g0 "+str(item))			

# Bash process spawn
def runProcess(command):
	result=""
	bashCommand = command
	
	process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
	while process.poll() is None:
		output = process.stdout.readline()
		if wordCount(output) >= 1 : result = result+output
	
	return(result)

# Calculates the rssi range of any registered BT device within its range
def rangefindBT():
	workingRange = 0
	vprint("Searching for bluetooth devices")
	for r in xrange(0,9):
		result = runProcess("/home/joseph/bin/eSecTools.sh btscan")
		if result is not None : workingRange += int(result)
		time.sleep(1)
	workingRange = workingRange/10
	vprint("BT working range : "+str(workingRange))
	return([workingRange-10,workingRange+15])

# Procceses range checks of registered BT devices
def checkBT(r, lastBT):
	bt = lastBT
	rssi = int(runProcess("/home/joseph/bin/eSecTools.sh btscan"))
	if rssi == 0 : bt = (3, "disconnect")
	if rssi < r[0]: bt = (1, "close")
	if rssi > r[1]: bt = (2, "gone")
	vprint("BT connection status : "+str(bt), extras=True)
	if bt is not lastBT :
		vprint("BT connection status : "+str(bt), reverse=True, extras=True)
		if bt[0] is 2: lockUnlock(1,"bt")
		if bt[0] is not 2 : lockUnlock(0,"bt")
	return(bt)
	
def checkUSB():
	usbio = runProcess("/home/joseph/bin/usbscan.sh")

def checkAC(lastacio):
	acio = runProcess("cat /sys/class/power_supply/ACAD/online")
	try: acio = int(acio)
	except: return(lastacio)
	
	vprint("AC connection status : "+str(acio), extras=True)
	if acio is not lastacio :
		vprint("AC connection status : "+str(acio), reverse=True, extras=True)
		if acio is 0:
			lockUnlock(1,"ac")
		if acio is 1:
			lockUnlock(0,"ac")
	return(acio)

def checkNet():
	netio = runProcess("/home/joseph/bin/netscan.sh")

def userSnapshot():
	runProcess("streamer -f jpeg -o user_snapshot.jpeg")
	pass

# Lock/unlock sequence
def lockUnlock(i, name):
	global key
	if name is key :
		if i is 0 : 
			runProcess("loginctl unlock-sessions")
			runProcess("xdotool mousemove_relative 1 1")
	if i is 1 : 
		runProcess("loginctl lock-sessions")
		key = name
	
# Discovers availible security devices and sets the mode accodingly
def modeManager():
	# Decides run mode at startup	
	vprint("Discovering security devices")
	mode = ""
	r = rangefindBT()
	a = checkAC(0)

	if r : mode = mode+"bluetooth "
	if a is 1 : mode = mode+"ac "
	if mode == "" : print("No security devices present")
	vprint("Mode set to "+mode, reverse=None, extras=True)
	return(r,a,mode)


def securityLoop():
	# Setup
	mode = ""
	r,p,mode = modeManager()
	vprint("Init complete")
	ac = checkAC(0)
	bt = checkBT(r, (0, "gone"))
	# Main Loop
	while 1:
		if "bluetooth" in mode:
			bt = checkBT(r, bt)
		if "ac" in mode:
			ac = checkAC(ac)

def main_thread():
	sprint("Starting extended security services, applying enhaced protocols")
	print("Type system or security commands below")
	# Main Loop
	while True:
		#sys.stdout.write('\r'+' '*(len(readline.get_line_buffer())+2)+'\r')
		# Main program
		securityLoop()
		#sys.stdout.write('> ' + readline.get_line_buffer())
		sys.stdout.flush()
		time.sleep(1)

# Setup
sys.stdout.write("\x1b]2;Extended security protocol BETA \x07") # Window title
os.system("xdotool key CTRL+SUPER+Left ; clear") # Window positioning and clearing
print("Script developed by boejaker industries v0.1") # Info
installDeps() # Dependancy check

# Main threads
thread.start_new_thread(main_thread, ())
time.sleep(1)

# Command line interface
while True:
    s = raw_input('> ')
    # Command handler
    try:
    	os.system(s)
    except:
   		pass
   


# systemHealthLoop()
# ringFence()
# 2FAdeamon()

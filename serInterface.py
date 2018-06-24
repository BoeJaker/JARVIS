#!/usr/bin/env python

import serial
import io
import time
import sys
import thread

class arduino:
	pass

def main_thread():
	pass

def commandParse(command):
	return(command)

#sys.stdout.write("\x1b]2;Serial Interface\x07") # Window title

ser = serial.Serial()
ser.baudrate = 9600
ser.port = '/dev/ttyACM3'
ser.open()

# Main thread
thread.start_new_thread(main_thread, ())

# Command line interface
while ser.is_open :
	
	ri = raw_input(">")
	ri = commandParse(ri)
	ser.write(b""+ri+" \n")	
	time.sleep(0)

ser.close()
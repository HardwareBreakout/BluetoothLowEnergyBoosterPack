#!/usr/bin/python

import time
import threading

import BGLib as ble
import serial
import array

def ConnectBLE():
	ble.searchForDevices(1)

	if not ble.deviceList:
		print "No devices found!"
	else:
		question = 'Available Devices:'			
		for i in range(len(ble.deviceList)):
			question = question + '\r\n' + str(i+1) + '.' + str(ble.deviceList[i])
			
		print question,"\n"
		
		print "Please select a device:"
		devNum = input()
		
		if (devNum > len(ble.deviceList)):
			print "Not a valid device!"
		else:
		
			dev = ble.deviceList[devNum-1]
			ble.connectToDevice(dev)
			
			print "Connected to: \"",dev.name,"\""
			RSSI = dev.RSSI
			RSSI = RSSI if RSSI <= 127 else RSSI - 256 
			print "RSSI: ",dev.RSSI,"dBm\n"
			
			ble.enableRXIndicator()
			
			
def TerminateProgram():
	global read_packet_stop
	print "Termination started..."
	ble.ble_disconnect(0)
	#stop the thread which is reading packets
	read_packet_stop.set()
	ble.ser.close()
	print "Closing..."
			
def InitBLE():
	global read_packet_stop
	ble.silent = 1
	ble.handleDataRX = ReceiveData

	ble.ser = serial.Serial("COM3", 256000, timeout=.2)
	ble.ser.flushInput()
	ble.ser.flushOutput()
	ble.ser.flush()

	read_packet_stop = threading.Event()
	ble.read_packet_thread = threading.Thread(target=ble.readPacketThread,  args=(2, read_packet_stop))
	ble.read_packet_thread.start()

	ble.initializeBLE()

	
def ReceiveData(data):
	global mode, CHECK_VCC, TEMP, vcc
	print "ReceiveData"
	if mode == 0:
		if (data == 'b'):
			print "Button Pressed!\n"
		else:
			print "Receive,", data
	elif mode == CHECK_VCC:
		vcc = ord(data)/255.0*1.5*2.0
		print "VCC = ", vcc
		mode = 0
	elif mode == TEMP:
		V = ord(data)/255.0*1.5
		C = (V-0.986)/0.00355
		print "T = ", (C*9.0/5.0)+32.0, "F"
		mode = 0
	elif mode == CHECK_BATT:
		print "V_battery = ", ord(data)/255.0*vcc*2
		mode = 0
	return
	
	
def MainLoop():
	global mode, CHECK_VCC, TEMP, CHECK_BATT
	
	selection = 1
	while (selection != 99):
			
		if (selection == 1):
			print "Menu:"
			print "   1. Print this menu"
			print "   2. Connect"
			print "   3. Disconnect"
			print "   4. Toggle LED"
			print "   5. Get VCC"
			print "   6. Get Temperature"
			print "   7. Get Battery V"
			print "   8. Send arbitrary data"
			print "   9. Reset system"
			print "   99. Quit"
			
		elif (selection == 2):
			ConnectBLE()
			
		elif (selection == 3):
			print "Disconnecting from device..."
			ble.ble_disconnect(0)
			
		elif (selection == 4):
			print "Toggling LED...\n"
			ble.sendData(array.array('B', '1') )
			
		elif (selection == 5):
			print "Getting VCC...\n"
			mode = CHECK_VCC
			ble.sendData(array.array('B', '4') )
			
		elif (selection == 6):
			print "Getting temperature...\n"
			mode = TEMP
			ble.sendData(array.array('B', '5') )
			
		elif (selection == 7):
			print "Getting battery voltage...\n"
			mode = CHECK_BATT
			ble.sendData(array.array('B', '6') )
			
		elif (selection == 8):
			value = raw_input("Please enter data to send: ")
			ble.sendData(array.array('B', value ) )
									
		elif (selection == 9):
			print "Resetting system..."
			ble.resetBLE()
						
			
		else:
			print "Not an option.\n"
			

		print "Please enter a number:"
		selection = input()
		print "\n"		
		
		
	return
	
	
read_packet_stop = None
mode = 0
CHECK_VCC = 1
TEMP = 2
CHECK_BATT = 3
vcc = 2.1

if __name__ == '__main__':
	
	print "Starting Bluetooth Low Energy Button and LED Demo!"
	print "Written by NJC of http://hardwarebreakout.com\n"

	InitBLE()
	
	MainLoop()
	
	print "Closing..."
	TerminateProgram()


	
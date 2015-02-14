
BLE_address = []
address_type = []
conn_handle = []
ser = []
deviceList = []
wait_flag = 0
wait_response_flag = 0
silent = 0
handleDataRX = []

class Device:
	def __init__(self, RSSI, address, address_type):
		self.RSSI = RSSI
		self.address = address
		self.address_type = address_type
		self.name = ""
	def __str__(self):
		return "Name: " + self.name + "\tAddress: " + self.address.tostring() + "\tRSSI: " + str(self.RSSI)

def getLowerByte(value):
	return (value & 0xFF)

def getUpperByte(value):
	return (value >> 8)

def get_uint16(upperByte, lowerByte):
	return (upperByte << 8) + lowerByte

def sendCommand( length, commandClass, commandID, payload=[]):	
	bgapiTXBuffer = [0]*(length + 4)
	bgapiTXBuffer[0] = 0x00
	bgapiTXBuffer[1] = (length & 0xFF)
	bgapiTXBuffer[2] = commandClass
	bgapiTXBuffer[3] = commandID
	lastCommand = [0]*2
	lastCommand[0] = commandClass
	lastCommand[1] = commandID
	bgapiTXBuffer[4:len(bgapiTXBuffer)] = payload

	bgapiTXBuffer= array.array('B', bgapiTXBuffer)
	ser.write(bgapiTXBuffer.tostring())

	return

def ble_reset():
	sendCommand(1,0,0,[0])	# reboot into main program
	return
		
def ble_hello():
	sendCommand(0,0,1)
	return

def ble_get_info():
	sendCommand(0,0,8)
	return

def ble_get_address():
	sendCommand(0,0,2)
	return
	
def ble_set_mode(discover, connect):
	payload = [0]*2
	payload[0] = discover
	payload[1] = connect
	sendCommand(len(payload),6,1,payload)
	return

def ble_set_scan_parameters(scan_interval, scan_window, active):
	payload = [0]*5
	payload[0] = getLowerByte(scan_interval)
	payload[1] = getUpperByte(scan_interval)
	payload[2] = getLowerByte(scan_window)
	payload[3] = getUpperByte(scan_window)
	payload[4] = active
	sendCommand(len(payload),6,7,payload)
	return

def ble_discover(mode):
	payload = [0]*1
	payload[0] = mode
	sendCommand(len(payload),6,2,payload)
	return

def ble_end_procedure():
	sendCommand(0,6,4)
	return

def ble_connect_direct(bd_addr, addr_type, conn_interval_min, conn_interval_max, timeout, latency):
	payload = [0]*15
	payload[0:5+1] = bd_addr
	payload[6] = addr_type
	payload[7] = getLowerByte(conn_interval_min)
	payload[8] = getUpperByte(conn_interval_min)
	payload[9] = getLowerByte(conn_interval_max)
	payload[10] = getUpperByte(conn_interval_max)
	payload[11] = getLowerByte(timeout)
	payload[12] = getUpperByte(timeout)
	payload[13] = getLowerByte(latency)
	payload[14] = getUpperByte(latency)
	sendCommand(len(payload),6,3,payload)
	return

def ble_disconnect(connection_handle):
	sendCommand(1,3,0,[connection_handle])
	return

def ble_find_information(connection_handle, first_attr, last_attr):
	payload = [0]*5
	payload[0] = connection_handle
	payload[1] = getLowerByte(first_attr)
	payload[2] = getUpperByte(first_attr)
	payload[3] = getLowerByte(last_attr)
	payload[4] = getUpperByte(last_attr)
	sendCommand(len(payload),4,3,payload)
	return

def ble_att_write(connection_handle, attribute_handle, data):
	global silent
	payload = [0]*(len(data) + 3)
	payload[0] = connection_handle
	payload[1] = getLowerByte(attribute_handle)
	payload[2] = getUpperByte(attribute_handle)        
	payload[3:len(payload)] = data
	if (silent == 0):
		print "\n\nAttribute write packet payload:",
		print payload
	sendCommand(len(payload),4,5,payload)
	return

def ble_prepare_write(connection_handle, attribute_handle, offset, data):
	global silent
	payload = [0]*(len(data) + 5)
	payload[0] = connection_handle
	payload[1] = getLowerByte(attribute_handle)
	payload[2] = getUpperByte(attribute_handle)
	payload[3] = getLowerByte(offset)
	payload[4] = getUpperByte(offset)
	payload[5:len(payload)] = data
	if (silent == 0):
		print "\n\nAttribute prepare write packet payload:",
		print payload
	sendCommand(len(payload),4,9,payload)
	return
	
#def ble_write(connection_handle, attribute_handle, data):
#	payload = [0]*(length(data) + 3)
#	payload[0] = connection_handle
#	payload[1] = getLowerByte(attribute_handle)
#	payload[2] = getUpperByte(attribute_handle)
#	payload[3:len(payload)] = data
	
def ble_execute_write(connection_handle, commit):
	payload = [0]*2
	payload[0] = connection_handle
	payload[1] = commit
	sendCommand(len(payload),4,0x0A,payload)
	return
	
def ble_read_by_handle(connection_handle, attribute_handle):
	payload = [0]*(3)
	payload[0] = connection_handle
	payload[1] = getLowerByte(attribute_handle)
	payload[2] = getUpperByte(attribute_handle)	
	sendCommand(len(payload),4,4,payload)
	return

def readPacket():
        header = ser.read(4)
        if ( len(header) == 0 ):
                return 0
        header= array.array('B', header)
#        print header
        length = header[1]
        data = ser.read(length)
        data= array.array('B', data)
#        print data
        parsePacket(header,data)
        return 1

def parsePacket(header, data):
	if (len(header) < 4):
		print "\nERROR READING HEADER!!!!"
		time.sleep(2)
		ser.flushInput()
		return
	messageClass = header[2]
	messageID = header[3]
	if ((header[0] & 0x80) == 0):
			ble_response_received(messageClass, messageID, data)
	else:
			ble_event_received(messageClass, messageID, data)
	return

def ble_response_received(messageClass, messageID, data):
	global wait_flag, silent
	if (silent == 0):
		print "Response:",
	if (messageClass == 0):
		if (silent == 0):
			print "class = system,",
		#if (messageID == 0):
		if (messageID == 1):
			if (silent == 0):
				print "hello received!",
		elif (messageID == 2):
			if (silent == 0):
				print "local address =",
				print data,
		elif (messageID == 0x05):
			if (silent == 0):
				print "get counters response,",
				print data,
		elif (messageID == 0x06):
			if (silent == 0):
				print "number of connections supported =",
				print data,
		elif (messageID == 0x08):
			if (silent == 0):
				print "info received",
		elif (messageID == 0x09):
			if (silent == 0):
				print "endpoint tx,",
			processResult(get_uint16(data[1], data[0]))
		elif (messageID == 0x0D):
			if (silent == 0):
				print "endpoint rx,",
			processResult(get_uint16(data[1], data[0]))
		elif (messageID == 0x0E):
			if (silent == 0):
				print "endpoint watermark set,",
			processResult(get_uint16(data[1], data[0]))
		else:
			if (silent == 0):
				print "messageID =",
				print messageID,
				
	elif (messageClass == 1):
		if (silent == 0):
			print "class = flash,",    
			print "messageID =",
			print messageID                    
	elif (messageClass == 3):
		if (silent == 0):
			print "class = connection,",
		if (messageID == 0):
			if (silent == 0):
				print "Device disconnect command sent,",
			#print data[0],
			processResult(get_uint16(data[2], data[1]))
			wait_flag = 0
		else:
			if (silent == 0):
				print "messageID =",
				print messageID,
	elif (messageClass == 4):
		if (silent == 0):
			print "class = attribute client,",
		if (messageID == 3):
				if (silent == 0):
					print "Finding information on handle started,",
				#print data[0],
				processResult(get_uint16(data[2], data[1]))
		elif (messageID == 4):
				if (silent == 0):
					print "reading by handle initiated,",
				processResult(get_uint16(data[2], data[1]))
		elif (messageID == 5):
				if (silent == 0):
					print "Write attribute command sent,",
				#print data[0],
				processResult(get_uint16(data[2], data[1]))
				wait_flag = 0
		elif (messageID == 9):
				if (silent == 0):
					print "preparing to write attribute,",
				processResult(get_uint16(data[2], data[1]))
		elif (messageID == 0x0A):
				if (silent == 0):
					print "Execute write sent to client,",
				processResult(get_uint16(data[2], data[1]))
		else:
			if (silent == 0):
				print "messageID =",
				print messageID,
	elif (messageClass == 6):
		if (silent == 0):
			print "class = GAP,",
		if (messageID == 1):
				if (silent == 0):
					print "setting mode,",
				processResult(get_uint16(data[1], data[0]))
				wait_flag = 0
		elif (messageID == 2):
				if (silent == 0):
					print "discovering devices,",
				processResult(get_uint16(data[1], data[0]))
				wait_flag = 0
		elif (messageID == 3):
				if (silent == 0):
					print "connecting to device,",
				#print data[2]
				processResult(get_uint16(data[1], data[0]))
				wait_flag = 0
		elif (messageID == 4):
				if (silent == 0):
					print "procedure has ended,",
				processResult(get_uint16(data[1], data[0]))
				wait_flag = 0
		elif (messageID == 7):
				if (silent == 0):
					print "scan parameters set,",
				processResult(get_uint16(data[1], data[0]))
				wait_flag = 0
		else:
			if (silent == 0):
				print "messageID =",
				print messageID,       
	elif (messageClass == 7):
		if (silent == 0):
			print "class = hardware,",
			print "messageID =",
			print messageID,
	else:
		if (silent == 0):
			print "Error, no class ID match!!",
			print "messageClass =",
			print messageClass,
	if (silent == 0):
		print "\n"
	return

def ble_event_received(messageClass, messageID, data):
	global silent, wait_respond_flag
	if (silent == 0):
		print "Event: ",
	if (messageClass == 0):
			if (silent == 0):
				print "class = system,",
			if (messageID == 0):
				ble_event_system_boot(data)
			elif (messageID == 2):
				ble_event_system_endpoint_watermark_rx(data)
			elif (messageID == 3):
				ble_event_system_endpoint_watermark_tx(data)
			elif (messageID == 4):
				ble_event_system_script_failure(data)
			else:
				if (silent == 0):
					print "messageID =",
					print messageID,
			
	elif (messageClass == 1):
			if (silent == 0):
				print "class = flash,",
			if (messageID == 0):
				ble_event_flash_ps_key(data)
			else:
				if (silent == 0):
					print "messageID =",
					print messageID,
	elif (messageClass == 2):
			if (silent == 0):
				print "class = attribute database,",
				print "messageID =",
				print messageID,
	elif (messageClass == 3):
			if (silent == 0):
				print "class = connection,",
			if(messageID == 0):
				wait_respond_flag = 0
				ble_event_scan_status(data)
			elif(messageID == 4):
				if (silent == 0):
					print "disconnected sucessfully,",
				#print data[0]
				wait_flag = 0
			else:
				if (silent == 0):
					print "messageID =",
					print messageID,
	elif (messageClass == 4):
			if (silent == 0):
				print "class = attribute client,",
			if (messageID == 0):
					ble_event_attr_client_indicated(data)
			elif (messageID == 1):
					wait_respond_flag = 0
					ble_event_attr_client_procedure_completed(data)
			elif (messageID == 2):
					ble_event_attr_client_group_found(data)
			elif (messageID == 4):
					ble_event_attr_client_information_found(data)
			elif (messageID == 5):
					ble_event_attr_client_attr_value(data)
			elif (messageID == 6):
					ble_event_attr_client_read_multiple(data)
			else:
				if (silent == 0):
					print "messageID =",
					print messageID,
	elif (messageClass == 5):
			if (silent == 0):
				print "class = security manager,",
				print "messageID =",
				print messageID,
	elif (messageClass == 6):
			if (silent == 0):
				print "class = GAP,",
			if (messageID == 0):
					ble_event_scan_response(data)
			else:
				if (silent == 0):
					print "messageID =",
					print messageID
	elif (messageClass == 7):
			if (silent == 0):
				print "class = hardware,",
				print "messageID =",
				print messageID,
	else:
			if (silent == 0):
				print "Error, no class ID match!!",
				print "classID =",
				print classID,
	if (silent == 0):
		print "\n"
	return
	
def ble_event_system_script_failure(data):
	global silent
	if (silent == 0):
		print "ERROR! script failure!!",
		print data,
	return

def ble_event_system_endpoint_watermark_tx(data):
	global silent
	if (silent == 0):
		print "system endpoint watermark tx,"
		print data,
	return
	
def ble_event_system_endpoint_watermark_rx(data):
	global silent
	if (silent == 0):
		print "system endpoint watermark rx,"
		print data,
	return
	
def ble_event_system_boot(data):
	global silent
	if (silent == 0):
		print "system booted,",
	return

def ble_event_flash_ps_key(data):
	global silent
	if (silent == 0):
		print "ps key,",
		print data,
	return
	
def ble_event_attr_client_read_multiple(data):
	global silent
	if (silent == 0):
		print "read multiple response,",
		print data,
	return

def ble_event_attr_client_procedure_completed(data):
	global silent
	if (silent == 0):
		print "Procedure completed on client,",
	#print data[0],
	processResult(get_uint16(data[2], data[1]))
	return
					
def ble_event_attr_client_indicated(data):
	global silent
	if (silent == 0):
		print "indicated,",
		print data,
	return
	
def ble_event_attr_client_information_found(data):
	global silent
	if (silent == 0):
		print "information found, device handle =",
		print data[0],
		print ", attribute handle =",
		print get_uint16(data[2], data[1]),
		print ", UUID =",
		print data[3:len(data)],

def ble_event_attr_client_group_found(data):
	global silent
	if (silent == 0):
		print "group found,",
		print data,
	return
		
def ble_event_attr_client_attr_value(data):
	#print "Attibute value received:",
	#print ", attribute type =",
	#print data[3],
	#print ", value (data) =",
	#print data[4:len(data)].tostring(),
	
	connection_handle = data[0]
	att_handle = get_uint16(data[2], data[1])
	data = data[5:5+data[4]].tostring()
	parseAttributeReceived(connection_handle, att_handle, data)
	return
	
def parseAttributeReceived(connection_handle, att_handle, data):
	if ( att_handle == 8 ):
		# UART data received
		receiveData(data)
	return
		
def ble_event_scan_status(data):
	global conn_handle, silent
	if (silent == 0):
		print "status received, device handle =",
	conn_handle = data[0]
	if (silent == 0):
		print data[0],
		print ", status flag =",
		print data[1],
		print ", address =",
		print data[2:7+1],
		print ", connection interval =",
		print get_uint16(data[9],data[8]),
		print ", timeout =",
		print get_uint16(data[11],data[10]),
		print ", slave latency = ",
		print get_uint16(data[13],data[12]),
		print ", bonding =",
		print data[14],
	return

def ble_event_scan_response(data):
	global BLE_address, address_type, silent
	
	if (silent == 0):
		print "scan response, RSSI =",
	RSSI = data[0] #should be int8
	if (silent == 0):
		print data[0],
	packet_type = data[1]
	if (silent == 0):
		print ", packet type =",
		print packet_type,
	bd_addr = data[2:7+1]
	if (silent == 0):
		print ", address =",
		print bd_addr,
	BLE_address = bd_addr
	address_type = data[8]
	if (address_type == 0):
		if (silent == 0):
			print ", public address,",
	else:
		if (silent == 0):
			print ", random address,",
	bond = data[9]
	data = data[10:len(data)]
	
	parseScanResponse(RSSI, packet_type, bd_addr, address_type,data)
	if (silent == 0):
		print "data =",
		print data.tostring(),
	return
	
def parseScanResponse(RSSI, packet_type, bd_addr, address_type,data):
#Device(self, RSSI, address, address_type):
	global silent
	length = data[0]
	AD_type = data[1]
	data = data[2:length]
	
	exists = 0;
	for dev in deviceList:
		if ( dev.address == bd_addr ):
			exists = 1
			break
	if (exists == 0):
		device = Device(RSSI,bd_addr,address_type)
		if ( AD_type == 9 ):
			#Localname complete
			device.name = data.tostring()
			if (silent == 0):
				print "Name = ", device.name
		else:
			if (silent == 0):
				print "AD Type = ", AD_type
		deviceList.append(device)
	else:
		if (silent == 0):
			print "Device already found"
		if (AD_type == 9 ):
			if (silent == 0):
				print "Old name:", dev.name
			dev.name = data.tostring()
			if (silent == 0):
				print "Added Name:", dev.name
		dev.RSSI = RSSI
	return
	
def processResult(result):
	global silent
	if (result == 0):
		if (silent == 0):
			print ("sucessful"),
	elif (result == 0x0180):
		if (silent == 0):
			print "Error! Invalid Parameter!",
	elif (result == 0x0181):
		if (silent == 0):
			print "Error! Device in wrong state!",
	elif (result == 0x0182):
		if (silent == 0):
			print "Error! Out of memory!",
	elif (result == 0x0185):
		if (silent == 0):
			print "Error! Device has timed out!",
	elif (result == 0x0186):
		if (silent == 0):
			print "Error! Device not connected!",
	elif (result == 0x0208):
		if (silent == 0):
			print "Error! Connection timeout!",
	elif (result == 0x0209):
		if (silent == 0):
			print "Error! Connection limit exceeded!",
	elif (result == 0x0401):
		if (silent == 0):
			print "Error! Invalid handle!",
	elif (result == 0x0402):
		if (silent == 0):
			print "Error! Read not permitted!",
	elif (result == 0x0403):
		if (silent == 0):
			print "Error! Write not permitted!",
	elif (result == 0x040A):
		if (silent == 0):
			print "Error! Attribute Not Found!",
	elif (result == 0x020C):
		if (silent == 0):
			print "Error! Command not allowed in current state!",
	else:
		if (silent == 0):
			print "Error!",
			print result
	return

def writeLog(text):
        return

def readPacketThread(arg1, stop_event):
	global silent
	if (silent == 0):
		print "Thread started...\n"
	while(not stop_event.is_set()):
		while ( readPacket() == 1):
			pass
		time.sleep(.1)
	return
	
def initializeBLE():
	disconnectDevice(0)
	stopAdvertising()
	cancelProcedures()
	return
	
# Does not work
def resetBLE():
	global wait_flag
	ble_reset()
	ser.close()
	ser = []
	time.sleep(2)
	ser = serial.Serial("COM14", 256000, timeout=1)
	ser.flushInput()
	ser.flushOutput()
	ser.flush()
	initializeBLE()
	return

def disconnectDevice(connection_handle):
	global wait_flag
	wait_flag = 1
	ble_disconnect(connection_handle)
	while (wait_flag == 1):
		time.sleep(.01)
	return
		
def stopAdvertising():
	global wait_flag
	wait_flag = 1
	ble_set_mode(0,0)	
	while (wait_flag == 1):
		time.sleep(.01)
	return
	
def cancelProcedures():
	global wait_flag
	wait_flag = 1
	ble_end_procedure()
	while (wait_flag == 1):
		time.sleep(.01)
	return
	
def searchForDevices(seconds):
	global wait_flag, deviceList
	deviceList = []
	
	wait_flag = 1
	ble_set_scan_parameters(200, 200, 1)
	while (wait_flag == 1):
		time.sleep(.01)
		
	wait_flag = 1
	ble_discover(1) # Discover generic mode
	while (wait_flag == 1):
		time.sleep(.01)
		
	time.sleep(seconds)
	
	wait_flag = 1
	ble_end_procedure()
	while (wait_flag == 1):
		time.sleep(.01)
	return

def enableRXIndicator():
	global wait_flag, wait_respond_flag
	att_handle = 10
	data = [2]
	wait_flag = 1
	wait_respond_flag = 1
	ble_att_write(conn_handle, att_handle, data)
	while (wait_flag == 1):
		time.sleep(.01)
	while (wait_respond_flag == 1):
		time.sleep(.01)
	return
	
def connectToDevice(dev):
	global wait_flag, wait_respond_flag
	wait_flag = 1
	wait_respond_flag = 1
	ble_connect_direct(dev.address, dev.address_type, 20, 3200, 3200, 0)
	while (wait_flag == 1):
		time.sleep(.01)
	while (wait_respond_flag == 1):
		time.sleep(.01)
	return

def receiveData(data):
	global silent
	if (silent == 0):
		print data,
	if handleDataRX:
		for i in range(0,len(data)):
			handleDataRX(data[i])
	return
	
def sendData(data):
	global wait_flag, wait_respond_flag
	data.insert(0,len(data))
	att_handle = 8
	wait_flag = 1
	wait_respond_flag = 1
	ble_att_write(conn_handle, att_handle, data)
	while (wait_flag == 1):
		time.sleep(.01)
	while (wait_respond_flag == 1):
		time.sleep(.01)
	return


import serial
import array
import threading
import time

if __name__ == "__main__":
	#ser = serial.Serial("COM4", 38400, timeout=1)
	ser = serial.Serial("COM10", 256000, timeout=1)
	ser.flushInput()
	ser.flushOutput()
	ser.flush()

	print "Starting read packet thread..."
	read_packet_stop = threading.Event()
	read_packet_thread = threading.Thread(target=readPacketThread,  args=(2, read_packet_stop))
	read_packet_thread.start()
	
	initializeBLE()
	
	selection = 0
	while (selection != 99):

		if (selection == 0):
			print "Menu:"
			print "   1. Print this menu"
			print "   2. Start scanning"
			print "   3. Connect to device"
			print "   4. Discover services"
			print "   5. Enable indicators"
			print "   6. Send data"
			print "   7. List devices"
			print "   8. Read attribute"
			print "   9. Write attribute"
			print "   10. Disconnect device"
			print "   11. Make discoverable"
			print "   12. Reset system"
			print "   13. Send \"Hello\""
			print "   14. Get device information"
			print "   15. Initialize"
			print "   99. Quit"
			
		elif (selection == 2):
			print "Scanning..."
			searchForDevices(1)
			
		elif (selection == 3):
			print "Which device would you like to connect to?"			
			for i in range(len(deviceList)):
				print str(i+1) + ".", deviceList[i]
			
			devNum = input("Please enter a number:")
			dev = deviceList[devNum-1]
			print "Connecting to device..."		
			connectToDevice(dev)
			
		elif (selection == 4):
			print "Discovering services..."
			ble_find_information(conn_handle, 1, 0xFFFF)
			
		elif (selection == 5):
			print "Enabling indicators..."
			enableRXIndicator()
			
		elif (selection == 6):
			value = raw_input("Please enter data to send: ")
			sendData(array.array('B', value ) )
			
		elif (selection == 7):
			print "List of Devices:"
			for dev in deviceList:
				print dev
				
		elif (selection == 8):
			att_handle = input("Which attribute handle to read from (uint16)?")
			print "Reading attribute..."
			ble_read_by_handle(conn_handle, att_handle)
			
		elif (selection == 9):
			print "Sending test data to sensor...\n"
			# This is done by writing to the long UUID
			data = [0]*2
			data[0] = 1
			data[1] = 0x33
			att_handle = 8
			ble_att_write(conn_handle, att_handle, data)
			#ble_prepare_write(conn_handle, att_handle, 0, data)
			
		elif (selection == 10):
			print "Disconnecting from device..."
			ble_disconnect(0)
			
		elif (selection == 11):
			print "Making discoverable..."
			ble_set_mode(3,1)
			
		elif (selection == 11):
			print "Resetting system..."
			resetBLE()
						
		elif (selection == 13):
			print "Sending Hello..."
			ble_hello()
			
		elif (selection == 14):
			print "Getting info..."
			ble_get_info()
			
		elif (selection == 15):
			print "Initializing..."
			initializeBLE()
			
		elif (selection == 99):
			print "Closing..."
		else:
			print "Not an option."

		selection = input()
		print "\n"

	# somehow we know that the handle we need to write to is 10, UUID = 0x2902
	#print "Enabling Indications by writing to UUID 0x2902..."
	# write value of 2 to UUID = 0x2902 to enable indications

	print "Disconnecting device..."
	ble_disconnect(0)
	time.sleep(2)

			
	#stop the thread which is reading packets
	read_packet_stop.set()

	ser.close()



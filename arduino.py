import serial
import time
from serial.tools import list_ports


def getPortAvalaible():
	return [tuple(p)[0] for p in list(serial.tools.list_ports.comports())]

class Arduino:
	def __init__(self,port = "com3", baudrate = 9600, timeout = 5000):
		self.ready = False
		
		self.ser = serial.Serial()
		self.port = port
		self.baudrate = baudrate
		self.timeout = timeout
		self.args = ''
		self.maximum = 100

	def connect(self, port = "com3", baudrate = "9600"):
		self.port = port
		self.baudrate = int(baudrate)
		self.ser.baudrate = self.baudrate
		self.ser.port = self.port
		self.ser.timeout = self.timeout

		try:
			self.ser.open()
			self.args = 'Connected'
			self.ready = self.ser.is_open
			msg = self.getData()
			# self.maximum = int(self.sendAndGetDataOnly("MAX?"))
			return "CONN, "+msg

		except serial.SerialException as e:
			self.args = e
			self.ready = self.ser.is_open
			return "ERROR,"+ str(e)

		except OSError as e:
			self.args = e
			self.ready = self.ser.is_open
			return "ERROR,"+ str(e)

	def disconnect(self):
		self.ser.close()
		self.args = "Port are close"
		self.ready = self.ser.is_open

	def checkStatus(self):
		# return dir(self.ser)
		return self.ser.isOpen()

	def getData(self):
		self.ready = self.ser.is_open
		if self.ser.is_open:
			try:
				# self.ser.open()
				x = self.ser.readline()
				x = x.decode("utf-8")
				x = x.rstrip()
				self.args = x
				return "DATA," + x
				# self.ser.close()
			except serial.SerialException as e:
				self.ser.close()
				self.ready = self.ser.is_open
				self.args = e
				return "ERROR,"+ str(e)
	
			except OSError as e:
				self.ser.close()
				self.ready = self.ser.is_open
				self.args = e
				return "ERROR,"+ str(e)

		elif not self.ser.is_open:
			self.ready = False
			return("ERROR, port are closed")

	def sendData(self, data):
		self.ready = self.ser.is_open
		if self.ser.is_open:
			try:
				# self.ser.open()
				x = self.ser.write(data.encode())
				self.args = data
				return "SEND," + data
				# self.ser.close()
			except serial.SerialException as e:
				self.ser.close()
				self.ready = self.ser.is_open
				self.args = e
				return "ERROR,"+ str(e)
	
			except OSError as e:
				self.ser.close()
				self.ready = self.ser.is_open
				self.args = e
				return "ERROR,"+ str(e)

		elif not self.ser.is_open:
			self.ready = False
			return("ERROR, port are closed")

	def sendAndGet(self, msg):
		self.sendData(msg)
		return self.getData()

	def sendAndGetDataOnly(self, msg):
		if self.ready:
			self.sendData(msg)
			data = self.getData()
			adata = data.split(",")
			if adata[0] == "DATA":
				return adata[1]
			if adata[0] != "DATA":
				return data

		elif not self.ready:
			return "ERROR, "+self.args

	def doMove(self, direction, jarak):
		if self.ready:
			msg = "MOVE,"+str(direction)+","+str(jarak)
			self.sendData(msg)
			#  This will wait for arduino respon.
			return self.getData()

	def getMaximum(self):
		self.maximum = int(self.sendAndGetDataOnly("MAX?"))
		return self.maximum

if __name__ =="__main__":
	ard = Arduino()
	conn = ard.connect()
	print(conn)
	print(ard.maximum)

	# ard.disconnect()	
	# print(data)

	# while True:
	# 	print(ard.checkStatus())
	# 	time.sleep(1)
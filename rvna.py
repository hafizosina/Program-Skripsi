import pyvisa as visa  
import time

def tampilkanData(datas, length = 0):
	if length==0:
		for d in datas:
			print(d)
	else:
		for i,data in enumerate(datas, start=1):
			print(data)
			if i>=length:
				break

class CMT(object):
	def __init__(self):
		self.rm = visa.ResourceManager()
		self.values = []
		self.ready = False
		self.lastConn = ""

	def connect(self, timeout = 50000):
		try:
			self.CMT = self.rm.open_resource('TCPIP0::localhost::5025::SOCKET')
			self.CMT.read_termination='\n'	
			self.CMT.timeout = timeout
			self.ready = True	
			return "CONNECT"
		except visa.VisaIOError as e:
			self.ready = False
			self.lastConn = str(e)
			return "ERROR,"+str(e)
		except Exception as e:
			self.ready = False
			self.lastConn = str(e)
			return "ERROR,"+str(e)

	def disconnect(self):
		# print(dir(self.CMT))
		# self.rm.close()
		if self.ready:
			self.CMT.close()
			self.ready = False
		self.ready = False

	def clear(self):
		if self.ready:
			self.CMT.write_ascii_values(f'CLS\n',self.values)

	def reset(self):
		if self.ready:
			self.CMT.write_ascii_values(f'RST\n',self.values)

	def checkIDN(self):
		if self.ready:
			return self.CMT.query("IDN?")

	def systemRes(self):
		if self.ready:
			self.CMT.write_ascii_values(f'SYST:PRES\n',self.values)

	def setStartFreq(self, freq):
		if self.ready:
			self.CMT.write_ascii_values(f'SENS:FREQ:STAR {freq} MHZ\n',self.values)

	def setStopFreq(self, freq):
		if self.ready:
			self.CMT.write_ascii_values(f'SENS:FREQ:STOP {freq} MHZ\n',self.values)

	def setTrigMode(self, trigType):
		if self.ready:
			self.CMT.write_ascii_values(f'TRIG:SOUR {trigType}\n',self.values)

	def setNumberPoint(self, point):
		if self.ready:
			self.CMT.write_ascii_values(f'SENS:SWE:POIN {point}\n',self.values)  #Number of points
			self.point = int(point)

	def setCalcFormat(self, form): 
		if self.ready:
			self.CMT.write_ascii_values(f'CALC:FORM {form}\n',self.values)  #log Mag forma

	def setStartDis(self, star):
		if self.ready:
			self.CMT.write_ascii_values(f'CALC:TRAN:TIME:STAR {star}\n',self.values)

	def setStopDis(self, stop):
		if self.ready:
			self.CMT.write_ascii_values(f'CALC:TRAN:TIME:STOP {stop}\n',self.values)

	def getData(self):
		data = []
		try:
			data = self.CMT.query('CALC:DATA:FDAT?\n')
			data = data.split(",")
			data = data[::2]
			data = [float(d) for d in data]
		except visa.VisaIOError as e:
			data.append("ERROR,"+str(e))
		except Exception as e:
			data.append("ERROR,"+str(self.lastConn))
		return data

	def getData2D(self, x):
		data = []
		for i in range(x):
			d = self.getData()
			if d[0]=="ERROR":
				data=[]
				break
			elif d[0]!="ERROR":
				data.append(d)
		return data

if __name__=="__main__":
	print("Begin")
	RADAR = CMT()
	print("Get")
	x = RADAR.connect(5000)
	print("Connect")
	print()
	# RADAR.setTrigMode('BUS')
	print(x)

	RADAR.systemRes()
	print("Reset")
	print()


	print("begin stpe 2")
	RADAR.setStartDis(0)
	RADAR.setStopDis(10)	
	RADAR.setStartFreq(3500)
	RADAR.setStopFreq(5300)
	RADAR.setNumberPoint(200)
	RADAR.setCalcFormat('DRLO')
	print()

	print("sleeep")
	time.sleep(3)
	print()

	print("get data")
	data = RADAR.getData()
	print(data)

	# data = RADAR.getData2D(10)
	# tampilkanData(data)

	RADAR.disconnect()

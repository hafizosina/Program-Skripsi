import sys
import matplotlib
import random
import pandas as pd
import numpy as np
import math

from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QThread, pyqtSignal, QTimer


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np

from tools import *
from rvna import *
from arduino import Arduino, getPortAvalaible



matplotlib.use('Qt5Agg')

################################################################
#   THREADING
################################################################

class MyThread(QThread):
	progress = pyqtSignal(int,list)
	finished = pyqtSignal()
	def __init__(self, RADAR, ARD):
		QThread.__init__(self, None)
		self.step   = 10
		self.dprogress = 100/self.step
		self.RADAR = RADAR
		self.ARD = ARD
		self.delta = int(self.ARD.maximum/self.step)
		self.RADAR.setStartDis(0)
		self.RADAR.setStopDis(10)

	def setValue(self, startD = None, stopD = None, step = None):
		if self.RADAR.ready:
			if startD != None and type(startD) == int :
				self.RADAR.setStartDis(startD)
			if stopD  != None and type(stopD) == int :
				self.RADAR.setStopDis(stopD)
			if step   != None:
				self.step   = step

	def getData(self):
		if self.RADAR.ready:
			return self.RADAR.getData()
		elif not self.RADAR.ready:
			return self.RADAR.lastConn[0].split(",")

	def run(self):
		pgr = 0

		if self.step>1 and self.ARD.ready and self.RADAR.ready:
			step = self.step-1
			self.ARD.getMaximum() # this put right here to prevent lag while connecting to arduino
			self.dprogress = 100/step
			self.delta = math.ceil(self.ARD.maximum/step)
			i = 0
			msg = "DATA,MOVE,0"
			for r in range(0,self.ARD.maximum,self.delta):
				i+=1

				if msg.split(",")[1] == "MOVE":
					data = self.getData()
				elif msg.split(",")[0] == "ERROR":
					data = msg.split(",")

				msg = self.ARD.doMove(1,self.delta)
				
				pgr += self.dprogress
				self.progress.emit(pgr,data)
			r = self.ARD.maximum

			if msg.split(",")[1] == "MOVE":
				data = self.getData()
			elif msg.split(",")[0] == "ERROR":
				data = msg.split(",")

			self.progress.emit(100,data)
			self.finished.emit()
		elif (self.step==1 or not self.ARD.ready) and self.RADAR.ready:	
			data = self.getData()
			self.progress.emit(100,data)
			self.finished.emit()


################################################################
#   PLOTING
################################################################

class PlotCanvas(FigureCanvas):
	def __init__(self, parent=None, width=5, height=4, dpi=100):
		fig = Figure(figsize=(width, height), dpi=dpi)
		self.axes = fig.add_subplot(111)

		FigureCanvas.__init__(self, fig)
		self.setParent(parent)

		FigureCanvas.setSizePolicy(self,
				QSizePolicy.Expanding,
				QSizePolicy.Expanding)
		FigureCanvas.updateGeometry(self)

	def contourf(self, values = []):
		ax = self.figure.add_subplot(111)
		ax.contourf(values)
		self.draw()

	def plot(self, values = []):
		ax = self.figure.add_subplot(111)
		ax.plot(values)
		self.draw()

################################################################
#   MAIN UI
################################################################

class Ui(QtWidgets.QMainWindow):
	def __init__(self):
		super(Ui, self).__init__()
		uic.loadUi('display2.ui', self) 
		self.setWindowTitle("Land Slide Monitoring")
		self.graph = PlotCanvas(self)
		self.verticalLayout.addWidget(self.graph)

		self.cmbxPort.addItems(getPortAvalaible())
		self.cmbxBaudrate.addItems(["1200", "2400", "4800", "9600", "14400", "19200", "38400", "31250", "57600",
									 "74880", "115200"])
		self.cmbxBaudrate.setCurrentIndex(3)


		######################################
		#   Variable Awal Raadar
		self.stopF = 5300
		self.bandW = 201
		self.firstTime = True
		self.boxData = []

		self.ARD = Arduino()
		self.RADAR = CMT()
		self.timerCheckPort = QTimer()
		# self.thread = Work()
		self.thread = MyThread(self.RADAR, self.ARD)

		self.connectAction()

	def connectAction(self):
		self.btnRADAR.clicked.connect(self.setupRadar)
		self.btnARD.clicked.connect(self.setupArduino)
		self.btnGetData.clicked.connect(self.startThreadData)
		self.thread.progress.connect(self.prbrProgressThread)
		self.thread.finished.connect(self.showData)
		self.timerCheckPort.timeout.connect(self.checkPort)
		self.timerCheckPort.start(1000)

	def setupRadar(self):
		if self.btnRADAR.text() == "Connect":
			conn = self.RADAR.connect(5000)
			if self.RADAR.ready:
				self.RADAR.setCalcFormat("DRLO")
				self.RADAR.setStartFreq(self.inputStartF.text())
				self.RADAR.setStopFreq(self.inputStopF.text())
				self.RADAR.setNumberPoint(self.inputPoint.text())
				self.ledRADAR.setStyleSheet("background-color: rgb(0, 255, 0);border-radius:7px;")
				self.btnRADAR.setText("Disconnect")
			elif not self.RADAR.ready:
				print("Disconnect Con")
				self.ledRADAR.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")
				self.btnRADAR.setText("Connect")
		
		elif self.btnRADAR.text() == "Disconnect":
			self.RADAR.disconnect()
			self.ledRADAR.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")
			self.btnRADAR.setText("Connect")    

		if self.RADAR.ready:
			self.btnGetData.setEnabled(True)
		elif not self.RADAR.ready:
			self.btnGetData.setEnabled(False)

	def setupArduino(self):
		if self.btnARD.text() == "Connect":
			self.ARD.connect(self.cmbxPort.currentText(), self.cmbxBaudrate.currentText())
			if self.ARD.ready:
				self.btnARD.setText("Disconnect")
				self.ledARD.setStyleSheet("background-color: rgb(0, 255, 0);border-radius:7px;")
			elif not self.ARD.ready:
				self.btnARD.setText("Connect")
				self.ledARD.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")
		elif self.btnARD.text() == "Disconnect":
			self.ARD.disconnect()
			if self.ARD.ready:
				self.btnARD.setText("Disconnect")
				self.ledARD.setStyleSheet("background-color: rgb(0, 255, 0);border-radius:7px;")
			elif not self.ARD.ready:
				self.btnARD.setText("Connect")
				self.ledARD.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")

	def checkPort(self):
		self.cmbxPort.clear()
		x = getPortAvalaible()
		self.cmbxPort.addItems(x)

		self.timerCheckPort.setSingleShot(True)
		self.timerCheckPort.start(1000)
		if self.btnARD.text() == "Disconnect":
			if len(x) == 0:
				self.ARD.ready = False
				self.btnARD.setText("Connect")
				self.ledARD.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")


	def startThreadData(self):
		print("BEGIN")
		self.boxData.clear()
		self.thread.setValue(int(self.inputStartD.text()), int(self.inputStopD.text()), int(self.inputStep.text()) )
		self.thread.start() 
		
		self.prbrGetData.setValue(0)
		self.btnRADAR.setEnabled(False)
		self.btnARD.setEnabled(False)
		self.btnGetData.setEnabled(False)

	def prbrProgressThread(self, x, data):
		self.prbrGetData.setValue(x)
		if len(data)==self.RADAR.point:
			printArray(data,5," ")
			self.boxData.append(data)
		else: # todo ADD CALL ERROR
			print(data)

	def showData(self):
		self.btnRADAR.setEnabled(True)
		self.btnARD.setEnabled(True)
		self.btnGetData.setEnabled(True)
		if (len(self.boxData)==self.thread.step) and (len(self.boxData)>1):
			self.graph.contourf(self.boxData)
		print("DONE!")
			
if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = Ui()
	window.show()
	app.exec_()

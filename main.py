import sys
import matplotlib
import random
import pandas as pd
import numpy as np

from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox,
							 QWidget, QPushButton)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer


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

class Work(QThread):
	change_value = pyqtSignal(int)
	finished = pyqtSignal()
	data = pyqtSignal(list)
	timer = 1
	def run(self):
		cnt = 0
		while cnt < 100:
			cnt+=1
			time.sleep(self.timer)
			data = [random.randint(0,30) for _ in range(10)]
			self.data.emit(data)
			self.change_value.emit(cnt)
		self.finished.emit()

class MyThread(QThread):
	progress = pyqtSignal(int,str)
	finished = pyqtSignal()
	def __init__(self, RADAR, ARD):
		QThread.__init__(self, None)
		self.timer = 0.1
		self.step   = 10
		self.dprogress = int(100/self.step)
		self.RADAR = RADAR
		self.ARD = ARD
		self.delta = int(self.ARD.maximum/self.step)
		self.RADAR.setStartDis(startD)
		self.RADAR.setStopDis(stopD)

	def setValue(self, startD = None, stopD = None, step = None):
		if self.RADAR.ready:
			if startD != None and type(startD) == int :
				self.RADAR.setStartDis(startD)
			if stopD  != None and type(stopD) == int :
				self.RADAR.setStopDis(stopD)
			if step   != None:
				self.step   = step
				self.dprogress = int(100/self.step)
				self.delta = int(self.ARD.maximum/self.step)

	def doMove(self):
		print("move")

	def getData(self):
		if self.RADAR.ready and self.ARD.ready:
			return self.RADAR.getData()
		elif not self.ARD.ready:
			return self.ARD.args
		elif not self.RADAR.ready:
			return self.RADAR.lastConn

	def run(self):
		pgr = 0
		for i in range(1,self.ARD.maximum,self.step):
			self.progress.emit(i,str(i))
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
		self.data = []

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
		self.thread.progress.connect(self.prbrGetData.setValue)
		self.thread.finished.connect(self.showData)
		self.timerCheckPort.timeout.connect(self.checkPort)
		self.timerCheckPort.start(1000)

	def setupRadar(self):
		if self.btnRADAR.text() == "Connect":
			conn = self.RADAR.connect()
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
			print("wierd")
			self.RADAR.disconnect()
			self.ledRADAR.setStyleSheet("background-color: rgb(255, 0, 0);border-radius:7px;")
			self.btnRADAR.setText("Connect")    

		if self.RADAR.ready and self.ARD.ready:
			self.btnGetData.setEnabled(True)
		elif not self.RADAR.ready or not self.ARD.ready:
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

		if self.RADAR.ready and self.ARD.ready:
			self.btnGetData.setEnabled(True)
		elif not self.RADAR.ready or not self.ARD.ready:
			self.btnGetData.setEnabled(False)

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
		self.thread.setValue(self.inputStartD, self.inputStopD, self.inputStep )
		self.thread.start() 
		self.btnRADAR.setEnabled(False)
		self.btnARD.setEnabled(False)

	def showData(self):
		self.btnRADAR.setEnabled(True)
		self.btnARD.setEnabled(True)
		print("DONE!")

	def getRadarData(self):
		if self.RADAR.ready == True:
			gstartF = self.inputStartF.text()
			gstopF = self.inputStopF.text()
			gbandW = self.inputBandW.text()
			if self.firstTime:
				self.startF = gstartF
				self.stopF = gstopF
				self.bandW = gbandW
				self.RADAR.setStartFreq(self.startF)
				self.RADAR.setStopFreq(self.stopF)
				self.RADAR.setNumberPoint(self.bandW)
				self.firstTime = False

			if self.startF!=gstartF:
				self.RADAR.setStartFreq(self.startF)
				self.startF = gstartF
			if self.stopF!=gstopF:
				self.RADAR.setStartFreq(self.stopF)
				self.stopF = gstopF
			if self.bandW!=gbandW:
				self.RADAR.setStartFreq(self.bandW)
				self.bandW = bandW
			data = self.manipulateData()
			return data

	def manipulateData(self):
		data = np.random.rand(100, int(self.bandW))
		return data
			
if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	window = Ui()
	window.show()
	app.exec_()

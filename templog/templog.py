from time import sleep
import numpy as np
import serial
import time
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import threading

global last_data

def main():
	c = logger(50)
	try:
		c.start()
	except KeyboardInterrupt:
		c.stop()

class plot(object):
	def __init__(self):
		app = QtGui.QApplication([])
		win = pg.GraphicsWindow(title="Temperature Log")
		win.resize(800, 600)
		self.p = win.addPlot(title = "temp plot")
		self.curve = self.p.plot(pen = 'y')
		self.ptr = 0
		self.data = [0] * 1000
		t = threading.Thread(target = self.start_plot)
		t.daemon = True
		t.start()
		pg.QtGui.QApplication.exec_()
	def start_plot(self):
		while True:
			self.update_plot()
			time.sleep(1.0/25.)
	def update_plot(self):
		global last_data
		self.curve.setData(self.data)

		self.ptr += 1
		self.data.pop()
		self.data.insert(0, last_data)
	
class logger(object):
	def __init__(self, freq):
		self.t0 = int(time.time())
		self.ser = serial.Serial('/dev/ttyACM0', 1200)
		self.last_data = 0
		self.f = open('temperaturelog', 'w')
		self.freq = float(freq)
	def start(self):
		print "ayyy"
		global last_data
		while True:
			#print "!!!!"
			dt = str(time.time() - self.t0)[:4]
			try:
				z = int(self.ser.readline())
				print z
				last_data = z
				self.f.write(dt + ' ' + str(z) + '\n')
			except:
				pass
			sleep(1.0/self.freq)
	def stop(self):
		self.f.close()
		print "Logging interrupted / stopped"



if __name__ == '__main__':
	t = threading.Thread(target = main)
	t.daemon = True
	t.start()

	g = plot()

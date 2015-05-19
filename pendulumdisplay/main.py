from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import time
import threading
import serial
import colorsys
import datetime
def main():
	p = plot()


class logger(object):
	def __init__(self):
		self.ser = serial.Serial('/dev/ttyACM0', 2400)
		self.sb = '---'
		self.eb = '==='
		self.sw = 0 # 1 --> started
	def start(self):
		while True:
			while self.sw == 0:
				d = ser.readline()
				print d
				if d == self.sb:
					self.sw = 1
			data = [ser.readline() for a in xrange(10)]
			time.sleep(0.01)
			self.sw = 0

class plot(object):
	def __init__(self):
		self.f = open('log','w')
		self.f.write(str(datetime.datetime.now()))
		app = QtGui.QApplication([])
		win = pg.GraphicsWindow(title="Arduino LDR Plot")
		win.resize(1000, 600)
		win.setWindowTitle('Arduino LDR Plot')
		pg.setConfigOptions(antialias = True)
		self.p = win.addPlot(title = "Arduino LDR Plot")
		self.p.setYRange(0,1000, padding = 0)
		#self.c0 = self.p.plot(pen = 'w')
		N = 10
		self.t0 = time.time()
		HSV_tuples = [(x * 1.0/N, 0.5, 0.5) for x in xrange(10)]
		RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
		RGB_tuples = map(lambda y: tuple(y + [100.0]), map(lambda x: map(lambda z: z * 255.0, x), RGB_tuples))
		#self.curve = self.p.plot(pen = (255, 0,0))
		#print RGB_tuples
		self.curves = [self.p.plot(pen = RGB_tuples[x]) for x in xrange(10)]
		#data = np.random.normal(size = (10, 1000))
		self.ser = serial.Serial('/dev/ttyACM0', 2400)
		self.sb = '---'
		self.eb = '==='
		self.sw = 0 # 1 --> started
		self.ptr = 0
		#self.data = [[np.random.normal() for i in xrange(100)] for j in xrange(10)]
		#self.data = list(np.random.normal(size = 1000))
		self.data = [[0.0] * 1010] * 10
		self.sma = [[0.0] * 1000] * 10
		#t1 = threading.Timer(1.0, self.debug)
		#t1.daemon = True
		#t1.start()
		t = threading.Thread(target = self.start_plot)
		t.daemon = True
		t.start()
		d = threading.Thread(target = self.read_data)
		d.daemon = True
		d.start()
		s = threading.Thread(target = self.update_sma)
		s.daemon = True
		s.start()


		pg.QtGui.QApplication.exec_()
	def start_plot(self):
		while True:
			self.update_plot()
			time.sleep(0.020) # 40 Hz writing but extra time for buffer
	def debug(self):
		print self.data
		print self.sma
	def update_sma(self, window = 10):
		while True:
			for i in xrange(len(self.sma)):
				weights = np.repeat(1.0,window)/window
				smas = np.convolve(self.data[i], weights, 'valid')
				self.sma[i] = list(smas)
			time.sleep(0.015)
	def read_data(self):
		while True:
			c = 0
			d = self.ser.readline().rstrip()
					
			if len(d) == 3:
				if d == self.sb:
					self.sw = 1
					c = 0
				elif d == self.eb:
					self.sw = 0
					
			else:
				self.data[c].pop()
				self.f.write(str(d) + '\n')				
				try:
					#print 'hm'
					#assert float(d)
					self.data[c].insert(0, float(d))
					print str(time.time() -self.t0) + '\t' + str(d)
				except:
					print "error. sorry."
					print d
					print datetime.datetime.now()
					self.data[c].insert(0, 100)
					pass
				c += 1
			
	def update_plot(self):
		#print sum(self.sma[0])
		for i in xrange(10):
			try:
				#print self.data[i]
				self.curves[0].setData(self.sma[0])
			except:
				print "DEATH ERROR"
				#print self.data[i]
				pass
		if self.ptr == 100:
			print('disabled auto range')
			self.p.enableAutoRange('xy', False)
		self.ptr += 1

if __name__ == '__main__':
	main()

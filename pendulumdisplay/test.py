import serial
import time
ser = serial.Serial('/dev/ttyACM0',2400)
t0 = time.time()
while True:
	t = time.time()
	dt = t - t0
	try:
		print str(dt) + '\t' + ser.readline().rstrip()
		time.sleep(0.005)
	except KeyboardInterrupt:
		break

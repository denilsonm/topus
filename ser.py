import RPi.GPIO as gpio
import time
import serial
import struct

ser = serial.Serial("/dev/ttyAMA0", 115200)
gpio.setmode(gpio.BOARD)
gpio.setup(18, gpio.IN)

print("Comecando")

ser.write("L")

print("L enviado")

def readUnsignedInt16():
	r = ser.read(size=2)
	
	buf=0
	for i in [1, 0]:
		buf = buf*256 + ord(r[i])

	return buf

def readUnsignedInt32():
	r = ser.read(size=4)

	buf=0
	for i in [3, 2, 1, 0]:
		print(ord(r[i]))
		buf = buf*256 + ord(r[i])

	return buf

def readInt16():
	s = struct.pack('>H', readUnsignedInt16())
	return struct.unpack('>h', s)[0]

def readFloat32():
	s = struct.pack('>I', readUnsignedInt32())
	return struct.unpack('>f', s)[0]

def readByte():
	r = ser.read(size=1)

	return ord(r[0])

print(readInt16())

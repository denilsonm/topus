# -*- coding: utf-8 -*-

import time
import serial
import struct

def readUnsignedInt16(ser):
	r = ser.read(size=2)
	
	buf=0
	for i in [1, 0]:
		buf = buf*256 + ord(r[i])

	return buf

def readUnsignedInt32(ser):
	r = ser.read(size=4)

	buf=0
	for i in [3, 2, 1, 0]:
		print(ord(r[i]))
		buf = buf*256 + ord(r[i])

	return buf

def readInt16(ser):
	s = struct.pack('>H', readUnsignedInt16(ser))
	return struct.unpack('>h', s)[0]

def readInt32(ser):
	s = struct.pack('>I', readUnsignedInt32(ser))
	return struct.unpack('>i', s)[0]

def readFloat32(ser):
	s = struct.pack('>I', readUnsignedInt32(ser))
	return struct.unpack('>f', s)[0]

def readByte(ser):
	r = ser.read(size=1)

	return ord(r[0])

read_map = [
	["unsignedInt16"] = readUnsignedInt16,
	["unsignedInt32"] = readUnsignedInt32,
	["int16"] = readInt16,
	["int32"] = readInt32,
	["float32"] = readFloat32,
	["byte"] = readByte
]

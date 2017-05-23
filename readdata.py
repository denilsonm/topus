# -*- coding: utf-8 -*-

import time
import serial
import struct

def readUnsignedInt16(lst):
	buf=0
	for i in [1, 0]:
		buf = buf*256 + ord(lst[i])

	return buf

def readUnsignedInt32(lst):
	buf=0
	for i in [3, 2, 1, 0]:
		buf = buf*256 + ord(lst[i])

	return buf

def readInt16(lst):
	s = struct.pack('>H', readUnsignedInt16(lst))
	return struct.unpack('>h', s)[0]

def readInt32(lst):
	s = struct.pack('>I', readUnsignedInt32(lst))
	return struct.unpack('>i', s)[0]

def readFloat32(lst):
	s = struct.pack('>I', readUnsignedInt32(lst))
	return struct.unpack('>f', s)[0]

def readByte(lst):
	return lst[0]

read_map = {
	"unsignedInt16": readUnsignedInt16,
	"unsignedInt32": readUnsignedInt32,
	"int16": readInt16,
	"int32": readInt32,
	"float32": readFloat32,
	"byte": readByte
}

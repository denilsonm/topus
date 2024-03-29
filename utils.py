# -*- coding: utf-8 -*-

import os

# Bytes de controle que a XBee no solo pode mandar
# para o foguete
CONST_START_TRANSMISSION = 0
CONST_REQUEST_ALIGN = 1
CONST_END_TRANSMISSION = 2

class FileWrite:
	def __init__(self, filename, mode):
		self.filename = filename

		self.file = open(filename, mode)

	def write_bytes(self, byte_list):
		self.file.write(
			bytearray(
				byte_list
			)
		)

	def close(self):
		self.file.flush()
		self.file.close()

def availableName():
	i=0

	while os.path.exists("rocketdata.bin." + str(i)):
		i=i+1;

	return "rocketdata.bin." + str(i)
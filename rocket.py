# -*- coding: utf-8 -*-

from packettypes import *
from stream import *
import packet
import utils

import serial

import Queue
from threading import Thread
import time

# Thread para escrever no cartão SD

write_to_sd = Queue.Queue()

def writeThread(write_to_sd):
	filewrite = utils.FileWrite("rocketdata.bin", "wb")

	while True:
		while write_to_sd.empty():
			time.sleep(1)

		while not write_to_sd.empty():
			packet = write_to_sd.get()

			if type(packet) != list:
				break
			else:
				filewrite.write_bytes(packet)

	filewrite.close()

# Configurações

keep_transmitting = True

arduino_serial = serial.Serial("/dev/ttyAMA0", 115200)
xbee_serial = serial.Serial("/dev/ttyUSB0", 230400)
arduino_stream = Stream(ser=arduino_serial, check_hash=False)

write_thread = Thread(target=writeThread, args=[write_to_sd])
write_thread.start()

ground_data = 256

# Começo do programa

print("Aguardando pedido para começar transmissão...")

while ground_data != utils.CONST_START_TRANSMISSION:
	ground_data = ord(xbee_serial.read(size=1)[0])

arduino_serial.write("L")

print("Recebido! Começando transmissão...")

arduino_packet_queue = Queue.Queue()

while keep_transmitting:

	# A prioridade é ler tudo que há na arduino na máxima velocidade possível
	while arduino_serial.in_waiting > 0:
		print("Received")
		# Lemos os dados da serial do arduino
		arduino_stream.read_serial()
		new_packets = arduino_stream.retrieve_packets()

		for new_packet in new_packets:
			write_to_sd.put(new_packet)

			Stream.prepare_for_transmission(new_packet)

			for packet_byte in new_packet:
				arduino_packet_queue.put(packet_byte)

	if xbee_serial.cts:

		# Se o foguete recebeu um dado pela serial da XBee, 
		# então o solo enviou um byte de controle
		if xbee_serial.in_waiting > 0:
			ground_data = ord(xbee_serial.read(size=1)[0])
			print("Received from ground: " + str(ground_data))

			if ground_data == utils.CONST_END_TRANSMISSION:
				keep_transmitting = False

		while xbee_serial.cts and not arduino_packet_queue.empty():	
			# Transmitimos pela xbee
			print("Transmitting")
			xbee_serial.write(chr(arduino_packet_queue.get()))

write_thread.join()


####################################3

# keep_transmitting = True

# arduino_serial = serial.Serial("/dev/ttyAMA0", 115200)
# xbee_serial = serial.Serial("/dev/ttyUSB0", 230400)
	
# # A transmissão de dados pela serial entre a Arduino e a Raspberry
# # Pi provavelmente não vai falhar
# packet.Packet.check_input = False

# # Usando XBee, por outro lado...
# packet.Packet.hash_output = True

# ground_data = 256

# sdwrite = utils.FileWrite("rocketdata.binary", "wb")

# print("Aguardando pedido para começar transmissão...")

# while ground_data != utils.CONST_START_TRANSMISSION:
# 	ground_data = ord(xbee_serial.read(size=1)[0])

# arduino_serial.write("L")

# print("Recebido! Começando transmissão...")

# arduino_packet_queue = Queue.Queue()

# arduino_stream = 

# while keep_transmitting:

# 	# A prioridade é ler tudo que há na arduino na máxima velocidade possível
# 	while arduino_serial.in_waiting > 0:
# 		print("Received")
# 		# Lemos os dados da serial do arduino
# 		status, packet_data = packet.Packet.read_packet(arduino_serial)

# 		arduino_packet_queue.put(packet_data)

# 		# Escrevemos no arquivo rocketdata.binary
# 		sdwrite.write_bytes(packet_data)

# 	if xbee_serial.cts:

# 		# Se o foguete recebeu um dado pela serial da XBee, 
# 		# então o solo enviou um byte de controle
# 		if xbee_serial.in_waiting > 0:
# 			ground_data = ord(xbee_serial.read(size=1)[0])
# 			print("Received ctrnl " + str(ground_data))

# 			if ground_data == utils.CONST_END_TRANSMISSION:
# 				keep_transmitting = False
# 				break

# 			elif ground_data == utils.CONST_REQUEST_ALIGN:
# 				xbee_serial.write(chr(255))

# 		while xbee_serial.cts and not arduino_packet_queue.empty():	
# 			# Transmitimos pela xbee
# 			print("Transmitting")
# 			packet.Packet.transmit_packet(xbee_serial, arduino_packet_queue.get())

# sdwrite.close()
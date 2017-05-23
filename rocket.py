from packettypes import *
import packet
import utils

import serial

import Queue

keep_transmitting = True

arduino_serial = Serial("/dev/ttyAMA0", 115200)
xbee_serial = Serial("/dev/ttyUSB0", 230400)
	
# A transmissão de dados pela serial entre a Arduino e a Raspberry
# Pi provavelmente não vai falhar
packet.Packet.check_input = False

# Usando XBee, por outro lado...
packet.Packet.hash_output = True

ground_data = 256

sdwrite = utils.FileWrite("rocketdata.binary", "wb")

print("Aguardando pedido para começar transmissão...")

while ground_data != utils.CONST_START_TRANSMISSION:
	ground_data = ord(xbee_serial.read(size=1)[0])

arduino_serial.write("L")

print("Recebido! Começando transmissão...")

arduino_packet_queue = Queue.Queue()

while keep_transmitting:

	# A prioridade é ler tudo que há na arduino na máxima velocidade possível
	while arduino_serial.in_waiting > 0:
		# Lemos os dados da serial do arduino
		status, packet_data = packet.Packet.read_packet(arduino_serial)

		arduino_packet_queue.put(packet_data)

		# Escrevemos no arquivo rocketdata.binary
		sdwrite.write_bytes(packet_data)

	if xbee_serial.cts:

		# Se o foguete recebeu um dado pela serial da XBee, 
		# então o solo enviou um byte de controle
		if xbee_serial.in_waiting > 0:
			ground_data = ord(xbee_serial.read(size=1)[0])

			if ground_data == utils.CONST_END_TRANSMISSION:
				keep_transmitting = False
				break

			elif ground_data == utils.CONST_REQUEST_ALIGN:
				xbee_serial.write(chr(255))

		while xbee_serial.cts and not arduino_packet_queue.empty():	
			# Transmitimos pela xbee
			packet.Packet.transmit_packet(xbee_serial, arduino_packet_queue.get())

sdwrite.close()
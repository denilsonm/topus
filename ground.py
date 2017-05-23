# -*- coding: utf-8 -*-

from packettypes import *
import packet
import utils

import serial
from threading import Thread
import datetime
import time
import mutex

xbee_serial = Serial("/dev/ttyUSB0", 230400)

keep_receiving = True
transmission_ended = False

serial_mutex = mutex.mutex()

def readInput():
	while raw_input() != "stop":
		pass

	keep_receiving = False


	while not transmission_ended:
		serial_mutex.lock()
		while not xbee_serial.cts:
			pass

		xbee_serial.write(chr(utils.CONST_END_TRANSMISSION))
		serial_mutex.unlock()

		time.sleep(1)

# A transmissão de dados entre as XBees não é confiável,
# precisamos verificar os checksums dos pacotes
packet.Packet.check_input = True

sdwrite = utils.FileWrite("rocketdata.binary", "wb")

print("Enviando um pedido para que a transmissão comece...")

xbee_serial.write(chr(utils.CONST_START_TRANSMISSION))

input_thread = Thread(target=readInput)
input_thread.start()

last_received = datetime.datetime.now()
last_align_request = datetime.datetime.now() - datetime.timedelta(minutes=30)
last_packet_failed = False

while not transmission_ended:
	serial_mutex.lock()

	# Se o buffer de entrada da XBee não estiver vazio, tentamos ler os dados
	while xbee_serial.in_waiting > 0:
		status, packet_data = packet.Packet.read_packet(xbee_serial)
		serial_mutex.unlock()

		# Se a leitura não for bem sucedida, então:
		# 	- Se a última leitura foi bem sucedida, não fazer nada
		#	- Se a última leitura não foi bem sucedida também,
		#		éntão podemos ter um problema de alinhamento.
		# 		Nesse caso, pedimos um demarcador de alinhamento
		# 		Mais especificamente, fazemos esse pedido 1x por 
		# 		segundo até que o delimitador chegue

		if not status:
			if last_packet_failed:
				while last_packet_failed:
					serial_mutex.lock()
					while > xbee_serial.in_waiting > 0:
						r = ord(xbee_serial.read(size=1)[0])
						if r == 255:
							last_packet_failed = False
					serial_mutex.unlock()

					if last_packet_failed and datetime.datetime.now() - last_packet_failed > datetime.timedelta(seconds=1):
						serial_mutex.lock()
						while xbee_serial.cts:
							pass
						xbee_serial.write(chr(CONST_REQUEST_ALIGN))
						serial_mutex.unlock()


			else:
				last_packet_failed = True
		else:
			last_packet_failed = False

		last_received = datetime.datetime.now()
		serial_mutex.lock()

	serial_mutex.unlock()

	# Se o usuário já pediu que a transmissão cesasse e não obtivemos nenhum pacote por 
	if not keep_receiving and datetime.datetime.now() - last_received > datetime.timedelta(seconds=10):
		transmission_ended = True

transmission_ended = True
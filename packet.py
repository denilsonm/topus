# -*- coding: utf-8 -*-

import readdata
import datatypes
import serial

sensor_map = {}

class Packet:
	# Todo pacote começa com um byte, sendo que os primeiros 8-sensor_bits bits sao de checksum
	# e os proximos sensor_bits bits identificam um sensor. um pacote que começa com o byte 0xFF
	# é destinado exclusivamente ao controle do fluxo de dados
	sensor_bits = 3
	
	sensor_mask = None
	checksum_mask = None

	# Se check_input for True, entao a origem produz checksums e coloca junto com o primeiro byte,
	# que identifica os sensores. Se hash_output for True, entao o programa gerará os checksums para colocar no primeiro 
	# byte
	check_input = False
	hash_output = False

	packet_count = -1
	failure_count = 0

	def __init__(self, sensor_id=None):
		if sensor_id == None or type(sensor_id) != int or sensor_id < 0 or sensor_id >= 2**Packet.sensor_bits:
			raise ValueError("Id do sensor deve ser especificada, e nao deve ser um inteiro entre 0 e 2^sensor_bits-1.")

		self.sensor_id = sensor_id

		sensor_map[sensor_id] = self

		self.data_sequence = []
		

	def add_field(self, data_type):
		if data_type not in datatypes.data_types:
			raise ValueError("data_type invalido: " + str(data_type) + " do tipo " + str(type(data_type)))

		self.data_sequence.append(data_type)
		
	def read_specific_packet(self, ser):
		if not type(ser) == serial.Serial:
			raise ValueError("ser must be of type serial.Serial")

		data_list = []
			
		for data_type in self.data_sequence:
			for i in range(0, datatypes.data_lengths[data_type]):
				data_list.append(ord(
					ser.read(size=1)[0]
					))

		return data_list

	@staticmethod
	def hash_data(data_list):
		buff = 0

		for byte in data_list:
			buff=buff*127 + byte

		return buff & ((1<<(8-Packet.sensor_bits))-1)

	@staticmethod
	def make_masks():
		Packet.sensor_mask = 0

		for i in range(0, Packet.sensor_bits):
			Packet.sensor_mask = (Packet.sensor_mask << 1) + 1

		Packet.checksum_mask = 0

		for i in range(0, 8-Packet.sensor_bits):
			Packet.checksum_mask = (Packet.checksum_mask << 1) + 1

		Packet.checksum_mask = Packet.checksum_mask << Packet.sensor_bits

	@staticmethod
	def read_packet(ser):
		r = ord(ser.read(size=1)[0])

		if Packet.sensor_mask == None:
			Packet.make_masks()

		sensor_id = r & Packet.sensor_mask

		packet_data = [sensor_id]

		packet_data.extend(
			Packet.read_specific_packet(sensor_map[sensor_id], ser)
			)

		Packet.packet_count = Packet.packet_count + 1
		
		if Packet.check_input:
			packet_hash = Packet.hash_data(packet_data)
			original_hash = (r & Packet.checksum_mask) >> Packet.sensor_bits

			if packet_hash != original_hash:
				print("Falha no pacote #" + str(packet_count))
				Packet.failure_count = Packet.failure_count + 1

				return False, []

		return True, packet_data

	@staticmethod
	def transmit_packet(ser, packet_data):
		if Packet.hash_output:
			packet_hash = Packet.hash_data(packet_data)
			packet_data[0] = (packet_hash << Packet.sensor_bits) | packet_data[0]

		for byte in packet_data:
			print("\tTransmitting byte " + str(byte))
			ser.write(chr(byte))
# -*- coding: utf-8 -*-

import serial
import packet
import utils

class Stream:
	sensor_bits = 3

	CONST_NOT_ENOUGH_BYTES = 0
	CONST_INVALID_SENSOR = 1
	CONST_INVALID_HASH = 2
	CONST_SUCCESS = 3

	def __init__(self, ser=None, check_hash=False):
		if ser == None:
			raise ValueError("Every Stream instance needs a serial specified.")
		if not type(ser) == serial.Serial:
			raise ValueError("serial must be of type serial.Serial")

		self.data = []
		self.serial = ser
		self.check_hash = check_hash

	def read_serial(self):
		while self.serial.in_waiting > 0:
			d = ord(ser.read(size=1)[0])
			self.data.append(d)

	@staticmethod
	def hash_data(data_list):
		buff = 0

		for byte in data_list:
			buff=buff*127 + byte

		return buff

	def retrieve_packet(self):
		if len(self.data) == 0:
			return Stream.CONST_NOT_ENOUGH_BYTES, []

		hash_expected = self.data[0] >> Stream.sensor_bits
		sensor_type = self.data[0] & ((1<<Stream.sensor_bits)-1)

		if not sensor_type in packet.sensor_map:
			return Stream.CONST_INVALID_SENSOR, []

		packet_type = packet.sensor_map[sensor_type]
		packet_length = packet_type.get_length()

		# Um byte extra para o header
		if len(self.data) < 1 + packet_length:
			return Stream.CONST_NOT_ENOUGH_BYTES, []

		if self.check_hash:
			hash_generated = Stream.hash_data([sensor_type] + self.data[1:(packet_length+1)])

			if hash_generated != hash_expected:
				return Stream.CONST_INVALID_HASH

		packet_data = self.data[1:(packet_length+1)]
		packet_data[0] = sensor_type

		return Stream.CONST_SUCCESS, packet_data

	def retrieve_packets(self):
		collected_packets = []

		while True:
			retrieve_return, packet_data = self.retrieve_packet()

			if retrieve_return == Stream.CONST_NOT_ENOUGH_BYTES:
				break
			elif retrieve_return == Stream.CONST_INVALID_HASH:
				self.data.pop(0)
			elif retrieve_return == Stream.CONST_INVALID_SENSOR:
				# Nunca deveria acontecer mas... vai que né
				self.data.pop(0)
			else:
				# Sucesso
				collected_packets.append(packet_data)
				self.data = self.data[
					packet.sensor_map[packet_data[0]].get_length()+1:
					]

		return collected_packets

	@staticmethod
	def prepare_for_transmission(packet_data, hash_data=False):
		if not hash_data:
			return packet_data

		packet_hash = Stream.hash_data(packet_data) & ((1<<8-Stream.sensor_bits)-1)
		packet_hash = packet_hash << Stream.sensor_bits
		
		packet_data[0] = packet_data[0] | packet_hash
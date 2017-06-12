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
			d = ord(self.serial.read(size=1)[0])
			self.data.append(d)

	@staticmethod
	def hash_data(data_list):
		modval = 2**(8-Stream.sensor_bits)

		s0 = 0
		s1 = 0

		for byte in data_list:
			s0 = (s0 + byte) % modval
			s1 = (s1 + s0) % modval

		return s1 & ((1<<8-Stream.sensor_bits)-1)

	def retrieve_packet(self):
		if len(self.data) == 0:
			return Stream.CONST_NOT_ENOUGH_BYTES, []

		hash_expected = self.data[0] >> Stream.sensor_bits

		if self.check_hash:
			sensor_type = self.data[0] & ((1<<Stream.sensor_bits)-1)
		else:
			sensor_type = self.data[0]

		if not sensor_type in packet.sensor_map:
			return Stream.CONST_INVALID_SENSOR, []

		packet_type = packet.sensor_map[sensor_type]
		packet_length = packet_type.get_length()

		# Um byte extra para o header
		if len(self.data) < 1 + packet_length:
			# print(str(len(self.data)) + " / " + str(1+packet_length))
			return Stream.CONST_NOT_ENOUGH_BYTES, []

		if self.check_hash:
			hash_generated = Stream.hash_data([sensor_type] + self.data[1:(packet_length+1)])

			if hash_generated != hash_expected:
				return Stream.CONST_INVALID_HASH, []

		packet_data = self.data[0:(packet_length+1)]
		packet_data[0] = sensor_type

		return Stream.CONST_SUCCESS, packet_data

	def retrieve_packets(self):
		collected_packets = []

		while True:
			retrieve_return, packet_data = self.retrieve_packet()

			if retrieve_return == Stream.CONST_NOT_ENOUGH_BYTES:
				break
			elif retrieve_return == Stream.CONST_INVALID_HASH:
				print("A")
				self.data.pop(0)
			elif retrieve_return == Stream.CONST_INVALID_SENSOR:
				print("B")
				# Nunca deveria acontecer mas... vai que né
				self.data.pop(0)
			else:
				print("C, sensor " + str(packet_data[0]))
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

		packet_hash = Stream.hash_data(packet_data) << Stream.sensor_bits

		packet_data[0] = packet_data[0] | packet_hash
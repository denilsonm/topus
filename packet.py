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

	# Se check_input for True, entao a origem produz checksums e coloca junto com o primeiro byte,
	# que identifica os sensores. Se hash_output for True, entao o programa gerará os checksums para colocar no primeiro 
	# byte
	check_input = False
	hash_output = False

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
			
		for 

	@staticmethod
	def make_masks():
		sensor_mask = 0

		for i in range(0, Packet.sensor_bits):
			sensor_mask = (sensor_mask << 2) + 1

	@staticmethod
	def read_packet(ser):
		r = ord(ser.read(size=1)[0])

		if sensor_mask == None:
			make_mask()

		sensor = r & sensor_mask

		

		

		

		
		
		
		
		

# -*- coding: utf-8 -*-

import packet

# Barometro

barom = packet.Packet(sensor_id=1)
barom.add_field("unsignedInt32")
barom.add_field("float32")

# Umidade

umid = packet.Packet(sensor_id=2)
umid.add_field("unsignedInt32")
umid.add_field("float32")

# Magnetometro

magn = packet.Packet(sensor_id=3)
magn.add_field("unsignedInt32")
magn.add_field("float32")
magn.add_field("float32")
magn.add_field("float32")

# Acelerômetro / Gyro

acel = packet.Packet(sensor_id=4)
acel.add_field("unsignedInt32")
acel.add_field("float32")
acel.add_field("float32")
acel.add_field("float32")
acel.add_field("float32")
acel.add_field("float32")
acel.add_field("float32")

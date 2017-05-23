# -*- coding: utf-8 -*-

import packet

timer = packet.Packet(sensor_id=0)
timer.add_field("unsignedInt32")
timer.add_field("unsignedInt16")
timer.add_field("int32")
timer.add_field("int16")
timer.add_field("byte")
timer.add_field("float32")
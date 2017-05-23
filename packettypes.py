import packet

timer = packet.Packet(sensor_id=0)
timer.add_field("unsignedInt32")
def message_checksum(msg):
    crc = x25crc()
    crc.accumulate_str(msg.name + ' ')
    crc_end = msg.base_fields()
    for i in range(crc_end):
        f = msg.ordered_fields[i]
        crc.accumulate_str(f.type + ' ')
        crc.accumulate_str(f.name + ' ')
        if f.array_length:
            crc.accumulate([f.array_length])
    return (crc.crc & 0xFF) ^ (crc.crc >> 8)

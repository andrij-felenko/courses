import struct

FRAME_START = 0x7E          # маркер початку кадру

# проста контрольна сума-XOR для наочності (у бойовому коді — CRC-16, див. лінк)
def checksum(data):
    s = 0
    for b in data:
        s ^= b
    return s

# зібрати й повернути кадр телеметрії як bytes
def pack_telemetry(temp_c100, status):
    # '>h' диктує big-endian int16 явно — незалежно від платформи, як зсуви в C
    payload = struct.pack(">hB", temp_c100, status)   # температура (2 Б) + статус (1 Б)
    return bytes([FRAME_START, len(payload)]) + payload + bytes([checksum(payload)])

import struct, uuid

TELE_UUID = uuid.UUID("8b5f1e2a-9c44-4d71-a30e-2f1877c49103").bytes
TELE_FMT  = ">qiiihhhH"          # 28 байтів після UUID

def sei_messages(rbsp: bytes):
    """rbsp — тіло SEI-одиниці БЕЗ заголовка NAL і вже БЕЗ захисних байтів."""
    i = 0
    while i < len(rbsp) - 1:               # хвостовий 0x80 повідомленням не є
        ptype = 0
        while rbsp[i] == 0xFF: ptype += 255; i += 1
        ptype += rbsp[i]; i += 1
        psize = 0
        while rbsp[i] == 0xFF: psize += 255; i += 1
        psize += rbsp[i]; i += 1
        yield ptype, rbsp[i : i + psize]
        i += psize

def telemetry_of(rbsp: bytes):
    for ptype, payload in sei_messages(rbsp):
        if ptype == 5 and payload[:16] == TELE_UUID:
            t_us, lat, lon, alt, yaw, pitch, roll, seq = \
                struct.unpack(TELE_FMT, payload[16:])
            return dict(t_us=t_us, lat=lat / 1e7, lon=lon / 1e7,
                        alt_m=alt / 1000, yaw=yaw / 100,
                        pitch=pitch / 100, roll=roll / 100, seq=seq)
    return None

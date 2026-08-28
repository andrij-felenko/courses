# Хостовий бік (Python на станції): зібрати образ розділу під одну плату.
import struct, zlib

PROV_MAGIC   = 0x564F5250   # той самий, що в прошивці ("PROV" у пам'яті)
PROV_VERSION = 1

def build_record(serial: bytes, mac: bytes, cal: list[float]) -> bytes:
    assert len(serial) == 8 and len(mac) == 6 and len(cal) == 6
    # Розкладка ТОЧНО як packed-структура в C: '<' — little-endian, без вирівнювання.
    #   I  magic   | H version | 8s serial | 6s mac | 6f калібрування
    body = struct.pack("<IH8s6s6f", PROV_MAGIC, PROV_VERSION, serial, mac, *cal)
    crc  = zlib.crc32(body) & 0xFFFFFFFF        # той самий CRC-32, що й у прошивці
    return body + struct.pack("<I", crc)        # CRC — останні 4 байти

# Приклад: зібрати запис під плату №0x41 і зберегти образ розділу у файл.
rec = build_record(serial=bytes.fromhex("0000000000000041"),
                   mac=bytes.fromhex("A1B2C3D4E5F6"),
                   cal=[0.0, 1.0, 0.02, -0.01, 1.003, 0.0])
open("prov_0x41.bin", "wb").write(rec)

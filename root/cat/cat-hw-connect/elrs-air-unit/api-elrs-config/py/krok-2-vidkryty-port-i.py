import serial
import time
from collections import Counter

PORT = "COM7"       # Windows; на Linux — "/dev/ttyUSB0", на macOS — "/dev/tty.usbserial-XXXX"
BAUD = 420000       # ELRS-CRSF; для MAVLink-режиму поставили б 460800

CRSF_SYNC = 0xC8    # байт-старт (він же адреса польотного контролера)

def crc8_dvb_s2(data: bytes) -> int:
    """CRC8/DVB-S2, поліном 0xD5 — той самий, що в кадрі CRSF."""
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

def sniff(seconds: float = 3.0):
    ser = serial.Serial(PORT, BAUD, timeout=0.05)
    types = Counter()          # скільки кадрів кожного типу
    bad_crc = 0                # скільки кадрів не пройшли CRC
    buf = bytearray()
    t_end = time.time() + seconds
    try:
        while time.time() < t_end:
            buf += ser.read(256)                 # порція довільного розміру
            # виловлюємо кадри: старт(0xC8) + довжина + тіло
            while len(buf) >= 2:
                if buf[0] != CRSF_SYNC:
                    del buf[0]                   # не старт — зсуваємось на байт
                    continue
                length = buf[1]                  # тип + дані + CRC
                if length < 2 or length > 62:    # довжина поза діапазоном — фальстарт
                    del buf[0]
                    continue
                if len(buf) < 2 + length:        # кадр іще не добрано — чекаємо
                    break
                frame = bytes(buf[:2 + length])
                del buf[:2 + length]
                ftype = frame[2]                 # байт типу — одразу після довжини
                # CRC накриває тип+дані (без старту, без довжини, без самого CRC)
                calc = crc8_dvb_s2(frame[2:2 + length - 1])
                if calc != frame[-1]:
                    bad_crc += 1
                    continue
                types[ftype] += 1
    finally:
        ser.close()

    print(f"Порт {PORT} @ {BAUD}: {sum(types.values())} цілих кадрів, "
          f"{bad_crc} із битим CRC")
    for t, n in types.most_common():
        print(f"  тип 0x{t:02X}: {n}")

if __name__ == "__main__":
    sniff()

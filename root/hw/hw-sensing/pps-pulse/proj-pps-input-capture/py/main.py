# Виловлює кадри UBX-TIM-TP із серійного потоку (pyserial), поля дістає struct.
# UBX іде little-endian; формат "<IIiHBB": towMS, towSubMS, qErr(знакова!),
# week, flags, refInfo — саме те, що C-версія збирає зсувами вручну.
import struct
from collections import namedtuple

SYNC = b"\xB5\x62"
CLS, MID, PAYLEN = 0x0D, 0x01, 16
TimTp = namedtuple("TimTp", "towMS towSubMS qErr week flags refInfo")

def _fletcher(data: bytes) -> tuple[int, int]:
    """8-бітна сума Флетчера UBX над діапазоном клас..кінець навантаження."""
    ck_a = ck_b = 0
    for byte in data:
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return ck_a, ck_b

def read_timtp(ser):
    """Читати з порту, віддаючи кожен валідний кадр TIM-TP (генератор)."""
    while True:
        # Синхронізуватися на 0xB5 0x62.
        if ser.read(1) != SYNC[:1] or ser.read(1) != SYNC[1:]:
            continue
        header = ser.read(4)                      # cls, id, len(LE u16)
        cls, mid, length = header[0], header[1], header[2] | (header[3] << 8)
        payload = ser.read(length)
        ck_a, ck_b = ser.read(2)
        # Звірити суму ПЕРЕД тим, як довіритись кадру; збитий байт → відкинути.
        if (ck_a, ck_b) != _fletcher(header + payload):
            continue
        # Пропускаємо все, крім TIM-TP потрібної довжини.
        if (cls, mid, length) != (CLS, MID, PAYLEN):
            continue
        yield TimTp._make(struct.unpack("<IIiHBB", payload))

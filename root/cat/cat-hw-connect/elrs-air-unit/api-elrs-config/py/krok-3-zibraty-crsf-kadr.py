import serial

CRSF_SYNC = 0xC8                    # адреса польотного контролера / байт-старт
CRSF_FRAMETYPE_RC = 0x16            # тип: пакет 16 RC-каналів
CRSF_CENTER = 992                   # центр стіка (1500 мкс) у «тіках» CRSF

def crc8_dvb_s2(data: bytes) -> int:
    crc = 0
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = ((crc << 1) ^ 0xD5) & 0xFF if (crc & 0x80) else (crc << 1) & 0xFF
    return crc

def pack_channels(ch: list[int]) -> bytes:
    """16 каналів по 11 біт (0…2047) → 22 байти, little-endian."""
    assert len(ch) == 16
    acc = 0        # накопичувач бітів
    bits = 0       # скільки валідних бітів зараз в acc
    out = bytearray()
    for value in ch:
        acc |= (value & 0x7FF) << bits   # доливаємо 11 біт зверху
        bits += 11
        while bits >= 8:                 # зчерпуємо всі готові байти знизу
            out.append(acc & 0xFF)
            acc >>= 8
            bits -= 8
    if bits > 0:                         # останній неповний байт (тут не буває: 176 % 8 == 0)
        out.append(acc & 0xFF)
    return bytes(out)                    # рівно 22 байти

def build_rc_frame(ch: list[int]) -> bytes:
    """Повний CRSF-кадр каналів: старт + довжина + тип + 22 байти + CRC."""
    payload = pack_channels(ch)          # 22 байти
    length = len(payload) + 2            # тип(1) + дані(22) + CRC(1) = 24
    body = bytes([CRSF_FRAMETYPE_RC]) + payload   # тип + дані
    crc = crc8_dvb_s2(body)              # CRC накриває тип+дані
    return bytes([CRSF_SYNC, length]) + body + bytes([crc])

def send_sticks(port: str = "COM7", baud: int = 420000):
    """Слати нейтральні канали 50 разів на секунду (типовий темп CRSF-стенду)."""
    import time
    ser = serial.Serial(port, baud)
    ch = [CRSF_CENTER] * 16              # усі стіки в центрі
    ch[2] = 172                          # канал газу (індекс 2) — у мінімум (172 ≈ 988 мкс)
    frame = build_rc_frame(ch)
    try:
        while True:
            ser.write(frame)             # один готовий кадр
            time.sleep(0.02)             # 20 мс → 50 Гц
    finally:
        ser.close()

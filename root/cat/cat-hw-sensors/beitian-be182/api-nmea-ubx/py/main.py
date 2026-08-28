# Побудувати кадр UBX-CFG-VALSET і надіслати в модуль (хост, pyserial).
import serial

CFG_RATE_MEAS      = 0x30210001    # період вимірів, мс   (U2, 2 байти)
CFG_UART1_BAUDRATE = 0x40520001    # швидкість UART1      (U4, 4 байти)

def ubx_valset(key: int, value: int, vlen: int) -> bytes:
    body  = bytes([0x06, 0x8A])                       # клас, номер: CFG-VALSET
    plen  = 4 + 4 + vlen                              # заголовок + ключ + значення
    body += plen.to_bytes(2, "little")                # довжина, молодший уперед
    body += bytes([0x00, 0x01, 0x00, 0x00])           # версія, шар RAM, резерв
    body += key.to_bytes(4, "little")                 # ключ, LE
    body += value.to_bytes(vlen, "little")            # значення, LE
    ck_a = ck_b = 0                                    # сума Флетчера
    for x in body:
        ck_a = (ck_a + x) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return bytes([0xB5, 0x62]) + body + bytes([ck_a, ck_b])

# Надіслати: підняти частоту до 10 Гц
with serial.Serial("COM5", 38400, timeout=1) as ser:
    ser.write(ubx_valset(CFG_RATE_MEAS, 100, 2))      # 100 мс = 10 Гц
    # ser.write(ubx_valset(CFG_UART1_BAUDRATE, 115200, 4))  # змінити швидкість порту

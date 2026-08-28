# CircuitPython: сирий обмін через busio.I2C, без бібліотеки давача
import time
import board
import busio

GY21_ADDR = 0x40   # фіксована адреса, джамперами не змінюється
CMD_TEMP  = 0xF3   # вимір T, no-hold master
CMD_HUM   = 0xF5   # вимір RH, no-hold master

i2c = busio.I2C(board.SCL, board.SDA)

# si7021_crc8() означимо трохи нижче.

# Спільне ядро: послати команду `cmd`, зачекати `wait_ms`, прочитати 3 байти,
# звірити CRC і повернути 16-бітне СИРЕ значення (з обнуленими службовими бітами).
# Повертає raw при успіху; None — якщо давач не відповів або CRC не зійшлася.
def gy21_read_raw(cmd, wait_ms):
    while not i2c.try_lock():
        pass
    try:
        # -- Крок 1: послати командний байт --
        try:
            i2c.writeto(GY21_ADDR, bytes([cmd]))
        except OSError:
            return None                  # давач не підтвердив команду

        # -- Крок 2: витримати паузу, поки давач міряє --
        time.sleep(wait_ms / 1000)

        # -- Крок 3: прочитати рівно 3 байти (MSB, LSB, CRC) --
        buf = bytearray(3)
        try:
            i2c.readfrom_into(GY21_ADDR, buf)
        except OSError:
            return None
        msb, lsb, crc = buf[0], buf[1], buf[2]
    finally:
        i2c.unlock()

    # -- Крок 4a: перевірити контрольну суму над двома байтами даних --
    if si7021_crc8(buf[:2]) != crc:      # зіпсовано в дорозі — відкинути
        return None

    # -- Крок 4b: зібрати число й обнулити 2 службових біти --
    raw = (msb << 8) | lsb
    raw &= 0xFFFC
    return raw


# Публічні читання: та сама функція, різний командний байт і пауза + формула.
def gy21_read_temperature():
    raw = gy21_read_raw(CMD_TEMP, 10)
    if raw is None:
        return None
    return 175.72 * raw / 65536 - 46.85


def gy21_read_humidity():
    raw = gy21_read_raw(CMD_HUM, 20)
    if raw is None:
        return None
    rh = 125.0 * raw / 65536 - 6.0
    # Формула може дати трохи <0 або трохи >100 біля країв — притиснути до 0..100:
    if rh < 0.0:
        rh = 0.0
    if rh > 100.0:
        rh = 100.0
    return rh

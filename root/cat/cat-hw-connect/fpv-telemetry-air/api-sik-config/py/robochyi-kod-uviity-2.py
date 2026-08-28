import serial
import time

PORT = "COM7"          # Windows; на Linux — "/dev/ttyUSB0", на macOS — "/dev/tty.usbserial-XXXX"
BAUD = 57600           # ПОТОЧНА швидкість порту модуля (код 57 у ATI5 = 57600 бод)

def configure_sik():
    # timeout малий: ми самі керуємо паузами, не хочемо блокуватися надовго
    ser = serial.Serial(PORT, BAUD, timeout=0.2)
    try:
        # 1) Увійти в режим команд
        if not enter_command_mode(ser):
            print("Не вдалося ввійти в режим команд.")
            print("Найчастіша причина: щось шле в порт ДО +++ (не витримана тиша),")
            print("або порт відкрито не на тій швидкості, на якій модуль слухає.")
            return
        print("У режимі команд.")

        # 2) Прочитати, що є зараз
        print("Версія:", at(ser, "ATI"))          # напр. 'SiK 2.0 on HM-TRP'
        print("--- поточні параметри (ATI5) ---")
        print(at(ser, "ATI5"))                     # весь список S-регістрів

        # 3) Змінити параметри (поки лише в RAM!)
        #    S3 NETID=25, S2 AIR_SPEED=64, S4 TXPOWER=20 дБм, S6 MAVLINK=1
        for reg, val, name in [
            (3, 25, "NETID"),
            (2, 64, "AIR_SPEED"),
            (4, 20, "TXPOWER"),
            (6, 1,  "MAVLINK"),
        ]:
            r = at(ser, f"ATS{reg}={val}")         # очікуємо 'OK'
            print(f"ATS{reg}={val} ({name}) -> {r}")

        # 4) Закарбувати в EEPROM — БЕЗ цього кроку все зникне з перезапуском
        print("AT&W ->", at(ser, "AT&W"))          # write; очікуємо 'OK'

        # 5) Перезавантажити, щоб швидкості/частоти перечиталися
        print("ATZ (перезапуск) ...")
        ser.write(b"ATZ\r\n")
        ser.flush()
        # ATZ РВЕ зв'язок: модуль перезавантажується, старий сеанс недійсний.
        # НЕ намагаємося читати відповідь — її не буде.
    finally:
        ser.close()                                # завжди звільняємо порт

if __name__ == "__main__":
    configure_sik()

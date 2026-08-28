# ground_config.py — увійти в командний режим, прочитати й записати S-регістри.
import time
import serial

PORT = "COM7"
BAUD = 57600

def enter_command_mode(ser):
    # Ключ до +++: ТИША секунду до і секунду після, інакше три плюси
    # серед даних могли б спрацювати випадково — тому їх обрамлюють паузою.
    time.sleep(1.1)                 # 1 с тиші ДО
    ser.reset_input_buffer()        # викинути все, що накапало в буфер
    ser.write(b"+++")               # БЕЗ переводу рядка — саме три плюси
    time.sleep(1.1)                 # 1 с тиші ПІСЛЯ
    resp = ser.read(64)             # модуль відповість "OK\r\n"
    return b"OK" in resp

def at(ser, cmd, wait=0.3):
    # надіслати AT-команду (з переводом рядка) і повернути відповідь
    ser.reset_input_buffer()
    ser.write(cmd + b"\r\n")
    time.sleep(wait)
    return ser.read(512)

def main():
    ser = serial.Serial(PORT, BAUD, timeout=1)

    if not enter_command_mode(ser):
        print("не вдалося ввійти в командний режим (не той порт/швидкість?)")
        ser.close(); return 1
    print("у командному режимі")

    # прочитати ВСІ параметри одним махом
    print(at(ser, b"ATI5").decode(errors="replace"))

    # прочитати конкретний регістр: S3 = NetID
    print("NetID зараз:", at(ser, b"ATS3?").decode(errors="replace").strip())

    # ЗМІНИТИ NetID на 42 — і ОБОВ'ЯЗКОВО зберегти + перезавантажити
    at(ser, b"ATS3=42")             # 1) записали в живу пам'ять
    at(ser, b"AT&W")                # 2) зберегли в EEPROM — БЕЗ цього все дарма
    at(ser, b"ATZ", wait=1.0)       # 3) перезавантажили, щоб зміна почала діяти
    print("NetID записано в EEPROM і модуль перезавантажено")

    ser.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

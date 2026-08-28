# Завести SiK у режим AT-команд і прочитати версію.
import time
import serial   # pyserial

def sik_enter_at_mode(ser):
    time.sleep(1.1)                 # guard time ПЕРЕД: ≥1 с тиші
    ser.write(b"+++")               # без CR/LF! саме три плюси
    time.sleep(1.1)                 # guard time ПІСЛЯ: ще ≥1 с тиші

    line = ser.readline()           # таймаут задано при відкритті порту
    if not line:
        return -1                   # модем не відповів
    if not line.startswith(b"OK"):
        return -2                   # очікували "OK" — не той стан/швидкість

    ser.write(b"ATI\r")             # запит версії прошивки
    ser.readline()                  # напр. b"SiK 2.0 on HM-TRP"
    # ... розібрати рядок версії за потреби ...

    ser.write(b"ATZ\r")             # перезавантажити → назад у прозорий режим
    return 0

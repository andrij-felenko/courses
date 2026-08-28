import serial
import time

def enter_command_mode(ser: serial.Serial) -> bool:
    """Вивести SiK-модуль із прозорого режиму в режим команд.
    Ритуал: >1 с тиші → '+++' (без \\n) → >1 с тиші → чекай 'OK'."""
    ser.reset_input_buffer()          # викинути телеметрію, що вже натекла
    time.sleep(1.2)                   # СТОРОЖОВА ПАУЗА до +++ (не пишемо нічого!)
    ser.write(b"+++")                 # рівно три плюси, БЕЗ переведення рядка
    ser.flush()
    time.sleep(1.2)                   # СТОРОЖОВА ПАУЗА після +++
    resp = ser.read(ser.in_waiting or 1)   # модуль відповідає 'OK\r\n'
    return b"OK" in resp

def at(ser: serial.Serial, cmd: str, wait: float = 0.3) -> str:
    """Послати одну AT/RT-команду (з CR) і зібрати відповідь як текст."""
    ser.reset_input_buffer()
    ser.write((cmd + "\r\n").encode())     # команди — З переведенням рядка
    ser.flush()
    time.sleep(wait)
    data = b""
    while ser.in_waiting:
        data += ser.read(ser.in_waiting)
        time.sleep(0.05)
    return data.decode(errors="replace").strip()

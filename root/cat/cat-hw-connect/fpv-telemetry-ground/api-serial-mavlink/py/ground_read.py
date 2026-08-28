# ground_read.py — відкрити наземний модуль і читати прозорий потік.
# Встановити:  pip install pyserial
import sys
import serial              # pyserial

PORT = "COM7"              # Windows; на Linux — "/dev/ttyUSB0", на macOS — "/dev/tty.usbserial-XXXX"
BAUD = 57600              # локальна швидкість USB-UART, НЕ швидкість ефіру

def main():
    # 8N1 — 8 біт даних, без парності, 1 стоп-біт (типово для SiK).
    # timeout=1 — read() чекає щонайбільше секунду й повертає те, що встигло прийти.
    try:
        ser = serial.Serial(PORT, BAUD, bytesize=8, parity="N",
                            stopbits=1, timeout=1)
    except serial.SerialException as e:
        print("не відкрити порт %s: %s" % (PORT, e))
        print("перевір: той порт? модуль у USB? порт не зайнятий станцією?")
        return 1

    print("порт %s відкрито на %d бод — читаю прозорий потік…" % (PORT, BAUD))
    try:
        while True:
            chunk = ser.read(256)          # до 256 байтів або поки не спливе timeout
            if chunk:
                # сирі байти: тут це суміш кадрів MAVLink; розберемо їх нижче
                sys.stdout.buffer.write(chunk.hex(" ").encode() + b"\n")
                sys.stdout.flush()
            # щоб ЩОСЬ послати на дрон — просто пишемо в той самий порт:
            # ser.write(b"...")   # байти полетять в ефір прозоро
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

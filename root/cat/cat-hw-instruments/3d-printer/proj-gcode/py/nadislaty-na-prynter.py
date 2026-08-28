import serial, time, sys

PORT = "COM3"          # Windows; у Linux — "/dev/ttyUSB0"
BAUD = 115200          # швидкість; має збігатися з тою, що в прошивці

def send_gcode(path):
    # відкриваємо порт; це смикає скидання плати — принтер перезавантажиться
    printer = serial.Serial(PORT, BAUD, timeout=5)
    print("порт відкрито, чекаємо, поки принтер очуняє…")
    time.sleep(3)                     # дати платі перезавантажитися
    printer.reset_input_buffer()      # викинути завантажувальне базікання

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            # викинути порожні рядки й коментарі (принтеру вони ні до чого)
            if not line or line.startswith(";"):
                continue
            # відрізати коментар у кінці рядка, якщо є
            line = line.split(";", 1)[0].strip()
            if not line:
                continue

            printer.write((line + "\n").encode("ascii"))   # надіслати рядок
            print(">>", line)

            # ── ЧЕКАТИ на "ok" — не слати наступний, поки не прийде ──
            while True:
                answer = printer.readline().decode("ascii", "ignore").strip()
                if answer:
                    print("  <<", answer)
                if answer.startswith("ok"):
                    break                     # принтер готовий до наступного
                if answer.startswith("Error") or answer.startswith("!!"):
                    print("ПРИНТЕР ПОВІДОМИВ ПОМИЛКУ, зупиняємось")
                    printer.close()
                    sys.exit(1)

    printer.close()
    print("готово.")

if __name__ == "__main__":
    send_gcode("square.gcode")

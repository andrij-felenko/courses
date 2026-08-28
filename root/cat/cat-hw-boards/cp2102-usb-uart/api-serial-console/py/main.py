# pip install pyserial
import serial

PORT = "COM7"        # Windows; на Linux — "/dev/ttyUSB0", на macOS — "/dev/cu.SLAB_USBtoUART"
BAUD = 115200

# with-блок гарантує, що порт закриється навіть при винятку чи Ctrl+C
with serial.Serial(PORT, BAUD, bytesize=8, parity="N", stopbits=1, timeout=1) as ser:
    print(f"Відкрито {ser.name} на {BAUD} бод. Ctrl+C — вихід.")
    # надіслати пристрою команду (не забути перевід рядка, якщо він його чекає)
    ser.write(b"status\n")

    while True:
        line = ser.readline()          # читає до \n або поки не спрацює timeout
        if line:                        # порожньо = timeout без даних, просто чекаємо далі
            # decode із errors="replace": один битий байт не завалить увесь рядок
            print(line.decode("utf-8", errors="replace").rstrip())

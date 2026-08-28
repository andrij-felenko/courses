# read_gps.py — послухати BE-182 через перехідник USB↔UART і показати координати.
# Постав бібліотеки:  pip install pyserial pynmea2
import serial
import pynmea2

PORT = "COM5"          # Windows; на Linux — "/dev/ttyUSB0"
BAUD = 38400           # BE-182 за замовчуванням саме стільки

with serial.Serial(PORT, BAUD, timeout=1) as ser:
    while True:
        raw = ser.readline().decode("ascii", errors="replace").strip()
        if not raw.startswith("$"):
            continue                              # не рядок NMEA — пропустити
        try:
            msg = pynmea2.parse(raw)              # звіряє суму й розбирає поля
        except pynmea2.ParseError:
            continue                              # бита рядок — на смітник

        if msg.sentence_type == "GGA":
            if int(msg.gps_qual) == 0:            # поле fix: 0 — нема положення
                print("fix ще нема — під небо або до вікна…")
                continue
            # .latitude / .longitude — уже десяткові градуси, зі знаком!
            print(f"lat={msg.latitude:.6f}  lon={msg.longitude:.6f}  "
                  f"sats={msg.num_sats}")

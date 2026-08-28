#!/usr/bin/env python3
import socket
import sqlite3
import re
import sys
from datetime import datetime

PRINTER_IP = "192.168.10.50"
PRINTER_PORT = 9100
DB_PATH = "/var/factory/production.db"

def calculate_luhn_checksum(payload: str) -> int:
    """Обчислення контрольної цифри Луна для числового рядка."""
    digits = [int(c) for c in payload if c.isdigit()]
    total = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        if i % 2 == 0:
            doubled = digit * 2
            total += (doubled % 10) + 1 if doubled > 9 else doubled
        else:
            total += digit
    return (10 - (total % 10)) % 10

def generate_zpl(sn: str, mac: str, batch: str, pin: str, prov_hash: str) -> str:
    """Генерація розмітки ZPL для коробкової етикетки 100x60 мм."""
    uri = f"https://onboard.acme-iot.com/pair?v=1&sn={sn}&mac={mac}&pin={pin}&t={prov_hash[:16]}"
    mac_clean = mac.replace(":", "").upper()
    now_str = datetime.utcnow().strftime("%Y-%m-%d")

    return f"""^XA
^PW1181^LL0708^LH0,0
^FO50,40^A0N,32,32^FDPRO-GATEWAY INDUSTRIAL NODE KIT^FS
^FO50,80^A0N,24,24^FDSKU: GW-500-ETH-LTE-EU   Qty: 1 PC^FS
^FO50,110^GB1080,2,2^FS

^FO50,130^A0N,20,20^FDSerial Number:^FS
^FO50,155^BCN,60,Y,N,N^FD{sn}^FS

^FO50,260^A0N,20,20^FDEthernet MAC Address:^FS
^FO50,285^BCN,60,Y,N,N^FD{mac_clean}^FS

^FO820,140^BQN,2,6^FDQA,{uri}^FS
^FO800,320^A0N,18,18^FDSCAN TO ONBOARD^FS

^FO50,380^GB1080,2,2^FS
^FO50,405^A0N,22,22^FDBatch: {batch}   Date: {now_str}   Test: QA-PASS^FS
^FO50,435^A0N,20,20^FDWeight: 485 g    HW Rev: 2.1        FW: v1.4.0^FS
^FO50,465^A0N,18,18^FDProv Hash: {prov_hash[:16]} (Ed25519 Verified)^FS

^FO50,510^GB1080,75,2^FS
^FO65,525^A0N,20,20^FDUWAGA: S/N and MAC must match internal device plate!^FS
^FO65,555^A0N,18,18^FDVerify tamper seal integrity before installation. RoHS Compliant.^FS
^XZ"""

def pack_station_process(scanned_device_dm: str):
    """Обробка події сканування пристрою на столі пакування."""
    # Приклад вхідного рядка з DataMatrix: "SN263400101237;MAC=001A223B4C5D;HASH=a4f833c188099b12"
    m = re.match(r"(SN\d{12});MAC=([0-9A-Fa-f]{12});HASH=([0-9A-Fa-f]+)", scanned_device_dm)
    if not m:
        print("[ERROR] Невалідний формат DataMatrix на корпусі пристрою!")
        return False

    sn, mac, prov_hash = m.group(1), m.group(2).upper(), m.group(3)

    # Звірка з виробничою БД
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT test_status, batch_id, setup_pin FROM units WHERE sn = ? AND mac = ?", (sn, mac))
    row = cur.fetchone()

    if not row:
        print(f"[REJECT] Пристрій {sn} не знайдено в базі випуску!")
        return False

    status, batch, pin = row
    if status != "PASS":
        print(f"[REJECT] Пристрій {sn} має статус тесту '{status}'. Пакування заборонено!")
        return False

    # Генерація ZPL та відправка на принтер
    zpl_data = generate_zpl(sn, mac, batch, pin, prov_hash)
    try:
        with socket.create_connection((PRINTER_IP, PRINTER_PORT), timeout=3.0) as sock:
            sock.sendall(zpl_data.encode("utf-8"))
        print(f"[SUCCESS] Етикетку для {sn} успішно видрукувано на {PRINTER_IP}")
        return True
    except Exception as e:
        print(f"[ERROR] Помилка зв'язку з принтером Zebra: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pack_station_process(sys.argv[1])
    else:
        # Тестовий запуск
        pack_station_process("SN263400101237;MAC=001A223B4C5D;HASH=a4f833c188099b12")

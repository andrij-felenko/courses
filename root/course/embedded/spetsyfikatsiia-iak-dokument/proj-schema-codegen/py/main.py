#!/usr/bin/env python3
"""Стендовий скрипт валідації бінарних пакетів проти схеми Kaitai Struct."""
import io
import struct
from telemetry_protocol import TelemetryProtocol


def test_golden_telemetry_packet():
    # Байт 0: SOF (0xAA)
    # Байт 1: Version (0x01)
    # Байт 2: Msg ID (0x20 -> Telemetry)
    # Байт 3: Seq ID (0x4A)
    # Байти 4..5: Length (0x0008 -> 8 байтів LE)
    # Байти 6..7: temp_raw = 2450 (24.50 °C -> 0x0992 LE -> 0x92 0x09)
    # Байти 8..9: pressure_raw = 10132 (1013.2 hPa -> 0x2794 LE -> 0x94 0x27)
    # Байти 10..11: voltage_mv = 3300 mV (0x0CE4 LE -> 0xE4 0x0C)
    # Байт 12: flags = 0x01
    # Байт 13: reserved = 0x00
    # Байти 14..15: CRC-16 CCITT над байтами 1..13
    # Байт 16: EOF (0x55)

    header_payload = bytes([
        0x01,        # Version
        0x20,        # Msg ID
        0x4A,        # Seq ID
        0x08, 0x00,  # Payload Len = 8
        0x92, 0x09,  # Temp = 24.50 C
        0x94, 0x27,  # Pressure = 1013.2 hPa
        0xE4, 0x0C,  # Voltage = 3300 mV
        0x01,        # Flags
        0x00         # Reserved
    ])

    # Обчислення CRC-16 CCITT (init 0xFFFF, poly 0x1021)
    crc = 0xFFFF
    for b in header_payload:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF

    golden_frame = bytes([0xAA]) + header_payload + struct.pack("<H", crc) + bytes([0x55])

    # Розпакування через згенерований Kaitai Struct парсер
    pkt = TelemetryProtocol.from_io(io.BytesIO(golden_frame))

    assert pkt.sof == b"\xaa"
    assert pkt.version == 1
    assert pkt.msg_id == TelemetryProtocol.MsgType.telemetry_report
    assert pkt.seq_id == 0x4A
    assert pkt.payload_len == 8
    assert abs(pkt.payload.temperature_c - 24.50) < 1e-3
    assert abs(pkt.payload.pressure_hpa - 1013.2) < 1e-3
    assert pkt.payload.voltage_mv == 3300
    assert pkt.payload.flags == 0x01
    assert pkt.crc16 == crc
    assert pkt.eof == b"\x55"

    print(f"[OK] Golden Vector: Temp={pkt.payload.temperature_c} C, Press={pkt.payload.pressure_hpa} hPa, CRC=0x{crc:04X}")


if __name__ == "__main__":
    test_golden_telemetry_packet()

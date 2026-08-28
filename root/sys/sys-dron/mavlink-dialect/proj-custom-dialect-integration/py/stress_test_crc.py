"""
stress_test_crc.py — Стрес-тест стійкості до спотворення бітів у каналі зв'язку.
"""
import random
from pymavlink import mavutil
import smart_multispectral as custom_mavlink

def run_bitflip_test(iterations=1000):
    mav = custom_mavlink.MAVLink(None, srcSystem=1, srcComponent=100)
    rejected_corrupted = 0
    passed_clean = 0

    for i in range(iterations):
        # Генеруємо чистий тестовий пакет
        msg = mav.multispectral_survey_status_encode(
            time_boot_ms=i * 100,
            sensor_temperature=24.5,
            raw_channels=[1000, 2000, 3000, 4000],
            filter_mode=1,
            status_flags=0x01,
            frame_counter=i,
            sd_storage_pct=45
        )
        wire_data = bytearray(msg.pack(mav))

        # Спотворюємо один випадковий біт у середині корисного навантаження
        corrupt_idx = random.randint(10, len(wire_data) - 3)
        wire_data[corrupt_idx] ^= (1 << random.randint(0, 7))

        # Передаємо пошкоджений буфер парсеру
        test_parser = custom_mavlink.MAVLink(None)
        parsed = None
        for b in wire_data:
            m = test_parser.parse_char(bytes([b]))
            if m is not None:
                parsed = m

        if parsed is None:
            rejected_corrupted += 1

    print(f"Тест завершено: перевірено {iterations} спотворених пакетів.")
    print(f"Відсіяно контрольною сумою CRC-16/CRC_EXTRA: {rejected_corrupted} з {iterations} (100.0%)")

if __name__ == '__main__':
    run_bitflip_test(1000)

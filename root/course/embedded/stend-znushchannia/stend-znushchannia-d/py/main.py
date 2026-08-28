#!/usr/bin/env python3
"""
HIL Torture Testbench: автоматизований пошук меж стійкості (Shmoo Plot).
Керує стендом через послідовний порт, надсилає стрес-пакети та формує звіт.
"""

import time
import struct
import serial
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class TestResult:
    voltage_mv: int
    dropout_us: int
    status_char: str  # '.' = Pass (A), 'b' = Recovered (B), 'F' = Reset/Hang (C)
    current_ma: int
    dut_alive: bool


class TortureBenchHost:
    def __init__(self, port: str, baudrate: int = 115200):
        self.ser = serial.Serial(port, baudrate, timeout=1.5)
        time.sleep(0.1)
        self.ser.reset_input_buffer()

    def run_stress_step(self, voltage_mv: int, dropout_us: int, spark_en: bool = False) -> TestResult:
        """Надсилає бінарну команду стресу на контролер стенду."""
        # Формат кадру: [0xAA, 0x55, CMD_STRESS(0x01), Voltage(2B), Dropout(4B), Spark(1B), CRC(1B)]
        cmd_id = 0x01
        payload = struct.pack("<HHIB", 0x55AA, voltage_mv, dropout_us, 1 if spark_en else 0)
        crc = sum(payload) & 0xFF
        packet = payload + struct.pack("<B", crc)
        
        self.ser.write(packet)
        
        # Очікуємо відповідь від стенду: [Status(1B), Meas_V(2B), Meas_I(2B), Reset(1B), CRC(1B)]
        resp = self.ser.read(7)
        if len(resp) < 7:
            return TestResult(voltage_mv, dropout_us, "F", 0, False)
            
        status, meas_v, meas_i, reset_pin = struct.unpack("<BHHB", resp[:6])
        
        # Опитування консолі самого DUT (heartbeat)
        time.sleep(0.05)
        dut_bytes = self.ser.in_waiting
        dut_alive = (reset_pin == 0) and (meas_i > 5)

        if dut_alive and reset_pin == 0:
            res_char = "."  # Критерій A (Повна стабільність)
        elif reset_pin != 0 and meas_i > 5:
            res_char = "C"  # Критерій C (Апаратне скидання / BOD)
        else:
            res_char = "F"  # Повна відмова / зависання

        return TestResult(voltage_mv, dropout_us, res_char, meas_i, dut_alive)

    def generate_shmoo_plot(self, v_start_mv: int = 3600, v_stop_mv: int = 2400, v_step_mv: int = -100,
                            dropouts_us: List[int] = None) -> None:
        """Здійснює сітковий перебір параметрів і малює Shmoo-діаграму."""
        if dropouts_us is None:
            dropouts_us = [10, 50, 100, 500, 1000, 5000, 10000, 50000]

        print("=" * 72)
        print("ПОЧАТОК СТРЕС-ТЕСТУ: АВТОМАТИЗОВАНИЙ SHMOO-PLOT")
        print(f"Діапазон напруг: {v_start_mv}..{v_stop_mv} мВ | Провали: {dropouts_us} мкс")
        print("=" * 72)

        # Заголовок таблиці
        header = "VDD (мВ) | " + " ".join(f"{d:>6}µs" for d in dropouts_us)
        print(header)
        print("-" * len(header))

        for v in range(v_start_mv, v_stop_mv + v_step_mv, v_step_mv):
            row_chars = []
            for d in dropouts_us:
                res = self.run_stress_step(v, d, spark_en=False)
                row_chars.append(f"{res.status_char:>8}")
                time.sleep(0.02)  # Пауза між ударами для стабілізації DUT
            print(f"{v:7} |" + "".join(row_chars))

        print("-" * len(header))
        print("Легенда: [.] = Pass (Клас A)  [C] = Reset/BOD (Клас C)  [F] = Hang (Відмова)")
        print("=" * 72)


if __name__ == "__main__":
    # Демонстраційний запуск за відсутності живого COM-порту
    print("HIL Torture Bench Host Controller Module loaded.")

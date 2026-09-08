"""Стрес-тестування передачі даних через гальванічно ізольований UART.

Скрипт генерує випадкові пакети з контрольною сумою CRC32, відправляє їх
у послідовний порт на швидкості 115200 бод і перевіряє цілісність
отриманого апаратного луна-відлуння від мікроконтролера.
"""

import argparse
import os
import sys
import time
import zlib
from typing import Dict, List, Optional
import serial


class UartStressTester:
    """Керування послідовним портом, формування пакетів та підрахунок статистики помилок."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.2) -> None:
        """Ініціалізація параметрів тестувальника послідовного порту."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.latencies_ms: List[float] = []
        self.total_packets = 0
        self.corrupted_packets = 0
        self.timeout_packets = 0
        self.total_bit_errors = 0
        self.total_bits_sent = 0

    def connect(self) -> None:
        """Відкриття послідовного порту з очищенням буферів FIFO."""
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.timeout,
        )
        # Очищення вхідних та вихідних апаратних черг
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        time.sleep(0.1)

    def disconnect(self) -> None:
        """Закриття послідовного порту."""
        if self.ser and self.ser.is_open:
            self.ser.close()

    @staticmethod
    def _count_bit_differences(a: bytes, b: bytes) -> int:
        """Підрахунок кількості спотворених бітів між відправленими та прийнятими даними."""
        bit_errors = 0
        min_len = min(len(a), len(b))
        for i in range(min_len):
            xor_byte = a[i] ^ b[i]
            bit_errors += bin(xor_byte).count("1")
        # Враховуємо повністю втрачені байти як 8 бітових помилок на байт
        bit_errors += abs(len(a) - len(b)) * 8
        return bit_errors

    def run_test(self, packet_count: int = 100, packet_size: int = 64) -> Dict[str, float]:
        """Виконання циклу відправки пакетів та аналізу відлуння."""
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито перед запуском тесту.")

        print(f"Початок тестування порту {self.port} на швидкості {self.baudrate} бод...")
        print(f"Кількість пакетів: {packet_count}, розмір корисного навантаження: {packet_size} байт\n")

        self.latencies_ms.clear()
        self.total_packets = packet_count
        self.corrupted_packets = 0
        self.timeout_packets = 0
        self.total_bit_errors = 0
        self.total_bits_sent = 0

        for i in range(1, packet_count + 1):
            # Генерація псевдовипадкового навантаження
            payload = os.urandom(packet_size)
            # Додавання 32-бітної контрольної суми CRC32
            crc = zlib.crc32(payload)
            packet = payload + crc.to_bytes(4, byteorder="little")
            self.total_bits_sent += len(packet) * 8

            # Фіксація часу відправки
            t_start = time.perf_counter()
            self.ser.write(packet)
            self.ser.flush()

            # Зчитування очікуваної кількості байтів
            rx_data = self.ser.read(len(packet))
            t_elapsed_ms = (time.perf_counter() - t_start) * 1000.0

            if len(rx_data) < len(packet):
                self.timeout_packets += 1
                bit_diff = self._count_bit_differences(packet, rx_data)
                self.total_bit_errors += bit_diff
                print(f"[{i:04d}] ТАЙМАУТ: отримано {len(rx_data)}/{len(packet)} байт (RTT: {t_elapsed_ms:.2f} мс)")
            elif rx_data != packet:
                self.corrupted_packets += 1
                bit_diff = self._count_bit_differences(packet, rx_data)
                self.total_bit_errors += bit_diff
                print(f"[{i:04d}] СПОТВОРЕННЯ ДАНИХ: бітових помилок = {bit_diff} (RTT: {t_elapsed_ms:.2f} мс)")
            else:
                self.latencies_ms.append(t_elapsed_ms)
                if i % 25 == 0 or i == packet_count:
                    print(f"[{i:04d}] ОК: RTT = {t_elapsed_ms:.2f} мс")

            # Коротка пауза між пачками для стабілізації буферів приймача
            time.sleep(0.005)

        return self.get_summary()

    def get_summary(self) -> Dict[str, float]:
        """Формування підсумкових показників тестування."""
        avg_rtt = (sum(self.latencies_ms) / len(self.latencies_ms)) if self.latencies_ms else 0.0
        ber = (self.total_bit_errors / self.total_bits_sent) if self.total_bits_sent > 0 else 0.0
        success_packets = self.total_packets - self.corrupted_packets - self.timeout_packets
        packet_delivery_rate = (success_packets / self.total_packets * 100.0) if self.total_packets > 0 else 0.0

        return {
            "total_packets": float(self.total_packets),
            "success_packets": float(success_packets),
            "delivery_rate_pct": packet_delivery_rate,
            "avg_rtt_ms": avg_rtt,
            "bit_error_rate": ber,
            "total_bit_errors": float(self.total_bit_errors),
        }

    def print_report(self) -> None:
        """Виведення підсумкового звіту стрес-тесту в консоль."""
        stats = self.get_summary()
        print("\n" + "=" * 50)
        print("           ПІДСУМКИ СТРЕС-ТЕСТУВАННЯ")
        print("=" * 50)
        print(f"Порт / Швидкість      : {self.port} @ {self.baudrate} бод")
        print(f"Відправлено пакетів   : {int(stats['total_packets'])}")
        print(f"Успішно підтверджено  : {int(stats['success_packets'])} ({stats['delivery_rate_pct']:.1f}%)")
        print(f"Втрачено через таймаут: {self.timeout_packets}")
        print(f"Пакетів зі спотворенням: {self.corrupted_packets}")
        print(f"Середня затримка RTT  : {stats['avg_rtt_ms']:.2f} мс")
        print(f"Загалом бітових помилок: {int(stats['total_bit_errors'])}")
        print(f"Коефіцієнт помилок BER: {stats['bit_error_rate']:.2e}")
        print("=" * 50)


def main() -> None:
    """Точка входу для командного рядка."""
    parser = argparse.ArgumentParser(description="Стрес-тестування якості гальванічно ізольованого порту UART")
    parser.add_argument("-p", "--port", default="COM3", help="Ім'я послідовного порту (наприклад, COM3 або /dev/ttyUSB0)")
    parser.add_argument("-b", "--baud", type=int, default=115200, help="Швидкість обміну (за замовчуванням 115200)")
    parser.add_argument("-n", "--count", type=int, default=100, help="Кількість тестових пакетів (за замовчуванням 100)")
    parser.add_argument("-s", "--size", type=int, default=64, help="Розмір корисного навантаження в байтах (за замовчуванням 64)")
    args = parser.parse_args()

    tester = UartStressTester(port=args.port, baudrate=args.baud)
    try:
        tester.connect()
        tester.run_test(packet_count=args.count, packet_size=args.size)
        tester.print_report()
    except Exception as exc:
        print(f"Помилка тестування: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        tester.disconnect()


if __name__ == "__main__":
    main()

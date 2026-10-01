"""
Скрипт діагностики сигнальних ліній DTR та RTS перетворювача CH340.
Використовує бібліотеку pySerial для керування модемними сигналами
та вимірює часові затримки драйвера USB-UART мосту.
"""

import time
import sys
from typing import Dict, List, Tuple, Optional
import serial


class CH340LineDiagnostics:
    """
    Клас апаратного керування та діагностики сигнальних ліній DTR/RTS
    для перетворювача CH340.
    """

    def __init__(self, port_name: str, baudrate: int = 115200, timeout: float = 1.0) -> None:
        """
        Ініціалізація параметрів послідовного порту.
        """
        self.port_name: str = port_name
        self.baudrate: int = baudrate
        self.timeout: float = timeout
        self.ser: Optional[serial.Serial] = None

    def open_port(self) -> None:
        """
        Відкриття послідовного порту CH340 з початковим вимкненням ліній.
        """
        try:
            self.ser = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout,
                dtr=False,
                rts=False
            )
            time.sleep(0.1)
        except serial.SerialException as err:
            print(f"[ПОМИЛКА] Не вдалося відкрити порт {self.port_name}: {err}", file=sys.stderr)
            raise

    def close_port(self) -> None:
        """
        Закриття послідовного порту та повернення ліній у вихідний стан.
        """
        if self.ser and self.ser.is_open:
            self.ser.dtr = False
            self.ser.rts = False
            self.ser.close()

    def toggle_dtr(self, state: bool) -> float:
        """
        Перемикання стану лінії DTR з вимірюванням затримки драйвера.
        Повертає час виконання операції у мілісекундах.
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито.")

        start_time = time.perf_counter()
        self.ser.dtr = state
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return elapsed_ms

    def toggle_rts(self, state: bool) -> float:
        """
        Перемикання стану лінії RTS з вимірюванням затримки драйвера.
        Повертає час виконання операції у мілісекундах.
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито.")

        start_time = time.perf_counter()
        self.ser.rts = state
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return elapsed_ms

    def measure_line_toggles(self, iterations: int = 10) -> Dict[str, Dict[str, float]]:
        """
        Серія випробувальних перемикань ліній DTR/RTS для фіксації
        мінімальної, середньої та максимальної затримки системного драйвера.
        """
        dtr_latencies: List[float] = []
        rts_latencies: List[float] = []

        for _ in range(iterations):
            dtr_latencies.append(self.toggle_dtr(True))
            time.sleep(0.01)
            dtr_latencies.append(self.toggle_dtr(False))
            time.sleep(0.01)

            rts_latencies.append(self.toggle_rts(True))
            time.sleep(0.01)
            rts_latencies.append(self.toggle_rts(False))
            time.sleep(0.01)

        def calc_stats(latencies: List[float]) -> Dict[str, float]:
            return {
                "min_ms": min(latencies),
                "avg_ms": sum(latencies) / len(latencies),
                "max_ms": max(latencies)
            }

        return {
            "DTR": calc_stats(dtr_latencies),
            "RTS": calc_stats(rts_latencies)
        }

    def generate_autoreset_sequence(self, reset_hold_ms: float = 100.0, boot_hold_ms: float = 50.0) -> None:
        """
        Генерація часової послідовності сигналів автоскиду (Auto-Reset)
        для переведення цільового мікроконтролера в режим завантажувача.
        """
        if not self.ser or not self.ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито.")

        print("[ІНФО] Запуск послідовності автоматичного скидання цільового МК...")

        self.ser.dtr = True
        self.ser.rts = True
        time.sleep(reset_hold_ms / 1000.0)

        self.ser.rts = False
        time.sleep(boot_hold_ms / 1000.0)

        self.ser.dtr = False
        print("[ІНФО] Послідовність Auto-Reset успішно згенеровано.")

    def run_diagnostics(self) -> None:
        """
        Повний цикл діагностики роботи ліній DTR/RTS перетворювача CH340.
        """
        self.open_port()
        try:
            print(f"[ІНФО] Порт {self.port_name} успішно відкрито (бодрейт: {self.baudrate}).")
            print("[ІНФО] Тестування часових затримок драйвера CH340...")

            stats = self.measure_line_toggles(iterations=10)

            print("\n--- Результати заміру затримок драйвера (ms) ---")
            print(f"DTR :: Мін: {stats['DTR']['min_ms']:.3f} ms | Середнє: {stats['DTR']['avg_ms']:.3f} ms | Макс: {stats['DTR']['max_ms']:.3f} ms")
            print(f"RTS :: Мін: {stats['RTS']['min_ms']:.3f} ms | Середнє: {stats['RTS']['avg_ms']:.3f} ms | Макс: {stats['RTS']['max_ms']:.3f} ms")

            print("\n--- Перевірка апаратного автомату автоскиду ---")
            self.generate_autoreset_sequence()

        finally:
            self.close_port()
            print(f"[ІНФО] Порт {self.port_name} закрито.")


def main() -> None:
    """
    Точка входу скрипту.
    """
    port = sys.argv[1] if len(sys.argv) > 1 else "COM3"
    print(f"=== Діагностика перетворювача CH340 на порту {port} ===")

    diag = CH340LineDiagnostics(port_name=port)
    try:
        diag.run_diagnostics()
    except Exception as e:
        print(f"[ПОМИЛКА] Завершення виконання через збій: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

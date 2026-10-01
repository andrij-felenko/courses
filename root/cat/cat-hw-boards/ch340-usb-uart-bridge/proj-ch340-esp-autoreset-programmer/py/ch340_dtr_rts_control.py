"""
Скрипт керування лініями DTR та RTS через USB-UART перетворювач CH340.
Демонструє відкриття послідовного порту, маніпуляцію логічними рівнями
з урахуванням апаратної інверсії сигналів чипа CH340 та обробку помилок pySerial.
"""

import time
import sys
import serial
from serial.tools import list_ports


class CH340Controller:
    """
    Клас для керування службовими лініями DTR та RTS перетворювача CH340.
    Враховує апаратну інверсію: прапорець True у pySerial встановлює низький
    електричний рівень (0 В) на піні мікросхеми CH340, а False — високий (3.3 В / 5 В).
    """

    def __init__(self, port_name: str, baudrate: int = 115200, timeout: float = 1.0):
        """
        Ініціалізує параметри порту, але не відкриває його автоматично.
        """
        self.port_name = port_name
        self.baudrate = baudrate
        self.timeout = timeout
        self._ser: serial.Serial | None = None

    def open(self) -> None:
        """
        Відкриває послідовний порт із заданими параметрами.
        """
        try:
            self._ser = serial.Serial(
                port=self.port_name,
                baudrate=self.baudrate,
                timeout=self.timeout,
                # Початково скидаємо DTR та RTS у стан неактивності (високий рівень)
                dtr=False,
                rts=False,
            )
            print(f"[УСПІХ] Порт {self.port_name} успішно відкрито на швидкості {self.baudrate} бод.")
        except serial.SerialException as err:
            print(f"[ПОМИЛКА] Не вдалося відкрити порт {self.port_name}: {err}", file=sys.stderr)
            raise

    def close(self) -> None:
        """
        Безпечно закриває послідовний порт та повертає лінії у високий рівень.
        """
        if self._ser and self._ser.is_open:
            try:
                # Переводимо лінії у неактивний стан перед закриттям
                self.set_dtr(False)
                self.set_rts(False)
                self._ser.close()
                print(f"[ІНФО] Порт {self.port_name} закрито.")
            except serial.SerialException as err:
                print(f"[ПОМИЛКА] Помилка при закритті порту: {err}", file=sys.stderr)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def set_dtr(self, active: bool) -> None:
        """
        Управління лінією DTR.
        :param active: True — активний стан (на піні CH340 встановлюється 0 В);
                       False — неактивний стан (на піні CH340 встановлюється 3.3 В / 5 В).
        """
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито.")

        # У pySerial властивість dtr=True піднімає сигнал RS-232, що на виході CH340 дає 0 В
        self._ser.dtr = active
        voltage_state = "0 V (GND)" if active else "3.3V/5V (VCC)"
        print(f"  -> DTR set to active={active} (На піні чипа: {voltage_state})")

    def set_rts(self, active: bool) -> None:
        """
        Управління лінією RTS.
        :param active: True — активний стан (на піні CH340 встановлюється 0 В);
                       False — неактивний стан (на піні CH340 встановлюється 3.3 В / 5 В).
        """
        if not self._ser or not self._ser.is_open:
            raise RuntimeError("Послідовний порт не відкрито.")

        self._ser.rts = active
        voltage_state = "0 V (GND)" if active else "3.3V/5V (VCC)"
        print(f"  -> RTS set to active={active} (На піні чипа: {voltage_state})")

    def generate_reset_pulse(self, reset_duration_ms: int = 100, boot_hold_ms: int = 50) -> None:
        """
        Генерує послідовність сигналів автоскидання для переведення мікроконтролера (наприклад, ESP8266/ESP32)
        у режим завантажувача (Bootloader Mode):
        1. Встановлює RTS у 0 В (активує GPIO0 в режим прошивки).
        2. Формує коротке опускання DTR у 0 В (імпульс скидання RESET).
        3. Повертає DTR у високий рівень, дозволяючи стартувати чипу.
        4. Повертає RTS у високий рівень.
        """
        print(f"\n--- Генерація імпульсу автоскидання (Reset: {reset_duration_ms} мс) ---")

        # 1. Притискаємо RTS (GPIO0 -> GND)
        self.set_rts(True)
        time.sleep(boot_hold_ms / 1000.0)

        # 2. Подаємо імпульс скидання DTR (RESET -> GND)
        self.set_dtr(True)
        time.sleep(reset_duration_ms / 1000.0)

        # 3. Відпускаємо RESET (DTR -> VCC)
        self.set_dtr(False)
        time.sleep(boot_hold_ms / 1000.0)

        # 4. Відпускаємо GPIO0 (RTS -> VCC)
        self.set_rts(False)
        print("--- Цикл автоскидання завершено ---\n")


def list_available_ports() -> list[str]:
    """
    Повертає список доступних послідовних портів у системі.
    """
    ports = list_ports.comports()
    return [port.device for port in ports]


def main() -> None:
    print("=== Скрипт керування DTR/RTS для USB-UART CH340 ===")

    available = list_available_ports()
    print(f"Знайдені послідовні порти: {available if available else 'Не знайдено портів'}")

    if not available:
        print("[УВАГА] Не знайдено активних пристроїв USB-UART. Підключіть адаптер CH340 та повторіть спробу.")
        return

    # Для прикладу використовуємо перший знайдений порт
    target_port = available[0]
    print(f"Використовуємо порт: {target_port}")

    try:
        # Використання менеджера контексту для автоматичного закриття
        with CH340Controller(port_name=target_port, baudrate=115200) as controller:
            print("\n1. Тестування ліній DTR та RTS у покроковому режимі...")

            print("Встановлення DTR в активний стан (0 В)...")
            controller.set_dtr(True)
            time.sleep(0.5)

            print("Встановлення RTS в активний стан (0 В)...")
            controller.set_rts(True)
            time.sleep(0.5)

            print("Скидання DTR та RTS у неактивний стан (VCC)...")
            controller.set_dtr(False)
            controller.set_rts(False)
            time.sleep(0.5)

            print("\n2. Виконання тестового імпульсу автоскидання завантажувача...")
            controller.generate_reset_pulse(reset_duration_ms=150, boot_hold_ms=50)

    except serial.SerialException as err:
        print(f"\n[АПТАЙМ ПОМИЛКА] Збій зв'язку через послідовний порт: {err}", file=sys.stderr)
    except Exception as err:
        print(f"\n[НЕОЧІКУВАНА ПОМИЛКА] {err}", file=sys.stderr)


if __name__ == "__main__":
    main()

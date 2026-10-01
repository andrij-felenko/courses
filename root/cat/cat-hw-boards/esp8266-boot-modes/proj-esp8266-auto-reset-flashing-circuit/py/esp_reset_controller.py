import time
import serial

class ESPResetController:
    """
    Класична схема auto-reset для ESP8266 на базі двох NPN транзисторів (nodemcu/esptool):
    - DTR керує GPIO0 (через транзистор, інверсія)
    - RTS керує RST (через транзистор, інверсія)

    Таблиця істинності транзисторного вузла Auto-Reset:
    DTR=0, RTS=0 -> GPIO0=1, RST=1 (Нейтральний стан)
    DTR=1, RTS=1 -> GPIO0=1, RST=1 (Захист від блокування)
    DTR=0, RTS=1 -> GPIO0=1, RST=0 (Скидання у звичайний режим)
    DTR=1, RTS=0 -> GPIO0=0, RST=1 (Підготовка до защеплення GPIO0=0)
    """

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self._serial: serial.Serial | None = None

    def open(self) -> None:
        """Відкриває послідовний порт із вимкненими за замовчуванням лініями DTR/RTS."""
        if self._serial is None or not self._serial.is_open:
            self._serial = serial.Serial()
            self._serial.port = self.port
            self._serial.baudrate = self.baudrate
            self._serial.timeout = self.timeout
            # Початковий стан: DTR/RTS у False, щоб не викликати довільне скидання при відкритті
            self._serial.dtr = False
            self._serial.rts = False
            self._serial.open()

    def close(self) -> None:
        """Закриває послідовний порт та відпускає лінії DTR/RTS."""
        if self._serial and self._serial.is_open:
            self._serial.dtr = False
            self._serial.rts = False
            self._serial.close()
            self._serial = None

    def reset_to_bootloader(self) -> None:
        """
        Формує часову діаграму автоскидання для входу в режим UART Download Mode (GPIO0=0, RST=0 -> RST=1):
        1. DTR=1, RTS=0 -> GPIO0 переходить у Low (0V)
        2. DTR=1, RTS=1 -> Скидання RST у Low (0V) під час утримання GPIO0 у Low
        3. Затримка 100 мс для розрядження RC-ланцюга RST
        4. DTR=0, RTS=1 -> Відпускання RST (перехід у High), GPIO0 лишається в Low
        5. Затримка 50 мс для фіксації логічного рівня завантажувачем (Boot Latch)
        6. DTR=0, RTS=0 -> Повернення в нейтральний стан
        """
        if not self._serial or not self._serial.is_open:
            self.open()

        # Крок 1: Встановлюємо GPIO0 = Low (через DTR)
        self._serial.dtr = True
        self._serial.rts = False
        time.sleep(0.05)

        # Крок 2: Активуємо імпульс скидання RST = Low (утримуючи GPIO0 = Low)
        self._serial.dtr = True
        self._serial.rts = True
        time.sleep(0.1)  # 100 мс для гарантованої фіксації скидання

        # Крок 3: Відпускаємо RST = High, утримуючи GPIO0 = Low (ROM защеплює режим UART Download)
        self._serial.dtr = False
        self._serial.rts = True
        time.sleep(0.05)  # 50 мс вікно защеплення ROM

        # Крок 4: Повертаємо лінії в нейтральний стан
        self._serial.dtr = False
        self._serial.rts = False
        time.sleep(0.05)

    def reset_to_app(self) -> None:
        """
        Формує імпульс скидання для автономного запуску програми з Flash (SPI Flash Boot):
        RTS=1, DTR=0 -> RST=0 (Low), GPIO0=1 (High)
        Потім відпускає RST=1 при GPIO0=1.
        """
        if not self._serial or not self._serial.is_open:
            self.open()

        # Подаємо імпульс скидання при високому GPIO0
        self._serial.dtr = False
        self._serial.rts = True
        time.sleep(0.1)

        # Відпускаємо RST
        self._serial.dtr = False
        self._serial.rts = False
        time.sleep(0.05)

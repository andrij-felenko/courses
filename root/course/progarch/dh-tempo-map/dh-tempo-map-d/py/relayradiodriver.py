# 1. Апаратний драйвер: низька частота змін (роки)
class RelayRadioDriver:
    def __init__(self) -> None:
        self._start_byte: int = 0xAA

    def send_switch_command(self, channel: int, state: bool) -> None:
        command_byte = 0x01 if state else 0x00
        checksum = (self._start_byte ^ command_byte ^ channel) & 0xFF
        frame = bytes([self._start_byte, command_byte, channel, checksum])
        self._transmit_uart(frame)

    def _transmit_uart(self, frame: bytes) -> None:
        # Фізичний обмін байтами через апаратну шину хабу
        pass


# 2. Доменні правила та безпека обладнання: середня частота змін (місяці)
import time

class RelaySafetyGuard:
    def __init__(self, driver: RelayRadioDriver) -> None:
        self._driver: RelayRadioDriver = driver
        self._min_interval_sec: float = 0.5
        self._last_switch_time: float = 0.0

    def execute_switch(self, channel: int, state: bool) -> None:
        now = time.monotonic()
        if now - self._last_switch_time < self._min_interval_sec:
            raise RuntimeError("Захист реле від брязкоту: команда відхилена")

        self._driver.send_switch_command(channel, state)
        self._last_switch_time = now


# 3. Інтерфейсне оформлення: надвисока частота змін (дні)
class LightNotificationPresenter:
    def format_state(self, channel_name: str, state: bool, is_eco: bool) -> str:
        eco_suffix = " (екорежим)" if is_eco else ""
        if state:
            return f"Освітлення «${channel_name}» активовано{eco_suffix}"
        return f"Освітлення «${channel_name}» вимкнено"

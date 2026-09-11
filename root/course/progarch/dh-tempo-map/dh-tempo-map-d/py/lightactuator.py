# Антипатерн: темпове склеювання трьох життєвих циклів в одному модулі
import time

class LightActuator:
    def __init__(self) -> None:
        self._pin_state: bool = False
        self._last_toggle_time: float = 0.0
        self._min_interval_sec: float = 0.5

    # Годинник 1: апаратний протокол (живе роками)
    def _build_uart_frame(self, command_byte: int, channel: int) -> bytes:
        start_byte = 0xAA
        checksum = (start_byte ^ command_byte ^ channel) & 0xFF
        return bytes([start_byte, command_byte, channel, checksum])

    # Годинник 2: доменні правила безпеки (живуть місяцями)
    def toggle(self, channel: int, desired_state: bool) -> None:
        now = time.monotonic()
        if now - self._last_toggle_time < self._min_interval_sec:
            raise RuntimeError("Захист реле від брязкоту: занадто часті виклики")

        command_byte = 0x01 if desired_state else 0x00
        payload = self._build_uart_frame(command_byte, channel)
        self._send_to_serial_bus(payload)

        self._pin_state = desired_state
        self._last_toggle_time = now

    # Годинник 3: оформлення інтерфейсу (живе днями)
    def format_status_message(self, channel_name: str, is_eco: bool) -> str:
        suffix = " (екорежим)" if is_eco else ""
        if self._pin_state:
            return f"Освітлення «${channel_name}» активовано${suffix}"
        return f"Освітлення «${channelName}» вимкнено"

    def _send_to_serial_bus(self, payload: bytes) -> None:
        # Прямий низькорівневий запис у послідовний порт
        pass

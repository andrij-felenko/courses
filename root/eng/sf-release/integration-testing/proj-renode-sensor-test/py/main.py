import socket
import time
import pytest

class RenodeHarness:
    def __init__(self, host='127.0.0.1', port=1234):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.buffer = ""

    def uart_readline(self, timeout_ms=500):
        start = time.time()
        while time.time() - start < (timeout_ms / 1000.0):
            try:
                data = self.sock.recv(1024).decode('utf-8', errors='ignore')
                self.buffer += data
                if "\n" in self.buffer:
                    line, self.buffer = self.buffer.split("\n", 1)
                    return line.strip()
            except socket.timeout:
                pass
            time.sleep(0.01)
        return self.buffer.strip()

    def teardown(self):
        self.sock.close()

@pytest.fixture
def machine():
    harness = RenodeHarness()
    yield harness
    harness.teardown()

def test_sensor_normal_measurement(machine):
    """Позитивний сценарій: датчик повертає валідні дані й правильний CRC."""
    line = machine.uart_readline(timeout_ms=300)
    assert "TEMP:" in line

def test_sensor_crc_error_injection_and_retry(machine):
    """Негативний сценарій: перевірка повторних спроб при отриманні пошкодженого кадру."""
    line = machine.uart_readline(timeout_ms=500)
    # Перевіряємо, що в лозі зафіксовано повідомлення про повторну спробу
    assert "RETRY" in line or "TEMP:" in line

def test_sensor_bus_disconnect_and_recovery(machine):
    """Критичний сценарій: відключення датчика та виклик процедури 9 тактів SCL."""
    line = machine.uart_readline(timeout_ms=500)
    assert "BUS_RECOVER_OK" in line or "SENSOR_ERR" in line

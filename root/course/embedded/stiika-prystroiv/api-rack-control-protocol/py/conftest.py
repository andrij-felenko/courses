# conftest.py — Промислова фікстура роботи з апаратним слотом стійки
import pytest
import requests
import time
import serial

RACK_DAEMON_URL = "http://127.0.0.1:8080/rpc"

class RackSlotClient:
    def __init__(self, slot_id: int):
        self.slot_id = slot_id
        self.token = None
        self.uart_path = None
        self.serial_conn = None

    def acquire(self, timeout_sec: int = 120):
        payload = {
            "jsonrpc": "2.0",
            "method": "slot.acquire",
            "params": {"slot_id": self.slot_id, "lease_timeout_sec": timeout_sec},
            "id": 1
        }
        res = requests.post(RACK_DAEMON_URL, json=payload).json()
        if "error" in res:
            raise RuntimeError(f"Не вдалося орендувати слот {self.slot_id}: {res['error']['message']}")
        self.token = res["result"]["lease_token"]
        self.uart_path = res["result"]["uart_device"]

    def power_cycle(self, off_ms: int = 150):
        payload = {
            "jsonrpc": "2.0",
            "method": "slot.power_cycle",
            "params": {
                "slot_id": self.slot_id,
                "lease_token": self.token,
                "off_duration_ms": off_ms,
                "soft_start_enabled": True,
                "verify_no_backfeed": True
            },
            "id": 2
        }
        res = requests.post(RACK_DAEMON_URL, json=payload).json()
        if "error" in res:
            raise RuntimeError(f"Помилка живлення слота {self.slot_id}: {res['error']['message']}")
        return res["result"]

    def flash(self, binary_path: str):
        payload = {
            "jsonrpc": "2.0",
            "method": "slot.flash_image",
            "params": {
                "slot_id": self.slot_id,
                "lease_token": self.token,
                "image_path": binary_path,
                "verify": True,
                "reset_after_flash": True
            },
            "id": 3
        }
        res = requests.post(RACK_DAEMON_URL, json=payload).json()
        if "error" in res:
            raise RuntimeError(f"Помилка прошивання слота {self.slot_id}: {res['error']['message']}")

    def open_uart(self, baud: int = 115200):
        self.serial_conn = serial.Serial(self.uart_path, baudrate=baud, timeout=0.1)
        self.serial_conn.reset_input_buffer()

    def expect_string(self, target: str, timeout_sec: float = 5.0) -> str:
        start_time = time.time()
        accumulated = ""
        while (time.time() - start_time) < timeout_sec:
            chunk = self.serial_conn.read(128).decode(errors="replace")
            if chunk:
                accumulated += chunk
                if target in accumulated:
                    return accumulated
            time.sleep(0.02)
        raise TimeoutError(f"Очікуваний рядок '{target}' не знайдено за {timeout_sec} с. Отримано:\n{accumulated}")

    def release(self):
        if self.serial_conn and self.serial_conn.is_open:
            self.serial_conn.close()
        if self.token:
            payload = {
                "jsonrpc": "2.0",
                "method": "slot.release",
                "params": {"slot_id": self.slot_id, "lease_token": self.token},
                "id": 4
            }
            requests.post(RACK_DAEMON_URL, json=payload)
            self.token = None


@pytest.fixture(scope="function")
def hardware_slot():
    slot = RackSlotClient(slot_id=1)
    slot.acquire(timeout_sec=60)
    
    # 1. Відкриваємо UART ДО подачі живлення, щоб не пропустити early bootlog
    slot.open_uart(baud=115200)
    
    # 2. Робимо апаратний холодний рестарт
    slot.power_cycle(off_ms=150)
    
    yield slot
    
    # 3. Гарантоване очищення та знеструмлення у фіналі
    slot.release()

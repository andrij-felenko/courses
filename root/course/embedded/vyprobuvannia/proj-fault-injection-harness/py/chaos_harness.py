"""
chaos_harness.py — Інструмент ін'єкції збоїв та верифікації надійності IoT.
"""
import os
import time
import random
import socket
import struct
import subprocess
import threading
from typing import List, Dict, Any
import serial
import paho.mqtt.client as mqtt
import pytest


class PowerRelay:
    """Керування лінією живлення мікроконтролера через віртуальний COM-порт."""
    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self._dev = None

    def open(self):
        try:
            self._dev = serial.Serial(self.port, self.baudrate, timeout=1.0)
            time.sleep(0.5)
        except serial.SerialException:
            # Запасний режим для CI без фізичного реле
            self._dev = None

    def power_off(self):
        if self._dev:
            self._dev.write(b"RELAY:OFF\n")
            self._dev.flush()

    def power_on(self):
        if self._dev:
            self._dev.write(b"RELAY:ON\n")
            self._dev.flush()

    def power_cycle(self, off_duration_sec: float = 0.5):
        self.power_off()
        time.sleep(off_duration_sec)
        self.power_on()

    def close(self):
        if self._dev:
            self._dev.close()


class NetworkChaos:
    """Керування втратами, затримками та ізоляцією трафіку через Linux tc-netem."""
    def __init__(self, iface: str = "veth_dut"):
        self.iface = iface

    def _run(self, cmd: str):
        subprocess.run(f"sudo {cmd}", shell=True, check=False,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def clear(self):
        """Скидання всіх мережевих обмежень до штатного режиму."""
        self._run(f"tc qdisc del dev {self.iface} root")

    def set_loss_and_jitter(self, loss_pct: float = 15.0, delay_ms: int = 100, jitter_ms: int = 30):
        """Встановлення випадкових втрат, затримок та дублікатів пакетів."""
        self.clear()
        cmd = (f"tc qdisc add dev {self.iface} root netem "
               f"loss {loss_pct}% delay {delay_ms}ms {jitter_ms}ms 25% "
               f"duplicate 2% corrupt 0.1%")
        self._run(cmd)

    def set_blackout(self):
        """Повна ізоляція пристрою від мережі (100% drop)."""
        self.clear()
        self._run(f"tc qdisc add dev {self.iface} root netem loss 100%")


class FakeNtpServer:
    """Імітатор SNTP-сервера з можливістю введення штучного зсуву часу."""
    NTP_DELTA = 2208988800  # Різниця між 1900 та 1970 роками

    def __init__(self, host: str = "0.0.0.0", port: int = 12300):
        self.host = host
        self.port = port
        self.offset_sec = 0.0
        self._sock = None
        self._thread = None
        self._running = False

    def start(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sock.bind((self.host, self.port))
        self._running = True
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def set_time_shift(self, shift_seconds: float):
        """Встановити зсув часу: позитивний (вперед) або негативний (назад)."""
        self.offset_sec = shift_seconds

    def _serve(self):
        while self._running:
            try:
                data, addr = self._sock.recvfrom(1024)
                if len(data) >= 48:
                    recv_time = time.time() + self.offset_sec + self.NTP_DELTA
                    sec = int(recv_time)
                    frac = int((recv_time - sec) * (2**32))

                    # Формування базового SNTPv4 відповіді
                    resp = bytearray(48)
                    resp[0] = 0x24  # LI=0, VN=4, Mode=4 (Server)
                    resp[1] = 1     # Stratum 1
                    resp[2] = 6     # Poll
                    resp[3] = 0xEC  # Precision
                    struct.pack_into("!II", resp, 32, sec, frac) # Transmit Timestamp
                    struct.pack_into("!II", resp, 40, sec, frac)
                    self._sock.sendto(resp, addr)
            except Exception:
                break

    def stop(self):
        self._running = False
        if self._sock:
            self._sock.close()


class TelemetryCollector:
    """Підписник MQTT для збору та перевірки неперервності лічильників."""
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.received_messages: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
        self.client = mqtt.Client(client_id="pytest_chaos_observer")
        self.client.on_message = self._on_message

    def _on_message(self, client, userdata, msg):
        import json
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            with self.lock:
                self.received_messages.append({
                    "topic": msg.topic,
                    "payload": payload,
                    "recv_ts": time.time()
                })
        except Exception:
            pass

    def start(self, topics: List[str]):
        self.client.connect(self.broker_host, self.broker_port, 60)
        for t in topics:
            self.client.subscribe(t, qos=1)
        self.client.loop_start()

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()

    def clear(self):
        with self.lock:
            self.received_messages.clear()


@pytest.fixture(scope="module")
def harness():
    """Фікстура ініціалізації апаратних та мережевих інтерфейсів стенду."""
    relay = PowerRelay()
    relay.open()
    chaos = NetworkChaos(iface="eth0")
    ntp = FakeNtpServer()
    ntp.start()
    collector = TelemetryCollector()
    collector.start(topics=["nodes/+/state", "nodes/+/replay"])

    yield {"relay": relay, "chaos": chaos, "ntp": ntp, "collector": collector}

    chaos.clear()
    relay.power_on()
    relay.close()
    ntp.stop()
    collector.stop()

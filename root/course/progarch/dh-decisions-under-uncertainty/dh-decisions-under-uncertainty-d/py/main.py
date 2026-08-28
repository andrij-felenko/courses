from typing import Protocol

class DevicePort(Protocol):          # шов: мовою хаба, не мовою радіо
    def set_state(self, device_id: str, on: bool) -> None: ...
    def read(self, device_id: str) -> dict: ...

class ZigbeeAdapter:                 # усе знання про Zigbee замкнене ТУТ
    def __init__(self, radio):
        self._radio = radio          # клієнт конкретного радіо
    def set_state(self, device_id, on):
        self._radio.send(device_id, {"onoff": 1 if on else 0})
    def read(self, device_id):
        return self._radio.query(device_id)

# Правила, стан, логи знають лише DevicePort — і жодного разу «Zigbee».
def run_rule(port: DevicePort):
    if port.read("temp-1")["value"] < 20:
        port.set_state("heater-1", on=True)

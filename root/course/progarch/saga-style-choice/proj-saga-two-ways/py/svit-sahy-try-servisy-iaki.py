# Три сервіси DH. Кожна дія має компенсацію; прапорець down імітує відмову.
from dataclasses import dataclass

class Registry:
    def __init__(self): self.reserved = set()
    async def reserve(self, device_id, home_id): self.reserved.add(device_id)
    async def unreserve(self, device_id):        self.reserved.discard(device_id)

class Hub:
    def __init__(self): self.configured = set(); self.down = False
    async def push_config(self, home_id, device_id):
        if self.down: raise RuntimeError("хаб недоступний")
        self.configured.add(device_id)
    async def wipe_config(self, home_id, device_id): self.configured.discard(device_id)

class Billing:
    def __init__(self): self.metered = set(); self.down = False
    async def start_meter(self, home_id, device_id):
        if self.down: raise RuntimeError("білінг недоступний")
        self.metered.add(device_id)
    async def stop_meter(self, home_id, device_id): self.metered.discard(device_id)

@dataclass
class Enroll:
    home_id: str
    device_id: str

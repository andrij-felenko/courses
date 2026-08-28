import asyncio
import time
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Optional


@dataclass
class DeviceState:
    device_id: str
    reported_temp: float = 0.0
    reported_flow: float = 0.0
    relay_active: bool = False
    last_seen: float = field(default_factory=time.monotonic)


class LocalHubCoordinator:
    def __init__(self, lease_ttl_sec: float = 5.0, heartbeat_interval_sec: float = 2.0):
        self.lease_ttl_sec = lease_ttl_sec
        self.heartbeat_interval_sec = heartbeat_interval_sec
        self.devices: Dict[str, DeviceState] = {}
        self.running = False
        self.electricity_spot_price: float = 0.04  # $/kWh (отримано з хмари)

    def register_telemetry(self, device_id: str, temp: float, flow: float, relay: bool) -> None:
        """Оновлення фактичного стану пристрою (Reported State)."""
        now = time.monotonic()
        if device_id not in self.devices:
            self.devices[device_id] = DeviceState(device_id=device_id)
        
        dev = self.devices[device_id]
        dev.reported_temp = temp
        dev.reported_flow = flow
        dev.relay_active = relay
        dev.last_seen = now

    async def send_mcu_command(self, device_id: str, target_state: bool, power_w: int) -> None:
        """Імітація відправки бінарного кадру на Edge MCU з урахуванням Lease TTL."""
        # У реальній системі тут викликається UART write або публікація в MQTT-SN топік
        print(f"[HUB -> MCU {device_id}] Target: {'ON' if target_state else 'OFF'}, "
              f"Power: {power_w}W, Lease: {int(self.lease_ttl_sec * 1000)}ms")

    async def evaluate_cross_device_rules(self) -> None:
        """Оцінка міжпристроєвих правил рівня комфорту та оптимізації."""
        boiler = self.devices.get("boiler_01")
        if not boiler:
            return

        # Правило комфорту: гріти, якщо ціна вигідна і бак не нагрітий до максимуму
        should_heat = (self.electricity_spot_price < 0.05) and (boiler.reported_temp < 70.0)

        # Локальний хаб не перевіряє аварійний перегрів 85°C — цим займається Edge MCU.
        # Хаб вирішує задачу комфортної уставки та економічної вигоди.
        await self.send_mcu_command("boiler_01", target_state=should_heat, power_w=3000 if should_heat else 0)

    async def run_loop(self) -> None:
        self.running = True
        print("Local Hub Rule Engine Coordinator started.")
        while self.running:
            try:
                await self.evaluate_cross_device_rules()
            except Exception as ex:
                print(f"Error evaluating hub rules: {ex}")
            
            await asyncio.sleep(self.heartbeat_interval_sec)

    def stop(self) -> None:
        self.running = False

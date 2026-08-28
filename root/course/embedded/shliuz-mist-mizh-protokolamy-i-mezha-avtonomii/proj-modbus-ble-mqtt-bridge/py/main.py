import asyncio
import json
import random
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class TelemetryRecord:
    topic: str
    payload: dict
    timestamp: float
    sequence_id: int


class StoreForwardBuffer:
    """Асинхронний циклічний буфер із витісненням застарілих даних (FIFO Drop)."""

    def __init__(self, max_capacity: int = 500):
        self._max_capacity = max_capacity
        self._queue: list[TelemetryRecord] = []
        self._dropped_count = 0
        self._lock = asyncio.Lock()

    async def push(self, record: TelemetryRecord) -> None:
        async with self._lock:
            if len(self._queue) >= self._max_capacity:
                self._queue.pop(0)  # Витіснення найстарішого запису
                self._dropped_count += 1
            self._queue.append(record)

    async def pop(self) -> Optional[TelemetryRecord]:
        async with self._lock:
            if not self._queue:
                return None
            return self._queue.pop(0)

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def dropped(self) -> int:
        return self._dropped_count


class IndustrialIoTGateway:
    """Програмний міст Modbus/BLE-to-MQTT з локальною автономією."""

    PRESSURE_THRESHOLD = 10.0  # bar

    def __init__(self):
        self.buffer = StoreForwardBuffer(max_capacity=500)
        self.wan_connected = False
        self.running = True
        self._seq = 0

    async def execute_autonomy_rule(self, pressure: float) -> None:
        """Прямий локальний контур керування без участі хмари."""
        print(
            f"[AUTONOMY ALERT Py] Критичний тиск {pressure:.2f} bar! "
            f"Локальна дія: Запис Modbus Coil 0x0010 = ON (Аварійне скидання)"
        )

    async def poll_modbus_loop(self) -> None:
        """Задача регулярного опитування Modbus RTU пристроїв."""
        while self.running:
            raw_pressure = 8.0 + random.uniform(-1.0, 3.5)
            self._seq += 1

            print(f"[MODBUS Py] Зчитано тиск: {raw_pressure:.2f} bar")

            # Локальна автономія
            if raw_pressure > self.PRESSURE_THRESHOLD:
                await self.execute_autonomy_rule(raw_pressure)

            record = TelemetryRecord(
                topic="plant/unit1/telemetry/pressure",
                payload={
                    "dev": "boiler_1",
                    "val": round(raw_pressure, 2),
                    "unit": "bar",
                    "ts": time.time(),
                },
                timestamp=time.time(),
                sequence_id=self._seq,
            )
            await self.buffer.push(record)
            await asyncio.sleep(1.0)

    async def receive_ble_loop(self) -> None:
        """Задача отримання телеметрії від бездротових давачів BLE."""
        while self.running:
            raw_temp = 40.0 + random.uniform(-2.0, 4.0)
            self._seq += 1

            record = TelemetryRecord(
                topic="plant/unit1/telemetry/temperature",
                payload={
                    "dev": "ble_sensor_a4",
                    "val": round(raw_temp, 2),
                    "unit": "C",
                    "ts": time.time(),
                },
                timestamp=time.time(),
                sequence_id=self._seq,
            )
            await self.buffer.push(record)
            await asyncio.sleep(1.5)

    async def upstream_mqtt_flusher(self) -> None:
        """Фоновий процес передачі телеметрії та відкладеного дренажу."""
        while self.running:
            if not self.wan_connected:
                await asyncio.sleep(0.2)
                continue

            # Дренаж накопиченої черги зі згладжуванням швидкості
            while self.wan_connected:
                record = await self.buffer.pop()
                if record is None:
                    break

                # Емуляція відправки по MQTT
                serialized = json.dumps(record.payload)
                print(f"[MQTT PUB Py] -> {record.topic} : {serialized}")
                await asyncio.sleep(0.02)  # Rate-limit 50 msg/sec

            await asyncio.sleep(0.1)


async def main():
    gateway = IndustrialIoTGateway()

    # Запуск фонових воркерів
    tasks = [
        asyncio.create_task(gateway.poll_modbus_loop()),
        asyncio.create_task(gateway.receive_ble_loop()),
        asyncio.create_task(gateway.upstream_mqtt_flusher()),
    ]

    print("=== Старт IoT-шлюзу (Python Asyncio) ===")

    # Моделювання 10 тактів роботи
    for step in range(1, 11):
        print(f"\n--- ТАКТ СИСТЕМИ {step} ---")
        if 3 <= step <= 7:
            if gateway.wan_connected or step == 3:
                print(
                    "[WAN] Обрив інтернет-каналу! Активовано буфер Store-and-Forward."
                )
                gateway.wan_connected = False
        else:
            if not gateway.wan_connected:
                print("[WAN] Зв'язок відновлено! Старт фонового дренажу черги.")
                gateway.wan_connected = True

        print(
            f"[BUFFER STATUS] Записів у черзі: {gateway.buffer.size}, "
            f"Втрачено: {gateway.buffer.dropped}"
        )
        await asyncio.sleep(1.0)

    gateway.running = False
    for t in tasks:
        t.cancel()
    print("=== Роботу шлюзу завершено ===")


if __name__ == "__main__":
    asyncio.run(main())

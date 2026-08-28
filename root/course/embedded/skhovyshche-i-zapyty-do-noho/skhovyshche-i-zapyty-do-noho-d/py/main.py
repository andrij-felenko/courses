import asyncio
import asyncpg
from typing import List, Dict, Any
from datetime import datetime

class StoragePipeline:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=5, max_size=20)

    async def flush_telemetry_batch(self, batch: List[Dict[str, Any]]):
        """
        Одночасний запис пачки вимірювань:
        1. Вставка сирих точок у гіпертаблицю через швидкий бінарний протокол COPY.
        2. Атомарний UPSERT поточного стану кожного пристрою в device_state.
        """
        if not batch:
            return

        # Підготовка записів для сирої телеметрії
        raw_records = [
            (
                item["timestamp"],
                item["device_id"],
                item.get("temperature"),
                item.get("humidity"),
                item.get("relay_state"),
                item.get("battery_voltage"),
                item.get("rssi")
            )
            for item in batch
        ]

        async with self.pool.acquire() as conn:
            async with conn.transaction():
                # 1. Швидкісна пакетна вставка сирих даних (COPY протокол)
                await conn.copy_records_to_table(
                    "telemetry_raw",
                    records=raw_records,
                    columns=["time", "device_id", "temperature", "humidity", 
                             "relay_state", "battery_voltage", "rssi"]
                )

                # 2. Атомарне оновлення поточного стану (UPSERT)
                upsert_query = """
                INSERT INTO device_state (
                    device_id, last_seen, temperature, humidity, 
                    relay_state, battery_voltage, rssi, updated_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                ON CONFLICT (device_id) DO UPDATE SET
                    last_seen       = EXCLUDED.last_seen,
                    temperature     = COALESCE(EXCLUDED.temperature, device_state.temperature),
                    humidity        = COALESCE(EXCLUDED.humidity, device_state.humidity),
                    relay_state     = COALESCE(EXCLUDED.relay_state, device_state.relay_state),
                    battery_voltage = COALESCE(EXCLUDED.battery_voltage, device_state.battery_voltage),
                    rssi            = COALESCE(EXCLUDED.rssi, device_state.rssi),
                    updated_at      = NOW()
                WHERE device_state.last_seen <= EXCLUDED.last_seen;
                """
                
                # Знаходимо найсвіжіший стан для кожного пристрою в межах пачки
                latest_by_device = {}
                for item in batch:
                    dev_id = item["device_id"]
                    if dev_id not in latest_by_device or item["timestamp"] > latest_by_device[dev_id]["timestamp"]:
                        latest_by_device[dev_id] = item

                for dev in latest_by_device.values():
                    await conn.execute(
                        upsert_query,
                        dev["device_id"],
                        dev["timestamp"],
                        dev.get("temperature"),
                        dev.get("humidity"),
                        dev.get("relay_state"),
                        dev.get("battery_voltage"),
                        dev.get("rssi")
                    )

    async def get_device_history(self, device_id: str, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        """
        Адаптивний запит історії з автоматичним вибором гранулярності.
        """
        delta = end - start
        async with self.pool.acquire() as conn:
            if delta.total_seconds() <= 86400:  # Менше доби -> бакети по 1 хвилині
                query = """
                SELECT 
                    time_bucket('1 minute', time) AS ts,
                    AVG(temperature) AS temp_avg,
                    MIN(temperature) AS temp_min,
                    MAX(temperature) AS temp_max
                FROM telemetry_raw
                WHERE device_id = $1 AND time >= $2 AND time < $3
                GROUP BY ts
                ORDER BY ts ASC;
                """
            else:  # Понад добу -> читаємо з погодинного матеріалізованого представлення
                query = """
                SELECT 
                    bucket AS ts,
                    temp_avg,
                    temp_min,
                    temp_max
                FROM telemetry_hourly
                WHERE device_id = $1 AND bucket >= $2 AND bucket < $3
                ORDER BY ts ASC;
                """
            rows = await conn.fetch(query, device_id, start, end)
            return [dict(row) for row in rows]

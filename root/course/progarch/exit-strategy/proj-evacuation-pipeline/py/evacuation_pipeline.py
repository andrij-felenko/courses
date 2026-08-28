#!/usr/bin/env python3
"""
evacuation_pipeline.py — Потоковий пайплайн евакуаційного транслятора даних
"""
import hashlib
import json
import logging
import time
import typing
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@dataclass
class EvacuationRecord:
    record_id: str
    timestamp: float
    payload: dict
    checksum: str

class NeutralSchemaConverter:
    """Нормалізує proprietary-типи вендора (DynamoDB/CosmosDB) у відкритий канонічний формат"""

    @staticmethod
    def convert_dynamodb_record(vendor_record: dict) -> EvacuationRecord:
        raw_payload = vendor_record.get("Item", {})
        clean_payload = {}

        # Рекурсивне зняття proprietary-тегів типу {"S": "val"}, {"N": "42"}
        for key, val in raw_payload.items():
            if isinstance(val, dict):
                if "S" in val:
                    clean_payload[key] = str(val["S"])
                elif "N" in val:
                    clean_payload[key] = float(val["N"]) if "." in str(val["N"]) else int(val["N"])
                elif "BOOL" in val:
                    clean_payload[key] = bool(val["BOOL"])
                elif "M" in val:
                    clean_payload[key] = val["M"]
                else:
                    clean_payload[key] = str(val)
            else:
                clean_payload[key] = val

        rec_id = str(clean_payload.get("id", "unknown_id"))
        ts = float(vendor_record.get("CreatedAt", time.time()))

        # Обчислення канонічного SHA-256 хешу для перевірки цілісності
        serialized = json.dumps(clean_payload, sort_keys=True)
        chksum = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        return EvacuationRecord(record_id=rec_id, timestamp=ts, payload=clean_payload, checksum=chksum)

class EvacuationStreamPipeline:
    def __init__(self, target_writer: typing.Callable[[EvacuationRecord], bool], batch_size: int = 100):
        self.writer = target_writer
        self.batch_size = batch_size
        self.evacuated_count = 0
        self.failed_count = 0

    def process_stream_batch(self, vendor_batch: typing.List[dict]) -> dict:
        start_time = time.time()
        logging.info(f"Starting batch evacuation of {len(vendor_batch)} items...")

        for raw_item in vendor_batch:
            try:
                record = NeutralSchemaConverter.convert_dynamodb_record(raw_item)
                success = self.writer(record)
                if success:
                    self.evacuated_count += 1
                else:
                    self.failed_count += 1
                    logging.warning(f"Target writer rejected record {record.record_id}")
            except Exception as err:
                self.failed_count += 1
                logging.error(f"Critical error converting record: {err}")

        duration = time.time() - start_time
        logging.info(f"Batch completed in {duration:.3f}s. Evacuated: {self.evacuated_count}, Failed: {self.failed_count}")
        return {"evacuated": self.evacuated_count, "failed": self.failed_count, "duration": duration}

def open_postgres_target_writer(record: EvacuationRecord) -> bool:
    """Імітація зчитування нейтрального запису та збереження у відкритий PostgreSQL/MinIO-кластер"""
    # У продакшені тут викликається SQL `INSERT INTO telemetry VALUES (...) ON CONFLICT DO UPDATE`
    if not record.checksum:
        return False
    return True

if __name__ == "__main__":
    # Тестовий потік даних у proprietary-форматі DynamoDB Streams
    sample_vendor_stream = [
        {
            "Item": {
                "id": {"S": "sensor_living_room_01"},
                "temp": {"N": "22.4"},
                "humidity": {"N": "45.0"},
                "active": {"BOOL": True}
            },
            "CreatedAt": 1690000000
        },
        {
            "Item": {
                "id": {"S": "sensor_kitchen_02"},
                "temp": {"N": "26.1"},
                "humidity": {"N": "58.2"},
                "active": {"BOOL": True}
            },
            "CreatedAt": 1690000100
        }
    ]

    pipeline = EvacuationStreamPipeline(target_writer=open_postgres_target_writer)
    stats = pipeline.process_stream_batch(sample_vendor_stream)
    print(f"\nFinal Summary: {stats['evacuated']} records successfully migrated.")

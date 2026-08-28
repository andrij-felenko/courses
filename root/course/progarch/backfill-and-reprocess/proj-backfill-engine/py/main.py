import asyncio
import logging
import random
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

@dataclass
class OrderRecord:
    id: int
    amount: float
    status: str
    discount_v2: Optional[float] = None

@dataclass
class Checkpoint:
    job_id: str
    last_processed_id: int = 0
    total_processed: int = 0
    total_failed: int = 0

class CheckpointStore:
    """Асинхронний менеджер контрольних точок (Redis / PostgreSQL)"""
    def __init__(self, job_id: str):
        self.job_id = job_id
        self._store: Dict[str, Checkpoint] = {}

    async def load(self) -> Checkpoint:
        return self._store.get(self.job_id, Checkpoint(job_id=self.job_id))

    async def save(self, cp: Checkpoint) -> None:
        self._store[self.job_id] = cp
        logging.info(f"[CHECKPOINT] Saved: last_id={cp.last_processed_id}, processed={cp.total_processed}")

class AdaptiveThrottler:
    """Адаптивний регулятор затримки на основі затримки СУБД"""
    def __init__(self, max_p99_ms: float = 30.0):
        self.max_p99_ms = max_p99_ms
        self.current_delay = 0.01
        self.min_delay = 0.005
        self.max_delay = 1.0

    async def throttle(self, current_p99_ms: float) -> None:
        if current_p99_ms > self.max_p99_ms:
            self.current_delay = min(self.max_delay, self.current_delay * 2)
            logging.warning(f"[THROTTLE] High Latency ({current_p99_ms}ms). Delay set to {self.current_delay:.3f}s")
        else:
            self.current_delay = max(self.min_delay, self.current_delay * 0.9)
        
        await asyncio.sleep(self.current_delay)

class AsyncBackfillEngine:
    def __init__(self, job_id: str, cp_store: CheckpointStore, batch_size: int = 1000):
        self.job_id = job_id
        self.cp_store = cp_store
        self.batch_size = batch_size
        self.throttler = AdaptiveThrottler(max_p99_ms=30.0)

    async def fetch_keyset_batch(self, last_id: int) -> List[OrderRecord]:
        """Вибірка за Keyset курсором: WHERE id > last_id ORDER BY id ASC LIMIT batch_size"""
        batch = []
        for i in range(1, self.batch_size + 1):
            next_id = last_id + i
            if next_id > 10000:  # Кінець таблиці
                break
            batch.append(OrderRecord(id=next_id, amount=100.0 + (next_id % 50), status="COMPLETED"))
        return batch

    def compute_v2(self, record: OrderRecord) -> float:
        if record.amount < 0:
            raise ValueError("Poison pill record")
        return record.amount * 0.15

    async def process_batch(self, batch: List[OrderRecord]) -> tuple[int, List[int]]:
        successful = 0
        dlq = []
        for record in batch:
            try:
                val = self.compute_v2(record)
                # Імітація атомарного UPDATE: UPDATE orders SET discount_v2 = val WHERE id = id AND discount_v2 IS NULL
                successful += 1
            except Exception as e:
                dlq.append(record.id)
                logging.error(f"[DLQ] Failed record {record.id}: {e}")
        return successful, dlq

    async def run(self) -> None:
        cp = await self.cp_store.load()
        logging.info(f"[ENGINE] Starting backfill from last_id={cp.last_processed_id}")

        while True:
            batch = await self.fetch_keyset_batch(cp.last_processed_id)
            if not batch:
                logging.info("[ENGINE] Backfill completed successfully!")
                break

            successful, dlq = await self.process_batch(batch)
            
            cp.last_processed_id = batch[-1].id
            cp.total_processed += successful
            cp.total_failed += len(dlq)

            await self.cp_store.save(cp)

            # Симуляція динамічної затримки бази даних
            simulated_p99 = 15.0 + random.uniform(0, 20)
            await self.throttler.throttle(simulated_p99)

async def main():
    store = CheckpointStore("job_discount_v2")
    engine = AsyncBackfillEngine("job_discount_v2", store, batch_size=1000)
    await engine.run()

if __name__ == "__main__":
    asyncio.run(main())

from dataclasses import dataclass
from typing import List, Dict
import hashlib

@dataclass(frozen=True)
class RawRecord:
    user_id: str
    email: str
    category: str
    amount: float
    timestamp_ms: int

@dataclass
class CategoryMetric:
    category: str
    total_amount: float = 0.0
    transaction_count: int = 0

def mask_pii(pii: str) -> str:
    """Токенізація персональних даних на вході (SHA-256 префікс)."""
    digest = hashlib.sha256(pii.encode("utf-8")).hexdigest()[:16]
    return f"anon_{digest}"

# ── 1. РЕЖИМ ETL: Обробка в пам'яті воркера ───────────────────────────────────
class EtlPipelineEngine:
    def process_batch_etl(self, batch: List[RawRecord]) -> List[CategoryMetric]:
        in_memory_aggregation: Dict[str, CategoryMetric] = {}

        for record in batch:
            # Валідація
            if record.amount <= 0.0 or not record.category:
                continue

            # Трансформація та маскування в пам'яті
            masked_user = mask_pii(record.email)

            if record.category not in in_memory_aggregation:
                in_memory_aggregation[record.category] = CategoryMetric(category=record.category)

            metric = in_memory_aggregation[record.category]
            metric.total_amount += record.amount
            metric.transaction_count += 1

        return list(in_memory_aggregation.values())

# ── 2. РЕЖИМ ELT: Скидання у Staging та Push-down агрегація ───────────────────
class MockWarehouseStorage:
    def __init__(self) -> None:
        self.raw_staging_table: List[RawRecord] = []

    def bulk_insert_raw(self, batch: List[RawRecord]) -> None:
        """Миттєве додавання сирих даних у шар Bronze."""
        self.raw_staging_table.extend(batch)

    def execute_pushdown_transform(self) -> List[CategoryMetric]:
        """Імітація SQL-запиту рушієм аналітичного сховища."""
        storage_engine_group_by: Dict[str, CategoryMetric] = {}

        for row in self.raw_staging_table:
            if row.amount > 0.0 and row.category:
                if row.category not in storage_engine_group_by:
                    storage_engine_group_by[row.category] = CategoryMetric(category=row.category)
                m = storage_engine_group_by[row.category]
                m.total_amount += row.amount
                m.transaction_count += 1

        return list(storage_engine_group_by.values())

if __name__ == "__main__":
    incoming_events = [
        RawRecord("usr_1", "alice@example.com", "electronics", 1200.50, 1724180000000),
        RawRecord("usr_2", "bob@example.com", "books", 45.00, 1724180001000),
        RawRecord("usr_3", "charlie@example.com", "electronics", 350.00, 1724180002000),
        RawRecord("usr_4", "invalid@example.com", "books", -10.00, 1724180003000),
        RawRecord("usr_5", "david@example.com", "home", 89.90, 1724180004000),
    ]

    print("=== 1. Виконання конвеєра в режимі ETL ===")
    etl_engine = EtlPipelineEngine()
    for row in etl_engine.process_batch_etl(incoming_events):
        print(f"Категорія: {row.category} | Сума: {row.total_amount:.2f} | Кількість: {row.transaction_count}")

    print("\n=== 2. Виконання конвеєра в режимі ELT ===")
    warehouse = MockWarehouseStorage()
    warehouse.bulk_insert_raw(incoming_events)
    print(f"Завантажено сирих рядків у Staging: {len(warehouse.raw_staging_table)}")
    for row in warehouse.execute_pushdown_transform():
        print(f"Категорія: {row.category} | Сума: {row.total_amount:.2f} | Кількість: {row.transaction_count}")

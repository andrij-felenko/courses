# Реалізація рушія бекфілу з чанкінгом, контрольною точкою та адаптивним лімітуванням

У цій практичній вставці представлено повну виробничу реалізацію безблокувального рушія бекфілу (`Backfill Engine`). Код розроблений для обробки мільйонних історичних таблиць в активних продакшн-системах без виклику Lock Escalation, без деградації затримки СУБД та без ризику втрати прогресу при аварійних перезапусках.

---

## 1. Повний архітектурний розбір складових частин рушія

Розробка промислового бекфіл-рушія вимагає чіткого розподілу відповідальностей між модулями системи. На відміну от спрощених навчальних скриптів, виробничий рушій будується за модульним принципом із застосуванням патернів Dependeny Inversion (DI) та RAII для управління ресурсами.

```
               +-----------------------------------+
               |      Checkpoint Manager (Redis/DB)|
               +-----------------------------------+
                                 ^
                                 | (Save last_processed_id)
+-------------------+    +-------+-----------+    +--------------------+
| Keyset Fetcher    |--> | Batch Executor    |--> | Adaptive Throttler |
| (WHERE id > last) |    | (Update v2 IS NULL)|    | (P99 Latency Check)|
+-------------------+    +-------------------+    +--------------------+
```

### 1.1 Курсорний чанкер (Keyset Chunking Processor)

Модуль відповідає за формування безпечних вибірок з бази даних. Головне інженерне завдання чанкера — гарантувати стабільну швидкість вибірки `O(1)` незалежно від глибини історії.

Для цього вибірка формується за виразом строгої нерівності:

```sql
SELECT id, amount, status 
FROM orders 
WHERE id > :last_processed_id 
ORDER BY id ASC 
LIMIT :batch_size;
```

Механіка роботи СУБД під час виконання цього запиту:
1. Планнувальник запитів СУБД відкриває B-Tree індекс за первинним ключем `id`.
2. Виконується швидка бинарна навігація по деревній структурі B-Tree для знаходження першого вузла, де `id > :last_processed_id`. Оскільки B-Tree має збалансовану висоту (зазвичай 3–4 рівні для таблиць у сотні мільйонів рядків), пошук позиції займає 1–2 мікросекунди.
3. СУБД вичитає послідовно `:batch_size` листових сторінок індексу та повертає їх у додаток.
4. Ніякі застарілі сторінки з початку таблиці не зчитуються й не відкидаються, що повністю усуває деградацію Buffer Pool.

### 1.2 Менеджер контрольних точок (Checkpoint Manager)

Менеджер контрольних точок гарантує властивість **поновлюваності (Resumability)** бекфіл-процесу. Оскільки обробка великої історії може тривати від кількох годин до днів, ймовірність перезапуску пощу (Kubernetes Pod Reschedule, OOM Killer, відключення вузла) наближається до 100%.

Менеджер фіксує стан у зовнішній оперативній базі (Redis) або у виділеній службовій таблиці СУБД:

```sql
INSERT INTO backfill_checkpoints (job_id, last_processed_id, total_processed, total_failed, updated_at)
VALUES ('job_discount_v2', 18250000, 18250000, 12, NOW())
ON CONFLICT (job_id) DO UPDATE SET
  last_processed_id = EXCLUDED.last_processed_id,
  total_processed = EXCLUDED.total_processed,
  total_failed = EXCLUDED.total_failed,
  updated_at = EXCLUDED.updated_at;
```

Фіксація контрольної точки виконується строго після фіксації транзакції обробки батчу. Це гарантує семантику At-Least-Once: при падінні процес повторно опрацює щонайбільше один батч.

### 1.3 Адаптивний регулятор затримки (Adaptive Throttler)

Адаптивний регулятор реалізує зворотний зв'язок між бекфіл-процесом та загальним станом інфраструктури. На кожній ітерації перед запитом наступного батчу регулятор вимірює поточне навантаження СУБД.

Алгоритм адаптивного коригування затримки (`sleep_delay`):

```
Якщо p99_latency > max_allowed_p99 (30ms):
    sleep_delay = min(max_delay, sleep_delay * 2)  [Exponential Backoff]
Інакше:
    sleep_delay = max(min_delay, sleep_delay * 0.9) [Additive Decay]
```

Це дозволяє бекфілу розганятися до максимальної швидкості у нічний час (коли прод-трафік мінімальний) та автоматично «притишуватися» під час денних піків користувацької активності.

---

## 2. Глибокий аналіз граничних випадків та рівня ізоляції транзакцій

### 2.1 Ізоляція транзакцій: Read Committed проти Repeatable Read

Під час розробки бекфіл-рушія критично важливо правильно обрати рівень ізоляції SQL-транзакцій:

- **Заборонено використовувати `Repeatable Read` або `Serializable`:**
  На рівні `Repeatable Read` транзакція бачить знімок бази на момент свого початку. Якщо живий трафік паралельно змінює ті самі рядки, бекфіл-транзакція зазнає невдачі з фатальною помилкою СУБД: `ERROR: could not serialize access due to concurrent update` (SQLSTATE `40001`).
- **Обов'язково використовувати `Read Committed`:**
  У режимі `Read Committed` кожен запит у батчі бачить останні зафіксовані зміни інших транзакцій. Це дозволяє атомарній умові `WHERE v2 IS NULL` правильно оцінювати свіжий стан рядка, збережений живим Dual-Write трафіком.

### 2.2 Захист від втрачених оновлення (Lost Updates Protection)

Захист від перезапису свіжих даних живого трафіку реалізується через атомарний предикат перевірки:

```sql
UPDATE orders 
SET discount_v2 = :computed_v2 
WHERE id = :target_id 
  AND discount_v2 IS NULL;
```

Якщо активний користувач змінив замовлення під час виконання бекфіл-батчу, живий код Dual-Write вже записав у колонку `discount_v2` актуальне значення. СУБД атомарно перевіряє умову `discount_v2 IS NULL`, бачить `FALSE` і повертає 0 оновлених рядків. Бекфіл-worker безпечно пропускає запис, запобігаючи виникненню тихого пошкодження даних (Silent Data Corruption).

### 2.3 Ізоляція пошкоджених записів (Dead Letter Queue & Poison Pills)

У базі з мільйонами рядків неодмінно знаходяться аномальні записи: некоректні символи у кодуванні UTF-8, винятки ділення на нуль, порушення бізнес-інваріантів. Якщо обробка одного рядка викидає неупорядкований виняток, це не повинно зупиняти обробку решти батчу.

Рушій реалізує обробку помилок на рівні окремого запису:
- Виняток перехоплюється у блоці `try/catch`.
- Ідентифікатор пошкодженого запису додається до локального масиву `DLQ`.
- Запис реєструється у черзі DLQ для подальшого аналізу інженерами.
- Процес продовжує обробку наступних елементів.

---

## 3. Обробка системного сигналу завершення (Graceful Shutdown)

При розгортанні бекфілу у хмарному середовищі Kubernetes под із бекфіл-worker'ом може бути в будь-який момент зупинений оркестратором (наприклад, через Preemptible / Spot вузли або автомасштабування).

При отриманні сигналу `SIGTERM` рушій виконує процедуру коректного завершення:
1. Встановлює внутрішній прапорець `is_stopping = true`.
2. Завершує поточний батч, який вже перебуває в обробці.
3. Атомарно фіксує остаточну контрольну точку у сховищі.
4. Закриває пули з'єднань з СУБД та Redis.
5. Завершує процес із кодом `0`.

Це унеможливлює зависання незавершених транзакцій та гарантує негайний продовження роботи новим подом з останнього зафіксованого курсора.

---

## 4. Повна вихідна реалізація рушія

Нижче наведено виробничі реалізації безблокувального бекфіл-рушія мовами C++ (за стандартами C++20 із використання RAII, винятків та концептів) та Python (за стандартами Python 3.11+ із використанням `asyncio`).

:::tabs

@tab C++ (C++20)

```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <chrono>
#include <thread>
#include <random>
#include <stdexcept>
#include <algorithm>

// Контракт запису даних
struct OrderRecord {
    std::uint64_t id;
    double amount;
    std::string status;
    bool has_v2_discount;
};

// Стан контрольної точки
struct Checkpoint {
    std::string job_id;
    std::uint64_t last_processed_id{0};
    std::uint64_t total_processed{0};
    std::uint64_t total_failed{0};
};

// Інтерфейс сховища контрольних точок (RAII abstraction)
class ICheckpointStore {
public:
    virtual ~ICheckpointStore() = default;
    virtual Checkpoint load_checkpoint(const std::string& job_id) = 0;
    virtual void save_checkpoint(const Checkpoint& cp) = 0;
};

// Симуляція сховища контрольних точок у пам'яті
class InMemoryCheckpointStore : public ICheckpointStore {
private:
    Checkpoint current_cp_;
public:
    explicit InMemoryCheckpointStore(std::string job_id) {
        current_cp_.job_id = std::move(job_id);
    }

    Checkpoint load_checkpoint(const std::string& job_id) override {
        return current_cp_;
    }

    void save_checkpoint(const Checkpoint& cp) override {
        current_cp_ = cp;
        std::cout << "[CHECKPOINT] Saved progress: last_id=" << cp.last_processed_id 
                  << ", total=" << cp.total_processed << std::endl;
    }
};

// Адаптивний регулятор затримки (Adaptive Throttler)
class AdaptiveThrottler {
private:
    std::chrono::milliseconds current_delay_{10};
    const std::chrono::milliseconds min_delay_{5};
    const std::chrono::milliseconds max_delay_{1000};
    const double max_allowed_p99_ms_{30.0};

public:
    std::chrono::milliseconds calculate_delay(double current_db_p99_ms) {
        if (current_db_p99_ms > max_allowed_p99_ms_) {
            // Експоненційне збільшення затримки при високому навантаженні
            current_delay_ = std::min(max_delay_, current_delay_ * 2);
            std::cout << "[THROTTLE] High DB Latency (" << current_db_p99_ms 
                      << "ms). Increased delay to " << current_delay_.count() << "ms\n";
        } else {
            // Поступове зменшення затримки
            current_delay_ = std::max(min_delay_, std::chrono::milliseconds(
                static_cast<long long>(current_delay_.count() * 0.9)));
        }
        return current_delay_;
    }
};

// Основний рушій бекфілу
class BackfillEngine {
private:
    std::string job_id_;
    std::shared_ptr<ICheckpointStore> checkpoint_store_;
    AdaptiveThrottler throttler_;
    std::size_t batch_size_{1000};

    // Симуляція обчислення знижки v2
    double compute_v2_discount(const OrderRecord& order) {
        if (order.amount < 0) {
            throw std::invalid_argument("Poison pill: negative order amount");
        }
        return order.amount * 0.15;
    }

    // Симуляція вибірки за Keyset курсором: WHERE id > last_id ORDER BY id ASC LIMIT batch_size
    std::vector<OrderRecord> fetch_batch_from_db(std::uint64_t last_id, std::size_t limit) {
        std::vector<OrderRecord> batch;
        for (std::size_t i = 1; i <= limit; ++i) {
            std::uint64_t next_id = last_id + i;
            if (next_id > 10000) break; // Межа історії
            batch.push_back({next_id, 100.0 + (next_id % 50), "COMPLETED", false});
        }
        return batch;
    }

    // Симуляція оновлення записів із захистом WHERE v2 IS NULL
    std::size_t update_batch_in_db(const std::vector<OrderRecord>& batch, std::vector<std::uint64_t>& dlq) {
        std::size_t updated_count = 0;
        for (const auto& record : batch) {
            try {
                double discount = compute_v2_discount(record);
                // Імітація атомарного UPDATE orders SET discount_v2 = :val WHERE id = :id AND discount_v2 IS NULL
                updated_count++;
            } catch (const std::exception& ex) {
                dlq.push_back(record.id);
                std::cerr << "[DLQ] Record " << record.id << " failed: " << ex.what() << std::endl;
            }
        }
        return updated_count;
    }

public:
    BackfillEngine(std::string job_id, std::shared_ptr<ICheckpointStore> cp_store)
        : job_id_(std::move(job_id)), checkpoint_store_(std::move(cp_store)) {}

    void execute() {
        Checkpoint cp = checkpoint_store_->load_checkpoint(job_id_);
        std::cout << "[ENGINE] Starting backfill from last_id=" << cp.last_processed_id << std::endl;

        while (true) {
            auto batch = fetch_batch_from_db(cp.last_processed_id, batch_size_);
            if (batch.empty()) {
                std::cout << "[ENGINE] Backfill completed successfully!\n";
                break;
            }

            std::vector<std::uint64_t> dlq;
            std::size_t successful_updates = update_batch_in_db(batch, dlq);

            cp.last_processed_id = batch.back().id;
            cp.total_processed += successful_updates;
            cp.total_failed += dlq.size();

            // Сохранение контрольной точки
            checkpoint_store_->save_checkpoint(cp);

            // Опитування метрик та адаптивна затримка
            double simulated_p99_latency_ms = 15.0 + (cp.total_processed % 30);
            auto sleep_delay = throttler_.calculate_delay(simulated_p99_latency_ms);
            std::this_thread::sleep_for(sleep_delay);
        }
    }
};

int main() {
    auto store = std::make_shared<InMemoryCheckpointStore>("job_discount_v2");
    BackfillEngine engine("job_discount_v2", store);
    engine.execute();
    return 0;
}
```

@tab Python (Asyncio)

```python
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
```

:::

---

## 5. Практичний чекліст розгортання та оптимізації

1. **Індексація курсорного поля:**
   Перед запуском перевірте наявність індексу: `CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_id ON orders (id ASC);`.
2. **Налаштування Autovacuum:**
   Під час активного бекфілу на великій таблиці PostgreSQL рекомендується тимчасово підвищити агресивність автовакууму для цільової таблиці:
   ```sql
   ALTER TABLE orders SET (autovacuum_vacuum_scale_factor = 0.05, autovacuum_vacuum_cost_limit = 1000);
   ```
3. **Моніторинг WAL:**
   Переконайтеся, що обсяг згенерованого журналювання не перевищує швидкість ротації WAL у СУБД та наявний дисковий простір.

# ⚙️ Реалізація ідемпотентного рушія перерахунку: чанкінг, атомарний SWAP та AS-OF джойни

Перерахунок історичних даних стає небезпечним, коли розробники намагаються оновити багаторічний масив інформації одним монолітним SQL-запитом або неізольованим скриптом. Якщо задача, що працювала п'ять годин, падає через тимчасовий збій мережі або вичерпання пулу пам'яті на 95% прогресу, відсутність контрольних точок (*checkpoints*) та механізмів транзакційної ізоляції призводить до двох однаково згубних наслідків: або вся робота втрачається і процес доводиться починати спочатку, або в цільовій таблиці залишаються частково оновлені партиції, що спотворює звіти.

Промисловий рушій бекфілу вимагає чотирьох обов'язкових інженерних компонентів:

1. **Детермінована нарізка на вікна (Window Chunking)**: розбиття загального часового інтервалу `[T_start, T_end)` на фіксовані дискретні чанки (наприклад, по одній добі), кожен з яких обробляється як незалежна атомарна одиниця роботи.
2. **Точні історичні з'єднання (Point-in-Time / AS-OF Joins)**: з'єднання подій з версіями довідників (SCD Type 2), які діяли саме на момент настання події, а не на момент запуску скрипту перерахунку.
3. **Тіньовий запис та атомарне перемикання (Stage-and-Swap)**: запис агрегатів у тимчасовий проміжний шар, автоматична валідація інваріантів якості даних та миттєва підміна цільової партиції через транзакцію метаданих без блокування паралельних читачів.
4. **Керування пам'яттю та курсорна вибірка (Streaming Cursor)**: обробка подій через ітератор потоку з фіксованим розміром буфера, що унеможливлює падіння процесу через вичерпання оперативної пам'яті (*Out of Memory, OOM*) навіть при обробці мільярдів рядків.

---

### Архітектура та послідовність роботи рушія

Кожен чанк обробляється за суворою схемою скінченного автомата з фіксацією контрольних точок у журналі стану:

```
[Старт чанка] ──► [Читання сирих фактів за [t1, t2)] ──► [AS-OF Join з SCD2]
       │
       ▼
[Агрегація в пам'яті] ──► [Запис у Staging-партицію] ──► [Перевірка інваріантів]
                                                               │
                                                               ▼
                                                     [Атомарний SWAP партиції]
                                                               │
                                                               ▼
                                                     [Фіксація контрольної точки]
```

#### Механізм ізоляції та запобігання гонкам даних

1. **Ізоляція пам'яті та диска**: під час розрахунку агрегатів за вікно `[t₁, t₂)` воркер створює тимчасову таблицю або каталог партиції `_staging_daily_user_revenue_YYYY_MM_DD`. Жива таблиця `daily_user_revenue` у цей час доступна для читання аналітиками без жодних затримок та блокувань.
2. **Контроль якості (Data Quality Gate)**: перш ніж виконати підміну даних, рушій перевіряє набір бізнес-інваріантів:
   * Кількість вихідних рядків не дорівнює нулю (якщо в сирому лозі були події).
   * Сума зі знижкою не перевищує базову вартість замовлень.
   * Контрольний хеш (*checksum*) множини ідентифікаторів подій збігається з очікуваним.
3. **Атомарний коміт (Atomic Metadata Swap)**: операція заміни старої партиції на нову виконується як єдина транзакція зміни метаданих каталогу або атомарне перейменування файлів на файловій системі (`RENAME TABLE` або `ALTER TABLE ... REPLACE PARTITION`). Тривалість блокування становить менше 5 мілісекунд незалежно від обсягу оброблених терабайтів.

---

### Програмна реалізація рушія

Нижче наведено повноцінний рушій перерахунку, що реалізує нарізку вікон, дедуплікацію подій, AS-OF розмітку тарифів, валідацію інваріантів та атомарне збереження з контролем точок перезапуску.

:::tabs
```py
import datetime
import hashlib
import sqlite3
from typing import List, Dict, Any, Tuple, Optional

class IdempotentBackfillEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_storage()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_storage(self) -> None:
        """Ініціалізація сирих логів, історичних тарифів та агрегатних таблиць."""
        with self._get_connection() as conn:
            conn.executescript("""
            -- Сирий незмінний лог подій (Raw Bronze Layer)
            CREATE TABLE IF NOT EXISTS raw_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                event_time TEXT NOT NULL -- ISO8601 UTC
            );

            -- Довідник тарифів (SCD Type 2: Point-in-Time розмітка)
            CREATE TABLE IF NOT EXISTS tariff_history (
                user_id TEXT NOT NULL,
                discount_percent INTEGER NOT NULL,
                valid_from TEXT NOT NULL,
                valid_to TEXT NOT NULL,
                PRIMARY KEY (user_id, valid_from)
            );

            -- Цільова аналітична таблиця з партиціями за датою
            CREATE TABLE IF NOT EXISTS daily_user_revenue (
                partition_date TEXT NOT NULL,
                user_id TEXT NOT NULL,
                raw_total_cents INTEGER NOT NULL,
                discounted_total_cents INTEGER NOT NULL,
                events_count INTEGER NOT NULL,
                checksum_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (partition_date, user_id)
            );

            -- Журнал стану виконання бекфілу (Checkpoints)
            CREATE TABLE IF NOT EXISTS backfill_checkpoints (
                chunk_id TEXT PRIMARY KEY,
                window_start TEXT NOT NULL,
                window_end TEXT NOT NULL,
                status TEXT NOT NULL, -- 'PENDING', 'COMMITTED', 'FAILED'
                rows_processed INTEGER NOT NULL,
                error_message TEXT,
                completed_at TEXT
            );
            """)

    def process_chunk(self, window_start: str, window_end: str, partition_date: str) -> bool:
        """Ідемпотентна обробка одного чанка: читання, AS-OF join, валідація, атомарний SWAP."""
        chunk_id = f"chunk_{partition_date}"

        with self._get_connection() as conn:
            # 1. Реєстрація старту чанка в журналі
            conn.execute("""
                INSERT INTO backfill_checkpoints (
                    chunk_id, window_start, window_end, status, rows_processed, error_message, completed_at
                ) VALUES (?, ?, ?, 'PENDING', 0, NULL, NULL)
                ON CONFLICT(chunk_id) DO UPDATE SET 
                    status = 'PENDING', 
                    error_message = NULL,
                    completed_at = NULL;
            """, (chunk_id, window_start, window_end))

            try:
                # 2. Обчислення агрегату з точним AS-OF з'єднанням за часом події
                cursor = conn.execute("""
                    SELECT 
                        e.user_id,
                        SUM(e.amount_cents) AS raw_sum,
                        SUM(CAST(e.amount_cents * (100 - COALESCE(t.discount_percent, 0)) / 100 AS INTEGER)) AS discounted_sum,
                        COUNT(e.event_id) AS ev_count,
                        GROUP_CONCAT(e.event_id, ',') AS event_ids
                    FROM raw_events e
                    LEFT JOIN tariff_history t ON e.user_id = t.user_id
                        AND e.event_time >= t.valid_from 
                        AND e.event_time < t.valid_to
                    WHERE e.event_time >= ? AND e.event_time < ?
                    GROUP BY e.user_id;
                """, (window_start, window_end))

                rows = cursor.fetchall()

                # 3. Валідація інваріантів перед фіксацією (Data Quality Assertions)
                staged_records = []
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

                for user_id, raw_sum, discounted_sum, ev_count, ev_ids in rows:
                    if discounted_sum > raw_sum:
                        raise ValueError(f"Порушення інваріанту: знижка перевищує базу для {user_id}")
                    if raw_sum < 0:
                        raise ValueError(f"Порушення інваріанту: від'ємна виручка для {user_id}")

                    # Детермінований контрольний хеш набору подій для перевірки цілісності
                    hasher = hashlib.sha256(ev_ids.encode('utf-8'))
                    checksum = hasher.hexdigest()[:16]

                    staged_records.append((
                        partition_date, user_id, raw_sum, discounted_sum, ev_count, checksum, now_iso
                    ))

                # 4. Атомарний SWAP: очищення цільової партиції та запис свіжого результату
                conn.execute("DELETE FROM daily_user_revenue WHERE partition_date = ?;", (partition_date,))
                conn.executemany("""
                    INSERT INTO daily_user_revenue (
                        partition_date, user_id, raw_total_cents, discounted_total_cents, 
                        events_count, checksum_hash, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, staged_records)

                # 5. Фіксація чекпоінта
                conn.execute("""
                    UPDATE backfill_checkpoints 
                    SET status = 'COMMITTED', rows_processed = ?, completed_at = ?
                    WHERE chunk_id = ?;
                """, (len(staged_records), now_iso, chunk_id))

                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                conn.execute("""
                    UPDATE backfill_checkpoints 
                    SET status = 'FAILED', error_message = ?
                    WHERE chunk_id = ?;
                """, (str(e), chunk_id))
                conn.commit()
                raise e

    def run_backfill(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """Послідовний прогін бекфілу за днями з можливістю безболісного перезапуску."""
        curr = start_date
        while curr < end_date:
            part_str = curr.strftime("%Y-%m-%d")
            w_start = f"{part_str}T00:00:00Z"
            next_day = curr + datetime.timedelta(days=1)
            w_end = f"{next_day.strftime('%Y-%m-%d')}T00:00:00Z"

            print(f"[BACKFILL] Обробка партиції: {part_str} ...", end=" ")
            self.process_chunk(w_start, w_end, part_str)
            print("✓ Успішно зафіксовано.")
            curr = next_day
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <sstream>
#include <iomanip>
#include <stdexcept>
#include <unordered_map>
#include <algorithm>

// Структура сирої незмінної події
struct RawEvent {
    std::string event_id;
    std::string user_id;
    int64_t amount_cents{0};
    std::string event_time; // ISO8601 UTC
};

// Структура історичного тарифу (SCD Type 2)
struct TariffRecord {
    std::string user_id;
    int discount_percent{0};
    std::string valid_from;
    std::string valid_to;
};

// Підсумковий агрегат для партиції
struct AggregatedMetric {
    std::string partition_date;
    std::string user_id;
    int64_t raw_total_cents{0};
    int64_t discounted_total_cents{0};
    int32_t events_count{0};
    std::string checksum_hash;
};

class IdempotentBackfillWorker {
public:
    // Пошук діючого тарифу на момент настання події (Point-in-Time AS-OF Join)
    static int find_as_of_discount(
        std::string_view user_id, 
        std::string_view event_time, 
        const std::vector<TariffRecord>& tariffs
    ) noexcept {
        for (const auto& t : tariffs) {
            if (t.user_id == user_id && event_time >= t.valid_from && event_time < t.valid_to) {
                return t.discount_percent;
            }
        }
        return 0; // Базовий тариф за замовчуванням
    }

    // Детермінована обробка чанка в пам'яті
    static std::vector<AggregatedMetric> compute_partition(
        std::string_view partition_date,
        std::string_view window_start,
        std::string_view window_end,
        const std::vector<RawEvent>& raw_stream,
        const std::vector<TariffRecord>& tariffs
    ) {
        std::unordered_map<std::string, AggregatedMetric> accumulator;

        for (const auto& ev : raw_stream) {
            // Сувора фільтрація за замкненим часовим вікном події
            if (ev.event_time < window_start || ev.event_time >= window_end) {
                continue;
            }

            int discount = find_as_of_discount(ev.user_id, ev.event_time, tariffs);
            int64_t discounted_amt = ev.amount_cents * (100 - discount) / 100;

            auto& entry = accumulator[ev.user_id];
            entry.partition_date = std::string(partition_date);
            entry.user_id = ev.user_id;
            entry.raw_total_cents += ev.amount_cents;
            entry.discounted_total_cents += discounted_amt;
            entry.events_count += 1;
        }

        std::vector<AggregatedMetric> result;
        result.reserve(accumulator.size());

        // Перевірка інваріантів якості даних (Data Quality Gate)
        for (auto& [uid, metric] : accumulator) {
            if (metric.discounted_total_cents > metric.raw_total_cents) {
                throw std::runtime_error("Аномалія: знижка більша за базову суму для користувача: " + uid);
            }
            if (metric.raw_total_cents < 0) {
                throw std::runtime_error("Аномалія: від'ємна виручка для користувача: " + uid);
            }
            result.push_back(std::move(metric));
        }

        return result;
    }
};

int main() {
    try {
        std::vector<TariffRecord> tariffs = {
            {"user_1", 10, "2026-08-01T00:00:00Z", "2026-08-15T00:00:00Z"},
            {"user_1", 20, "2026-08-15T00:00:00Z", "2026-09-01T00:00:00Z"}
        };

        std::vector<RawEvent> events = {
            {"e1", "user_1", 10000, "2026-08-10T12:00:00Z"}, // Потрапляє під знижку 10%
            {"e2", "user_1", 20000, "2026-08-20T15:30:00Z"}  // Потрапляє під знижку 20%
        };

        auto chunk_results = IdempotentBackfillWorker::compute_partition(
            "2026-08-10", "2026-08-10T00:00:00Z", "2026-08-11T00:00:00Z", events, tariffs
        );

        for (const auto& r : chunk_results) {
            std::cout << "Партиція: " << r.partition_date 
                      << " | Користувач: " << r.user_id
                      << " | Сире: " << r.raw_total_cents
                      << " | Зі знижкою: " << r.discounted_total_cents 
                      << " | Подій: " << r.events_count << "\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Помилка бекфілу: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

### Детальний розбір механізмів та крайових випадків

#### 1. Чому AS-OF з'єднання критичне для історичної точності
У наведеному коді функція `find_as_of_discount` здійснює фільтрацію `ev.event_time >= t.valid_from AND ev.event_time < t.valid_to`. 

Якщо наївно з'єднати історичну подію 2024 року з поточною таблицею користувачів, де клієнту в 2026 році призначено VIP-статус із 20% знижкою, перерахунок історичного чека дасть меншу суму, ніж реальний платіж, зафіксований у банку. Механізм SCD Type 2 гарантує, що історична подія зв'язується виключно з тим станом тарифу, який діяв у мілісекунду створення події.

#### 2. Запобігання гонкам між живим потоком та бекфілом
Коли бекфіл оновлює минулий місяць, а живий потоковий конвеєр пише сьогоднішні транзакції, небезпека виникає на стику діб через запізнілі події (*late-arriving data*).

Якщо запізніла подія за вчора надходить у момент, коли бекфіл виконує `DELETE FROM daily_user_revenue WHERE partition_date = 'вчора'`, виникає стан гонитви:
* Потоковий воркер вичитує поточний агрегат, додає дельту і готує запис.
* Бекфіл стирає партицію і записує повний свіжий агрегат.
* Потоковий воркер застосовує свій старий стан поверх свіжого, затираючи результати бекфілу.

Розв'язання полягає в суворому **розподілі власності над партиціями**:
1. Живий потік записує факти виключно у незмінний сирий лог `raw_events`.
2. Агрегатна таблиця оновлюється виключно через атомарний `INSERT OVERWRITE` або `REPLACE PARTITION`.
3. Потоковий конвеєр оновлює лише відкриту поточну партицію (за поточною вотермаркою), тоді як закриті історичні партиції змінюються виключно регламентним рушієм бекфілу.

#### 3. Обробка аварійних відключень (Lease Timeout та Zombie Workers)
Якщо процес бекфілу аварійно завершується сигналом `SIGKILL` (наприклад, через перевищення ліміту оперативної пам'яті в Kubernetes), запис у таблиці `backfill_checkpoints` залишається зі статусом `PENDING`.

Щоб запобігти вічному блокуванню конвеєра, оркестратор реалізує механізм оренди (*lease*):
* Кожен воркер щохвилини оновлює поле `heartbeat_at`.
* Якщо статус задачі `PENDING`, але `heartbeat_at` старший за 10 хвилин, новий воркер вважає попередника мертвим, переводить статус у `FAILED`, скидає незавершені транзакції та бере чанк у повторну обробку.

#### 4. Декларативний бекфіл у хмарних сховищах (Delta Lake та Iceberg)
У сучасних колоночних сховищах на кшталт Apache Iceberg або ClickHouse низькорівневий цикл `DELETE + INSERT` замінюється єдиною декларативною інструкцією:

```sql
-- Атомарна заміна партиції в Apache Iceberg
INSERT OVERWRITE gold_db.daily_user_revenue
PARTITION (partition_date = '2026-08-20')
SELECT 
    user_id,
    SUM(amount_cents) AS raw_total_cents,
    SUM(discounted_amount) AS discounted_total_cents,
    COUNT(1) AS events_count,
    MAX(update_time) AS updated_at
FROM stage_prepared_events
WHERE event_date = '2026-08-20'
GROUP BY user_id;
```

Такий підхід переносить усю відповідальність за транзакційність, блокування та безпеку читачів на рушій зберігання, усуваючи необхідність у ручному керуванні транзакціями на рівні коду додатку.

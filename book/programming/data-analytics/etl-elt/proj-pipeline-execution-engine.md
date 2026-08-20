# ⚙️ Двомодальний конвеєр даних: потоковий ETL та SQL-орієнтований ELT

Програмний конвеєр обробки подій повинен приймати потік сирих журнальних записів операцій (наприклад, кліків або фінансових транзакцій користувачів із полями ідентифікатора, мітки часу, чутливими персональними даними PII, сумою та геолокацією) і формувати аналітичну вітрину активності за категоріями товарів.

Цей проєкт демонструє обидві архітектурні парадигми на спільній модельній задачі:
1. **Режим ETL (Streaming In-Memory Transformation):** записи видобуваються порціями, негайно трансформуються в оперативній пам'яті (маскування PII, валідація, агрегація сум за категоріями) і лише у фінальному зведеному вигляді записуються в цільову базу.
2. **Режим ELT (Staging Ingestion + Push-down Transformation):** сирі записи без модифікації записуються в шар прийому (staging-таблицю), після чого запускається декларативна SQL-трансформація рушієм збереження даних.

## Архітектурний дизайн та внутрішній стан

У потоковому режимі **ETL** обчислювальний вузол бере на себе функцію фільтра й агрегатора. Він отримує посилання на незмінний буфер сирих записів через легкий зріз пам'яті (`std::span` у C++ або список у Python), відсікає некоректні транзакції (з від'ємною або нульовою сумою), криптографічно токенізує персональні дані та акумулює проміжні суми в локальній хеш-таблиці `unordered_map`. До цільового сховища передаються лише компактні агреговані структури, що мінімізує мережевий трафік і навантаження на диск сховища.

У режимі **ELT** конвеєр розділений на дві незалежні фази. Перша фаза — високопродуктивне пакетне завантаження (`bulk_insert_raw`), яке здійснює виключно операції додавання (*append-only*) у сирий шар Bronze без синтаксичного розбору й фільтрації. Друга фаза — відкладена аналітична трансформація (`execute_pushdown_transform`), яка делегує фільтрацію, розпакування JSON та групування безпосередньо внутрішньому оптимізатору сховища (використовуючи векторні інструкції та паралелізм ядер).

## Реалізація конвеєра двома мовами

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <chrono>
#include <span>
#include <sstream>
#include <iomanip>

// Структура сирого вхідного запису
struct RawRecord {
    std::string user_id;
    std::string email;          // Чутливі персональні дані (PII)
    std::string category;
    double amount;
    int64_t timestamp_ms;
};

// Структура очищеного агрегованого результату для вітрини
struct CategoryMetric {
    std::string category;
    double total_amount{0.0};
    uint64_t transaction_count{0};
};

// Імітатор криптографічного хешування для маскування PII (FNV-1a 64-bit)
std::string mask_pii(std::string_view pii) {
    uint64_t hash = 14695981039346656037ULL;
    for (char c : pii) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 1099511628211ULL;
    }
    std::stringstream ss;
    ss << "anon_" << std::hex << std::setw(16) << std::setfill('0') << hash;
    return ss.str();
}

// ── 1. РЕЖИМ ETL: Трансформація в пам'яті конвеєра перед завантаженням ────────
class EtlPipelineEngine {
public:
    // Видобування -> Трансформація в оперативній пам'яті -> Завантаження вітрини
    std::vector<CategoryMetric> process_batch_etl(std::span<const RawRecord> batch) {
        std::unordered_map<std::string, CategoryMetric> in_memory_aggregation;

        for (const auto& record : batch) {
            // Валідація некоректних даних
            if (record.amount <= 0.0 || record.category.empty()) {
                continue;
            }

            // Маскування PII в пам'яті воркера (сирі дані не виходять за межі контуру)
            std::string masked_user = mask_pii(record.email);

            // Агрегація метрик на льоту
            auto& metric = in_memory_aggregation[record.category];
            metric.category = record.category;
            metric.total_amount += record.amount;
            metric.transaction_count += 1;
        }

        // Формування компактного результату для завантаження в аналітичну базу
        std::vector<CategoryMetric> destination_mart;
        destination_mart.reserve(in_memory_aggregation.size());
        for (auto& [cat, metric] : in_memory_aggregation) {
            destination_mart.push_back(std::move(metric));
        }

        return destination_mart;
    }
};

// ── 2. РЕЖИМ ELT: Скидання сирих даних та Push-Down трансформація ────────────
class MockWarehouseStorage {
public:
    // Сире сховище (Bronze Staging Layer)
    std::vector<RawRecord> raw_staging_table;

    // Пряме неблокуюче завантаження сирих даних
    void bulk_insert_raw(std::span<const RawRecord> batch) {
        raw_staging_table.insert(raw_staging_table.end(), batch.begin(), batch.end());
    }

    // Декларативна SQL-трансформація всередині рушія сховища (Push-Down)
    // Еквівалент: SELECT category, SUM(amount), COUNT(*) FROM raw_staging WHERE amount > 0 GROUP BY category
    std::vector<CategoryMetric> execute_pushdown_transform() {
        std::unordered_map<std::string, CategoryMetric> storage_engine_group_by;

        for (const auto& row : raw_staging_table) {
            if (row.amount > 0.0 && !row.category.empty()) {
                auto& m = storage_engine_group_by[row.category];
                m.category = row.category;
                m.total_amount += row.amount;
                m.transaction_count += 1;
            }
        }

        std::vector<CategoryMetric> gold_mart;
        gold_mart.reserve(storage_engine_group_by.size());
        for (auto& [cat, m] : storage_engine_group_by) {
            gold_mart.push_back(std::move(m));
        }
        return gold_mart;
    }
};

int main() {
    // Вхідний батч подій
    std::vector<RawRecord> incoming_events = {
        {"usr_1", "alice@example.com", "electronics", 1200.50, 1724180000000},
        {"usr_2", "bob@example.com", "books", 45.00, 1724180001000},
        {"usr_3", "charlie@example.com", "electronics", 350.00, 1724180002000},
        {"usr_4", "invalid@example.com", "books", -10.00, 1724180003000}, // Битий запис
        {"usr_5", "david@example.com", "home", 89.90, 1724180004000}
    };

    std::cout << "=== 1. Виконання конвеєра в режимі ETL ===\n";
    EtlPipelineEngine etl_engine;
    auto etl_result = etl_engine.process_batch_etl(incoming_events);
    for (const auto& row : etl_result) {
        std::cout << "Категорія: " << row.category 
                  << " | Сума: " << row.total_amount 
                  << " | Кількість: " << row.transaction_count << "\n";
    }

    std::cout << "\n=== 2. Виконання конвеєра в режимі ELT ===\n";
    MockWarehouseStorage warehouse;
    // Крок 1: Швидке скидання сирих рядків у Bronze Staging
    warehouse.bulk_insert_raw(incoming_events);
    std::cout << "Завантажено сирих рядків у Staging: " << warehouse.raw_staging_table.size() << "\n";

    // Крок 2: Push-down SQL-агрегація в шар Gold
    auto elt_result = warehouse.execute_pushdown_transform();
    for (const auto& row : elt_result) {
        std::cout << "Категорія: " << row.category 
                  << " | Сума: " << row.total_amount 
                  << " | Кількість: " << row.transaction_count << "\n";
    }

    return 0;
}
```
```py
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
```
:::

## Покроковий розбір коду та робота з пам'яттю

1. **Ефективне використання пам'яті в C++:**
   У методі `process_batch_etl` вхідний масив передається через легкий зріз `std::span<const RawRecord>`. Це виключає зайве копіювання векторів між функціями та дозволяє обробляти фрагменти великих буферів без виділення динамічної пам'яті. Для формування вихідного списку заздалегідь викликається `destination_mart.reserve()`, що усуває повторний динамічний перерозподіл пам'яті на купі (*heap reallocations*) під час ітерації.
2. **Ізоляція сирого стану в ELT:**
   Клас `MockWarehouseStorage` імітує поведінку хмарного сховища або озера даних. Метод `bulk_insert_raw` є неблокуючим: він не здійснює перевірок валідності чи парсингу рядків. У реальних системах ця операція зводиться до прямого потокового запису блоку файлу на S3 через `multipart upload` або `COPY INTO` у стовпцеву таблицю.
3. **Механізм Push-down трансформації:**
   Метод `execute_pushdown_transform` відображає роботу внутрішнього оптимізатора сховища. У реальній реляційній базі (DuckDB, ClickHouse чи Snowflake) цей код компілюється в конвеєр векторних інструкцій SIMD, які обробляють стовпці блоками по 2048 значень у регістрах процесора. Це усуває накладні витрати на віртуальні виклики функцій та інтерпретацію типів даних.

## Виробничі пастки та крайові випадки

1. **Переповнення пам'яті при високій кардинальності ключів (ETL Out-Of-Memory):**
   У наведеному прикладі агрегація ведеться за категоріями (низька кардинальність, десятки ключів). Якщо замінити категорію на `user_id` або `session_id` (мільйони унікальних значень), розмір хеш-таблиці `in_memory_aggregation` перевищить ліміт RAM процесу. Програма впаде за сигналом операційної системи `OOM-killer`. Для запобігання цьому у великих ETL-пайплайнах впроваджують періодичне скидання проміжних хеш-таблиць на локальний NVMe-накопичувач з подальшим сортуванням-злиттям (*external merge sort*).
2. **Витік чутливих персональних даних у шар Bronze (ELT Security Trap):**
   Якщо конвеєр ELT сліпо зберігає сирі логи у відкритому сховищі, поле `email` опиниться на диску в незашифрованому вигляді. Це пряме порушення регламентів GDPR та HIPAA, оскільки доступ до сирого озера даних мають десятки інженерів та аналітиків. Вирішення полягає у гібридному підході **EtLT**: легка функція `mask_pii` викликається на стадії екстракції до запису в Staging, а важка агрегація виконується вже за схемою ELT.
3. **Неідемпотентні повторні запуски (Duplicate Ingestion Trap):**
   Якщо мережеве з'єднання обривається в момент завершення методу `bulk_insert_raw`, оркестратор повторить спробу завантаження того самого батчу. Без дедуплікації таблиця `raw_staging_table` отримає дублікати, і розрахунок `SUM(amount)` дасть подвійний виторг. Для забезпечення ідемпотентності завантаження здійснюється в унікальну партицію з атомарною заміною (`INSERT OVERWRITE PARTITION`) або з використанням сурогатного ключа транзакції `deduplication_hash`.
4. **Контроль зворотного тиску (Backpressure Management):**
   Якщо джерело подій генерує 100 000 записів за секунду, а цільове сховище здатне приймати лише 40 000, проміжний буфер воркера швидко переповниться. Конвеєр повинен підтримувати зворотний тиск: призупиняти опитування джерела (зменшувати `max_poll_records` у клієнті Kafka) або скидати надлишковий потік у персистентну чергу дисків.
5. **Обробка пізніх подій (Late Arriving Data):**
   У реальних розподілених системах події з мобільних пристроїв можуть надходити із запізненням у кілька годин або діб через офлайн-режим клієнта. В архітектурі ETL пізні події або відкидаються, або вимагають дорогого коригувального перерахунку зведеної вітрини в реальному часі. В архітектурі ELT пізня подія просто записується в поточну партицію шару Bronze, а щоденний або щогодинний SQL-модуль перераховує агрегати за відповідний історичний день без зупинки основного конвеєра.

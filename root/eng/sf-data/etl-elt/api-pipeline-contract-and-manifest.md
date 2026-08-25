# 📋 Специфікація маніфесту та інтерфейс стадій конвеєра даних

Виробничий конвеєр даних потребує формального контракту між сервісами-постачальниками подій, інфраструктурою транспортування та аналітичним сховищем. Без чітко зафіксованого контракту неминучий дрейф схем (*schema drift*): розробник бекенду додає або перейменовує колонку в операційній базі, що призводить до тихого збою нічного регламенту або появи спотворених нульових значень у фінансових звітах.

Ця специфікація визначає структуру декларативного маніфесту конвеєра, політику еволюції схем, протокол фіксації походження даних (*data lineage*), механізми ізоляції пошкоджених записів та програмний інтерфейс абстрактних стадій обробки.

## 1. Специфікація декларативного маніфесту (`pipeline_manifest.yaml`)

Маніфест конвеєра є єдиним джерелом конфігурації для планувальника та оркестратора. Він зберігається у системі контролю версій Git разом із кодом аналітичних моделей і визначає весь життєвий цикл руху даних від джерела до вітрин.

```yaml
version: "2.1"
pipeline_id: "pipe_orders_ingestion"
paradigm: "ELT"  # Варіанти: "ETL" | "ELT" | "EtLT"

source:
  type: "postgres_cdc"
  endpoint: "db-master.internal:5432"
  database: "shop_prod"
  table: "orders"
  watermark_column: "updated_at"
  batch_window_seconds: 60
  max_batch_records: 50000

staging_layer:  # Bronze / Raw шар
  enabled: true
  storage_protocol: "s3"
  bucket: "corporate-lakehouse-bronze"
  path_prefix: "raw/orders"
  file_format: "parquet"
  compression: "zstd"
  partitioning:
    - column: "ingestion_date"
      type: "DATE"
      expression: "to_date(ingestion_time)"
    - column: "region"
      type: "STRING"
  schema_evolution_policy: "ADD_NEW_COLUMNS"  # "STRICT_FAIL" | "ADD_NEW_COLUMNS" | "EVOLVE_TYPES"

transformation_layer:  # Silver / Gold шар
  engine: "duckdb_sql"  # "spark_sql" | "trino" | "snowflake" | "duckdb_sql"
  target_table: "gold.mart_daily_revenue"
  write_mode: "MERGE_UPSERT"  # "APPEND" | "OVERWRITE_PARTITION" | "MERGE_UPSERT"
  primary_key: ["order_id", "order_date"]
  sql_model_path: "models/gold/mart_daily_revenue.sql"

error_handling:
  policy: "DEAD_LETTER_QUEUE"  # "FAIL_FAST" | "DEAD_LETTER_QUEUE" | "DISCARD_AND_LOG"
  dlq_path: "s3://corporate-lakehouse-dlq/orders_corrupted/"
  retry_attempts: 3
  backoff_exponent_seconds: 5
```

### Детальний опис блоків маніфесту

1. **Блок метаданих конвеєра:** Поле `version` визначає версію схеми самого маніфесту для підтримки зворотної сумісності парсера. Поле `pipeline_id` служить унікальним глобальним ідентифікатором у каталозі метаданих та системі моніторингу. Поле `paradigm` задає фундаментальний режим виконання (`ETL`, `ELT` або `EtLT`), що визначає, чи повинен оркестратор викликати проміжний модуль обробки до запису у сховище.
2. **Блок джерела (`source`):** Описує протокол з'єднання з операційною системою. Поле `watermark_column` вказує на монотонно зростаючий стовпець (мітка часу `updated_at` або автоінкрементний ID), за яким конвеєр відстежує межу вже видобутих даних (*high watermark*). Параметр `batch_window_seconds` визначає частоту зрізу даних, а `max_batch_records` обмежує максимальний розмір вибірки для захисту від переповнення буферів пам'яті під час сплесків трафіку.
3. **Блок прийому сирих даних (`staging_layer`):** Визначає структуру збереження шару Bronze в об'єктному сховищі. Вказуються протокол доступу (`s3`, `gcs`, `azure_blob`), цільовий бакет і шлях. Поле `file_format` задає формат файлів (стовпцевий `parquet` або рядковий `jsonl`), а `compression` вказує алгоритм компресії блоків (`zstd`, `snappy`, `gzip`). Масив `partitioning` визначає ієрархію підкаталогів на диску для оптимізації майбутнього відсікання нерелевантних файлів під час читання (*partition pruning*).
4. **Блок трансформації (`transformation_layer`):** Вказує аналітичний рушій для виконання трансформацій (Spark, DuckDB, Trino, Snowflake), шлях до файлу декларативної моделі SQL та режим запису у фінальну вітрину (`APPEND` для незмінних логів, `OVERWRITE_PARTITION` для повного перезапису дня або `MERGE_UPSERT` для оновлення існуючих записів за первинним ключем).
5. **Блок стійкості та помилок (`error_handling`):** Задає політику реакції на пошкоджені записи: негайна зупинка (`FAIL_FAST`), маршрутизація битих рядків в ізольоване сховище пошкоджених даних (`DEAD_LETTER_QUEUE`) або пропуск із записом у системний журнал. Параметри `retry_attempts` та `backoff_exponent_seconds` регулюють механізм повторних спроб при тимчасових мережевих збоях.

## 2. Режими еволюції схеми даних

Контракт маніфесту підтримує три стратегії обробки структурних змін у джерелі:

### `STRICT_FAIL` (Суворий контроль)
Будь-яка невідповідність між схемою вхідного батчу та зареєстрованою схемою таблиці (поява нового поля, відсутність обов'язкового стовпця чи зміна типу даних) негайно анулює транзакцію і генерує аварійне сповіщення в системі чергування інженерів. Застосовується у фінансових та регуляторних контурах, де неконтрольована поява нових атрибутів може свідчити про вразливість або порушення безпеки.

### `ADD_NEW_COLUMNS` (Автоматичне розширення)
Якщо у вхідному JSON чи CDC-потоці з'являються нові стовпці, яких немає у цільовій таблиці, конвеєр автоматично виконує `ALTER TABLE ADD COLUMN` зі значеннями `NULL` для всіх раніше збережених рядків. Зміна існуючих типів даних або видалення колонок суворо забороняються. Це стандартний режим для озер даних та аналітичних сховищ за моделлю ELT, що усуває потребу в ручному втручанні інженера при додаванні некритичних полів на бекенді.

### `EVOLVE_TYPES` (Безпечне розширення типів)
Дозволяє автоматичне розширення діапазонів числових типів (наприклад, перетворення `INT32` у `INT64` або `FLOAT` у `DOUBLE`), якщо таке перетворення не призводить до втрати точності чи переповнення. Спроби звуження типів (`BIGINT` у `INT` або `VARCHAR(255)` у `VARCHAR(50)`) блокуються як несумісні зміни, що можуть спотворити дані.

## 3. Структурні типи та сигнатури інтерфейсів (API Contract)

Усі програмні компоненти конвеєра взаємодіють через типізовані інтерфейси екстракції, завантаження та трансформації.

### Таблиця кодів помилок та реакцій системи

| Код помилки | Константа | Опис причини | Дія конвеєра |
| :--- | :--- | :--- | :--- |
| `0` | `SUCCESS` | Фаза завершена без зауважень | Перехід до наступної стадії |
| `101` | `SOURCE_UNAVAILABLE` | Збій мережі або недоступність джерела | Експоненційний повтор (Retry з backoff) |
| `102` | `SCHEMA_VIOLATION` | Структура батчу порушує контракт | Маршрутизація в DLQ або аварійна зупинка |
| `103` | `OOM_SPILL_FAILURE` | Нестача оперативної пам'яті воркера | Зменшення розміру батчу / збільшення партицій |
| `104` | `STORAGE_WRITE_ABORT` | Відмова запису в об'єктне сховище S3 | Анулювання транзакції партиції |
| `105` | `WATERMARK_DRIFT` | Порушення монотонності міток часу | Синхронізація годинників та аудит логів |

### Інтерфейс стадій конвеєра (C++20 та Python)

:::tabs
```cpp
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <span>
#include <expected>
#include <chrono>

// Метадані виконання фази конвеєра (Lineage & Audit)
struct ExecutionAudit {
    std::string pipeline_id;
    std::string stage_name;
    uint64_t records_read{0};
    uint64_t records_written{0};
    uint64_t bytes_transferred{0};
    std::chrono::milliseconds duration_ms{0};
    std::string target_commit_id;
};

// Абстрактний інтерфейс стадії конвеєра
class IPipelineStage {
public:
    virtual ~IPipelineStage() = default;
    virtual std::string_view stage_name() const noexcept = 0;
};

// Стадія видобування (Extract)
class IExtractor : public IPipelineStage {
public:
    // Повертає список сирих рядків або код помилки
    virtual std::expected<std::vector<std::string>, int> extract_batch(
        std::string_view watermark_start, 
        std::string_view watermark_end, 
        size_t limit) = 0;
};

// Стадія сирого або цільового завантаження (Load)
class ILoader : public IPipelineStage {
public:
    // Завантажує сирі дані у шар Bronze або цільову таблицю
    virtual std::expected<ExecutionAudit, int> load_raw_staging(
        std::string_view destination_table,
        std::span<const std::string> raw_json_records) = 0;
};

// Стадія декларативної або імперативної трансформації (Transform)
class ITransformer : public IPipelineStage {
public:
    // Виконує SQL-трансформацію всередині рушія сховища
    virtual std::expected<ExecutionAudit, int> execute_transformation(
        std::string_view sql_query,
        std::string_view target_partition) = 0;
};
```
```py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Tuple

@dataclass
class ExecutionAudit:
    pipeline_id: str
    stage_name: str
    records_read: int
    records_written: int
    bytes_transferred: int
    duration_ms: int
    target_commit_id: str

class IPipelineStage(ABC):
    @abstractmethod
    def stage_name(self) -> str:
        """Повертає унікальну назву стадії конвеєра."""
        pass

class IExtractor(IPipelineStage):
    @abstractmethod
    def extract_batch(self, watermark_start: str, watermark_end: str, limit: int) -> Tuple[List[str], Optional[int]]:
        """Видобуває порцію сирих записів за діапазоном водяного знака."""
        pass

class ILoader(IPipelineStage):
    @abstractmethod
    def load_raw_staging(self, destination_table: str, raw_records: List[str]) -> Tuple[ExecutionAudit, Optional[int]]:
        """Здійснює неблокуюче завантаження у шар Bronze."""
        pass

class ITransformer(IPipelineStage):
    @abstractmethod
    def execute_transformation(self, sql_query: str, target_partition: str) -> Tuple[ExecutionAudit, Optional[int]]:
        """Виконує SQL-трансформацію всередині аналітичного рушія."""
        pass
```
:::

## 4. Протокол обробки пошкоджених записів (Dead Letter Queue, DLQ)

Коли у вхідному потоці з'являється синтаксично некоректний JSON або поле з несумісним форматом (наприклад, рядок `"N/A"` у числовому полі суми платежу), конвеєр із політикою `DEAD_LETTER_QUEUE` не зупиняє обробку валідних 99.9% записів, а ізолює биті рядки у спеціальний каталог DLQ.

Структура повідомлення DLQ містить первинний сирий рядок, точний стек помилки та мітку часу:

```json
{
  "dlq_record_id": "dlq_98412_err",
  "pipeline_id": "pipe_orders_ingestion",
  "occurred_at": "2026-08-20T21:00:15Z",
  "error_code": 102,
  "error_message": "JSON parsing failure: unexpected token at line 1 col 42",
  "raw_payload_base64": "eyJvcmRlcl9pZCI6MTIzLCJhbW91bnQiOiJOL0EifQ=="
}
```

Ці записи зберігаються для подальшого ручного аналізу або автоматичного повторного перерахунку після виправлення валідатора.

## 5. Маніфест аудиту та походження даних (Data Lineage Entry)

Для забезпечення повної відтворюваності розрахунків кожен запуск конвеєра реєструє структурований запис аудиту в центральному каталозі метаданих. Цей запис пов'язує конкретні партиції джерела з вихідними вітринами, фіксує хеш версії SQL-коду, час обробки та обсяги переданих байтів:

```json
{
  "audit_version": "1.0",
  "pipeline_run_id": "run_2026_08_20_2100_001",
  "source_urn": "urn:datasource:postgres:shop_prod:public:orders",
  "staging_urn": "urn:lakehouse:s3:bronze:orders:date=2026-08-20",
  "target_urn": "urn:lakehouse:gold:mart_daily_revenue:date=2026-08-20",
  "metrics": {
    "records_extracted": 45120,
    "records_corrupted_dlq": 3,
    "records_written_gold": 12,
    "bytes_processed": 14285090,
    "transformation_time_ms": 1420
  },
  "execution_context": {
    "engine_name": "duckdb_embedded",
    "engine_version": "1.1.0",
    "worker_host": "node-worker-analytics-04"
  },
  "code_hash": "sha256:7f83b1657ff1fc53b92dc18148a1d65dfc2d4b1fa3d677284addd200126d9069"
}
```

Завдяки незмінності цього маніфесту дата-інженер у будь-який момент може простежити повний шлях кожного числа в аналітичній системі: з яких саме сирих транзакцій, у якому файлі на S3, за яким комітом SQL-моделі та на якому вузлі кластера було згенеровано підсумковий показник прибутку.

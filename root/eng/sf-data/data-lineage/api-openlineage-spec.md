# 📋 Специфікація OpenLineage: модель подій, запусків та фасетів

Специфікація OpenLineage — це відкритий індустріальний стандарт консорціуму Linux Foundation AI & Data для уніфікованого збору, серіалізації та передачі метаданих про походження даних (Data Lineage) у розподілених гетерогенних середовищах обробки інформації. Її головна інженерна мета полягає у створенні єдиного протоколу взаємодії між продюсерами метаданих (рушіями обчислень, оркестраторами, сервісами трансформації) та споживачами (каталогами метаданих, платформами спостережуваності та аудиту).

Завдяки відокремленню збору інформації від її збереження OpenLineage дозволяє об'єднати в єдиний граф процеси, написані на Apache Spark, dbt, Apache Flink, Trino, Airflow та Dagster, без необхідності розробляти спеціалізовані двосторонні мости між кожною парою інструментів.

---

### Архітектурна модель: Run, Job, Dataset

Модель даних OpenLineage спирається на три фундаментальні сутності та механізм розширень, що називаються фасетами (англ. *Facets*):

```
       ┌─────────────────────────────────────────────────────────┐
       │                        RunEvent                         │
       │  eventType: START | RUNNING | COMPLETE | ABORT | FAIL   │
       │  eventTime: ISO-8601 UTC                                │
       └───────────┬───────────────────┬────────────────────┬────┘
                   │                   │                    │
                   ▼                   ▼                    ▼
             ┌───────────┐       ┌───────────┐       ┌─────────────┐
             │    Job    │       │    Run    │       │   Dataset   │
             │ (Процес)  │       │ (Запуск)  │       │ (Вхід/Вихід)│
             └─────┬─────┘       └─────┬─────┘       └──────┬──────┘
                   │                   │                    │
                   ▼                   ▼                    ▼
             ┌───────────┐       ┌───────────┐       ┌─────────────┐
             │ JobFacets │       │ RunFacets │       │DatasetFacets│
             └───────────┘       └───────────┘       └─────────────┘
```

1. **Job (Завдання / Процес):** логічна одиниця коду або конвеєра, яка виконує перетворення даних і призначена для багаторазового запуску в часі. Завдання ідентифікується однозначною парою координат `(namespace, name)`. Простір імен `namespace` визначає контекст розгортання або оркестратор (наприклад, `airflow://prod-cluster` чи `dbt://finance-analytics`), а `name` — ім'я самої моделі чи завдання (`stg_payments_cleanup`).
2. **Run (Запуск / Екземпляр виконання):** окремий фізичний запуск завдання `Job` у певний момент часу з конкретними параметрами. Кожен запуск має унікальний глобальний ідентифікатор `runId` у форматі UUID v4, фіксує власний часовий інтервал виконання, стан життєвого циклу та посилання на батьківський процес.
3. **Dataset (Набір даних):** фізичний стан даних у спокої (англ. *data at rest*), який зчитується завданням як вхід (Input Dataset) або створюється чи модифікується як вихід (Output Dataset). Набором даних може бути реляційна таблиця у PostgreSQL, вітрина у Snowflake, каталог Parquet/Iceberg в об'єктному сховищі S3 або топік Kafka. Набір даних також ідентифікується парою `(namespace, name)`, де `namespace` вказує на фізичний екземпляр сховища (наприклад, `postgres://db-primary.internal:5432` або `s3://company-lakehouse`), а `name` — на конкретний об'єкт (`public.orders` або `bucket/bronze/events`).
4. **Facet (Фасет):** атомарний, типізований та версіонований JSON-об'єкт, що прикріплюється до `Job`, `Run` або `Dataset`. Фасети забезпечують розширюваність специфікації: вони дозволяють передавати довільні контекстні метадані (схеми стовпців, метрики якості даних, Git-коміти, параметри середовища виконання) без зміни базового протоколу. Кожен фасет має обов'язкове поле `_schemaURL`, що посилається на JSON Schema відповідної версії.

---

### Життєвий цикл подій (Event Lifecycle) та протокол станів

Під час виконання будь-якого процесу обробки даних клієнтська бібліотека OpenLineage генерує серію повідомлень `RunEvent`, які надсилаються до бекенд-колектора метаданих. Поле `eventType` відображає зміну стану виконання:

* `START`: генерується у момент старту обчислювального процесу. Фіксує початкові вхідні набори даних, час старту та планові часові вікна (Nominal Time). Якщо точний вихідний набір даних ще невідомий (наприклад, ім'я вихідного файлу формується динамічно), список `outputs` може бути порожнім.
* `RUNNING`: періодичне або проміжне повідомлення для тривалих завдань (наприклад, стрімінгових конвеєрів Flink або Spark Streaming). Дозволяє оновлювати стан метрик, фіксувати проміжні чекпоїнти та динамічно виявлені партиції без завершення самого завдання.
* `COMPLETE`: фінальне повідомлення успішного завершення. Обов'язково фіксує остаточний список модифікованих наборів даних (`outputs`), актуальну схему стовпців, кількість оброблених рядків (`rowCount`), розмір у байтах і детальний граф стовпчикового лініджу (`columnLineage`).
* `FAIL`: фінальне повідомлення про аварійну зупинку завдання через помилку. Містить фасет `errorMessage`, у якому зберігається текст винятку, мова програмування та повне трасування стека (Stack Trace) для автоматизації діагностики інцидентів.
* `ABORT`: фіксує примусове скасування завдання зовнішнім сигналом оператора або тайм-аутом оркестратора до отримання логічного результату.
* `OTHER`: службовий тип події для передачі додаткових метаданих без зміни поточного статусу екземпляра запуску.

---

### Каталог стандартних фасетів (Standard Facets Reference)

Специфікація OpenLineage визначає набір базових фасетів, розділених за цільовими сутностями.

#### 1. Фасети запусків (Run Facets)

* **`nominalTime`:** використовується оркестраторами (Airflow, Dagster) для прив'язки запуску до логічного вікна обробки даних (інтервалу розкладу):
  * `nominalStartTime` (ISO-8601): номінальний початок часового проміжку вибірки даних.
  * `nominalEndTime` (ISO-8601): номінальний кінець часового проміжку.
* **`parent`:** фіксує ієрархічні зв'язки у конвеєрах (наприклад, коли загальний DAG Airflow породжує окреме Spark-завдання):
  * `run.runId`: ідентифікатор батьківського запуску.
  * `job.namespace` та `job.name`: ім'я батьківського конвеєра.
* **`errorMessage`:** діагностична інформація збою:
  * `message`: короткий опис помилки або винятку.
  * `programmingLanguage`: мова, у якій сталася помилка (Python, Java, Scala, SQL).
  * `stackTrace`: повний текст трасування стека викликів.
* **`environmentProperties`:** конфігурація кластера чи контейнера (версія ядра, ліміти пам'яті, змінні оточення).

#### 2. Фасети завдань (Job Facets)

* **`sourceCodeLocation`:** зв'язок обчислювальної логіки з репозиторієм коду:
  * `type`: система контролю версій (наприклад, `git`).
  * `url`: повна адреса репозиторію (GitHub, GitLab).
  * `repoUrl`, `path`, `version`: шлях до файлу програми та хеш Git-коміту.
* **`sqlJob`:** повний первинний текст SQL-запиту, що виконувався у базі даних чи сховищі.
* **`ownership`:** команда або особа, відповідальна за працездатність моделі (`owners: [{ name, type }]`).

#### 3. Фасети наборів даних (Dataset Facets)

* **`schema`:** детальна типізована структура стовпців:
  * `fields`: масив об'єктів `{ name: string, type: string, description: string }`.
* **`columnLineage`:** найважливіший фасет мікрорівня, який відображає точне походження кожного вихідного стовпця:
  * `fields`: словник, де ключ — ім'я вихідного стовпця, а значення містить список `inputFields` (масив пар `{ namespace, name, field }`) та тип трансформації `transformationType` (`IDENTITY`, `AGGREGATION`, `TRANSFORMATION`, `INDIRECT`).
* **`dataSource`:** опис фізичного сховища:
  * `name`: унікальне ім'я джерела даних у каталозі інфраструктури.
  * `uri`: протокольна адреса доступу до екземпляра сховища.
* **`dataQualityMetrics`:** метрики якості, отримані інструментами автоматичної валідації (Great Expectations, Soda):
  * `rowCount`: загальна кількість прочитаних або записаних рядків.
  * `bytes`: фізичний обсяг у байтах.
  * `columnMetrics`: словник статистичних параметрів стовпців (кількість `null`, унікальність, мінімальні та максимальні значення).
* **`outputStatistics`:** статистика операції запису (кількість вставлених, оновлених чи видалених рядків).

---

### Детальна структура проводового JSON-повідомлення

Нижче наведено повне повідомлення `RunEvent` для події завершення обробки фінансової вітрини у Snowflake:

```json
{
  "eventType": "COMPLETE",
  "eventTime": "2026-08-20T18:30:00.120Z",
  "run": {
    "runId": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "facets": {
      "nominalTime": {
        "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
        "_schemaURL": "https://openlineage.io/spec/facets/1-0-1/NominalTimeRunFacet.json",
        "nominalStartTime": "2026-08-20T18:00:00.000Z",
        "nominalEndTime": "2026-08-20T18:30:00.000Z"
      },
      "parent": {
        "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/integration/airflow",
        "_schemaURL": "https://openlineage.io/spec/facets/1-0-1/ParentRunFacet.json",
        "run": {
          "runId": "f7813a10-1a22-4a30-8a40-00aa11bb22cc"
        },
        "job": {
          "namespace": "airflow://prod-scheduler",
          "name": "daily_financial_rollup"
        }
      }
    }
  },
  "job": {
    "namespace": "dwh://snowflake-prod",
    "name": "mart.fct_daily_revenue",
    "facets": {
      "sqlJob": {
        "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/integration/dbt",
        "_schemaURL": "https://openlineage.io/spec/facets/1-0-0/SQLJobFacet.json",
        "query": "SELECT o.order_id, SUM(o.amount / fx.usd_rate) AS usd_revenue FROM raw.orders o JOIN fx ON o.currency = fx.code WHERE o.status = 'PAID' GROUP BY o.order_id"
      }
    }
  },
  "inputs": [
    {
      "namespace": "postgres://prod-db:5432",
      "name": "raw.orders",
      "facets": {
        "schema": {
          "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
          "_schemaURL": "https://openlineage.io/spec/facets/1-1-1/SchemaDatasetFacet.json",
          "fields": [
            { "name": "order_id", "type": "INT64" },
            { "name": "amount", "type": "NUMERIC(18,2)" },
            { "name": "status", "type": "VARCHAR(32)" },
            { "name": "currency", "type": "VARCHAR(3)" }
          ]
        }
      }
    },
    {
      "namespace": "postgres://prod-db:5432",
      "name": "ref.fx_rates",
      "facets": {
        "schema": {
          "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
          "_schemaURL": "https://openlineage.io/spec/facets/1-1-1/SchemaDatasetFacet.json",
          "fields": [
            { "name": "code", "type": "VARCHAR(3)" },
            { "name": "usd_rate", "type": "DOUBLE" }
          ]
        }
      }
    }
  ],
  "outputs": [
    {
      "namespace": "dwh://snowflake-prod",
      "name": "mart.fct_daily_revenue",
      "facets": {
        "schema": {
          "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
          "_schemaURL": "https://openlineage.io/spec/facets/1-1-1/SchemaDatasetFacet.json",
          "fields": [
            { "name": "order_id", "type": "INT64" },
            { "name": "usd_revenue", "type": "NUMERIC(18,2)" }
          ]
        },
        "columnLineage": {
          "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
          "_schemaURL": "https://openlineage.io/spec/facets/1-0-1/ColumnLineageDatasetFacet.json",
          "fields": {
            "order_id": {
              "inputFields": [
                { "namespace": "postgres://prod-db:5432", "name": "raw.orders", "field": "order_id" }
              ],
              "transformationDescription": "direct identity copy",
              "transformationType": "IDENTITY"
            },
            "usd_revenue": {
              "inputFields": [
                { "namespace": "postgres://prod-db:5432", "name": "raw.orders", "field": "amount" },
                { "namespace": "postgres://prod-db:5432", "name": "ref.fx_rates", "field": "usd_rate" }
              ],
              "transformationDescription": "SUM(amount / usd_rate)",
              "transformationType": "AGGREGATION"
            }
          }
        },
        "outputStatistics": {
          "_producer": "https://github.com/OpenLineage/OpenLineage/tree/1.18.0/client",
          "_schemaURL": "https://openlineage.io/spec/facets/1-0-1/OutputStatisticsOutputDatasetFacet.json",
          "rowCount": 142050,
          "size": 8421000
        }
      }
    }
  ]
}
```

---

### Транспортні протоколи та гарантії доставки

Специфікація стандартизує два способи транспортування телеметрії метаданих:

#### 1. Синхронний HTTP REST Transport

* **Ендпоінт:** `POST /api/v1/lineage`
* **Заголовки запиту:**
  * `Content-Type: application/json`
  * `Authorization: Bearer <api-token>`
  * `User-Agent: openlineage-java/1.18.0`
* **Коди відповідей та семантика:**
  * `200 OK` або `201 Created`: повідомлення валідовано за схемою та успішно прийнято бекендом до черги обробки.
  * `400 Bad Request`: помилка валідації JSON Schema, відсутність обов'язкових полів `eventType`, `eventTime`, `job` чи `run`. Клієнт не повинен повторювати такий самий запит без виправлення структури.
  * `401 Unauthorized` / `403 Forbidden`: помилка автентифікації клієнта або відсутність прав на запис у вказаний `namespace`.
  * `429 Too Many Requests`: перевищення лімітів навантаження бекенда. Клієнт зобов'язаний застосувати експоненційну паузу (англ. *exponential backoff*).
  * `503 Service Unavailable`: тимчасова недоступність сховища метаданих. Клієнт зберігає подію у локальному буфері пам'яті та повторює спробу відправки.

#### 2. Асинхронний брокерський Kafka Transport

Для високонавантажених обчислювальних кластерів із тисячами одночасних завдань пряме HTTP-підключення може перевантажити API бекенда. У цьому випадку клієнти записують події безпосередньо в Apache Kafka:

* **Цільовий топік:** `openlineage.events` (за замовчуванням).
* **Ключ повідомлення (Message Key):** рядок вигляду `Job.namespace + ":" + Job.name`. Використання імені завдання як ключа гарантує, що всі події одного конвеєра (`START`, `RUNNING`, `COMPLETE`) потрапляють до однієї партиції Kafka, зберігаючи суворий хронологічний порядок обробки.
* **Тіло повідомлення (Value):** серіалізований UTF-8 рядок валідного JSON-об'єкта `RunEvent`.
* **Семантика доставки:** `at-least-once` (щонайменше один раз). Бекенд-колектор зобов'язаний підтримувати ідемпотентну обробку подій за комбінацією `(runId, eventType, eventTime)`.

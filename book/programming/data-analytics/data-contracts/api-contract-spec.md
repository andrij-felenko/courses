# 📋 Специфікація Data-контракту (Open Data Contract Standard)

Специфікація data-контракту — це людиночитаний і машинозчитуваний маніфест у форматі YAML або JSON, який формалізує технічну та організаційну угоду між сервісом-продюсером даних і платформами-споживачами. Маніфест встановлює непорушні межі публічного інтерфейсу даних (англ. *data product interface*), фіксуючи синтаксис схем, семантику бізнес-полів, інваріанти якості даних та юридично-регламентні зобов'язання команд.

Стандарт спирається на відкриту специфікацію Open Data Contract Standard (ODCS). Маніфест не обмежується простим переліком типів колонок (як класичний DDL у реляційних СУБД або файл Protobuf), а охоплює п'ять обов'язкових структурних розділів, що описують повний життєвий цикл інформаційного потоку.

## Анатомія структури маніфесту контракту

Маніфест контракту є декларативним документом із суворою ієрархічною структурою. Кожен блок відповідає за ізольовану площину взаємодії між продюсером і споживачем:

1. **Ідентифікація та метадані (`info`):** версія стандарту, унікальний уніфікований ідентифікатор ресурсу (URN), поточний стан життєвого циклу контракту (`draft`, `active`, `deprecated`, `retired`) та прямі контакти команди-власника.
2. **Фізичні сервери та канали транспорту (`servers`):** точки підключення до брокерів повідомлень (Apache Kafka topics), аналітичних таблиць (Snowflake, BigQuery, ClickHouse) або об'єктних сховищ (Amazon S3, Apache Iceberg, Delta Lake).
3. **Моделі та фізичні схеми даних (`models`):** повний опис таблиць або потоків подій, типів даних кожного поля, обмежень на порожні значення (`nullability`), форматів кодування та валідаційних регулярних виразів.
4. **Семантика та бізнес-правила (`semantics`):** опис реального життєвого змісту показників, одиниць виміру (центи замість дробових доларів, копійки замість гривень, мілісекунди UTC) та логічних інваріантів між різними полями одного запису.
5. **Інваріанти якості та угоди про рівень обслуговування (`quality` / SLO):** вимірювані критерії допустимого лагу надходження подій (freshness), унікальності первинних ключів, повноти заповнення та допустимого відсотка браку.
6. **Регламент, безпека та управління даними (`governance`):** класифікація конфіденційності, маркування персональних даних (PII згідно з GDPR / CCPA), правила маскування, терміни зберігання (retention) та гарантований період сповіщення перед виведенням схеми з експлуатації (deprecation period).

## Повний зразок маніфесту для потоку замовлень

Нижче наведено робочий маніфест data-контракту версії 2.3.0 для вихідного потоку подій оформлення замовлень інтернет-магазину `orders_stream`:

```yaml
dataContractSpecification: 2.1.0
id: urn:datacontract:checkout:orders-stream
info:
  title: Orders Stream Output Contract
  version: 2.3.0
  status: active
  description: Офіційний вихідний потік підтверджених замовлень для аналітичного сховища DWH та ML-моделей.
  owner:
    team: checkout-core
    lead: "andrij.f@example.com"
    channel: "#team-checkout-alerts"
    escalationContact: "oncall-checkout@internal.net"

servers:
  production-kafka:
    type: kafka
    topic: events.checkout.orders.v2
    format: json
    schemaRegistry: "https://schema-registry.internal.net"
    cluster: "kafka-prod-eu-central"
  analytics-lakehouse:
    type: s3
    location: "s3://company-lakehouse-gold/checkout/orders_v2/"
    format: iceberg

models:
  order_event:
    description: Подія зміни стану замовлення клієнта в операційному контурі.
    type: table
    fields:
      event_id:
        type: string
        format: uuid
        required: true
        unique: true
        description: Унікальний ідентифікатор події (ідемпотентний ключ дедуплікації).
      order_id:
        type: string
        format: uuid
        required: true
        description: Ідентифікатор сутності замовлення в сервісі оформлення покупок.
      user_id:
        type: string
        format: uuid
        required: true
        description: Ідентифікатор покупця для зв'язку з профілем клієнта.
      order_state:
        type: string
        required: true
        enum: ["PENDING", "PAID", "PROCESSING", "SHIPPED", "CANCELLED", "REFUNDED"]
        description: Поточний стан скінченного автомата життєвого циклу замовлення.
      currency:
        type: string
        minLength: 3
        maxLength: 3
        pattern: "^[A-Z]{3}$"
        required: true
        description: Трилітерний код валюти за стандартом ISO-4217 (USD, EUR, UAH).
      total_amount_cents:
        type: integer
        minimum: 0
        maximum: 1000000000
        required: true
        description: Загальна сума замовлення в цілих одиницях найменшого номіналу (центи/копійки).
      tax_amount_cents:
        type: integer
        minimum: 0
        required: true
        description: Сума нарахованого податку в центах/копійках.
      items_count:
        type: integer
        minimum: 1
        maximum: 500
        required: true
        description: Кількість унікальних товарних позицій у замовленні.
      created_at:
        type: timestamp
        format: date-time
        required: true
        description: Часова мітка генерації події у форматі ISO-8601 UTC.

semantics:
  businessRules:
    - name: tax_less_than_total
      rule: "tax_amount_cents <= total_amount_cents"
      description: Сума податку не може перевищувати повну вартість чека.
    - name: valid_order_progression
      rule: "items_count > 0"
      description: Підтверджене замовлення зобов'язане містити хоча б один товар.

quality:
  type: custom
  specification:
    freshness:
      maxLagSeconds: 300
      timestampField: created_at
      description: Допустиме запізнення доставки події у сховище не більше 5 хвилин.
    completeness:
      minSuccessPercentage: 99.99
      description: Не більше 0.01% записів у батчі можуть містити відхилення від схеми.
    uniqueness:
      primaryKey: [event_id]
      maxDuplicateRate: 0.0
      description: Повна відсутність дублікатів ідентифікаторів подій.

governance:
  classification: confidential
  containsPii: true
  piiFields: [user_id]
  retentionDays: 2555  # 7 років згідно з фінансовим аудитом
  deprecationPolicy:
    noticePeriodDays: 90
    migrationGuideUrl: "https://wiki.internal.net/contracts/orders/migration-v3"
```

## Довідник структурних елементів та типів даних

У маніфесті контракту використовуються строгі типи та валідаційні директиви, що транслюються у схеми валідації різних мов (JSON Schema, Avro, Protobuf, SQL DDL):

| Секція маніфесту | Поле конфігурації | Тип значення | Опис призначення та граничні умови |
| :--- | :--- | :--- | :--- |
| `info` | `version` | String (SemVer) | Версія контракту `MAJOR.MINOR.PATCH`. Зміна `MAJOR` вимагає 90-денного міграційного вікна. |
| `info` | `status` | Enum | Стан контракту: `draft` (розробка), `active` (виробництво), `deprecated` (застарілий), `retired` (відключений). |
| `info.owner` | `team` | String | Назва продуктової команди, що несе повну відповідальність за емісію даних. |
| `servers` | `format` | Enum | Формат серіалізації: `json`, `avro`, `protobuf`, `parquet`, `iceberg`, `delta`. |
| `models.fields` | `type` | String | Логічний тип: `string`, `integer`, `decimal`, `timestamp`, `boolean`, `array`, `object`. |
| `models.fields` | `required` | Boolean | Заборона порожніх значень. Якщо `true`, передача `null` або пропуск ключа викликає збій валідації. |
| `models.fields` | `pattern` | String (Regex) | Регулярний вираз для перевірки відповідності рядкових форматів (наприклад, коди валют, IBAN). |
| `models.fields` | `minimum` / `maximum` | Numeric | Допустимі числові межі для виявлення грубих відхилень та переповнень. |
| `semantics` | `businessRules` | Array[Rule] | Декларативні логічні вирази над полями одного запису. |
| `quality.freshness` | `maxLagSeconds` | Integer | Максимально дозволена різниця між часом події та моментом її фіксації в сховищі. |
| `governance` | `containsPii` | Boolean | Індикатор присутності персональних даних. Вмикає автоматичне шифрування або знеособлення в DWH. |

## Структура конверта помилки валідації в рантаймі

Коли вхідне повідомлення не відповідає затвердженому контракту, шлюз прийому даних (Ingestion Gateway) формує стандартний діагностичний конверт помилки та надсилає його в чергу карантину (DLQ). Конверт містить вичерпні дані для автоматичної категоризації аварії та сповіщення розробників продюсера:

```json
{
  "dlq_id": "8f3b2e1a-4c5d-6e7f-8a9b-0c1d2e3f4a5b",
  "failed_at": "2026-08-20T12:05:32.148Z",
  "contract_id": "urn:datacontract:checkout:orders-stream",
  "contract_version": "2.3.0",
  "violation_type": "BUSINESS_RULE_VIOLATION",
  "violation_details": {
    "rule_name": "tax_less_than_total",
    "failing_expression": "tax_amount_cents <= total_amount_cents",
    "evaluated_values": {
      "tax_amount_cents": 18000,
      "total_amount_cents": 15000
    },
    "field_path": "/tax_amount_cents"
  },
  "producer_metadata": {
    "source_host": "checkout-pod-7b9c4-8xk2q",
    "producer_version": "v1.42.0",
    "partition": 3,
    "offset": 9482015
  },
  "raw_payload": "{\"event_id\":\"a1b2c3d4-0000-0000-0000-000000000002\",\"order_id\":\"b2c3d4e5-0000-0000-0000-000000000004\",\"user_id\":\"c3d4e5f6-0000-0000-0000-000000000005\",\"order_state\":\"PAID\",\"currency\":\"USD\",\"total_amount_cents\":15000,\"tax_amount_cents\":18000,\"items_count\":2,\"created_at\":\"2026-08-20T12:05:30Z\"}"
}
```

Конверт карантину дозволяє бекенд-інженерам відтворити проблему в локальному середовищі за лічені хвилини: він містить точний зліпок сирих байтів, версію контракту, яка визнала запис бракованим, та точну причину відхилення.

## Команди консольного інтерфейсу (CLI) для конвеєрів CI/CD

Автоматизація контролю контрактів базується на використанні CLI-утиліти `datacontract` на етапі безперервної інтеграції (Shift-Left перевірка в репозиторії продюсера).

### 1. Синтаксична перевірка маніфесту
Перевіряє валідність структури YAML-файлу проти метасхеми стандарту ODCS:

```bash
datacontract lint ./contracts/orders-contract.yaml
```

*Коди повернення CLI:*
- `0`: Синтаксис коректний, усі обов'язкові блоки заповнені.
- `1`: Помилка синтаксису YAML або відсутні критичні поля метаданих (наприклад, відсутній блок `owner` або некоректний формат версії SemVer).

### 2. Перевірка зворотної сумісності (Breaking Change Detection)
Порівнює локальний файл контракту з версією, яка зараз опублікована в центральному реєстрі виробничого середовища:

```bash
datacontract test-compatibility \
  --local ./contracts/orders-contract.yaml \
  --remote https://schema-registry.internal.net/contracts/orders/v2.2.0 \
  --mode BACKWARD
```

*Правила перевірки режимів сумісності:*
- `BACKWARD`: Заборонено видаляти наявні поля, заборонено змінювати типи даних на несумісні, заборонено додавати нові обов'язкові поля (`required: true` без значення за замовчуванням).
- `FORWARD`: Заборонено видаляти поля зі значеннями за замовчуванням, заборонено звужувати множини `enum`.
- `FULL`: Одночасна перевірка вимог прямої та зворотної сумісності.

### 3. Автоматична генерація схем та артефактів
Утиліта може автоматично компілювати контракт у цільові технічні формати для використання розробниками та інженерами сховищ:

```bash
# Генерація Avro Schema для продюсера
datacontract export --format avro ./contracts/orders-contract.yaml > ./generated/orders.avsc

# Генерація моделі dbt для сховища Snowflake / BigQuery
datacontract export --format dbt ./contracts/orders-contract.yaml > ./dbt/models/orders_model.sql

# Генерація DDL для створення Iceberg-таблиці
datacontract export --format sql-ddl --dialect iceberg ./contracts/orders-contract.yaml
```

### 4. Публікація затвердженого контракту в реєстр
Після успішного злиття Pull Request у гілку `main` контракт публікується в центральний корпоративний каталог:

```bash
datacontract publish ./contracts/orders-contract.yaml \
  --registry https://schema-registry.internal.net \
  --token "$REGISTRY_AUTH_TOKEN" \
  --tag production
```

Завдяки цьому реєстр схем стає єдиним джерелом правди про формати, типи даних та бізнес-правила для всієї інфраструктури компанії.

## Двигун обчислення бізнес-інваріантів (CEL та SQL Assertions)

Специфікація бізнес-правил у блоці `semantics.businessRules` підтримує два формати виразів для перевірки складної логіки між полями одного запису або в межах мікробатчу:

1. **Common Expression Language (CEL):** швидкий, безпечний та вбудовуваний неповний за Тюрінгом двигун виразів, розроблений Google. Він дозволяє обчислювати предикати над полями без ризику зависання потоку (відсутність нескінченних циклів та рекурсії):
   ```yaml
   businessRules:
     - name: discount_check
       rule: "this.discount_amount_cents <= this.total_amount_cents"
     - name: delivery_date_sequence
       rule: "this.estimated_delivery_at > this.created_at"
   ```
2. **SQL Assertions:** діалект SQL-виразів над мікробатчем для обчислення статистичних обмежень:
   ```yaml
   businessRules:
     - name: max_null_ratio
       rule: "count(user_id) / count(*) >= 0.999"
   ```

## Інтеграція з Data Lineage та каталогами метаданих

Маніфест data-контракту є основним джерелом метаданих для побудови наскрізного графа походження даних (Data Lineage). Під час кожної публікації контракту в реєстр автоматичний агент генерує подію специфікації OpenLineage:

- **Фасет схеми (Schema Facet):** оновлює дерево полів цільових таблиць у DataHub або Apache Atlas.
- **Фасет власності (Ownership Facet):** призначає продуктовий домен і команду-власника за полями блоку `info.owner`.
- **Фасет конфіденційності (Dataset Facet):** маркує поля `user_id` міткою `pii:gdpr`, що автоматично активує політики маскування (Data Masking) та контроль прав доступу на рівні колонок (Column-Level Access Control, CLAC) у Snowflake або Databricks Unity Catalog.

## Крайові випадки серіалізації та пастки сумісності типів

При формалізації контрактів на межі між операційними мовами (Go, Java, Python, C++) та аналітичними сховищами виникають типові інженерні пастки узгодження типів:

- **Дробові числа з рухомою комою (Float vs Decimal):** використання типів `float32` або `float64` для фінансових сум є неприпустимим через накопичення похибок двійкового округлення за стандартом IEEE 754. Специфікація контракту жорстко вимагає переведення грошей у цілочисельні центи/копійки (`integer` з мінімальним номіналом) або використання точного формату з фіксованою комою (`decimal(18, 4)`).
- **Часові мітки та часові пояси (Timezone Offset Hazard):** запис рядків типу `"2026-08-20 14:30:00"` без явного зазначення зміщення часового поясу призводить до спотворення фінансових показників при зміні літнього часу або обробці серверів у різних географічних зонах. Стандарт контракту вимагає суворого дотримання формату ISO-8601 у нульовому поясі UTC (`date-time` із закінченням `Z` або `+00:00`).
- **Семантика відсутності значень (Null vs Missing Key):** у форматі JSON порожнє поле `{"discount": null}` та відсутність ключа `{}` можуть інтерпретуватися парсерами по-різному. Специфікація контракту вважає обидва випадки порушенням, якщо для поля явно встановлено `required: true`.
- **Деградація множин Enum:** видалення навіть одного невикористовуваного значення зі списку `enum` є порушенням зворотної сумісності (Breaking Change), оскільки історичні дані в архіві DWH можуть містити це значення. Застарілі варіанти `enum` позначаються міткою `deprecated: true`, але залишаються валідними для читання з архіву.

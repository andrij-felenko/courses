# 📋 Контракт та API конфігурації політик життєвого циклу даних

Цей довідник описує повний формальний контракт, декларативну специфікацію політик утримання даних (Data Retention Policy Specification), схему подій для хуків життєвого циклу, механізми перекриття судовими замовленнями (Legal Hold) та структуру повноцінного конверта помилок підсистеми життєвого циклу.

## Призначення та межі контракту

У розподіленій системі управління даними політика життєвого циклу не може бути зашита у вигляді довільних констант у вихідному коді окремих сервісів. Якщо кожен сервіс самостійно вирішує, коли витирати або архівувати свої записи, система швидко втрачає узгодженість. Наприклад, сервіс замовлень може видалити історію покупок через 90 днів, тоді як сервіс аналітики чекає на ці дані для річного звіту, а сервіс білінгу зобов'язаний тримати їх 10 років для податкового аудиту.

Декларативний контракт політик життєвого циклу даних виступає єдиним джерелом правди (*single source of truth*) для всіх підсистем. Він розмежовує правила утримання для різних типів сутностей, визначає допустимі шляхи міграції даних між фізичними шарами сховища та задає жорсткі межі SLA для виконання регуляторних запитів приватності.

Контракт підтримує гаряче оновлення конфігурації без перезапуску сервісів, валідується сторожовими фітнес-функціями в CI/CD та транслюється у форми подій для шини повідомлень.

## Принципи версіонування та еволюції контракту

Конфігураційний контракт життєвого циклу даних версіонується за принципами семантичного версіонування специфікацій. Головне правило еволюції контракту — **зворотна сумісність**:

1. **Адитивність полів**: Додавання нових необов'язкових полів у специфікацію (наприклад, нового алгоритму стиснення або параметра розміру Row Group) є сумісною зміною і не вимагає підвищення мажорної версії (`1.0` -> `1.1`).
2. **Заборона змішування семантики**: Існуючі поля не можуть змінювати свою семантику. Якщо поле `hot_days` означало кількість днів у гарячій базі, воно не може раптово перетворитися на кількість годин.
3. **Строга валідація на етапі CI/CD**: Будь-які зміни у конфігурації політик проходять автоматичну перевірку у CI/CD за допомогою сторожових фітнес-функцій. Фітнес-функція перевіряє, що жодна політика не зменшує термін утримання нижче законодавчого мінімуму (наприклад, `hot_days < 3650` для фінансових записів).

## Контракт декларативної політики утримання (Retention Policy Schema)

Конфігурація життєвого циклу описується у декларативному форматі YAML або JSON. Кожен блок декларує правила утримання для конкретної сутності (таблиці або доменного агрегату), її фізичний шар, термін життя (TTL), формат архівування та стратегію виконання вимог приватності.

```yaml
version: "1.0"
namespace: "digital_homes_prod"
global_settings:
  default_archive_bucket: "s3://dh-cold-archives-prod/"
  kms_master_key_arn: "arn:aws:kms:eu-central-1:123456789012:key/master-dh"
  legal_hold_override_enabled: true

policies:
  - entity: "telemetry_readings"
    description: "Первинний потік показань давачів температури, напруги та протікання"
    partition_strategy: "TIME_RANGE_MONTHLY"
    partition_column: "created_at"
    retention:
      hot_days: 90
      warm_days: 275
      cold_archive:
        enabled: true
        storage_format: "PARQUET"
        compression: "ZSTD"
        destination: "s3://dh-cold-archives-prod/telemetry/"
        row_group_size_mb: 128
    deletion_strategy: "HARD_DROP_PARTITION"
    compliance:
      contains_pii: false
      requires_crypto_shredding: false

  - entity: "user_accounts"
    description: "Облікові записи користувачів, профілі та налаштування автентифікації"
    partition_strategy: "TENANT_HASH"
    partition_column: "tenant_id"
    retention:
      hot_days: 3650  # 10 років за вимогами податкового та фінансового аудиту
      warm_days: 0
      cold_archive:
        enabled: false
    deletion_strategy: "CRYPTO_SHREDDING"
    compliance:
      contains_pii: true
      requires_crypto_shredding: true
      kms_key_pattern: "kms/tenants/{tenant_id}/users/{user_id}"
      erasure_sla_hours: 72
      cascade_entities:
        - "user_sessions"
        - "user_preferences"
        - "notification_channels"

  - entity: "audit_events"
    description: "Журнал безпекових подій, аутентифікацій та зміни прав доступу"
    partition_strategy: "TIME_RANGE_MONTHLY"
    partition_column: "event_time"
    retention:
      hot_days: 365
      warm_days: 1460 # 4 роки в теплом шарі
      cold_archive:
        enabled: true
        storage_format: "PARQUET"
        compression: "ZSTD"
        destination: "s3://dh-cold-archives-prod/security-audit/"
    deletion_strategy: "IMMUTABLE_WORM" # Write Once Read Many (неможливо видалити до закінчення TTL)
    compliance:
      contains_pii: false
      requires_crypto_shredding: false
```

## Схема полів та валідаційні правила конфігуратора

Кожна декларація політики перевіряється строгою схемою під час завантаження вузла життєвого циклу. Нижче наведено розширений опис кожного поля контракту, його семантику та правила валідації.

| Поле | Тип | Обов'язкове | Значення за замовчуванням | Опис та правила валідації |
| :--- | :--- | :--- | :--- | :--- |
| `entity` | `string` | Так | — | Унікальне ім'я сутності або назва головної OLTP-таблиці в базі даних. Мусить відповідати масці `^[a_z0-9_]+$`. |
| `description` | `string` | Ні | `""` | Людиночитаний опис призначення даних для аудиторів та інженерів. |
| `partition_strategy` | `enum` | Так | — | Допустимі значення: `TIME_RANGE_DAILY`, `TIME_RANGE_MONTHLY`, `TENANT_HASH`, `LIST_EXPLICIT`, `NONE`. |
| `partition_column` | `string` | Так | `created_at` | Колонка таблиці, за якою виконується нарізка партицій. Мусить бути відіндексована. |
| `retention.hot_days` | `integer` | Так | — | Термін перебування даних у гарячій OLTP-базі під активними B-tree індексами. Мусить бути `> 0`. |
| `retention.warm_days` | `integer` | Ні | `0` | Тривалість зберігання у від'єднаних read-only партиціях. Значення `0` означає прямий експорт у Cold Tier. |
| `retention.cold_archive.enabled` | `boolean` | Так | `false` | Прапор дозволу експорту у холодний об'єктний шар S3 перед вилученням. |
| `retention.cold_archive.storage_format` | `enum` | Ні | `PARQUET` | Формат збереження холодного архіву: `PARQUET`, `ORC`, `AVRO`, `JSON_GZ`. |
| `retention.cold_archive.compression` | `enum` | Ні | `ZSTD` | Алгоритм стиснення файлів: `ZSTD`, `SNAPPY`, `GZIP`, `UNCOMPRESSED`. |
| `deletion_strategy` | `enum` | Так | — | Метод очищення: `HARD_DROP_PARTITION`, `ANONYMIZE_IN_PLACE`, `CRYPTO_SHREDDING`, `IMMUTABLE_WORM`. |
| `compliance.contains_pii` | `boolean` | Так | — | Ознака наявності персональних даних. Якщо `true`, обов'язково вказується `erasure_sla_hours`. |
| `compliance.requires_crypto_shredding` | `boolean` | Так | `false` | Чи вимагає сутність шифрування унікальними ключами KMS та їх вилучення за GDPR Article 17. |
| `compliance.erasure_sla_hours` | `integer` | Ні | `720` | Максимальний SLA виконання запиту на вилучення в годинах (за законодавством ЄС — не більше 720 годин / 30 днів). |
| `compliance.cascade_entities` | `array[string]` | Ні | `[]` | Перелік дочірніх сутностей, які підлягають каскадному вилученню або анонімізації. |

## Крайовий випадок: Замок юридичного перекриття (Legal Hold)

Особливим крайовим випадком у контракті життєвого циклу є стан **Legal Hold** (юридичне заморожування). Якщо проти компанії розпочато судовий розгляд або розслідування регулятора, правоохоронні органи або юридичний відділ накладають судову заборону на вилучення будь-яких даних, пов'язаних із конкретним користувачем, орендарем або часовим інтервалом.

У такому разі прапор `legal_hold` перевизначає будь-які планові політики TTL:

```json
{
  "legalHoldId": "hold_2026_court_881",
  "entity": "telemetry_readings",
  "targetTenantId": "tnt_corp_4410",
  "reason": "Судовий запит №441/2026 щодо розслідування інциденту мережі",
  "appliedAt": "2026-08-18T08:30:00Z",
  "appliedBy": "legal_officer_kovalenko",
  "status": "ACTIVE",
  "effectiveOverride": "BLOCK_ALL_PURGE_AND_SHREDDING"
}
```

Коли фоновий рушій життєвого циклу намагається від'єднати партицію або знищити ключ KMS для об'єкта, що перебуває під `Legal Hold`, операція скасовується, а у журнал аудиту повертається помилка `409 Conflict` з кодом `legal_hold_active`.

## Механіка накладання та зняття Legal Hold

Накладання юридичного замка відбувається за чітким регламентом через адміністративний API вузла життєвого циклу:

1. **Записування розпорядження**: Юридичний офіцер відправляє підписаний запит `POST /api/v1/lifecycle/legal-holds` із зазначенням підстави, цільового ідентифікатора орендаря та діапазону дат.
2. **Атомарний запис у реєстр заморожування**: Вузол життєвого циклу записує стан у таблицю `legal_holds` з високим пріоритетом.
3. **Перевірка на кожному кроці ротації**: Перед виконанням будь-якої операції `ALTER TABLE DETACH PARTITION`, `DROP TABLE` або `kms.destroyKey()` рушій виконує обов'язковий логічний предикат:

```sql
SELECT EXISTS (
  SELECT 1 FROM legal_holds
  WHERE entity = $1 
    AND (target_tenant_id IS NULL OR target_tenant_id = $2)
    AND status = 'ACTIVE'
);
```

Якщо предикат повертає `true`, ротація даної партиції або знищення ключа миттєво припиняються, а метрика `data_lifecycle_legal_holds_blocked_total` збільшується на одиницю.

Зняття замка відбуваються виключно за зворотним кваліфікованим запитом `DELETE /api/v1/lifecycle/legal-holds/{id}` із внесенням запису до незмінного аудит-логу.

## Контракт подій хуків життєвого циклу (Lifecycle Hooks API)

Підсистема життєвого циклу публікує асинхронні події в шину повідомлень на кожному критичному кроці транзиту даних. Це дозволяє вторинним підсистемам (пошуку, кешу, аналітиці) узгоджувати свій стан без прямого зчеплення з кодом рушія.

### 1. Подія початку ротації партицій (`data.lifecycle.partition_detach_started`)

Опубліковується за 5 хвилин до виконання операції `ALTER TABLE DETACH PARTITION`.

```json
{
  "eventId": "evt_lh_88102a",
  "eventType": "data.lifecycle.partition_detach_started",
  "timestamp": "2026-08-18T03:55:00Z",
  "producer": "data-lifecycle-node-worker",
  "payload": {
    "entity": "telemetry_readings",
    "partitionName": "telemetry_readings_2026_04",
    "cutoffDate": "2026-05-01T00:00:00Z",
    "estimatedRowCount": 12500000,
    "willArchiveToS3": true,
    "s3Destination": "s3://dh-cold-archives-prod/telemetry/telemetry_readings_2026_04.parquet"
  }
}
```

### 2. Подія підтвердження виконання GDPR-вилучення (`data.lifecycle.pii_erased`)

Опубліковується негайно після успішного знищення ключа KMS або виконання анонімізації на місці.

```json
{
  "eventId": "evt_erased_99120",
  "eventType": "data.lifecycle.pii_erased",
  "timestamp": "2026-08-18T09:12:44Z",
  "producer": "data-lifecycle-node-worker",
  "payload": {
    "userIdHash": "f8a912b4c1020498a12e3456789abcdef0123456789abcdef0123456789abcde",
    "tenantId": "tnt_smart_home_12",
    "erasureStrategy": "CRYPTO_SHREDDING",
    "kmsKeyArn": "arn:aws:kms:eu-central-1:123456789012:key/usr-9912",
    "shreddedAt": "2026-08-18T09:12:44Z",
    "cascadedEntitiesErased": [
      "user_sessions",
      "user_preferences",
      "notification_channels"
    ],
    "complianceReference": "GDPR_ARTICLE_17_REQ_4491"
  }
}
```

## Семантика обробки подій вторинними підсистемами

Отримавши подію `data.lifecycle.pii_erased`, вторинні сервіси виконують відповідні каскадні дії у власних локальних сховищах:

1. **Сервіс пошуку (Search Engine)**: Отримує `userIdHash`, знаходить відповідні документи в індексі Elasticsearch (`PUT /users/_delete_by_query`) та миттєво вилучає картки користувачів із результатів пошуку.
2. **Сервіс авторизації та кешування**: Виконує команди вилучення ключів у Redis `DEL session:usr_*` та анулює всі активні JWT-токени або сесії даного користувача.
3. **Аналітичний сервіс (OLAP)**: Перераховує агреговані знеособлені метрики, перевіряючи, що в кубах не залишилося жодного прямого посилання на особу.

Такий підхід на основі подій забезпечує остаточну узгодженість (*eventual consistency*) при вилученні даних без створення жорстких розподілених транзакцій (2PC) між базами даних різних сервісів.

## Довідник кодів помилок вузла життєвого циклу

Мережева межа API вузла життєвого циклу повертає помилки у стандартному конверті RFC 9457 Problem Details (`application/problem+json`). Жодна внутрішня деталь СУБД, стек викликів чи неооброблений SQL не просочуються назовні.

```json
{
  "type": "https://api.dh.io/errors/lifecycle-policy-violation",
  "title": "Порушення політики утримання даних",
  "status": 422,
  "code": "retention_policy_violation",
  "detail": "Неможливо вилучити партицію telemetry_readings_2026_05: термін утримання hot_days (90) ще не закінчився.",
  "requestId": "req_lifecycle_9912a",
  "invalidParams": [
    {
      "name": "partition_name",
      "reason": "Партиція містить записи від 2026-06-15, cutoff дозволяє лише < 2026-05-20"
    }
  ]
}
```

### Реєстр машинних кодів помилок (`code`)

Нижче наведено вичерпну таблицю всіх машинних кодів помилок, які може повернути вузол життєвого циклу під час виконання або налаштування політик.

| Код помилки (`code`) | HTTP Status | Семантика, причина та рекомендована дія |
| :--- | :--- | :--- |
| `retention_policy_violation` | 422 | Спроба вилучити дані до закінчення мінімального строку `hot_days`. Помилка конфігурації. Перевірте `cutoffDate`. |
| `legal_hold_active` | 409 | Операцію вилучення або знищення ключа KMS блоковано активним судовим замовленням `Legal Hold`. Видалення заборонено законом. |
| `kms_key_destruction_failed` | 502 | Помилка взаємодії з KMS під час спроби знищити ключ `K_user`. Повторіть запит із використанням `Retry-After`. |
| `partition_detach_timeout` | 504 | Операція `ALTER TABLE DETACH PARTITION` заблокована довготривалою транзакцією в OLTP. Перевірте блокування та зніміть довготривалі `SELECT`. |
| `archive_export_failed` | 500 | Збій запису Parquet-файла у холодний шар S3. Таблицю **не від'єднано** від бази, транзакція відкочена. |
| `pii_erasure_sla_exceeded` | 504 | Час виконання анонімізації перевищив встановлений SLA (72 години). Потрібне втручання чергового інженера. |
| `invalid_policy_schema` | 400 | Синтаксична помилка в YAML/JSON конфігурації політик життєвого циклу під час валідації в CI/CD або при завантаженні. |

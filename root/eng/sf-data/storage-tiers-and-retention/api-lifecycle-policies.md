# 📋 Специфікація декларативних політик життєвого циклу, WORM-блокувань та метрик тирування

Повний довідник конфігураційних схем переходів між ярусами (Lifecycle Transitions), правил автоматичного стирання за терміном (Expiration), регуляторних блокувань незмінності (WORM Object Lock) та інтерфейсу телеметрії Prometheus для моніторингу черг міграції й затримок сховища.

Ця специфікація стандартизує структуру декларативних маніфестів, якими керуються хмарні та локальні рушії тирування даних, визначає точні семантичні інваріанти обробки версій і часових міток, а також надає повний опис метрик спостережуваності для моніторингу затримок і помилок міграції.

---

### 1. Декларативна схема політики життєвого циклу (Lifecycle Specification)

Політики тирування та утримання описуються у форматі JSON або YAML і застосовуються до всього простору імен або вибіркових префіксів бакета. Обчислювальний рушій сховища виконує періодичний аудит усіх об'єктів (типово раз на добу о 00:00 за часом UTC) і розраховує вік кожної версії за формулою різниці між поточним системним часом і часовою міткою останньої модифікації (`Last-Modified`).

Якщо об'єкт задовольняє критерії фільтрації, рушій ставить завдання на перенесення в асинхронну чергу виконання. При цьому перехід між ярусами ніколи не блокує виконання поточних операцій читання або запису.

#### Повний маніфест конфігурації (YAML)

```yaml
version: "v1.2"
rules:
  # Правило 1: Життєвий цикл транзакційних логів та аналітичних партицій
  - id: "telemetry-and-logs-lifecycle"
    status: "Enabled"
    filter:
      and:
        prefix: "telemetry/events/"
        tags:
          environment: "production"
          classification: "audit"
        object_size_greater_than_bytes: 131072 # 128 КіБ (запобігання міграції дрібних файлів)
        object_size_less_than_bytes: 10737418240 # 10 ГіБ
    transitions:
      - days_after_creation: 14
        target_storage_class: "WARM_HDD"
      - days_after_creation: 90
        target_storage_class: "COLD_OBJECT_STORAGE"
      - days_after_creation: 365
        target_storage_class: "ARCHIVE_GLACIER_DEEP"
    noncurrent_version_transitions:
      - noncurrent_days: 7
        target_storage_class: "COLD_OBJECT_STORAGE"
      - noncurrent_days: 30
        target_storage_class: "ARCHIVE_GLACIER_DEEP"
    expiration:
      days_after_creation: 2555 # 7 років (регуляторний ліміт утримання)
      expired_object_delete_marker: true
    abort_incomplete_multipart_upload:
      days_after_initiation: 3 # Очищення незавершених багатокомпонентних завантажень

  # Правило 2: Тимчасові кеші та сесійні маркери
  - id: "ephemeral-cache-expiration"
    status: "Enabled"
    filter:
      prefix: "temp/staging-cache/"
    expiration:
      days_after_creation: 3
      expired_object_delete_marker: true
```

#### Семантичні правила обробки предикатів і фільтрів

Обчислення життєвого циклу ґрунтується на наступних інваріантах:

1. **Правило найсуворішого збігу префіксів:** Якщо об'єкт підпадає під дію кількох правил одночасно (наприклад, загальне правило для кореня бакета і спеціальне правило для префікса `logs/secure/`), рушій застосовує правило з найбільш специфічним префіксом і найкоротшим строком переходу до більш холодного ярусу.
2. **Фільтрація за розміром (Small Object Protection):** Предикат `object_size_greater_than_bytes` запобігає переміщенню об'єктів розміром менше 128 КіБ у класи Infrequent Access та Glacier. Дрібні об'єкти, переведені в холодний ярус індивідуально, викликають колосальні накладні витрати на зберігання метаданих і мінімальні тарифні штрафи.
3. **Обробка незавершених сесій (Multipart Upload Pruning):** Блок `abort_incomplete_multipart_upload` гарантує видалення тимчасових частин завантаження, які зависли через мережеві аварії клієнтів. Без цього правила незавершені завантаження можуть роками споживати сотні гігабайтів дорогого гарячого простору, залишаючись невидимими для стандартних операцій лістингу файлів.

#### Поля та семантика специфікації правил

| Поле конфігурації | Тип даних | Обов'язкове | Опис та семантичні обмеження |
|---|---|---|---|
| `id` | `string` | Так | Унікальний ідентифікатор правила в межах простору імен (до 255 символів). |
| `status` | `string` | Так | Стан виконання: `Enabled` (активне) або `Disabled` (тимчасово вимкнене). |
| `filter.prefix` | `string` | Ні | Префікс шляху до об'єкта (наприклад, `logs/2026/`). Якщо порожньо — застосовується до всіх. |
| `filter.tags` | `map[string]string` | Ні | Набір ключів і значень метаданих об'єкта для точкової фільтрації. |
| `filter.object_size_greater_than_bytes` | `integer` | Ні | Мінімальний розмір об'єкта в байтах для спрацьовування переходів (рекомендовано ≥ 131 072). |
| `transitions[].days_after_creation` | `integer` | Так* | Кількість діб від моменту створення поточної версії до міграції в цільовий ярус. |
| `transitions[].target_storage_class` | `string` | Так* | Цільовий клас сховища: `HOT_NVME`, `WARM_HDD`, `COLD_OBJECT_STORAGE`, `ARCHIVE_GLACIER_DEEP`. |
| `noncurrent_version_transitions[].noncurrent_days` | `integer` | Ні | Кількість днів від моменту створення нової версії об'єкта (заміщення старої версії). |
| `expiration.days_after_creation` | `integer` | Ні | Абсолютний строк життя даних (TTL), після якого об'єкт остаточно знищується або позначається як видалений. |
| `abort_incomplete_multipart_upload.days_after_initiation` | `integer` | Ні | Час у днях для автоматичного скасування завислих сесій збирання чанків. |

---

### 2. Специфікація контрактів WORM та Legal Hold

Регуляторні вимоги фінансового, медичного та безпекового секторів (GDPR, SEC Rule 17a-4, FINRA, HIPAA) вимагають жорсткого блокування можливості видалення, модифікації або скорочення терміну утримання записів до спливу встановленого терміну.

У таких сховищах діє модель незмінності WORM (англ. *Write Once, Read Many*). Дані, одного разу зафіксовані в системі, стають фізично та логічно захищеними від будь-яких маніпуляцій, включаючи дії суперкористувачів або спроби компрометації облікових записів root.

```
   Об'єкт записано ──> [ Перевірка WORM-блокування ] ──> Дозволено читання
                              │
                              ├──> Запит на видалення (DELETE / TRUNCATE)
                              │          │
                              │          ▼
                              ├──> [ Legal Hold == ON ? ] ──> ВІДХИЛЕНО: 403 Forbidden
                              │          │
                              │          ▼ (Hold == OFF)
                              └──> [ Retention Until Date > NOW ? ]
                                         │
                                         ├── ТАК ──> ВІДХИЛЕНО: 403 Forbidden
                                         └── НІ  ──> ДОЗВОЛЕНО: 204 No Content
```

#### Режими блокування утримання (Object Lock Modes)

```json
{
  "ObjectLockConfiguration": {
    "ObjectLockEnabled": "Enabled",
    "Rule": {
      "DefaultRetention": {
        "Mode": "COMPLIANCE",
        "Days": 2555
      }
    }
  }
}
```

Механізм утримання підтримує два взаємовиключні режими та один незалежний прапорець:

1. **Режим суворого комплаєнсу (`COMPLIANCE` Mode):**
   - Об'єкт не може бути видалений або перезаписаний **жодним користувачем**, включаючи обліковий запис адміністратора (`root`) та облікові записи з повними правами IAM.
   - Період утримання (`RetainUntilDate`) не може бути скорочений або знятий до настання вказаної дати.
   - Будь-яка спроба видалення повертає помилку `403 Access Denied (ObjectUnderRetention)`.
   - Продовження терміну утримання на більшу кількість днів дозволене в будь-який момент.

2. **Режим керованого комплаєнсу (`GOVERNANCE` Mode):**
   - Об'єкт захищений від випадкового видалення більшістю користувачів та автоматизованих скриптів системи.
   - Користувачі зі спеціальним привілейованим дозволом (`s3:BypassGovernanceRetention`) можуть скасувати блокування, скоротити строк утримання або примусово видалити об'єкт достроково.

3. **Юридичне блокування (`Legal Hold`):**
   - Незалежний бінарний прапорець (`ON` / `OFF`), що накладається на об'єкт під час судових розслідувань, податкових перевірок чи позапланових аудитів безпеки.
   - Не має фіксованої дати завершення й діє безстроково доти, доки уповноважений офіцер безпеки явно не зніме прапорець викликом `PutObjectLegalHold` зі значенням `Status=OFF`.
   - Наявність активного Legal Hold блокує будь-які операції видалення навіть у тому випадку, якщо термін дії `RetainUntilDate` уже вичерпано.

#### Архітектурне вирішення конфлікту між GDPR та WORM

Коли сервіс отримує запит на реалізацію «права бути забутим» (GDPR Right to be Forgotten) щодо користувача, чиї транзакційні записи заблоковані незмінним WORM-утриманням на 7 років за вимогами фінансового аудиту (SEC 17a-4), пряме фізичне видалення файлу є неможливим через апаратні та програмні обмеження.

Єдиним легітимним інженерним вирішенням цього протиріччя є застосування патерну крипто-шредінгу. При первинному записі персональні дані клієнта шифруються унікальним індивідуальним ключем шифрування даних (DEK), який зберігається в окремому сервісі керування ключами (KMS). На WORM-носій потрапляє виключно зашифрований шифротекст. 

При отриманні запиту на стирання даних система безповоротно знищує індивідуальний ключ DEK у сховищі KMS. Сам зашифрований масив залишається недоторканим на архівному носії, повністю задовольняючи вимоги незмінності WORM, тоді як розшифрування та відновлення персональних даних стає математично неможливим, що юридично й технічно еквівалентно повному видаленню за нормами GDPR.

---

### 3. API асинхронного розморожування та відновлення (Rehydration API)

Для доступу до об'єктів, переведених в архівні яруси (Glacier Flexible або Deep Archive), клієнт зобов'язаний виконати процедуру попереднього розморожування (англ. *Restore/Rehydration*).

```http
POST /telemetry/events/chunk-2025-01.parquet?restore HTTP/1.1
Host: data-lake.company.internal
Content-Type: application/xml

<RestoreRequest>
  <Days>7</Days>
  <GlacierJobParameters>
    <Tier>Standard</Tier>
  </GlacierJobParameters>
</RestoreRequest>
```

#### Тарифи та режими відновлення (Restore Tiers)

1. **Терміновий (`Expedited`):** Час відновлення від 1 до 5 хвилин для об'єктів розміром до 250 МБ. Застосовується для критичних відновлень після збоїв. Найвища вартість запиту.
2. **Стандартний (`Standard`):** Час відновлення від 3 до 5 годин для Glacier Flexible Retrieval та до 12 годин для Glacier Deep Archive. Оптимальний для планових аналітичних звітів.
3. **Пакетний (`Bulk`):** Час відновлення від 5 до 12 годин для Glacier і до 48 годин для Deep Archive. Найдешевший режим для фонової обробки петабайтних масивів.

Під час виконання відновлення заголовок об'єкта `x-amz-restore` містить статус `ongoing-request="true"`. Після завершення копіювання тимчасова копія стає доступною на теплому ярусі, а заголовок набуває вигляду `ongoing-request="false", expiry-date="Sun, 30 Aug 2026 00:00:00 GMT"`.

---

### 4. Телеметрія та метрики Prometheus для рушія тирування

Планувальник міграції експортує детальні лічильники та гістограми на ендпоінт `/metrics` у стандартному текстовому форматі OpenMetrics. Це дозволяє в реальному часі відстежувати ефективність тирування, навантаження на дискові контролери та ризик перевитрати бюджету.

```
# HELP storage_tier_bytes_total Поточний обсяг даних, збережених у кожному ярусі (у байтах)
# TYPE storage_tier_bytes_total gauge
storage_tier_bytes_total{tier="hot_nvme",namespace="telemetry"} 8796093022208
storage_tier_bytes_total{tier="warm_hdd",namespace="telemetry"} 54975581388800
storage_tier_bytes_total{tier="cold_s3",namespace="telemetry"} 219902325555200
storage_tier_bytes_total{tier="archive_glacier",namespace="telemetry"} 879609302220800

# HELP storage_tier_capacity_ratio Відсоток утилізації ємності гарячого ярусу
# TYPE storage_tier_capacity_ratio gauge
storage_tier_capacity_ratio{tier="hot_nvme"} 0.884

# HELP storage_tier_migration_queue_length Кількість чанків у черзі на переміщення
# TYPE storage_tier_migration_queue_length gauge
storage_tier_migration_queue_length{source_tier="hot_nvme",target_tier="warm_hdd"} 142

# HELP storage_tier_migration_operations_total Загальна кількість виконаних міграцій блоків
# TYPE storage_tier_migration_operations_total counter
storage_tier_migration_operations_total{source="hot_nvme",target="warm_hdd",status="success"} 48920
storage_tier_migration_operations_total{source="hot_nvme",target="warm_hdd",status="checksum_error"} 2
storage_tier_migration_operations_total{source="warm_hdd",target="cold_s3",status="timeout"} 5

# HELP storage_tier_retrieval_duration_seconds Гістограма часу розморожування/читання блоків
# TYPE storage_tier_retrieval_duration_seconds histogram
storage_tier_retrieval_duration_seconds_bucket{tier="hot_nvme",le="0.001"} 1450200
storage_tier_retrieval_duration_seconds_bucket{tier="warm_hdd",le="0.020"} 89400
storage_tier_retrieval_duration_seconds_bucket{tier="cold_s3",le="0.250"} 12400
storage_tier_retrieval_duration_seconds_bucket{tier="archive_glacier",le="1800.0"} 310
storage_tier_retrieval_duration_seconds_count 1552310
storage_tier_retrieval_duration_seconds_sum 589412.4
```

#### Правила алертингу для системи моніторингу (Prometheus Alerting Rules)

На базі цих метрик налаштовуються критичні сповіщення для чергових інженерів платформи:

```yaml
groups:
  - name: storage_tiering_alerts
    rules:
      # Загроза вичерпання простору на швидких накопичувачах
      - alert: HotTierCapacityCriticallyHigh
        expr: storage_tier_capacity_ratio{tier="hot_nvme"} > 0.92
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Hot Tier майже переповнений (> 92%). Ризик відмови операцій запису."

      # Відставання конвеєра міграції через перевантаження I/O
      - alert: TieringMigrationLagging
        expr: storage_tier_migration_queue_length > 1000
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Черга витіснення перевищує 1000 чанків. Швидкість надходження даних вища за швидкість копіювання."

      # Сплеск помилок контрольних сум або тайм-аутів
      - alert: TieringChecksumMismatchDetected
        expr: rate(storage_tier_migration_operations_total{status="checksum_error"}[5m]) > 0
        labels:
          severity: critical
        annotations:
          summary: "Виявлено невідповідність хешу BLAKE3 під час міграції. Ймовірний збій диска або оперативної пам'яті."
```

#### Словник метрик тирування

| Назва метрики | Тип | Мітки (Labels) | Інженерне призначення |
|---|---|---|---|
| `storage_tier_bytes_total` | Gauge | `tier`, `namespace` | Моніторинг балансу даних між швидкими й повільними носіями; розрахунок вартості TCO. |
| `storage_tier_capacity_ratio` | Gauge | `tier` | Відстеження досягнення High Watermark (0.85) та ризику переповнення гарячого диска. |
| `storage_tier_migration_queue_length` | Gauge | `source_tier`, `target_tier` | Розмір беклогу мігратора; детекція відставання фонових воркерів під час пікових навантажень. |
| `storage_tier_migration_operations_total` | Counter | `source`, `target`, `status` | Кількість успішних та аварійних переміщень; виявлення помилок мережі чи збоїв контрольних сум. |
| `storage_tier_retrieval_duration_seconds` | Histogram | `tier`, `le` | Затримка читання блоків з різних ярусів; верифікація дотримання SLA/SLO латентності. |

---

### 5. Контракт обробки помилок та статусів міграції

Коли потік-виконавець натрапляє на нештатну ситуацію, рушій виконує стандартизований алгоритм відновлення згідно з таблицею:

| Код стану | Константа API | Опис причини помилки | Дія рушія (Recovery Strategy) |
|---|---|---|---|
| `ERR_01` | `TIER_SOURCE_BUSY` | Чанк захоплений активною транзакцією з ексклюзивним записом. | Пропустити в поточному раунді; повторити спробу через 30 секунд. |
| `ERR_02` | `CHECKSUM_MISMATCH` | Обчислений BLAKE3-хеш на цільовому ярусі не збігся з джерелом. | Негайно видалити цільову копію; відкатити статус у `ONLINE`; інкрементувати лічильник збоїв. |
| `ERR_03` | `TARGET_STORAGE_UNAVAILABLE` | Тайм-аут мережевого з'єднання (S3 503 / Socket timeout) або помилка авторизації. | Перевести чанк у стан паузи; увімкнути експоненційну затримку повторів (Exponential Backoff). |
| `ERR_04` | `OBJECT_LOCKED_WORM` | Спроба видалити або перезаписати чанк, на який накладено чинний Legal Hold або Retention Lock. | Відхилити операцію з кодом `403 Access Denied`; зафіксувати спробу в аудит-лозі безпеки. |
| `ERR_05` | `BELOW_MINIMUM_SIZE` | Розмір об'єкта менший за допустимий поріг (наприклад, < 128 КіБ для S3-IA). | Заблокувати міграцію окремого файлу; відправити на конвеєр блокової консолідації (Chunk Compaction). |

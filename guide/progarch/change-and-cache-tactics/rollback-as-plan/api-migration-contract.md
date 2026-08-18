# 📋 Контракт та API автоматизованих зворотно-сумісних міграцій

Цей документ є нормативним інтерфейсним контрактом для побудови підсистем автоматизованого відкату (Rollback Controllers) та інфраструктури зворотно-сумісних міграцій бази даних і супутнього коду. Документ визначає декларативну конфігураційну схему, параметри утиліт командного рядка, JSON-формати телеметрії та вебхуків, формальну матрицю станів кінцевого автомата, коди повернення процесів, правила безпеки SQL DDL та контракти системних викликів.

---

## 1. Архітектурна концепція декларативного контракту міграції

Традиційний підхід до розгортання змін схем баз даних покладається на пару імперативних скриптів — `up.sql` (для застосування зміни) та `down.sql` (для її скасування). З інженерної точки зору цей підхід містить фундаментальну ваду: руйнівний `down.sql` (наприклад, `DROP TABLE` або `DROP COLUMN`) знищує нові дані, записані кодом нової версії під час її функціонування.

Декларативний контракт зворотної міграції заперечує концепцію руйнівного `down.sql`. Замість цього контракт гарантує, що база даних переводиться у фазу розширення (`EXPAND`), у якій нова та стара версії додатку функціонують паралельно над єдиним фізичним сховищем. Якщо нова версія коду занепадає або порушує пороги SLO, відкат полягає у миттєвому скиданні мережевого трафіку на стару версію без проведення зворотної DDL-транзакції.

Нижче наведено повну специфікацію декларативного YAML-контракту міграції `ReversibleMigration`:

```yaml
# migration-contract.v1.yaml - Декларативний контракт зворотної міграції
apiVersion: migration.progarch.io/v1alpha1
kind: ReversibleMigration
metadata:
  name: add-customer-tax-identifier
  version: "2.2.0"
  author: "team-billing@company.com"
  created_at: "2026-08-18T10:00:00Z"

spec:
  service:
    name: "payment-billing-service"
    current_stable_version: "v2.1.0"
    target_version: "v2.2.0"
    kill_switch_flag: "enable_v2_tax_calculation"

  database:
    driver: "postgresql"
    lock_timeout_ms: 2000
    statement_timeout_ms: 5000
    retry_attempts: 5
    retry_backoff_sec: 5

  phases:
    expand:
      description: "Неруйнівне розширення схеми: додавання полів та тригерів дзеркалювання"
      scripts:
        up: "migrations/0042_expand_tax_identifier.up.sql"
        down_safety_check: "migrations/0042_expand_tax_identifier.check.sql"
      reversibility_guarantee: "STRICT_REVERSIBLE"

    canary:
      initial_weight_pct: 5
      evaluation_window_sec: 300
      sampling_interval_sec: 5
      max_consecutive_breaches: 3

    contract:
      scheduled_delay_days: 30
      description: "Очистка застарілих полів після 100% підтвердження стабільності"
      scripts:
        up: "migrations/0042_contract_legacy_tax_code.up.sql"

  health_gate:
    telemetry_provider: "prometheus"
    endpoint_url: "http://prometheus-k8s.monitoring.svc:9090"
    slos:
      - name: "p99_latency"
        query: "histogram_quantile(0.99, sum(rate(http_request_duration_seconds_bucket{service='payment-billing-service', version='v2.2.0'}[2m])) by (le))"
        threshold_max: 150.0
        unit: "milliseconds"

      - name: "http_5xx_error_rate"
        query: "sum(rate(http_requests_total{service='payment-billing-service', version='v2.2.0', status=~'5..'}[2m])) / sum(rate(http_requests_total{service='payment-billing-service', version='v2.2.0'}[2m])) * 100"
        threshold_max: 0.5
        unit: "percent"

  reconciliation:
    enabled: true
    worker_image: "repo.company.com/billing/data-reconciler:v2.2.0"
    batch_size: 1000
    max_lag_seconds: 60
```

### Деталізація полів декларативного контракту

- **`spec.service.kill_switch_flag`**: Унікальний ідентифікатор прапора фічі у системі динамічної конфігурації. При виявленні аномалій контролер відкату деактивує цей прапор за час < 100 мілісекунд, що змушує додаток миттєво припинити виконання нового алгоритмічного коду без перезапуску процесів.
- **`spec.database.lock_timeout_ms`**: Граничний час очікування ексклюзивного блокування таблиці при виконанні операцій DDL. Значення у 2000 мс запобігає утворенню каскадних черг блокувань у високонавантажених системах.
- **`spec.phases.canary.max_consecutive_breaches`**: Кількість послідовних порушень порогових значень метрик (замірів), необхідна для прийняття рішення про автоматичний відкат. Це запобігає хибним спрацьовуванням через поодинокі мережеві спалахи.
- **`spec.reconciliation`**: Конфігурація фонового воркера узгодження даних, який після відкату з v2 на v1 знаходить записи, створені новою версією, та приводь їх у стан, повністю сумісний зі старим кодом v1.

---

## 2. Специфікація параметрів утиліти командного рядка (`rollback-ctrl`)

Утиліта `rollback-ctrl` виконує роль консольного агента оркестрації, який запускається у середовищах CI/CD або як окремий Pod у Kubernetes для моніторингу процесів деплою.

### Детальний опис прапорів утиліти `rollback-ctrl`

1. **`--config <path>`** (Тип: String, Значення за замовчуванням: `"migration.yaml"`):
   Визначає абсолютний або відносний шлях до файла конфігурації міграції. Інтерпретатор перевіряє синтаксичну валідність файла та наявність обов'язкових полів до початку будь-яких мережевих викликів.

2. **`--phase <name>`** (Тип: Enum, Варіанти: `expand`, `canary-monitor`, `rollback`, `contract`):
   Вказує контролеру, яку саме операційну фазу необхідно виконати:
   - `expand`: Застосовує неруйнівний DDL у базі даних та перевіряє працездатність тригерів.
   - `canary-monitor`: Запускає цикл безперервного вичитування метрик з Prometheus та керує вагами роутингу.
   - `rollback`: Негайно виконує аварійний відкат трафіку на v1 та вимикає кілл-світч.
   - `contract`: Виконує остаточну очистку застарілих колонок після 100% підтвердження успішності релізу.

3. **`--dry-run`** (Тип: Boolean, Значення за замовчуванням: `false`):
   Режим підтвердження безпеки. Контролер підключається до бази даних та сервісу метрик, перевіряє права доступу та симулює обчислення метрик і DDL без внесення реальних змін у систему.

4. **`--force-rollback`** (Тип: Boolean, Значення за замовчуванням: `false`):
   Прапор примусового ручного відкату. Використовується черговим SRE-інженером для негайної деактивації релізу v2 при виявленні нетипових аварій, які не покриваються автоматичними аналізаторами метрик.

5. **`--slo-latency-ms`** (Тип: Double, Значення за замовчуванням: `150.0`):
   Динамічне перевизначення максимальної затримки 99-го перцентиля (P99 Latency). Якщо замір метрики перевищує це значення, контролер ініціює процедуру скасування релізу.

6. **`--slo-error-pct`** (Тип: Double, Значення за замовчуванням: `0.5`):
   Динамічне перевизначення допустимого відсотка HTTP 5xx помилок. Значення 0.5 означає, що якщо понад 5 запитів з 1000 завершуються збійним кодом 5xx, деплой вважається аварійним.

7. **`--lock-timeout-sec`** (Тип: Integer, Значення за замовчуванням: `2`):
   Час очікування ексклюзивного блокування бази даних при виконанні `ALTER TABLE`. При перевищенні таймауту транзакція скасовується, запобігаючи заторм транзакцій живого трафіку.

8. **`--telemetry-url`** (Тип: String, Значення за замовчуванням: `""`):
   Базовий URL-адрес сервера Prometheus або Datadog API для виконання PromQL-запитів телеметрії.

9. **`--webhook-alert-url`** (Тип: String, Значення за замовчуванням: `""`):
   URL-адреса вебхука для відправки JSON-сповіщень у систему оперативного реагування (PagerDuty, Slack, Opsgenie).

### Таблиця параметрів утиліти `rollback-ctrl`

| Прапор CLI | Тип | За замовчуванням | Опис і операційний контракт |
| :--- | :--- | :--- | :--- |
| `--config <path>` | String | `"migration.yaml"` | Шлях до файла декларативного YAML-контракту міграції. |
| `--phase <name>` | Enum | `expand` | Операційна фаза: `expand`, `canary-monitor`, `rollback`, `contract`. |
| `--dry-run` | Boolean | `false` | Симуляція виконання без внесення змін у БД чи роутер трафіку. |
| `--force-rollback` | Boolean | `false` | Негайна ручна активація кілл-світча та відкат трафіку на v1. |
| `--slo-latency-ms` | Double | `150.0` | Перевизначення макс. допустимої затримки P99 для скасування деплою. |
| `--slo-error-pct` | Double | `0.5` | Перевизначення макс. допустимого відсотка 5xx помилок. |
| `--lock-timeout-sec` | Integer | `2` | Таймаут блокування таблиць для DDL у базі даних (у секундах). |
| `--telemetry-url` | String | `""` | URL-адреса сервера Prometheus / Datadog для вичитування метрик. |
| `--webhook-alert-url` | String | `""` | Webhook URL для відправки JSON-сповіщень про відкат у Slack/PagerDuty. |

---

## 3. Специфікація JSON Telemetry & Webhook API

Взаємодія між контролером відкату, джерелами метрик та системами сповіщення побудована на стандартизованих REST/JSON контрактах. Це дозволяє прозоро інтегрувати контролер із будь-якою платформою спостережуваності.

### 3.1. Запит телеметрії (Prometheus HTTP Query Contract)

Під час фази `canary-monitor` контролер з інтервалом у 5 секунд надсилає HTTP GET запити до Prometheus API. Нижче наведено структуру очікуваної JSON-відповіді:

```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "service": "payment-billing-service",
          "version": "v2.2.0"
        },
        "value": [
          1787050800.123,
          "185.4"
        ]
      }
    ]
  }
}
```

*Пояснення полів*:
- `data.result[0].value[0]`: UNIX-таймстамп виміру (в секундах з плаваючою крапкою).
- `data.result[0].value[1]`: Строкове представлення числового значення метрики (наприклад, 185.4 мілісекунди затримки). Рядковий формат використовується для запобігання втраті точності при передачі чисел з рухомою комою у JSON.

### 3.2. JSON-структура аварійного Webhook-сповіщення

При виявленні деградації метрик та ініціалізації аварійного відкату контролер генерує та надсилає наступне HTTP POST сповіщення:

```json
{
  "schema_version": "1.0",
  "event_type": "AUTOMATED_ROLLBACK_EXECUTED",
  "incident_id": "inc-20260818-0891",
  "timestamp": "2026-08-18T10:15:30.452Z",
  "service": {
    "name": "payment-billing-service",
    "rolled_back_version": "v2.2.0",
    "restored_version": "v2.1.0",
    "kill_switch_triggered": true
  },
  "failure_cause": {
    "code": "ERR_SLO_LATENCY_BREACH",
    "metric_name": "p99_latency",
    "observed_value": 185.4,
    "threshold_value": 150.0,
    "unit": "milliseconds",
    "consecutive_breaches": 3
  },
  "database_status": {
    "state": "EXPAND_SCHEMA_ACTIVE",
    "data_loss": false,
    "reconciliation_required": true,
    "reconciliation_job_started": true
  }
}
```

*Операційне значення полів*:
- `failure_cause.code`: Унікальний код причини аварії (`ERR_SLO_LATENCY_BREACH` або `ERR_SLO_ERROR_RATE_BREACH`), який використовується у системах автоматизованої аналітики інцидентів.
- `database_status.data_loss`: Гарантійний індикатор (завжди `false` при дотриманні зворотно-сумісної міграції), що інформує чергову бригаду про збереження цілісності всіх даних.

---

## 4. Формальна матриця переходів кінцевого автомата (FSM State Transition Matrix)

Функціонування контролера відкату формалізується як детермінований кінцевий автомат (Finite State Machine). Перехід між станами здійснюється лише при справдженні відповідних системних подій або тригерів.

### Деталізований аналіз станів та side-ефектів

1. **`IDLE` -> `SCHEMA_EXPANDING`**:
   - *Тригер*: Команда від CI/CD пайплайну `CMD_START_EXPAND`.
   - *Side-Effect*: Підключення до бази даних, встановлення `SET lock_timeout = '2s'`, виконання неруйнівного DDL `ALTER TABLE ADD COLUMN ... DEFAULT NULL`, реєстрація тригерів подвійного запису.

2. **`SCHEMA_EXPANDING` -> `CANARY_MONITORING`**:
   - *Тригер*: Успішне завершення DDL транзакції (`DDL_SUCCESS`).
   - *Side-Effect*: Виклик API Gateway / Envoy Service Mesh для спрямування 5% трафіку на Pods v2. Запуск фонового потоку оцінки метрик.

3. **`SCHEMA_EXPANDING` -> `FAILED`**:
   - *Тригер*: Перевищення таймауту блокування `DDL_LOCK_TIMEOUT`.
   - *Side-Effect*: Автоматичне `ROLLBACK` DDL-транзакції. Схема бази даних залишається недоторканою. Запуск сповіщення інженерів.

4. **`CANARY_MONITORING` -> `SCHEMA_CONTRACTING`**:
   - *Тригер*: Успішне завершення вікна спостереження без жодного порушення SLO (`SLO_OK_WINDOW_EXPIRED`).
   - *Side-Effect*: Перемикання 100% трафіку на версію v2. Запис у базу даних про успішне завершення першої фази. Планування фази `CONTRACT` через 30 днів.

5. **`CANARY_MONITORING` -> `ROLLBACK_TRAFFIC`**:
   - *Тригер*: Фіксація K послідовних порушень метрик SLO (`SLO_BREACH_DETECTED`).
   - *Side-Effect*: Миттєве скидання частки трафіку v2 до 0% на рівні Envoy. Викликається кілл-світч Feature Flag = `false`.

6. **`ROLLBACK_TRAFFIC` -> `ROLLBACK_SCHEMA`**:
   - *Тригер*: Завершення перемикання трафіку (`TRAFFIC_SHIFT_DONE`).
   - *Side-Effect*: Активація фонового воркера узгодження даних (Data Reconciliation Worker). Схема БД залишається у безпечному стані `EXPAND`.

7. **`ROLLBACK_SCHEMA` -> `COMPLETED`**:
   - *Тригер*: Завершення фонового узгодження даних (`RECONCILIATION_DONE`).
   - *Side-Effect*: Сервіс працює на версії v1. Система повертається у повністю стабільний стан.

8. **`SCHEMA_CONTRACTING` -> `COMPLETED`**:
   - *Тригер*: Запуск відкладеної міграції очистки (`CMD_START_CONTRACT`).
   - *Side-Effect*: Виконання DDL `ALTER TABLE DROP COLUMN` для видалення застарілих полів версії v1.

### Таблиця переходів кінцевого автомата

| Вхідний стан | Подія / Тригер | Вихідний стан | Дія контролера (Side Effect) |
| :--- | :--- | :--- | :--- |
| `IDLE` | `CMD_START_EXPAND` | `SCHEMA_EXPANDING` | Запуск неруйнівного DDL `ALTER TABLE ADD COLUMN` з `lock_timeout`. |
| `SCHEMA_EXPANDING` | `DDL_SUCCESS` | `CANARY_MONITORING` | Ввімкнення канарейки (5% трафіку v2). Запуск моніторингу SLO. |
| `SCHEMA_EXPANDING` | `DDL_LOCK_TIMEOUT` | `FAILED` | Скасування транзакції, відкат у початковий стан, генерування Alert. |
| `CANARY_MONITORING` | `SLO_OK_WINDOW_EXPIRED` | `SCHEMA_CONTRACTING` | 100% трафіку на v2. Планування згортання застарілої схеми через N днів. |
| `CANARY_MONITORING` | `SLO_BREACH_DETECTED` | `ROLLBACK_TRAFFIC` | Скидання трафіку v2 до 0%, активація Feature Flag = `false`. |
| `ROLLBACK_TRAFFIC` | `TRAFFIC_SHIFT_DONE` | `ROLLBACK_SCHEMA` | Активація reconciliation воркера. Збереження схеми у фазі EXPAND. |
| `ROLLBACK_SCHEMA` | `RECONCILIATION_DONE` | `COMPLETED` | Сервіс функціонує на v1 зі збереженням 100% цілісності даних. |
| `SCHEMA_CONTRACTING` | `CMD_START_CONTRACT` | `COMPLETED` | Виконання руйнівного DDL `DROP COLUMN` для видалення застарілого поля. |

---

## 5. Специфікація кодів завершення процесів (Exit Code Matrix)

Утиліта `rollback-ctrl` повертає стандартизовані коди завершення (Exit Codes), що дозволяє CI/CD пайплайнам (GitHub Actions, GitLab CI, Jenkins) розрізняти тип збою та автоматично запускати відповідні сценарії відновлення.

### Деталізація кодів повернення та правил автоматичного реагування

- **`0` (`EX_OK`)**:
  - *Опис*: Операцію успішно виконано. Деплой або відкат пройшов у штатному режимі.
  - *Дія*: CI/CD пайплайн переходить до наступного кроку.

- **`1` (`EX_GENERAL_ERROR`)**:
  - *Опис*: Системна помилка (наприклад, відсутність вільної пам'яті, збій файлової системи).
  - *Дія*: Зупинка пайплайну, збереження системних логів, надсилання сповіщення у канал DevOps.

- **`2` (`EX_CONFIG_INVALID`)**:
  - *Опис*: Схема YAML-файла конфігурації містить синтаксичні помилки або некоректні типи полів.
  - *Дія*: Блокування деплою ДО виконання будь-яких дій у базі даних чи оркестраторі.

- **`3` (`EX_DDL_LOCK_TIMEOUT`)**:
  - *Опис*: Операція DDL не змогла отримати ексклюзивне блокування таблиці за відведений `lock_timeout`.
  - *Дія*: Автоматичне скасування транзакції, повторний запуск спроби через паузу (Exponential Backoff).

- **`4` (`EX_SLO_LATENCY_BREACH`)**:
  - *Опис*: Метрика P99 Latency канареєчних Pods перевищила поріг SLO.
  - *Дія*: **Автоматична активація аварійного відкату трафіку на v1** та вимкнення Feature Flag.

- **`5` (`EX_SLO_ERROR_RATE_BREACH`)**:
  - *Опис*: Відсоток HTTP 5xx помилок перевищив допустиму межу SLO.
  - *Дія*: **Автоматична активація аварійного відкату трафіку на v1** та вимкнення Feature Flag.

- **`6` (`EX_SCHEMA_NOT_REVERSIBLE`)**:
  - *Опис*: Автоматичний аналізатор SQL виявив заборонену руйнівну операцію (`DROP COLUMN`, `RENAME`).
  - *Дія*: Блокування Pull Request у CI/CD з вимогою переписати міграцію за патерном Expand-Contract.

- **`7` (`EX_TELEMETRY_UNAVAILABLE`)**:
  - *Опис*: Сервер Prometheus не відповідає на HTTP-запити понад 30 секунд.
  - *Дія*: Захисне припинення канареєчного розгортання та переведення трафіку назад на v1 через втрату спостережуваності.

- **`8` (`EX_KILL_SWITCH_FAILED`)**:
  - *Опис*: Не вдалося зв'язатися з сервісом конфігурації для змінення стану Feature Flag.
  - *Дія*: Перемикання трафіку на рівні API Gateway як запасний канал ізоляції.

- **`9` (`EX_RECONCILIATION_FAILED`)**:
  - *Опис*: Фоновий воркер відновлення даних після відкату завершився з помилкою.
  - *Дія*: Переведення інциденту у стан `REQUIRES_HUMAN_INTERVENTION` та виклик чергового база даних (DBA).

- **`10` (`EX_HEALTHCHECK_TIMEOUT`)**:
  - *Опис*: Нові контейнери v2 не змогли пройти проби готовності (`readinessProbe`) за відведений час.
  - *Дія*: Скасування запуску канарейки без зміни ваг роутингу.

### Таблиця кодів повернення

| Exit Code | Символьна назва | Опис і причина відмови | Автоматична дія контролера |
| :---: | :--- | :--- | :--- |
| `0` | `EX_OK` | Операція успішно завершена (деплой або відкат). | Завершення з успіхом. |
| `1` | `EX_GENERAL_ERROR` | Необроблена системна помилка або виняток. | Збереження логів, сповіщення інженера. |
| `2` | `EX_CONFIG_INVALID` | Помилка парсингу YAML-контракту міграції. | Зупинка розгортання до виконання DDL. |
| `3` | `EX_DDL_LOCK_TIMEOUT` | Перевищено таймаут блокування таблиці при DDL. | Скасування DDL, повтор через backoff. |
| `4` | `EX_SLO_LATENCY_BREACH` | P99 затримка перевищила допустимий поріг SLO. | **Автоматичний відкат трафіку на v1**. |
| `5` | `EX_SLO_ERROR_RATE_BREACH` | Частка 5xx помилок перевищила поріг SLO. | **Автоматичний відкат трафіку на v1**. |
| `6` | `EX_SCHEMA_NOT_REVERSIBLE` | Виявлено руйнівний DDL (DROP / RENAME). | Блокування деплою на етапі CI/CD. |
| `7` | `EX_TELEMETRY_UNAVAILABLE` | Prometheus API недоступний понад 30 секунд. | Безпечна зупинка канарейки, відкат. |
| `8` | `EX_KILL_SWITCH_FAILED` | Помилка з'єднання з сервісом Feature Flags. | Скидання трафіку через API Gateway. |
| `9` | `EX_RECONCILIATION_FAILED` | Фоновий воркер не зміг узгодити дані. | Переведення у стан ПОТРЕБУЄ_РУЧНОГО_АНАЛІЗУ. |
| `10` | `EX_HEALTHCHECK_TIMEOUT` | Pods v2 не пройшли readinessProbe за 120с. | Скасування запуску канарейки. |

---

## 6. Правила зворотності SQL DDL (SQL Safety Rules Reference)

Для забезпечення гарантії зворотності міграції всі операції з розширення схеми бази даних розбиваються на дві категорії: дозволені (безпечні) та заборонені (руйнівні).

### Пояснення альтернативних безпечних патернів

1. **Додавання полів зі значенням за замовчуванням (`DEFAULT`)**:
   У сучасних версіях PostgreSQL (11+) операція `ALTER TABLE ADD COLUMN ... DEFAULT val` є миттєвою (O(1)), оскільки значення за замовчуванням зберігається у системному каталозі `pg_attribute` без переписання блоків таблиці на диску. Це робить операцію повністю безпечною для відкату.

2. **Заміна `DROP COLUMN` на відкладений `CONTRACT`**:
   Видалення колонки робить відкат коду v1 неможливим, оскільки старий код вимагає наявності даного поля. Замість видалення поле зберігається недоторканим протягом 30 днів (фаза `EXPAND`). Очистка виконується окремим релізом у фазі `CONTRACT`.

3. **Заміна `RENAME COLUMN` на дзеркалювання через тригер**:
   Перейменування колонки розриває сумісність зі старим кодом. Безпечний патерн полягає у додаванні нової колонки з новим ім'ям та створенні двофазного тригера, який дзеркалює значення між старим і новим полем при кожному `INSERT` чи `UPDATE`.

### Таблиця правил зворотності SQL DDL

| Операція SQL DDL | Класифікація | Статус зворотності | Альтернативний безпечний патерн |
| :--- | :--- | :--- | :--- |
| `ALTER TABLE ADD COLUMN col NULL` | **БЕЗПЕЧНА** | 100% Reversible | Дозволено у фазі `EXPAND`. |
| `ALTER TABLE ADD COLUMN col DEFAULT val` | **БЕЗПЕЧНА** | 100% Reversible | Дозволено (без переписання всієї таблиці в PG11+). |
| `CREATE INDEX CONCURRENTLY` | **БЕЗПЕЧНА** | 100% Reversible | Створення індексу без блокування записів. |
| `ALTER TABLE DROP COLUMN col` | **ЗАБОРОНЕНА** | Destructive | Виконувати ЛИШЕ у фазі `CONTRACT` через 30 днів. |
| `ALTER TABLE RENAME COLUMN a TO b` | **ЗАБОРОНЕНА** | Destructive | Додати нове поле `b`, ввімкнути тригер дзеркалювання. |
| `ALTER TABLE ALTER COLUMN SET NOT NULL` | **ЗАБОРОНЕНА** | Destructive | Додати `CHECK (col IS NOT NULL) NOT VALID` + `VALIDATE`. |
| `DROP TABLE table_name` | **ЗАБОРОНЕНА** | Destructive | Перейменувати таблицю у `deprecated_table` у фазі CONTRACT. |

---

## 7. C++ Контракт інтерфейсу кілл-світчів (`IKillSwitchProvider`)

Для негайної зміни алгоритмічної поведінки додатку без його перезапуску сервіси реалізують C++20 інтерфейс `IKillSwitchProvider`. Інтерфейс гарантує виконання перевірки стану прапора за час < 1 мікросекунди завдяки кешуванню у логіці atomic memory barrier.

```cpp
// kill_switch_contract.hpp - C++20 контракт кілл-світча
#include <string_view>
#include <expected>
#include <chrono>

enum class FeatureFlagError {
    ProviderUnavailable,
    KeyNotFound,
    Timeout
};

class IKillSwitchProvider {
public:
    virtual ~IKillSwitchProvider() = default;

    // Атомарна перевірка стану прапора (час виконання < 1 мкс)
    [[nodiscard]] virtual bool is_feature_enabled(std::string_view flag_key, bool default_value = false) noexcept = 0;

    // Примусова атомарна деактивація прапора контролером відкату
    virtual std::expected<void, FeatureFlagError> emergency_disable_flag(std::string_view flag_key) = 0;
};
```

---

## 8. Специфікація Kubernetes Custom Resource Definition (CRD)

У Cloud-Native інфраструктурі стан зворотної міграції описується об'єктом Kubernetes CRD `ReversibleMigration`. Це дозволяє Kubernetes Operator виконувати функції автоматизованого контролера відкату безпосередньо всередині кластера:

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: reversiblemigrations.migration.progarch.io
spec:
  group: migration.progarch.io
  names:
    kind: ReversibleMigration
    listKind: ReversibleMigrationList
    plural: reversiblemigrations
    singular: reversiblemigration
  scope: Namespaced
  versions:
    - name: v1alpha1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                serviceName:
                  type: string
                targetVersion:
                  type: string
                maxP99LatencyMs:
                  type: number
```

---

## 9. Послідовність взаємодії компонентів під час розгортання та відкату

Наведеній діаграмі послідовності відповідає чіткий покроковий регламент взаємодії між пайплайном, контролером, проксі-сервером Envoy, Prometheus та базою даних PostgreSQL:

```
[CI/CD Pipeline]      [Migration Controller]       [Envoy Gateway]      [Prometheus]       [Database (PostgreSQL)]
       |                         |                        |                  |                        |
       |--- 1. Apply Expand ---->|                        |                  |                        |
       |    Migration            |------------------------------------------------------------------->| 2. ALTER TABLE ADD COLUMN
       |                         |<-------------------------------------------------------------------|    (lock_timeout='2s')
       |                         |                        |                  |                        |
       |--- 3. Start Canary ---->|                        |                  |                        |
       |                         |--- 4. Set Weight 5% -->|                  |                        |
       |                         |                        |                  |                        |
       |                         |--- 5. Query Metrics (every 5s) ---------->|                        |
       |                         |<-- 6. P99=185ms (BREACH!) ----------------|                        |
       |                         |                        |                  |                        |
       |                         |=== 7. EXECUTE AUTOMATED ROLLBACK ===      |                        |
       |                         |--- 8. Set Weight 0% -->|                  |                        |
       |                         |--- 9. Kill Switch OFF->|                  |                        |
       |<-- 10. Exit Code 4 -----|                        |                  |                        |
```

---

## 10. Інтеграція з OpenTelemetry та поширення траси відкату

Для наскрізного аналізу інцидентів у розподілених системах контролер відкату збагачує контекст розподіленого простеження OpenTelemetry (W3C Trace Context / `traceparent`) специфічними тегами:

1. **`migration.id`**: Унікальний ідентифікатор сесії розгортання (`mig-20260818-001`).
2. **`migration.phase`**: Поточний стан кінцевого автомата (`EXPAND`, `CANARY_MONITORING`, `ROLLBACK_TRAFFIC`).
3. **`migration.rollback_reason`**: Код причини спрацювання відкату (`ERR_SLO_LATENCY_BREACH`).
4. **`migration.rollback_duration_ms`**: Час виконання перемикання трафіку у мілісекундах.

Завдяки цим атрибутам інженери можуть у системі Jaeger або Grafana Tempo в один клік відфільтрувати всі корисні запити користувачів, які пройшли через канареєчний вузол у момент аварії.

---

## 11. Регламентний чек-лист перевірки контракту міграції

Перед допуском Pull Request із міграцією схеми до виконання у виробничому середовищі інженерна команда зобов'язана підтвердити відповідність контракту за наступними пунктами:

1. [ ] Файл `migration-contract.v1.yaml` пройдено через валідатор синтаксису YAML та інваріантів JSONSchema.
2. [ ] Усі SQL DDL скрипти фази `EXPAND` є строго зворотними і не містять руйнівних операцій `DROP` або `RENAME`.
3. [ ] Усі SQL DDL скрипти містять директиву `SET lock_timeout = '2s'`.
4. [ ] Пороги затримки P99 та відсотка 5xx помилок у блоці `health_gate` узгоджені з офіційними SLO сервісу.
5. [ ] Спрацювання кілл-світча Feature Flag протестовано у тестовому середовищі без перезапуску Pods додатку.

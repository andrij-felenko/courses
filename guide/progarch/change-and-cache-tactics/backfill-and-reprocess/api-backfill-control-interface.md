# Специфікація API управління та контракт спостережності бекфіл-процесу

Ця вставка містить формальний контракт системного API та метрик моніторингу для інфраструктурного рушія бекфілу та репроцесингу. Інтерфейс призначений для інтеграції з панелями операційного управління (Internal Admin Portal), системами автоматичного розгортання (CI/CD Pipelines) та автоматизованими оркестраторами інфраструктури (Kubernetes Operators, Airflow DAGs).

---

## 1. Архітектура поверхні управління та модель стану

Управління бекфіл-процесом здійснюється за протоколом HTTP/REST із використанням JSON для тіла запитів та відповідей. Усі мутуючі операції вимагають передачі заголовка ідемпотентності `Idempotency-Key` для запобігання повторному виконанню однакових команд при мережевих збоях.

### 1.1 Детальний аналіз скінченного автомата станів (State Machine Invariants)

Кожне бекфіл-завдання (`Backfill Job`) у системі проходить чітко визначений життєвий цикл, регламентований скінченним автоматом станів. Автомат гарантує строго впорядковані переходи між станами й унеможливлює невалідні операційні дії (наприклад, спробу відновлення вже завершеного завдання чи зміну конфігурації у скасованому стані).

```
[ PENDING ] ---> [ RUNNING ] <---> [ PAUSED ]
                     |
                     +------------> [ COMPLETED ]
                     |
                     +------------> [ FAILED ]
                     |
                     +------------> [ CANCELLED ]
```

Інваріанти та інженерний зміст кожного стану:

1. **PENDING (Очікування виконання):**
   Завдання успішно створене в системі, його конфігурацію перевірено на валідність (перевірено наявність B-Tree індексу на курсорному полі, монотонність первинного ключа та доступність сховища контрольних точок). На цьому етапі worker-вузли ще не відкривали транзакцій у СУБД.

2. **RUNNING (Активне виконання):**
   Завдання прийнято в обробку первинним worker-вузлом. Рушій у циклі вибирає чанки записів за курсором, розраховує нові значення, виконує атомарні оновлення та зафіксовує контрольні точки. У цьому стані система постійно вимірює затримку p99 СУБД та затримку реплікації.

3. **PAUSED (Тимчасова зупинка):**
   Виконання бекфілу призупинено оператором через REST API або автоматично через спрацьовування захисного запобіжника (Circuit Breaker). У даному стані фонові запити до СУБД повністю припиняються, а поточна позиція курсора `last_processed_id` зберігається у Checkpoint Store. Обробку можна відновити без втрати прогресу.

4. **COMPLETED (Успішне завершення):**
   Термінальний стан. Рушій пройшов весь заданий діапазон записів (`last_processed_id >= max_target_id`), усі контрольні точки зафіксовано, а лічильник залишкових записів дорівнює нулю. Зміна конфігурації чи повторний запуск із цього стану заборонені.

5. **FAILED (Фатальний збій):**
   Термінальний стан, у який система переходить у разі перевищення порогу помилок у Dead Letter Queue (DLQ), втрати мережевого зв'язку із СУБД або падіння вузла без можливості автовідновлення. Вимагає втручання інженера для розслідування причин та ручного скидання.

6. **CANCELLED (Скасування оператором):**
   Термінальний стан, викликаний примусовою командою скасування. Усі ресурси (пули з'єднань, фонові потоки) вивільняються, а підсумковий звіт заноситься в аудит-лог.

---

## 2. Формальна специфікація REST API

### 2.1 Створення та запуск нового бекфіл-завдання

Ендпойнт призначений для реєстрації нового завдання у системі. Клієнт надсилає детальні параметри чанкінгу, швидкості та порогів безпеки.

```http
POST /api/v1/backfill/jobs HTTP/1.1
Host: infra-control.internal.net
Content-Type: application/json
Idempotency-Key: 7b9e4a12-8c3d-4e5f-9a1b-2c3d4e5f6a7b

{
  "job_name": "backfill_user_discount_v2",
  "target_table": "orders",
  "cursor_field": "id",
  "start_cursor": 1,
  "end_cursor": 50000000,
  "batch_size": 2500,
  "rate_limit_per_sec": 1000,
  "max_allowed_db_p99_latency_ms": 35,
  "max_allowed_replication_lag_sec": 5,
  "dlq_max_error_percentage": 0.5,
  "dry_run": false
}
```

Детальний розбір семантики полів запиту:
- `job_name`: унікальний системний ідентифікатор бекфілу для аудиту та групування метрик у Prometheus.
- `target_table`: назва цільової таблиці в реляційній СУБД, над якою виконується фонова міграція.
- `cursor_field`: назва колонки первинного ключа. Поле повинно бути строго монотонним (`BIGINT` автоінкремент, `ULID` або `TSID`).
- `start_cursor` / `end_cursor`: межі діапазону обробки. Дозволяють розбивати великий бекфіл на кілька паралельних діапазонів для різних worker-вузлів.
- `batch_size`: кількість записів, що зчитується та оновлюється в межах однієї SQL-транзакції.
- `max_allowed_db_p99_latency_ms`: критичний поріг затримки СУБД. При його перевищенні рушій вмикає експоненційний відступ.
- `dlq_max_error_percentage`: максимально припустимий відсоток пошкоджених записів. При перевищенні завдання переходить у стан `FAILED`.

#### Відповідь успішного створення (202 Accepted):

```http
HTTP/1.1 202 Accepted
Content-Type: application/json
Location: /api/v1/backfill/jobs/job_984f1a2b

{
  "job_id": "job_984f1a2b",
  "status": "PENDING",
  "created_at": "2026-08-18T10:00:00Z",
  "estimated_total_records": 50000000,
  "checkpoint": {
    "last_processed_id": 0,
    "processed_count": 0,
    "failed_count": 0
  },
  "links": {
    "self": "/api/v1/backfill/jobs/job_984f1a2b",
    "pause": "/api/v1/backfill/jobs/job_984f1a2b/pause",
    "metrics": "/api/v1/backfill/jobs/job_984f1a2b/metrics"
  }
}
```

---

### 2.2 Отримання детального стану виконання (Polling & Observability Endpoint)

Даний метод надає повний зріз оперативних метрик, поточного прогресу та обчисленого прогнозованого часу завершення (ETA).

```http
GET /api/v1/backfill/jobs/job_984f1a2b HTTP/1.1
Host: infra-control.internal.net
```

#### Відповідь стану (200 OK):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "job_id": "job_984f1a2b",
  "status": "RUNNING",
  "started_at": "2026-08-18T10:00:05Z",
  "elapsed_time_seconds": 3600,
  "progress": {
    "start_cursor": 1,
    "end_cursor": 50000000,
    "current_cursor": 18250000,
    "percentage_completed": 36.5,
    "processed_records": 18250000,
    "failed_records": 12,
    "current_throughput_eps": 985.4,
    "eta_seconds": 32220
  },
  "operational_metrics": {
    "db_p99_latency_ms": 14.2,
    "replica_lag_seconds": 0.8,
    "active_sleep_delay_ms": 150,
    "circuit_breaker_status": "CLOSED"
  }
}
```

Розбір ключових показників прогресу:
- `current_throughput_eps`: середня кількість оброблених елементів на секунду (Elements Per Second) за останнє 5-хвилинне вікно.
- `eta_seconds`: спрогнований залишок часу обробки, розрахований як `(end_cursor - current_cursor) / current_throughput_eps`.
- `active_sleep_delay_ms`: поточна затримка між чанками, розрахована адаптивним регулятором на основі навантаження бази.

---

### 2.3 Динамічне виправлення конфігурації під час виконання (Hot Config Patch)

Запит дозволяє дежурному інженеру або автоматичному скрипту коригувати параметри швидкості прямо під час обробки без зупинки процесу. Це особливо важливо під час пікових годин бізнес-навантаження.

```http
PATCH /api/v1/backfill/jobs/job_984f1a2b/config HTTP/1.1
Host: infra-control.internal.net
Content-Type: application/json

{
  "batch_size": 1000,
  "rate_limit_per_sec": 500,
  "max_allowed_db_p99_latency_ms": 25
}
```

#### Відповідь на зміну конфігурації (200 OK):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "job_id": "job_984f1a2b",
  "applied_config": {
    "batch_size": 1000,
    "rate_limit_per_sec": 500,
    "max_allowed_db_p99_latency_ms": 25,
    "updated_at": "2026-08-18T11:00:00Z"
  }
}
```

---

### 2.4 Тимчасова зупинка та відновлення (Pause & Resume Control)

Метод призупиняє обробку записів, гарантуючи фіксацію останнього чанку у сховищі контрольних точок.

```http
POST /api/v1/backfill/jobs/job_984f1a2b/pause HTTP/1.1
Host: infra-control.internal.net
Content-Type: application/json

{
  "reason": "High load on master DB during promo campaign"
}
```

#### Відповідь (200 OK):

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "job_id": "job_984f1a2b",
  "status": "PAUSED",
  "paused_at": "2026-08-18T11:05:00Z",
  "saved_checkpoint_cursor": 18250000
}
```

Для відновлення виконання надсилається запит:

```http
POST /api/v1/backfill/jobs/job_984f1a2b/resume HTTP/1.1
Host: infra-control.internal.net
```

---

### 2.5 Оформлення помилок за стандартом RFC 7807 Problem Details

Усі відмови та помилки валідації API оформлюються у відповідності до специфікації RFC 7807 (`application/problem+json`). Це надає машинно-зчитувані діагностичні коди та детальний опис проблеми для інженерів.

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json

{
  "type": "https://infra-control.internal.net/errors/invalid-cursor-field",
  "title": "Invalid Cursor Field Selection",
  "status": 422,
  "detail": "Target field 'uuid_id' of type UUIDv4 is not monotonically ordered. Keyset pagination requires monotonically increasing sequential fields.",
  "instance": "/api/v1/backfill/jobs/job_984f1a2b",
  "invalid_params": [
    {
      "name": "cursor_field",
      "reason": "UUIDv4 index causes B-Tree page split and random disk IO degradation."
    }
  ]
}
```

---

## 3. Контракт спостережності Prometheus (Prometheus Observability Contract)

Рушій бекфілу експортує серію стандартних Prometheus метрик на ендпойнті `/metrics`. Усі метрики постачаються з обов'язковими мітками (labels): `job_id`, `target_table`, `environment`.

### 3.1 Деталізація метрик та формули розрахунку

1. **Лічильники (Counters):**
   - `backfill_processed_records_total{job_id, target_table, status="success|failed"}`
     Повний лічильник усіх оброблених записів. Дозволяє розраховувати пропускну здатність через PromQL: `rate(backfill_processed_records_total{status="success"}[5m])`.
   - `backfill_checkpoint_saves_total{job_id, target_table}`
     Кількість збережень контрольних точок у Checkpoint Store.
   - `backfill_circuit_breaker_trips_total{job_id, reason}`
     Кількість випадків спрацьовування автоматичного вимикача.

2. **Гістограми (Histograms):**
   - `backfill_batch_duration_seconds{job_id, target_table}`
     Гістограма тривалості виконання одного чанку. Квантиль 99% розраховується як: `histogram_quantile(0.99, sum(rate(backfill_batch_duration_seconds_bucket[5m])) by (le))`.
   - `backfill_adaptive_backoff_delay_seconds{job_id}`
     Розподіл пауз, розрахованих адаптивним регулятором.

3. **Гауси (Gauges):**
   - `backfill_current_cursor_position{job_id, target_table}`
     Поточна позиція курсора в історії.
   - `backfill_progress_percentage{job_id}`
     Відсоток виконання бекфіл-завдання.
   - `backfill_target_db_p99_latency_seconds{job_id}`
     Поточна виміряна p99 затримка СУБД.
   - `backfill_replication_lag_seconds{job_id, replica_host}`
     Затримка вичитання журналів на ведених репліках.

---

## 4. Операційний Runbook та сценарії швидкого реагування

При виникненні аварійних ситуацій черговий інженер дотримується регламенту операційного Runbook:

1. **Спрацьовування алера BackfillHighFailureRate:**
   - Перевірити записи в Dead Letter Queue через API: `GET /api/v1/backfill/jobs/{id}/dlq`.
   - З'ясувати причинний тип винятку (невалідний JSON, збій привілеїв, порушення зовнішнього ключа).
   - Якщо помилки системні (наприклад, помилка у коді обчислення v2), поставте завдання на паузу через `POST /jobs/{id}/pause` та розгорніть хотфікс.

2. **Спрацьовування алера BackfillHighDbLatency:**
   - Оцінити p99 затримку основної СУБД та довжину черг очікування блокувань.
   - Зменшити розмір батчу та пропускну здатність через `PATCH /jobs/{id}/config` (`batch_size = 500`, `rate_limit_per_sec = 200`).
   - За потреби збільшити паузу адаптивного регулятора.

Цей контракт гарантує абсолютну прозорість, вимірюваність та повну операційну керованість фонових бекфіл-процесів у продакшн-середовищах будь-якого масштабу.

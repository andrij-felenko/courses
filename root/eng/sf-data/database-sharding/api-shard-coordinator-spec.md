# 📋 Специфікація інтерфейсу координатора шардингу: топологія, розщеплення діапазонів та лізи маршрутизації

Специфікація визначає формальний протокол взаємодії площини управління (Control Plane) та площини даних (Data Plane) розподіленої шардованої СКБД. Вона регламентує схему зберігання метаданих топології кластера, скінченний автомат станів фізичних шардів, REST-ендпоїнти координатора для динамічного розщеплення діапазонів даних (Online Shard Splitting), моніторинг лагу реплікації CDC та механізм захисту від розщеплення мозку за допомогою фенсингових токенів і ліз маршрутизації.

## 1. Архітектурні засади площини управління

У шардованій системі типу Shared-Nothing координатор виконує роль централізованого арбітра топології. Його головна задача — забезпечити, щоб усі маршрутизатори (Stateless Routers / Proxies) мали узгоджене бачення того, який фізичний вузол відповідає за кожен конкретний діапазон ключів, та унеможливити ситуацію подвійного запису (Split-Brain) під час зміни конфігурації кластера.

Координатор не бере участі в обробці користувацьких SQL-запитів і не перебуває на гарячому шляху читання та запису. Він функціонує як зовнішній контролер, який зберігає свій стан у розподіленому реєстрі консенсусу (etcd або Consul) та сповіщає проксі-шар про зміни топології через довготривалі gRPC-стріми або HTTP-опитування з умовними заголовками.

```
┌────────────────────────────────────────────────────────────────────────┐
│               ПЛОЩИНА УПРАВЛІННЯ (Control Plane Coordinator)           │
│                                                                        │
│  ┌───────────────────────┐         ┌────────────────────────────────┐  │
│  │   Raft / etcd Store   │ ◄─────► │   Shard Coordinator Daemon     │  │
│  │  /database/topology   │         │  State Machine & Split Engine  │  │
│  └───────────────────────┘         └───────────────┬────────────────┘  │
└────────────────────────────────────────────────────┼───────────────────┘
                                                     │ Watch Stream
                                                     ▼ (Topology Events)
┌────────────────────────────────────────────────────────────────────────┐
│               ПЛОЩИНА ДАНИХ (Data Plane Routing Layer)                 │
│                                                                        │
│  ┌───────────────────────┐         ┌────────────────────────────────┐  │
│  │   Router / Proxy 1    │         │   Router / Proxy 2             │  │
│  │  In-Memory Shard Map  │         │  In-Memory Shard Map           │  │
│  └───────────┬───────────┘         └───────────────┬────────────────┘  │
└──────────────┼─────────────────────────────────────┼───────────────────┘
               ▼                                     ▼
      Фізичні шарди (Shard-01)              Фізичні шарди (Shard-02)
```

## 2. Модель даних топології кластера (Topology Schema)

Топологія кластера є строго типізованим версійованим документом, який зберігається у реєстрі консенсусу за ключем `/database/topology/v1`. Документ описує повний набір фізичних вузлів, їхні адреси, поточні ролі (Primary/Replica) та мапінг числових діапазонів простору ключів.

### JSON-схема документу топології

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ClusterTopologySpec",
  "type": "object",
  "required": ["version", "generation", "sharding_strategy", "shards", "ranges"],
  "properties": {
    "version": {
      "type": "string",
      "description": "Семантична версія схеми топології",
      "example": "1.4.0"
    },
    "generation": {
      "type": "integer",
      "minimum": 1,
      "description": "Монотонно зростаючий лічильник змін топології (Fencing Token)",
      "example": 1048
    },
    "sharding_strategy": {
      "type": "string",
      "enum": ["RANGE", "HASH_RING", "DIRECTORY_LOOKUP"],
      "example": "RANGE"
    },
    "lease_ttl_ms": {
      "type": "integer",
      "description": "Час життя лізи маршрутизатора в мілісекундах",
      "default": 5000
    },
    "shards": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/ShardDefinition"
      }
    },
    "ranges": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/KeyRangeMapping"
      }
    }
  },
  "$defs": {
    "ShardDefinition": {
      "type": "object",
      "required": ["shard_id", "state", "primary_endpoint", "replicas"],
      "properties": {
        "shard_id": {
          "type": "string",
          "example": "shard-04"
        },
        "state": {
          "type": "string",
          "enum": ["ONLINE", "READ_ONLY", "SPLITTING", "MIGRATING", "DRAINING", "OFFLINE"]
        },
        "primary_endpoint": {
          "type": "string",
          "example": "10.240.10.14:3306"
        },
        "replicas": {
          "type": "array",
          "items": { "type": "string" },
          "example": ["10.240.10.15:3306", "10.240.10.16:3306"]
        },
        "weight": {
          "type": "integer",
          "default": 100
        }
      }
    },
    "KeyRangeMapping": {
      "type": "object",
      "required": ["range_id", "start_key_hex", "end_key_hex", "target_shard_id"],
      "properties": {
        "range_id": {
          "type": "string",
          "example": "rng-004-a"
        },
        "start_key_hex": {
          "type": "string",
          "pattern": "^[0-9A-Fa-f]+$",
          "example": "40000000"
        },
        "end_key_hex": {
          "type": "string",
          "pattern": "^[0-9A-Fa-f]+$",
          "example": "7FFFFFFF"
        },
        "target_shard_id": {
          "type": "string",
          "example": "shard-04"
        }
      }
    }
  }
}
```

### Семантика полів схеми топології

1. **`generation` (ціле число, монотонне):** лічильник покоління конфігурації. Будь-яка зміна в складі шардів, адресах вузлів або межах діапазонів інкрементує це число строго на одиницю. Маршрутизатори передають це значення в службових заголовках запитів до фізичних баз. Якщо база виявляє, що запит прийшов із застарілим `generation`, транзакція негайно відхиляється з помилкою `STALE_TOPOLOGY_GENERATION`, що унеможливлює фантомні записи від ізольованих проксі.
2. **`lease_ttl_ms` (мілісекунди):** гарантований часовий інтервал, протягом якого маршрутизатор має право обслуговувати клієнтські запити за збереженою в пам'яті мапою без повторного опитування координатора. Якщо зв'язок із координатором втрачається довше ніж на `lease_ttl_ms`, маршрутизатор зобов'язаний заблокувати нові записи (Fail-Closed).
3. **`start_key_hex` та `end_key_hex` (шістнадцятковий рядок):** межі діапазону ключів у шістнадцятковому представленні. Діапазон інтерпретується як напівінтервал `[start_key_hex, end_key_hex)`. Множина всіх діапазонів зобов'язана покривати весь простір без дірок та перекриттів.

## 3. Скінченний автомат станів шарду (Shard State Machine)

Кожен фізичний шард у системі має чітко визначений життєвий цикл. Зміна стану ініціюється виключно координатором кластера в ході виконання регламентних процедур або реакції на аварії.

| Стан | Запис (`W`) | Читання (`R`) | Опис режиму та інженерні гарантії |
| :--- | :---: | :---: | :--- |
| `ONLINE` | ✅ Дозволено | ✅ Дозволено | Штатний робочий режим. Приймає всі точкові та віялові запити. Здійснює локальне збереження транзакцій у WAL. |
| `SPLITTING` | ✅ Дозволено | ✅ Дозволено | Шард перебуває в процесі онлайн-розщеплення. Нові записи фіксуються в локальній базі та паралельно передаються в буфер CDC-стрімінгу для копіювання на нові дочірні шарди. |
| `READ_ONLY` | ❌ Заборонено | ✅ Дозволено | Шард заблоковано для нових записів на час фінального перемикання топології (Cutover). Будь-які спроби `INSERT/UPDATE` відхиляються помилкою `SHARD_READ_ONLY`. |
| `MIGRATING` | ✅ Дозволено | ✅ Дозволено | Дані діапазону переносяться на інший фізичний хост через подвійний запис або стрімінг реплікації. |
| `DRAINING` | ❌ Заборонено | ❌ Заборонено | Старий шард очікує завершення активних тривалих транзакцій та закриття пулів з'єднань від маршрутизаторів. Нові з'єднання не приймаються. |
| `OFFLINE` | ❌ Заборонено | ❌ Заборонено | Шард виведено з експлуатації. Дискові ресурси можуть бути очищені або передані під архівне зберігання. |

### Правила та інваріанти переходів між станами

1. **`ONLINE → SPLITTING`:** ініціюється автоматично при досягненні порогового розміру даних (наприклад, > 4 ТБ) або за командою адміністратора. Вимагає успішної реєстрації двох нових порожніх цільових шардів у стані `OFFLINE`.
2. **`SPLITTING → READ_ONLY`:** дозволений лише тоді, коли відставання реплікації CDC між батьківським і дочірніми шардами становить менше 50 мілісекунд (`cdc_lag_ms < 50`).
3. **`READ_ONLY → DRAINING`:** виконується відразу після успішної фіксації нового `generation` у реєстрі etcd та отримання підтверджень про перемикання трафіку від більшості маршрутизаторів.
4. **`DRAINING → OFFLINE`:** виконується після того, як лічильник активних клієнтських з'єднань на старому шарді досягає нуля або після вичерпання таймауту граційного дренажу (`drain_timeout_sec = 60`).

## 4. Специфікація REST API координатора (Control Plane Endpoints)

Усі HTTP-запити до координатора здійснюються через захищене з'єднання TLS із передачею службового токена в заголовку `Authorization: Bearer <token>`.

### 4.1 Отримання поточної топології (Get Topology)

`GET /api/v1/topology`

Ендпоїнт використовується маршрутизаторами для первинного завантаження топології або для синхронізації після розриву зв'язку.

**Заголовки запиту:**
- `If-None-Match: "1048"` — передає поточний відомий маршрутизатору номер генерації. Якщо на координаторі покоління не змінилося, повертається статус `304 Not Modified` без тіла відповіді, що заощаджує мережевий трафік.

**Приклад відповіді (`200 OK`):**
```json
{
  "version": "1.4.0",
  "generation": 1048,
  "timestamp": "2026-08-20T01:45:00Z",
  "sharding_strategy": "RANGE",
  "lease_ttl_ms": 5000,
  "shards": [
    {
      "shard_id": "shard-01",
      "state": "ONLINE",
      "primary_endpoint": "10.0.1.10:3306",
      "replicas": ["10.0.1.11:3306", "10.0.1.12:3306"],
      "weight": 100
    },
    {
      "shard_id": "shard-02",
      "state": "ONLINE",
      "primary_endpoint": "10.0.2.10:3306",
      "replicas": ["10.0.2.11:3306"],
      "weight": 100
    }
  ],
  "ranges": [
    {
      "range_id": "rng-01",
      "start_key_hex": "00000000",
      "end_key_hex": "7FFFFFFF",
      "target_shard_id": "shard-01"
    },
    {
      "range_id": "rng-02",
      "start_key_hex": "80000000",
      "end_key_hex": "FFFFFFFF",
      "target_shard_id": "shard-02"
    }
  ]
}
```

---

### 4.2 Ініціація онлайн-розщеплення шарду (Split Shard)

`POST /api/v1/shards/{shard_id}/split`

Запускає фонову процедуру розщеплення вказаного шарду на два нових дочірніх вузли.

**Параметри шляху:**
- `shard_id` (string, обов'язковий) — ідентифікатор цільового шарду (наприклад, `shard-01`).

**Тіло запиту (`application/json`):**
```json
{
  "split_key_hex": "40000000",
  "target_shards": [
    {
      "shard_id": "shard-01a",
      "primary_endpoint": "10.0.1.20:3306",
      "replicas": ["10.0.1.21:3306"]
    },
    {
      "shard_id": "shard-01b",
      "primary_endpoint": "10.0.1.30:3306",
      "replicas": ["10.0.1.31:3306"]
    }
  ],
  "max_allowed_lag_ms": 50,
  "backfill_rate_limit_mb_s": 250
}
```

**Опис параметрів:**
- `split_key_hex`: шістнадцятковий ключ, який розрізає існуючий діапазон батьківського шарду на дві половини: `[start_key, split_key)` для першого дочірнього шарду та `[split_key, end_key)` для другого;
- `target_shards`: мережеві адреси нових інстансів баз даних, які вже ініціалізовані й очікують на заливку даних;
- `backfill_rate_limit_mb_s`: обмеження швидкості копіювання історичного снапшота для захисту дисків батьківського шарду від перевантаження.

**Приклад відповіді (`202 Accepted`):**
```json
{
  "task_id": "split_job_99812",
  "status": "INITIALIZING_BACKFILL",
  "source_shard": "shard-01",
  "new_ranges": [
    { "range_id": "rng-01a", "start_key_hex": "00000000", "end_key_hex": "3FFFFFFF", "target_shard_id": "shard-01a" },
    { "range_id": "rng-01b", "start_key_hex": "40000000", "end_key_hex": "7FFFFFFF", "target_shard_id": "shard-01b" }
  ],
  "estimated_duration_sec": 420
}
```

---

### 4.3 Моніторинг прогресу та лагу реплікації (Get Split Status)

`GET /api/v1/shards/{shard_id}/split-status`

Повертає поточний статус виконання фонового копіювання та точний розмір відставання CDC-потоку.

**Приклад відповіді (`200 OK`):**
```json
{
  "task_id": "split_job_99812",
  "phase": "CDC_CATCHUP",
  "source_shard": "shard-01",
  "backfill": {
    "status": "COMPLETED",
    "total_bytes_copied": 4294967296000,
    "duration_sec": 382
  },
  "cdc_replication": {
    "source_wal_position": 98451200,
    "target_a_applied_position": 98450100,
    "target_b_applied_position": 98450050,
    "lag_bytes": 1150,
    "lag_ms": 14.2
  },
  "ready_for_cutover": true
}
```

---

### 4.4 Атомарне перемикання маршрутизації (Execute Cutover)

`POST /api/v1/topology/cutover`

Критична транзакційна дія площини управління. Виконує субмілісекундне перемикання трафіку з батьківського шарду на дочірні.

**Тіло запиту (`application/json`):**
```json
{
  "task_id": "split_job_99812",
  "expected_generation": 1048,
  "max_cutover_pause_ms": 500
}
```

**Алгоритм виконання на координаторі:**
1. Перевірка, що поточне покоління кластера дорівнює `expected_generation` (Optimistic Concurrency Control);
2. Надсилання команди `SET GLOBAL read_only = ON` на батьківський `shard-01`;
3. Очікування застосування залишку CDC-потоку на `shard-01a` та `shard-01b` до повного нульового лагу (`lag_bytes == 0`);
4. Атомарний запис оновленої мапи діапазонів в etcd із генерацією `generation = 1049`;
5. Відправка події `TOPOLOGY_UPDATED` усім активним маршрутизаторам.

**Приклад відповіді (`200 OK`):**
```json
{
  "status": "CUTOVER_SUCCESSFUL",
  "new_generation": 1049,
  "cutover_duration_ms": 6.8,
  "retired_shards": ["shard-01"],
  "active_shards": ["shard-01a", "shard-01b"],
  "effective_timestamp": "2026-08-20T01:52:14.120Z"
}
```

## 5. Контракт потоку подій (gRPC Streaming Watch)

Для забезпечення мінімальної затримки поширення оновлень топології маршрутизатори утримують постійне двонаправлене gRPC-з'єднання з координатором.

```protobuf
syntax = "proto3";

package database.coordinator.v1;

service TopologyService {
  // Постійний потік оновлень топології
  rpc WatchTopology (WatchRequest) returns (stream TopologyEvent);
  
  // Періодичний сигнал працездатності від роутера
  rpc Heartbeat (RouterHeartbeat) returns (HeartbeatResponse);
}

message WatchRequest {
  string router_id = 1;
  uint64 current_generation = 2;
}

message TopologyEvent {
  enum EventType {
    EVENT_TYPE_UNSPECIFIED = 0;
    TOPOLOGY_UPDATED = 1;
    SHARD_DEGRADED = 2;
    FORCE_DISCONNECT = 3;
  }

  EventType type = 1;
  uint64 generation = 2;
  bytes topology_payload_json = 3;
  string reason = 4;
}

message RouterHeartbeat {
  string router_id = 1;
  uint64 acknowledged_generation = 2;
  uint32 active_connections = 3;
  uint32 rps = 4;
}

message HeartbeatResponse {
  bool generation_synced = 1;
  uint64 latest_generation = 2;
}
```

## 6. Інваріанти безпеки та коди помилок

### Системні інваріанти цілісності
1. **Інваріант покриття (Total Range Coverage):** об'єднання всіх діапазонів `[start_key, end_key)` зобов'язане давати повний простір `[0x00000000, 0xFFFFFFFF]`. Жоден ключ не може залишитися без цільового шарду.
2. **Інваріант взаємного виключення (Disjoint Ranges):** перетин будь-яких двох активних діапазонів є порожньою множиною `R_i ∩ R_j = ∅` для `i ≠ j`.
3. **Фенсинг ліз (Lease Fencing Rule):** новий шард не може бути переведений у стан `ONLINE` на запис доти, доки не мине повний час `lease_ttl_ms` з моменту блокування старого шарду в `READ_ONLY`.

### Таблиця стандартних кодів помилок координатора

| HTTP Код | Внутрішній код помилки | Причина виникнення та спосіб усунення |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_SPLIT_KEY` | Запропонований ключ розщеплення виходить за межі діапазону батьківського шарду. |
| `409 Conflict` | `GENERATION_MISMATCH` | Версія топології змінилася паралельним процесом. Необхідно перезавантажити топологію через `GET /api/v1/topology`. |
| `412 Precondition Failed` | `CDC_LAG_TOO_HIGH` | Лаг реплікації перевищує допустимий ліміт для безпечного перемикання. Потрібно дати більше часу на доганяння змін. |
| `422 Unprocessable Entity` | `TARGET_SHARDS_NOT_READY` | Один із дочірніх вузлів недоступний або не відповідає вимогам конфігурації. |
| `504 Gateway Timeout` | `CUTOVER_TIMEOUT_EXCEEDED` | Батьківський шард не встиг підтвердити блокування записів за виділений ліміт `max_cutover_pause_ms`. |

## 7. Операційний регламент (Runbook) та метрики Prometheus

Для керування кластером у середовищі Kubernetes застосовується CLI-утиліта `shardctl`, яка транслює команди адміністратора у виклики REST API координатора.

### Приклади виконання типових операцій

1. **Запуск планового розщеплення шарду:**
```
$ shardctl split shard-03 --split-key 80000000 --target-a shard-03a:3306 --target-b shard-03b:3306
[INFO] Split job initialized: job_id=split_job_10492
[INFO] Phase 1: Snapshot backfill running (4.2 TB to copy)...
```

2. **Перевірка статусу та лагу реплікації:**
```
$ shardctl status split_job_10492
Phase: CDC_CATCHUP
Backfill: 100% [==============================] 4.2TB/4.2TB
CDC Lag: 12ms (1,420 bytes behind primary WAL)
Status: READY FOR CUTOVER
```

3. **Виконання фінального перемикання:**
```
$ shardctl cutover split_job_10492 --timeout 500ms
[INFO] Acquired global topology lease...
[INFO] Set shard-03 to READ_ONLY mode...
[INFO] CDC stream drained to 0 bytes in 3.1ms.
[INFO] Topology updated to generation 1050 in etcd.
[INFO] Broadcasted TOPOLOGY_UPDATED to 24 active routers.
[SUCCESS] Cutover completed successfully in 5.4ms.
```

### Метрики Prometheus для спостереження за координатором

- `coordinator_topology_generation_current`: поточний монотонний номер генерації кластера;
- `coordinator_split_job_duration_seconds`: гістограма загальної тривалості операцій розщеплення;
- `coordinator_cdc_lag_seconds{source_shard, target_shard}`: поточне відставання потоку захоплення змін у секундах;
- `coordinator_cutover_pause_duration_ms`: точний час блокування записів у мілісекундах під час фінального перемикання лізи;
- `coordinator_router_heartbeat_last_seen_seconds{router_id}`: час з моменту останнього пінгу від маршрутизатора;
- `coordinator_split_failures_total{reason}`: лічильник аварійно перерваних процедур розщеплення.

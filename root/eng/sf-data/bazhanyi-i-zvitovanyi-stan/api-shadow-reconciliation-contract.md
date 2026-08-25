# 📋 Специфікація протоколу та контракти синхронізації стану: Device Shadow, MQTT та gRPC API

Для надійної взаємодії між хмарними сервісами керування, клієнтськими додатками та віддаленими автономними вузлами необхідний суворий форматний і мережевий контракт. У цій специфікації визначено структуру документів цифрових двійників (Device Shadow), топіки та семантику протоколу MQTT, схему gRPC для контролерів узгодження та коди помилок оптимістичного блокування при виникненні конфліктів версій.

## Структура документа цифрового двійника (JSON Schema)

Документ стану складається з чотирьох обов'язкових кореневих об'єктів: `desired`, `reported`, `delta` та `metadata`. Окремим полем виступає цілочисельний монотонний лічильник `version`.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "DeviceShadowDocument",
  "type": "object",
  "required": ["state", "version", "timestamp"],
  "properties": {
    "state": {
      "type": "object",
      "required": ["desired", "reported"],
      "properties": {
        "desired": {
          "type": "object",
          "description": "Цільова специфікація параметрів, надіслана сервером/додатком",
          "additionalProperties": true
        },
        "reported": {
          "type": "object",
          "description": "Фактичний телеметричний стан сенсорів та регістрів пристрою",
          "additionalProperties": true
        },
        "delta": {
          "type": "object",
          "description": "Автоматично обчислювана сервером різниця (тільки для читання пристроєм)",
          "readOnly": true,
          "additionalProperties": true
        }
      }
    },
    "metadata": {
      "type": "object",
      "description": "Мітки часу оновлення кожного окремого атрибута",
      "properties": {
        "desired": { "type": "object" },
        "reported": { "type": "object" }
      }
    },
    "version": {
      "type": "integer",
      "minimum": 1,
      "description": "Монотонний лічильник версії документа для Optimistic Concurrency Control"
    },
    "timestamp": {
      "type": "integer",
      "description": "Час створення знімка стану в епосі UNIX (секунди)"
    },
    "clientToken": {
      "type": "string",
      "description": "Унікальний ідентифікатор запиту клієнта для дедуплікації"
    }
  }
}
```

## Ієрархія топіків MQTT та контракти повідомлень

Синхронізація стану між хмарним брокером та кінцевим вузлом здійснюється через набір зарезервованих системних топіків. Для кожного ідентифікатора пристрою `{thingName}` створюється власне дерево каналів:

| MQTT Топік | Напрямок | Призначення та семантика |
|---|---|---|
| `$aws/things/{thingName}/shadow/update` | Вузол / Клієнт → Брокер | Публікація оновлення `desired` або `reported` стану |
| `$aws/things/{thingName}/shadow/update/accepted` | Брокер → Вузол / Клієнт | Підтвердження успішного застосування змін і нова версія |
| `$aws/things/{thingName}/shadow/update/rejected` | Брокер → Вузол / Клієнт | Повідомлення про відхилення (конфлікт версій або невалідна схема) |
| `$aws/things/{thingName}/shadow/update/delta` | Брокер → Вузол (Push) | Асинхронне сповіщення про виявлений дрейф (`desired \ reported != ∅`) |
| `$aws/things/{thingName}/shadow/get` | Вузол / Клієнт → Брокер | Запит повного поточного знімка документа |
| `$aws/things/{thingName}/shadow/get/accepted` | Брокер → Вузол / Клієнт | Відповідь із повним документом стану та метаданими |
| `$aws/things/{thingName}/shadow/get/rejected` | Брокер → Вузол / Клієнт | Помилка зчитування (наприклад, тінь ще не створена) |
| `$aws/things/{thingName}/shadow/delete` | Клієнт → Брокер | Повне видалення документа цифрового двійника |

### 1. Запит на оновлення бажаного стану (Update Desired)
Клієнтський мобільний додаток або бекенд надсилає часткове оновлення цільового параметра. Незмінені поля не передаються. Для захисту від гонок оновлень передається очікувана поточна версія документа.

**Публікація в топік:** `$aws/things/pump-084/shadow/update`
```json
{
  "state": {
    "desired": {
      "target_flow_rate": 45.0,
      "valve_state": "OPEN"
    }
  },
  "version": 112,
  "clientToken": "req-98f2-4a11"
}
```

### 2. Автоматична генерація та доставка дельти (Delta Event)
Якщо після застосування оновлення поле `reported` не відповідає свіжому `desired`, брокер автоматично формує об'єкт дельти і надсилає його в топік підписки пристрою. Поле дельти містить виключно ті атрибути, де зафіксовано дрейф.

**Повідомлення в топіку:** `$aws/things/pump-084/shadow/update/delta`
```json
{
  "state": {
    "target_flow_rate": 45.0,
    "valve_state": "OPEN"
  },
  "metadata": {
    "target_flow_rate": { "timestamp": 1714568900 },
    "valve_state": { "timestamp": 1714568900 }
  },
  "timestamp": 1714568900,
  "version": 113
}
```

### 3. Звіт пристрою про застосування (Update Reported)
Після того як локальний контролер вузла перевірив датчики та повернув апаратний клапан у положення `OPEN`, він публікує звіт про фактичний стан. Після обробки цього повідомлення брокер оновлює `reported`, перераховує різницю — і оскільки `reported == desired`, топік `/delta` більше не генерує повідомлень.

**Публікація в топік:** `$aws/things/pump-084/shadow/update`
```json
{
  "state": {
    "reported": {
      "target_flow_rate": 45.0,
      "valve_state": "OPEN",
      "actual_flow_rate": 44.8,
      "internal_temp": 38.2
    }
  },
  "clientToken": "edge-ack-0042"
}
```

## Семантика злиття документів (JSON Merge Patch RFC 7396)

Оновлення стану в документах цифрових двійників підпорядковується правилам стандарту **JSON Merge Patch (RFC 7396)**. Це визначає точну поведінку при модифікації складних вкладених структур:

1. **Рекурсивне злиття об'єктів (Object Recursion):** якщо вхідний payload містить ключ, значенням якого є JSON-об'єкт, він не перезаписує весь батьківський вузол у базі, а рекурсивно об'єднується з наявними вкладеними полями.
2. **Атомарна заміна масивів (Array Replacement):** на відміну від об'єктів, списки та масиви не зливаються поелементно. Якщо вхідний документ містить масив `[1, 2]`, він повністю замінює попередній масив `[1, 2, 3, 4]`.
3. **Видалення ключів через `null` (Tombstones):** щоб видалити властивість із бажаного чи звітованого стану, клієнт передає ім'я ключа зі значенням `null`. Сервер видаляє цей ключ із документа та його метаданих.

```json
// Приклад вихідного стану
{
  "state": {
    "desired": { "network": { "ip": "10.0.0.5", "dhcp": true }, "alert": "HIGH" }
  }
}

// Запит на оновлення (Update Patch)
{
  "state": {
    "desired": { "network": { "dhcp": false }, "alert": null }
  }
}

// Результуючий стан після злиття
{
  "state": {
    "desired": { "network": { "ip": "10.0.0.5", "dhcp": false } }
  }
}
```

## Метадані атрибутів та пополярна фіксація часу (Per-Field Timestamps)

Брокер стану супроводжує кожен атрибут об'єкта `desired` та `reported` окремою міткою часу в блоці `metadata`. Це критично важливо для аудиту та аналізу конфліктів:

```json
{
  "metadata": {
    "desired": {
      "target_flow_rate": { "timestamp": 1714568900 },
      "valve_state": { "timestamp": 1714568850 }
    },
    "reported": {
      "target_flow_rate": { "timestamp": 1714568910 },
      "valve_state": { "timestamp": 1714568855 },
      "internal_temp": { "timestamp": 1714568910 }
    }
  }
}
```

Коли клієнт отримує документ, він може точно встановити вік кожного параметра. Якщо параметр `target_flow_rate` у звіті має мітку часу більшу, ніж у бажаному стані (`1714568910 > 1714568900`), система вважає цей атрибут успішно узгодженим і актуальним. Якщо ж мітка бажаного стану новіша за звітну, атрибут перебуває у стані виконання переходу (In-Flight Transition).

## Послідовність холодного старту та відновлення після збою (Cold-Start Lifecycle)

Коли віддалений пристрій вмикається після аварійного перезавантаження або тривалої втрати живлення, він не може довіряти кешованому в оперативній пам'яті стану. Протокол відновлення складається з таких обов'язкових фаз:

1. **Підписка на системні топіки (Subscription Phase):**
   - Підписатися на топік дельти: `$aws/things/{thingName}/shadow/update/delta`.
   - Підписатися на топік отримання знімка: `$aws/things/{thingName}/shadow/get/accepted` та `$aws/things/{thingName}/shadow/get/rejected`.
2. **Запит поточного еталону (Full State Fetch):**
   - Опублікувати порожнє повідомлення `{}` у топік `$aws/things/{thingName}/shadow/get`.
3. **Локальне узгодження (Local Reconciliation Step):**
   - З отриманого документа `get/accepted` витягти повні об'єкти `desired` та `reported`.
   - Зчитати поточний фізичний стан сенсорів і регістрів заліза.
   - Якщо фізичний стан не збігається зі звітованим у хмарі — опублікувати коригувальний `update reported`.
   - Обчислити локальну дельту між хмарним `desired` та реальним фізичним станом і запустити цикл узгодження.
4. **Перехід у черговий режим (Event-Driven Steady State):**
   - Обробляти нові події з топіка `/update/delta` по мірі їх надходження.

## Рівні обслуговування MQTT (QoS) та життєвий цикл токенів

При роботі через ненадійні бездротові мережі критично важливо правильно обрати рівень доставки повідомлень:

- **QoS 0 (At most once):** повідомлення відправляється без підтвердження доставки брокером. Використання QoS 0 для оновлення бажаного стану заборонено, оскільки втрата пакета призведе до непоміченого зависання системи в стані розбіжності. Допускається лише для високовольтної періодичної телеметрії, де втрата одного зрізу не критична.
- **QoS 1 (At least once):** обов'язковий стандарт для публікацій у топіки `/shadow/update`. Гарантує, що повідомлення дійде до брокера хоча б один раз. Оскільки можливе дублювання пакетів при повторних відправках, клієнт обов'язково передає поле `clientToken`. Брокер дедуплікує запити з однаковим токеном протягом короткого вікна ковзання (deduplication window).
- **QoS 2 (Exactly once):** у реальних розподілених IoT-системах практично не використовується через високий оверхед чотирифазного рукостискання (PUBREC/PUBREL/PUBCOMP), що викликає неприпустимі затримки на повільних стільникових каналах (2G/NB-IoT). Поєднання QoS 1 із вбудованою ідемпотентністю оновлення стану є значно надійнішим і дешевшим.

## Іменовані тіні (Named Shadows) для модульних систем

У складних індустріальних об'єктах один фізичний пристрій (наприклад, промисловий контролер) містить десятки незалежних модулів: підсистему живлення, драйвери приводів, модуль безпеки та мережевий шлюз. Об'єднання всіх параметрів в один монолітний документ спричиняє постійні конфлікти версій між незалежними сервісами.

Для ізоляції застосовуються **іменовані тіні (Named Shadows)**. Вони використовують розширене дерево топіків:

```
$aws/things/{thingName}/shadow/name/{shadowName}/update
$aws/things/{thingName}/shadow/name/{shadowName}/update/delta
$aws/things/{thingName}/shadow/name/{shadowName}/get
```

Кожна іменована тінь (`power_subsystem`, `motor_drive_01`, `diagnostics`) має власний незалежний документ, ізольовану історію версій `version` та окремий топік доставки дельти. Це дозволяє мікросервісам оновлювати свої підсистеми паралельно, не викликаючи відхилень запитів `409 Conflict`.

## Контракт gRPC для контролерів узгодження (Control Plane API)

У хмарних та серверних середовищах (наприклад, у Kubernetes Custom Resource Controllers або розподілених оркестраторах баз даних) синхронізація бажаного і звітованого стану виконується через високопродуктивні gRPC канали. Нижче наведено інтерфейс `ReconcilerService` на мові Protocol Buffers v3:

```protobuf
syntax = "proto3";

package controlplane.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/struct.proto";

// Сервіс узгодження розподіленого стану
service ReconcilerService {
  // Зчитування повного знімка стану ресурсу
  rpc GetResourceState(GetResourceStateRequest) returns (ResourceStateSnapshot);

  // Оновлення специфікації бажаного стану (Desired State)
  rpc UpdateDesiredState(UpdateDesiredStateRequest) returns (UpdateStateResponse);

  // Публікація фактичного статусу (Reported Status) від агента вузла
  rpc ReportStatus(ReportStatusRequest) returns (UpdateStateResponse);

  // Двонаправлений потік для миттєвого отримання подій дрейфу та оновлення статусу
  rpc StreamReconciliation(stream NodeStatusTelemetry) returns (stream DesiredStateDelta);
}

message ResourceIdentifier {
  string namespace = 1;
  string resource_name = 2;
  string cluster_id = 3;
}

message ResourceStateSnapshot {
  ResourceIdentifier id = 1;
  uint64 resource_version = 2;
  google.protobuf.Struct desired_spec = 3;
  google.protobuf.Struct reported_status = 4;
  google.protobuf.Struct computed_delta = 5;
  google.protobuf.Timestamp last_reconciled_at = 6;
}

message UpdateDesiredStateRequest {
  ResourceIdentifier id = 1;
  uint64 expected_version = 2; // Перевірка OCC (Optimistic Concurrency Control)
  google.protobuf.Struct desired_spec = 3;
  string caller_id = 4;
}

message ReportStatusRequest {
  ResourceIdentifier id = 1;
  google.protobuf.Struct reported_status = 2;
  google.protobuf.Timestamp observed_at = 3;
}

message UpdateStateResponse {
  bool success = 1;
  uint64 new_version = 2;
  ReconciliationStatus status = 3;
  string error_message = 4;
}

enum ReconciliationStatus {
  RECONCILIATION_STATUS_UNSPECIFIED = 0;
  RECONCILIATION_STATUS_SYNCHRONIZED = 1; // Desired == Reported
  RECONCILIATION_STATUS_DRIFT_DETECTED = 2; // Desired != Reported
  RECONCILIATION_STATUS_CONFLICT = 3;       // Помилка версії (OCC Conflict)
  RECONCILIATION_STATUS_ACTUATION_FAILED = 4;
}

message DesiredStateDelta {
  ResourceIdentifier id = 1;
  uint64 target_version = 2;
  google.protobuf.Struct delta_payload = 3;
}

message NodeStatusTelemetry {
  ResourceIdentifier id = 1;
  google.protobuf.Struct current_status = 2;
  google.protobuf.Timestamp timestamp = 3;
}
```

## Коди помилок та обробка конфліктів версій

Коли брокер або gRPC-сервер відхиляє спробу оновлення стану, він повертає стандартизовану структуру помилки в топік `/shadow/update/rejected` або gRPC Status Code:

```json
{
  "code": 409,
  "message": "Version conflict: provided version 112 does not match current document version 114",
  "clientToken": "req-98f2-4a11",
  "timestamp": 1714568905
}
```

| Код помилки | gRPC Еквівалент | Причина виникнення та правила відновлення клієнта |
|---|---|---|
| `400 Bad Request` | `INVALID_ARGUMENT` | Порушення JSON-схеми, невалідні типи даних або синтаксична помилка парсера. Клієнт не повинен повторювати запит без виправлення payload. |
| `404 Not Found` | `NOT_FOUND` | Запитуваний цифровий двійник або тінь пристрою не зареєстрована у реєстрі. Необхідно створити базовий ресурс. |
| `409 Conflict` | `ABORTED` | **Конфлікт оптимістичного блокування.** Версія, на яку спирався клієнт (`expected_version`), застаріла через паралельний запис іншого клієнта. **Дія клієнта:** виконати `GET`, зчитати новий `desired` стан версії `v_new`, перерахувати бізнес-правила та повторити запит із `version = v_new`. |
| `413 Payload Too Large` | `RESOURCE_EXHAUSTED` | Розмір документа або дельти перевищує ліміт (зазвичай 8 КБ для IoT тіней або 1.5 МБ для об'єктів etcd). Необхідно розбити конфігурацію на окремі підресурси. |
| `429 Too Many Requests` | `RESOURCE_EXHAUSTED` | Перевищено ліміт запитів до сховища стану (Rate Limiting). Клієнт повинен увімкнути експоненційний відкат із джитером. |
| `500 Server Error` | `INTERNAL` | Внутрішній збій бази даних сховища стану або розподіленого консенсусу. Клієнт повторює спробу через стандартний інтервал відкату. |

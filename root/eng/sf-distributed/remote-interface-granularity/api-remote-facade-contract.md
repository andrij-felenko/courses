# 📋 Специфікація контрактів віддаленого фасаду та пакетних схем

При переході від дрібнозернистого до грубозернистого інтерфейсу змінюється не лише кількість мережевих пакетів, а й сам формат і семантика контракту взаємодії. Дрібнозернистий інтерфейс описує методи для атомарної роботи з окремими полями або простими властивостями сутностей, тоді як грубозернистий фасад оперує складними агрегатами, композитними DTO та пакетними структурами з явною підтримкою часткових відмов, версіонування та вибіркової проєкції даних.

Нижче наведено формальну специфікацію обох підходів мовою Protocol Buffers (v3) та JSON Schema, а також детальний аналіз правил сумісності, двійкового кодування та обробки крайових випадків.

---

### 1. Дрібнозернистий контракт (Fine-Grained / Chatty API)

У дрібнозернистій моделі кожна дія або запит атрибута вимагає окремого методу в описі сервісу. Щоб завантажити профіль користувача, його поштову адресу, історію замовлень, деталі конкретної покупки та рівень персональної знижки, клієнт зобов'язаний оголосити та послідовно викликати п'ять незалежних віддалених процедур:

```protobuf
syntax = "proto3";

package commerce.finegrained.v1;

message GetUserProfileRequest {
  string user_id = 1;
}

message UserProfileResponse {
  string user_id = 1;
  string full_name = 2;
  string email = 3;
}

message GetUserAddressRequest {
  string user_id = 1;
}

message UserAddressResponse {
  string street = 1;
  string city = 2;
  string postal_code = 3;
  string country = 4;
}

message GetUserOrdersRequest {
  string user_id = 1;
  int32 limit = 2;
}

message UserOrdersResponse {
  repeated string order_ids = 1;
}

message GetOrderDetailsRequest {
  string order_id = 1;
}

message OrderDetailsResponse {
  string order_id = 1;
  int64 total_cents = 2;
  string status = 3;
}

message GetDiscountLevelRequest {
  string user_id = 1;
}

message DiscountLevelResponse {
  int32 discount_percent = 1;
  string tier_name = 2;
}

// Дрібнозернистий сервіс: клієнт робить 5+ викликів для одного екрана
service ChattyUserService {
  rpc GetUserProfile(GetUserProfileRequest) returns (UserProfileResponse);
  rpc GetUserAddress(GetUserAddressRequest) returns (UserAddressResponse);
  rpc GetUserOrders(GetUserOrdersRequest) returns (UserOrdersResponse);
  rpc GetOrderDetails(GetOrderDetailsRequest) returns (OrderDetailsResponse);
  rpc GetDiscountLevel(GetDiscountLevelRequest) returns (DiscountLevelResponse);
}
```

Недолік такого контракту полягає в жорсткому зв'язуванні клієнта з фізичною топологією серверних модулів. Клієнтський код бере на себе роль координатора бізнес-транзакції: він зобов'язаний відкривати незалежні сокети, перевіряти помилки кожного проміжного кроку та керувати послідовністю передачі ідентифікаторів (наприклад, отримувати `order_ids`, а потім у циклі викликати `GetOrderDetails`).

---

### 2. Консолідований контракт віддаленого фасаду (Chunky / Remote Facade API)

Контракт віддаленого фасаду об'єднує всі залежні сутності в єдиний агрегатний виклик `GetDashboard`. Для запобігання надлишковому завантаженню даних (*over-fetching*), коли мобільному клієнту потрібна лише частина полів, контракт підтримує маску полів `google.protobuf.FieldMask`.

```protobuf
syntax = "proto3";

package commerce.facade.v1;

import "google/protobuf/field_mask.proto";
import "google/protobuf/timestamp.proto";

message GetDashboardRequest {
  string user_id = 1;
  // Маска полів: клієнт явно зазначає потрібні секції
  // Наприклад: "profile,recent_orders.total_cents,discount"
  google.protobuf.FieldMask field_mask = 2;
  int32 recent_orders_limit = 3;
}

message OrderSummaryDTO {
  string order_id = 1;
  int64 total_cents = 2;
  string status = 3;
  google.protobuf.Timestamp created_at = 4;
}

message DashboardDTO {
  // Профіль клієнта
  string user_id = 1;
  string full_name = 2;
  string email = 3;

  // Адреса
  string city = 4;
  string country = 5;

  // Список замовлень
  repeated OrderSummaryDTO recent_orders = 6;

  // Знижка
  int32 discount_percent = 7;
  string tier_name = 8;
}

service UserDashboardFacadeService {
  // 1 виклик повертає всі потрібні дані за 1 круговий рейс
  rpc GetDashboard(GetDashboardRequest) returns (DashboardDTO);
}
```

#### Механізм обробки FieldMask на сервері
При отриманні запиту `GetDashboardRequest` серверний обробник перевіряє вміст `field_mask.paths`:
* Якщо список шляхів порожній, сервер застосовує стандартну проєкцію за замовчуванням (базові поля профілю та останні 5 замовлень);
* Якщо клієнт передав конкретні шляхи (наприклад, `discount,profile.email`), сервер виконує оптимізовані локальні запити до сховища даних, завантажуючи виключно запитані секції та залишаючи неактуальні гілки графа неініціалізованими (`null` або значення за замовчуванням);
* Це дозволяє зберегти всі переваги єдиного мережевого рейсу, повністю ліквідувавши накладні витрати на передачу непотрібних байтів.

---

### 3. Пакетний контракт із підтримкою часткових відмов (Batch Multi-Status Contract)

Коли клієнту необхідно виконати однакову операцію над списком сутностей (наприклад, пакетне оновлення адрес 50 користувачів), контракт оголошує пакетний конверт з обов'язковим масивом індивідуальних результатів:

```protobuf
syntax = "proto3";

package commerce.batch.v1;

message UpdateUserItemRequest {
  string user_id = 1;
  string email = 2;
  string phone = 3;
  // Поштучний ключ ідемпотентності для безпечного повтору окремого рядка
  string item_idempotency_key = 4;
}

message BatchUpdateUsersRequest {
  string batch_id = 1;
  repeated UpdateUserItemRequest items = 2;
}

enum ItemStatusCode {
  ITEM_STATUS_CODE_UNSPECIFIED = 0;
  ITEM_STATUS_CODE_OK = 200;
  ITEM_STATUS_CODE_INVALID_ARGUMENT = 400;
  ITEM_STATUS_CODE_NOT_FOUND = 404;
  ITEM_STATUS_CODE_CONFLICT = 409;
  ITEM_STATUS_CODE_INTERNAL_ERROR = 500;
  ITEM_STATUS_CODE_TIMEOUT = 504;
}

message ItemResultDTO {
  string user_id = 1;
  ItemStatusCode status_code = 2;
  string error_message = 3;
  // Повертається лише у разі успішного оновлення (status_code == 200)
  string updated_at = 4;
}

message BatchUpdateUsersResponse {
  string batch_id = 1;
  int32 total_items = 2;
  int32 succeeded_count = 3;
  int32 failed_count = 4;
  // Ізольований результат виконання для кожного елемента пакета
  repeated ItemResultDTO results = 5;
}

service BatchUserFacadeService {
  rpc BatchUpdateUsers(BatchUpdateUsersRequest) returns (BatchUpdateUsersResponse);
}
```

---

### 4. Специфікація JSON Schema для HTTP / REST фасадів (Multi-Status 207)

Для сервісів, що використовують протокол HTTP/REST, контракт пакетного оновлення відповідає стандарту коду стану `207 Multi-Status` (RFC 4918). Формат відповіді суворо валідується схемою JSON:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "BatchUpdateResponseEnvelope",
  "type": "object",
  "required": ["batch_id", "total", "succeeded", "failed", "items"],
  "properties": {
    "batch_id": { "type": "string", "format": "uuid" },
    "total": { "type": "integer", "minimum": 0 },
    "succeeded": { "type": "integer", "minimum": 0 },
    "failed": { "type": "integer", "minimum": 0 },
    "items": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["item_id", "status"],
        "properties": {
          "item_id": { "type": "string" },
          "status": { "type": "integer", "minimum": 100, "maximum": 599 },
          "error": {
            "type": "object",
            "properties": {
              "code": { "type": "string" },
              "message": { "type": "string" }
            }
          },
          "data": { "type": "object" }
        }
      }
    }
  }
}
```

---

### Порівняння двійкового пакування на фізичному рівні

Важливою перевагою грубозернистого контракту є оптимізація двійкового представлення в мережі. У протоколі Protocol Buffers кожне поле кодується як пара `(tag_number << 3 | wire_type)` та значення.

Коли дрібнозернистий клієнт робить п'ять окремих gRPC-викликів:
* Кожен виклик формує окремий HTTP/2 фрейм `HEADERS` (заголовки `:path`, `:method`, `:scheme`, `content-type`, токени авторизації JWT/OAuth);
* Кожен виклик генерує окремий HTTP/2 фрейм `DATA` з 5-байтовим префіксом gRPC (1 байт стиснення + 4 байти довжини);
* Сумарний розмір службових заголовків на п'ять викликів сягає 1200–2500 байтів, навіть якщо корисні дані становлять лише 150 байтів.

У грубозернистому контракті `DashboardDTO`:
* Передається рівно один набір HTTP/2 `HEADERS` та один gRPC `DATA` фрейм;
* Вкладені структури (`repeated OrderSummaryDTO`) пакуються як послідовність байтових блоків довжини `wire_type = 2` (Length-delimited), що забезпечує максимальну щільність пакування;
* Загальний обсяг службових метаданих скорочується на 80%, а серіалізатор одноразово виділяє цілісний буфер у пам'яті.

---

### Квотування та політика обмеження швидкості (Rate Limiting)

При проектуванні грубозернистих фасадів змінюється механізм підрахунку лімітів запитів (*Rate Limiting*):
* **Проблема наївного підрахунку:** якщо шлюз API налаштовано на ліміт `100 запитів/сек`, один клієнт може надіслати 100 дрібних запитів по 1 елементу, а інший — 100 пакетних запитів по 500 елементів у кожному (сумарно 50 000 операцій), що викличе відмову в обслуговуванні сервера (*Denial of Service*);
* **Вартісне квотування (Weighted Cost Rate Limiting):** грубозернистий контракт зобов'язує шлюз списувати одиниці квоти пропорційно до кількості елементів у масиві (`cost = len(items)` або `cost = 1 + len(field_mask.paths)`). Завдяки цьому алгоритми *Token Bucket* та *Leaky Bucket* коректно відображають реальне навантаження на обчислювальні вузли.

---

### Обробка помилок рівня транспорту проти рівня елемента

При проектуванні клієнтських SDK для грубозернистих контрактів слід чітко розмежовувати два рівні виникнення помилок:
1. **Транспортні помилки (Transport-Level Failures):**
   * Обрив TCP-з'єднання, таймаут шлюзу, помилки авторизації токена (HTTP 401/403) або падіння самого сервера (HTTP 500/502/503);
   * За цих умов пакетний конверт не може бути сформований; клієнт отримує системну помилку на рівні всього RPC-виклику і повинен виконати повтор із експоненційним відтермінуванням та новим або збереженим `batch_id`.
2. **Елементні помилки (Item-Level Failures):**
   * Помилки валідації конкретних полів (наприклад, некоректний номер телефону в елементі #3), відсутність запису в базі (HTTP 404 для елемента #7) або конфлікт версій (HTTP 409 для елемента #12);
   * Сам RPC-виклик завершується зі статусом успіху доставки (`200 OK / 207 Multi-Status`), а помилки локалізуються у відповідних структурах `ItemResultDTO`. Клієнт не повторює весь пакет, а вилучає лише невдалі елементи для повторної спроби або сповіщення користувача.

---

### Правила еволюції та зворотної сумісності контрактів

При тривалій експлуатації грубозернистих фасадів необхідно дотримуватися правил розширення схеми без порушення роботи застарілих клієнтів:
1. **Заборона видалення полів:** Поля в `DashboardDTO` ніколи не видаляються і не змінюють своїх числових тегів (тегів Protocol Buffers або назв ключів JSON). Застаріле поле позначається прапорцем `deprecated = true`, але продовжує наповнюватися сервером.
2. **Лише опціональні нові поля:** Будь-які нові атрибути, що додаються до композитного DTO, повинні бути необов'язковими (*optional*). Старі клієнти просто проігнорують незнайомі поля в двійковому потоці.
3. **Обмеження максимального розміру пакета:** Пакетний контракт зобов'язаний встановлювати явну верхню межу кількості елементів у масиві `items` (наприклад, `max_items = 100`). Якщо клієнт передає 1000 елементів, сервер повертає статус `400 Bad Request / INVALID_ARGUMENT`, захищаючи пам'ять і процесор від неконтрольованого перевантаження.

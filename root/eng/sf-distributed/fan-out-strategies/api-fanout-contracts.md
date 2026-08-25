# 📋 Контракти конфігурації топологій віялового розсилання та протоколи деградації

Ця довідкова специфікація містить нормативні контракти інтерфейсів, декларативні схеми інфраструктури та детальний опис поведінки систем для реалізації віялового розсилання у двох площинах: синхронному RPC-координаторі (gRPC / Protobuf v3) та асинхронних брокерах повідомлень (AWS SNS-SQS та RabbitMQ).

Специфікація стандартизує взаємодію між клієнтами, координаторами та цільовими бекендами, фіксуючи точні семантичні правила розподіленого трасування, тайм-аутів, спекулятивного геджування та часткової деградації при збоях.

## 1. Специфікація Protobuf v3: Scatter-Gather RPC Coordinator

Контракт визначає протокол взаємодії між клієнтським агрегатором та множиною віддалених шардів із явною передачею бюджету дедлайну, параметрів геджування та матриці критичності підсистем.

```protobuf
syntax = "proto3";

package distributed.fanout.v1;

import "google/protobuf/duration.proto";
import "google/protobuf/timestamp.proto";
import "google/protobuf/any.proto";

// Головний сервіс координатора
service ScatterGatherCoordinator {
  // Виконання паралельного розпитування множини шардів
  rpc ExecuteScatterGather(ScatterGatherRequest) returns (ScatterGatherResponse);
}

// Запит на віялове виконання
message ScatterGatherRequest {
  string request_id = 1;                         // Унікальний ідентифікатор сесії
  string traceparent = 2;                        // W3C Trace Context (розподілене трасування)
  google.protobuf.Duration global_deadline = 3;  // Максимальний допустимий час на весь запит
  HedgingPolicy hedging_policy = 4;              // Політика спекулятивного дублювання
  DegradationPolicy degradation_policy = 5;      // Правила обробки часткових відмов
  repeated TargetShard shards = 6;               // Список цільових вузлів / шардів
}

// Політика спекулятивного геджування
message HedgingPolicy {
  bool enabled = 1;                              // Прапорець увімкнення
  google.protobuf.Duration hedge_delay = 2;      // Затримка перед запуском дублера (наприклад, 25ms)
  int32 max_hedged_attempts = 3;                 // Максимальна кількість дублюючих спроб (зазвичай 1)
}

// Політика деградації та збору результатів
message DegradationPolicy {
  double min_success_ratio = 1;                  // Мінімальна частка успішних відповідей (наприклад, 0.8 для 80%)
  repeated string critical_shard_ids = 2;        // Ідентифікатори шардів, відмова яких є фатальною
  bool allow_stale_cache_fallback = 3;           // Дозвіл підстановки застарілих кешованих даних
}

// Цільовий шард для розпитування
message TargetShard {
  string shard_id = 1;                           // Ідентифікатор шарду (наприклад, "shard-eu-01")
  string primary_endpoint = 2;                   // gRPC адреса первинної репліки
  repeated string backup_endpoints = 3;          // gRPC адреси вторинних реплік для геджування
  google.protobuf.Any payload = 4;               // Тіло запиту до шарду
}

// Відповідь координатора
message ScatterGatherResponse {
  string request_id = 1;
  ExecutionStatus status = 2;                    // Загальний статус виконання
  google.protobuf.Duration execution_time = 3;   // Фактична тривалість виконання
  repeated ShardResult results = 4;              // Список отриманих відповідей
  repeated ShardError errors = 5;                // Список збоїв та таймаутів
}

enum ExecutionStatus {
  EXECUTION_STATUS_UNSPECIFIED = 0;
  EXECUTION_STATUS_FULL_SUCCESS = 1;             // Усі 100% шардів відповіли успішно
  EXECUTION_STATUS_PARTIAL_DEGRADED = 2;         // Частина некритичних шардів відмовила, повернуто частковий результат
  EXECUTION_STATUS_DEADLINE_EXCEEDED = 3;        // Перевищено глобальний дедлайн
  EXECUTION_STATUS_CRITICAL_FAILURE = 4;         // Відмовив критичний шард
}

message ShardResult {
  string shard_id = 1;
  string responding_endpoint = 2;                // Яка саме репліка надала фінальну відповідь
  bool was_hedged = 3;                           // Чи була відповідь отримана від геджованого дублера
  google.protobuf.Duration latency = 4;          // Латентність відповіді цього шарду
  google.protobuf.Any data = 5;                  // Отримані бізнес-дані
}

message ShardError {
  string shard_id = 1;
  string failed_endpoint = 2;
  string error_code = 3;                         // Код помилки (DEADLINE_EXCEEDED, UNAVAILABLE тощо)
  string error_message = 4;
}
```

### Семантика полів та правила обробки gRPC контракту

Координатор реалізує чіткі правила обробки кожного елемента запиту:

1. **Контекст трасування (`traceparent`):** Поле містить стандартизований 4-компонентний рядок W3C Trace Context (версія, 16-байтний Trace ID, 8-байтний Parent Span ID, прапорці трасування). Координатор зобов'язаний зберегти вихідний `Trace ID` незмінним, але створити новий дочірній `Span ID` для кожної з `N` паралельних гілок. У разі спрацьовування геджування запит-дублер отримує власний окремий спан із міткою `hedged=true`.
2. **Управління глобальним дедлайном (`global_deadline`):** Значення тривалості конвертується координатором в абсолютну часову мітку на сервері (`Deadline Timestamp = now() + global_deadline`). Цей залишковий бюджет автоматично передається в метаданих кожного вихідного RPC-виклику gRPC через заголовок `grpc-timeout`. Якщо віддалений шард отримує виклик, коли до дедлайну лишилося менше 2 мс, він відкидає виконання негайно (`DEADLINE_EXCEEDED`), не витрачаючи CPU.
3. **Обчислення статусу деградації (`DegradationPolicy`):** Після збору відповідей координатор перевіряє дві умови:
   * Якщо будь-який шард зі списку `critical_shard_ids` повернув помилку або не відповів до настання дедлайну, підсумковий статус запиту встановлюється в `EXECUTION_STATUS_CRITICAL_FAILURE`, а вся транзакція вважається неуспішною.
   * Якщо всі критичні шарди відповіли успішно, але частка успішних некритичних відповідей є нижчою за `min_success_ratio` (наприклад, відповіло лише 60% шардів при вимозі 80%), повертається статус `EXECUTION_STATUS_PARTIAL_DEGRADED` або помилка відповідно до конфігурації клієнта.
4. **Контроль геджування (`HedgingPolicy`):** Параметр `hedge_delay` задає час пасивного очікування первинної відповіді. Якщо значення встановлено в `0`, геджування вимикається. Значення `max_hedged_attempts` обмежує кількість повторних спекулятивних спроб (рекомендоване значення — 1, максимальне — 2), запобігаючи лавинному множенню трафіку.

### Матриця кодів помилок gRPC для гілок віяла

При виникненні збоїв у віддалених шардах координатор мапує внутрішні помилки на стандартизовані статуси gRPC:

* `DEADLINE_EXCEEDED (4)`: Шард не надав відповіді до завершення виділеного тайм-ауту. Гілка позначається як неуспішна, а з'єднання негайно скидається через RST_STREAM.
* `UNAVAILABLE (14)`: Репліка недоступна через мережевий розрив або перезавантаження процесу. Координатор негайно здійснює фалбек на вторинну репліку без очікування `hedge_delay`.
* `RESOURCE_EXHAUSTED (8)`: Шард перевантажений і активував механізм відхилення запитів (*Load Shedding*). Координатор передає сигнал відсікання автоматичному вимикачу (*Circuit Breaker*).

## 2. Декларативна топологія AWS SNS-SQS Fan-Out (Terraform HCL)

Специфікація описує хмарну топологію віялового розсилання подій замовлення: один топік SNS дублює події у дві незалежні черги SQS (платежі та склад) з ізольованими чергами мертвих листів (DLQ) та політиками повторів.

```hcl
# Топік публікації подій замовлень
resource "aws_sns_topic" "order_events" {
  name                        = "order-events-fanout.fifo"
  fifo_topic                  = true
  content_based_deduplication = true
}

# 1. Черга сервісу білінгу
resource "aws_sqs_queue" "billing_queue" {
  name                        = "billing-service-input.fifo"
  fifo_queue                  = true
  visibility_timeout_seconds  = 30
  message_retention_seconds   = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.billing_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "billing_dlq" {
  name       = "billing-service-dlq.fifo"
  fifo_queue = true
}

# Підписка білінгу на SNS-топік
resource "aws_sns_topic_subscription" "billing_subscription" {
  topic_arn            = aws_sns_topic.order_events.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.billing_queue.arn
  raw_message_delivery = true

  # Фільтрація: тільки оплачені або створені замовлення
  filter_policy = jsonencode({
    event_type = ["OrderCreated", "PaymentRequested"]
  })
}

# 2. Черга сервісу складу
resource "aws_sqs_queue" "warehouse_queue" {
  name                        = "warehouse-service-input.fifo"
  fifo_queue                  = true
  visibility_timeout_seconds  = 60
  message_retention_seconds   = 86400

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.warehouse_dlq.arn
    maxReceiveCount     = 5
  })
}

resource "aws_sqs_queue" "warehouse_dlq" {
  name       = "warehouse-service-dlq.fifo"
  fifo_queue = true
}

# Підписка складу на SNS-топік
resource "aws_sns_topic_subscription" "warehouse_subscription" {
  topic_arn            = aws_sns_topic.order_events.arn
  protocol             = "sqs"
  endpoint             = aws_sqs_queue.warehouse_queue.arn
  raw_message_delivery = true
}
```

### Механізми надійності в топології SNS-SQS

Декларація реалізує важливі захисні механізми:
* **Сувора послідовність та дедуплікація (FIFO Topics & Queues):** Параметр `fifo_topic = true` у поєднанні з `content_based_deduplication` гарантує, що повідомлення з однаковим хешем тіла, надіслані двічі протягом 5-хвилинного вікна дедуплікації, будуть розіслані у підписані черги рівно один раз.
* **Селективна фільтрація на боці брокера (`filter_policy`):** Замість того, щоб навантажувати сервіс білінгу читанням і локальним відкиданням подій зміни пароля чи відгуків про товари, SNS виконує фільтрацію на транспортному рівні за атрибутом `event_type`. Це заощаджує до 70% мережевого трафіку та витрат на операції SQS Read.
* **Ізоляція збоїв через черги мертвих листів (Dead Letter Redrive):** Політика `redrive_policy` автоматично переміщує повідомлення у відповідний `billing_dlq` або `warehouse_dlq` після `maxReceiveCount` невдалих спроб обробки (3 спроби для білінгу, 5 для складу). Це усуває проблему блокування черги отруйними повідомленнями (*Poison Pill Messages*).

## 3. Декларативна топологія RabbitMQ Fanout Exchange (RabbitMQ Definitions JSON)

Нормативна конфігурація брокера RabbitMQ через механізм Definitions: визначення Fanout Exchange, трьох споживчих черг, підключення політики скидання при переповненні (`x-overflow`) та мертвого обмінника (`x-dead-letter-exchange`).

```json
{
  "rabbit_version": "3.13.0",
  "exchanges": [
    {
      "name": "orders.fanout",
      "vhost": "/",
      "type": "fanout",
      "durable": true,
      "auto_delete": false,
      "arguments": {}
    },
    {
      "name": "orders.dlx",
      "vhost": "/",
      "type": "direct",
      "durable": true,
      "auto_delete": false,
      "arguments": {}
    }
  ],
  "queues": [
    {
      "name": "orders.billing.q",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-max-length": 50000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "billing.dead"
      }
    },
    {
      "name": "orders.warehouse.q",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-max-length": 50000,
        "x-overflow": "reject-publish",
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "warehouse.dead"
      }
    },
    {
      "name": "orders.analytics.q",
      "vhost": "/",
      "durable": true,
      "auto_delete": false,
      "arguments": {
        "x-max-length": 10000,
        "x-overflow": "drop-head",
        "x-dead-letter-exchange": "orders.dlx",
        "x-dead-letter-routing-key": "analytics.dead"
      }
    }
  ],
  "bindings": [
    {
      "source": "orders.fanout",
      "vhost": "/",
      "destination": "orders.billing.q",
      "destination_type": "queue",
      "routing_key": "",
      "arguments": {}
    },
    {
      "source": "orders.fanout",
      "vhost": "/",
      "destination": "orders.warehouse.q",
      "destination_type": "queue",
      "routing_key": "",
      "arguments": {}
    },
    {
      "source": "orders.fanout",
      "vhost": "/",
      "destination": "orders.analytics.q",
      "destination_type": "queue",
      "routing_key": "",
      "arguments": {}
    }
  ]
}
```

### Семантика налаштувань переповнення черг у RabbitMQ

У конфігурації продемонстровано диференційований підхід до захисту брокера від переповнення залежно від критичності даних:

* **Політика `reject-publish` для білінгу та складу:** Для фінансових та складських операцій втрата повідомлення є неприпустимою. Параметр `x-overflow: reject-publish` змушує брокер повертати помилку видавцю (*Publisher Nack*), якщо черга досягла ліміту в 50 000 повідомлень. Видавець призупиняє генерацію трафіку, захищаючи RAM кластера і запобігаючи неконтрольованій втраті транзакцій.
* **Політика `drop-head` для аналітики:** Аналітична підсистема не повинна зупиняти основний потік продажів. При досягненні 10 000 елементів параметр `x-overflow: drop-head` автоматично видаляє найстаріші незчитані повідомлення з голови черги, надсилаючи їх у `orders.dlx` для аудиту та звільняючи місце для нових подій.

## Матриця конфігураційних параметрів віялового брокера

| Параметр | Призначення | Рекомендоване значення | Ризик неправильного вибору |
| :--- | :--- | :--- | :--- |
| `hedge_delay` | Час до відправки дублюючого RPC-запиту | 95-й перцентиль (p95) затримки | Занадто малий (p50) подвоює трафік кластера; занадто великий (>p99) не встигає врятувати SLA |
| `global_deadline` | Твердий ліміт очікування агрегації | 2.5 × медіана найповільнішого шарду | Занадто малий ламає запити при дрібних коливаннях мережі; занадто великий заморожує воркери клієнта |
| `x-max-length` | Максимальний розмір буфера черги | 10 000 – 50 000 повідомлень | Необмежена черга спричиняє вичерпання RAM брокера при зависанні споживача |
| `x-overflow` | Поведінка при переповненні черги | `reject-publish` (білінг), `drop-head` (телеметрія) | `drop-head` у фінансових чергах веде до непоправної втрати грошових транзакцій |
| `min_success_ratio` | Поріг успішності для Scatter-Gather | 0.80 – 0.95 (80%–95%) | Занадто високий поріг (1.0) ламає сторінку при відмові будь-якого другорядного лічильника |

## Інженерний чеклист розгортання віялової інфраструктури

Перед введенням в експлуатацію віялової топології обов'язково перевіряються наступні показники:
1. **Моніторинг глибини черг (Queue Backlog Metric):** Налаштовано алерти на перевищення порогового значення `ApproximateNumberOfMessagesVisible > 10000` протягом більше ніж 3 хвилин.
2. **Метрики ефективності геджування (Hedging Win Rate):** У Prometheus вимірюється співвідношення `hedged_requests_won_total / hedged_requests_sent_total`. Якщо дублюючі запити перемагають первинні менш ніж у 30% випадків спрацьовування, поріг `hedge_delay` налаштовано неправильно і його слід збільшити.
3. **Ліміти відкритих сокетів (File Descriptor Limits):** Для процесів координатора ліміт `ulimit -n` збільшено щонайменше до 65 536 дескрипторів, що запобігає відмові `EMFILE (Too many open files)` під час масового віялового розпитування.

# ⚙️ Практика міграції зчеплення: від синхронного REST-запиту до Transactional Outbox

Практична різниця між синхронним викликом, який блокує розгортання релізів, та асинхронним шаблоном Transactional Outbox з поблажливим читачем розкривається на рівнях архітектури та коду. Подані робочі приклади коду мовами C, C++, Go та TypeScript демонструють, як зламати залежність між релізами двох сервісів під час міграції схеми даних.

---

## 1. Проблема синхронного REST-виклику: Пастка жорсткого зчеплення (Lockstep)

Розглянемо практичну ситуацію в архітектурі електронної комерції або родинного смарт-будинку. Сервіс замовлень (`OrderService`) при отриманні нової покупки робить прямолінійний синхронний HTTP REST-виклик до сервісу білінгу (`BillingService`). При оновленні сервісу білінгу до версії `v2` бізнес-вимога змінюється: тепер для кожного розрахунку вимагається обов'язкове поле податкового ідентифікатора (`tax_identifier`).

Старий код `OrderService v1` не має поняття про це нове поле і продовжує надсилати структури без нього.

```
+------------------+                    +------------------+
|   OrderService   | -- HTTP POST ----> |  BillingService  |
|  (Старий v1)     |    без tax_id      |   (Новий v2)     |
+------------------+                    +------------------+
                                                 |
                                          ❌ 400 BAD REQUEST
                                       "Missing tax_identifier"
```

У цій ситуації відбулося **порушення автономії релізів**:
1. Розгортання `BillingService v2` миттєво робить систему непрацездатною для всіх запитів від `OrderService v1`.
2. Команда `OrderService` змушена аварійно зупиняти свої поточні задачі й поспіхом розгортати підтримку нового поля.
3. Якщо у коді `BillingService v2` виявиться помилка й вимагатиметься відкат до `v1`, система знову впаде, бо `OrderService` вже надсилає нову форму DTO.

### Аналіз механіки збою на рівні HTTP-протоколу
При синхронній HTTP-взаємодії клієнтський процес виділяє потік виконання (або реєструє callback у циклі подій `epoll`/`io_uring`) і відкриває TCP-сокет до сервера. Якщо сервіс білінгу у версії `v2` повертає статус `400 Bad Request` із тілом `{"error": "missing field tax_identifier"}`, сервіс замовлень отримує виняток рівня застосунку.

Оскільки `400 Bad Request` належить до категорії клієнтських помилок `4xx`, автоматичний механізм повторних спроб (Retry Policy) не допомагає: повторне відправлення того самого пакета без поля `tax_identifier` гарантовано поверне той самий статус `400`. Якщо в клієнті налаштовано запобіжник (Circuit Breaker), він накопичує поріг помилок і розмикає ланцюг, повністю блокуючи створення нових замовлень у всій системі.

Нижче наведено робочий приклад, який відтворює цю помилку синхронного зчеплення.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Структура DTO для синхронного REST-запиту (версія 1) */
typedef struct {
    char order_id[32];
    double amount;
} OrderPayloadV1;

/* Старий клієнт відправляє лише V1 */
int send_billing_request_v1(const OrderPayloadV1* payload) {
    printf("[REST Client C] Sending V1 request: Order=%s, Amount=%.2f\n", 
           payload->order_id, payload->amount);
    
    /* Емуляція сервера V2, який чекає обов'язкове поле tax_id */
    int server_has_tax_id_requirement = 1;
    if (server_has_tax_id_requirement) {
        printf("[REST Server V2] ERROR 400: Missing required field 'tax_identifier'\n");
        return -1; /* Збій виклику — релізи зчеплені! */
    }
    return 0;
}

int main(void) {
    OrderPayloadV1 order = {"ORD-9901", 149.99};
    int res = send_billing_request_v1(&order);
    if (res != 0) {
        printf("[System] Lockstep Failure: Cannot deploy OrderService without updating BillingService!\n");
    }
    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <expected>
#include <memory>

struct OrderPayloadV1 {
    std::string order_id;
    double amount;
};

enum class RestErrorCode {
    BadRequestMissingField,
    NetworkError,
    ServerError
};

class SyncBillingClient {
public:
    [[nodiscard]] std::expected<void, RestErrorCode> send_request(const OrderPayloadV1& payload) const {
        std::cout << "[REST Client C++] Sending V1 request: " << payload.order_id << "\n";
        
        // Сервер V2 вимагає tax_identifier
        bool server_requires_tax_id = true;
        if (server_requires_tax_id) {
            std::cout << "[REST Server V2] ERROR 400: Missing required 'tax_identifier'\n";
            return std::unexpected(RestErrorCode::BadRequestMissingField);
        }
        return {};
    }
};

int main() {
    SyncBillingClient client;
    OrderPayloadV1 order{"ORD-9901", 149.99};
    auto result = client.send_request(order);
    
    if (!result) {
        std::cout << "[System] Synchronous Lockstep Failure: Release is blocked!\n";
    }
    return 0;
}
```
```go
// go
package main

import (
	"errors"
	"fmt"
)

type OrderPayloadV1 struct {
	OrderID string  `json:"order_id"`
	Amount  float64 `json:"amount"`
}

func sendBillingRequestV1(payload OrderPayloadV1) error {
	fmt.Printf("[REST Client Go] Sending Order=%s, Amount=%.2f\n", payload.OrderID, payload.Amount)
	
	// Сервер v2 чекає tax_identifier
	serverRequiresTaxID := true
	if serverRequiresTaxID {
		return errors.New("HTTP 400 Bad Request: missing tax_identifier")
	}
	return nil
}

func main() {
	order := OrderPayloadV1{OrderID: "ORD-9901", Amount: 149.99}
	if err := sendBillingRequestV1(order); err != nil {
		fmt.Printf("[System Error] %v\n", err)
	}
}
```
:::

---

## 2. Архітектурне рішення: Transactional Outbox та Подійна Розв'язка (Decoupled Flow)

Щоб розірвати часову та структурну залежність між релізами, ми переводимо взаємодію на патерн **Transactional Outbox** та впроваджуємо **поблажливого читача** (Tolerant Reader).

### Механіка роботи Transactional Outbox
Головна пастка асинхронних систем — це проблема подвійного запису (*Dual-Write Problem*). Якщо код спочатку зберігає замовлення в реляційну БД, а потім відправляє повідомлення в Kafka через мережу, мережевий збій або аварійне вимикання живлення між цими двома операціями призведе до розбіжності даних: замовлення створене, але подія втрачена назавжди.

Transactional Outbox вирішує це за допомогою транзакцій бази даних:
1. `OrderService` під час створення замовлення у межах єдиної ACID-транзакції БД записує сутність замовлення у таблицю `orders` ТА запис про подію у спеціальну таблицю `outbox_events`.
2. Окремий фоновий процес (Outbox Relay або CDC-демон Debezium) опитує таблицю `outbox_events` або читає transaction log БД і публікує події у брокер.
3. `BillingService` декодує подію за допомогою розбирача, який витягає відомі йому поля, а незнайомі або відсутні опціональні поля обробляє за фолбек-сценарієм.

```
+--------------------------------------------------------+
|                      OrderService                      |
|  +--------------------+      +----------------------+  |
|  | Таблиця Orders     |      | Таблиця Outbox       |  |
|  | (INSERT Order)     | ---> | (INSERT Event)       |  |
|  +--------------------+      +----------------------+  |
+------------------------------------------|-------------+
                                           | (CDC / Relay)
                                           v
                              +--------------------------+
                              |   Event Topic / Broker   |
                              +--------------------------+
                                           |
                                           v
                                 +--------------------+
                                 |   BillingService   |
                                 |  (Tolerant Reader) |
                                 +--------------------+
```

При такій схемі:
- `OrderService` розгортається у будь-який час, додаючи нові події в Outbox.
- `BillingService` розгортається незалежно, обробляючи як старі, так і нові події з черги.

### Захист від повторної обробки (Ідемпотентність споживача)
Оскільки Outbox Relay гарантує доставку повідомлень за принципом *at-least-once* (як мінімум один раз), мережевий моргання під час підтвердження (ACK) може призвести до того, що споживач отримає одну й ту саму подію двічі.

Для захисту від подвійного списання грошей споживач застосовує **таблицю ідемпотентності** (Idempotency Key Store). Перед виконанням бізнес-логіки споживач перевіряє у своїй БД факт наявності `event_id`:
- Якщо `event_id` вже існує — подія мовчки ігнорується та підтверджується брокеру.
- Якщо `event_id` новий — подія обробляється та її ID атомарно зберігається разом із результатом обробки.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* Модель подійної структури з опціональними полями */
typedef struct {
    char event_id[64];
    char order_id[32];
    double amount;
    char tax_identifier[32]; /* Нове поле v2 (може бути порожнім) */
    int has_tax_identifier;
} OrderPlacedEvent;

/* Транзакційний запис у таблицю Outbox (Емуляція) */
int write_to_transactional_outbox(const char* order_id, double amount, const char* tax_id) {
    printf("[Database Transaction] BEGIN\n");
    printf("  [DB Table 'orders'] INSERT INTO orders VALUES ('%s', %.2f)\n", order_id, amount);
    
    printf("  [DB Table 'outbox'] INSERT INTO outbox_events (event_type, payload) VALUES ('OrderPlaced', ");
    if (tax_id && strlen(tax_id) > 0) {
        printf("'{\"order_id\":\"%s\",\"amount\":%.2f,\"tax_id\":\"%s\"}')\n", order_id, amount, tax_id);
    } else {
        printf("'{\"order_id\":\"%s\",\"amount\":%.2f}')\n", order_id, amount);
    }
    printf("[Database Transaction] COMMIT SUCCESSFUL\n");
    return 0;
}

/* Поблажливий читач на стороні BillingService */
void consume_event_tolerant(const OrderPlacedEvent* event) {
    printf("[Billing Consumer C] Processing Order=%s, Amount=%.2f\n", event->order_id, event->amount);
    
    if (event->has_tax_identifier) {
        printf("  -> Tax ID present: %s (Processing V2 logic)\n", event->tax_identifier);
    } else {
        printf("  -> Tax ID missing: Using default fallback (Processing V1 legacy compatibility)\n");
    }
    printf("[Billing Consumer C] Event %s processed successfully!\n", event->event_id);
}

int main(void) {
    printf("=== КРОК 1: Викатка OrderService V2 (додає Outbox) ===\n");
    write_to_transactional_outbox("ORD-9902", 299.50, NULL);
    
    printf("\n=== КРОК 2: Обробка старою/перехідною версією BillingService ===\n");
    OrderPlacedEvent ev1 = {
        .event_id = "EVT-1001",
        .order_id = "ORD-9902",
        .amount = 299.50,
        .has_tax_identifier = 0
    };
    consume_event_tolerant(&ev1);
    
    printf("\n=== КРОК 3: Викатка оновленого BillingService V2 ===\n");
    write_to_transactional_outbox("ORD-9903", 450.00, "UA12345678");
    OrderPlacedEvent ev2 = {
        .event_id = "EVT-1002",
        .order_id = "ORD-9903",
        .amount = 450.00,
        .tax_identifier = "UA12345678",
        .has_tax_identifier = 1
    };
    consume_event_tolerant(&ev2);
    
    return 0;
}
```
```cpp
// cpp
#include <iostream>
#include <string>
#include <string_view>
#include <optional>
#include <memory>
#include <unordered_set>
#include <vector>

struct OrderPlacedEvent {
    std::string event_id;
    std::string order_id;
    double amount;
    std::optional<std::string> tax_identifier; // Опціональне поле для безпечної еволюції
};

class TransactionalOutboxWriter {
public:
    void create_order_with_outbox(std::string_view order_id, double amount, 
                                 std::optional<std::string_view> tax_id) {
        std::cout << "[DB Transaction] BEGIN\n";
        std::cout << "  INSERT INTO orders (id, amount) VALUES ('" << order_id << "', " << amount << ");\n";
        std::cout << "  INSERT INTO outbox (event_type, payload) VALUES ('OrderPlaced', ...);\n";
        std::cout << "[DB Transaction] COMMIT\n";
    }
};

class TolerantEventConsumer {
private:
    mutable std::unordered_set<std::string> processed_event_ids_;

public:
    void process_event(const OrderPlacedEvent& event) const {
        // Перевірка ідемпотентності (захист від дублікатів при деплої)
        if (processed_event_ids_.contains(event.event_id)) {
            std::cout << "[Consumer C++] Duplicate event " << event.event_id << " ignored.\n";
            return;
        }

        std::cout << "[Consumer C++] Event ID: " << event.event_id 
                  << " | Order: " << event.order_id 
                  << " | Amount: " << event.amount << "\n";
        
        if (event.tax_identifier) {
            std::cout << "  -> Tax Identifier: " << *event.tax_identifier << " (V2 Flow)\n";
        } else {
            std::cout << "  -> Tax Identifier: None (Default V1 Fallback Flow)\n";
        }
        
        processed_event_ids_.insert(event.event_id);
        std::cout << "[Consumer C++] Event processed without blocking!\n";
    }
};

int main() {
    TransactionalOutboxWriter outbox;
    TolerantEventConsumer consumer;
    
    std::cout << "--- Phase 1: Producer deploys V2 (Outbox), Consumer is V1 ---\n";
    outbox.create_order_with_outbox("ORD-701", 199.99, std::nullopt);
    consumer.process_event({"EV-01", "ORD-701", 199.99, std::nullopt});
    
    std::cout << "\n--- Phase 2: Consumer updates to V2 ---\n";
    outbox.create_order_with_outbox("ORD-702", 599.00, "TAX-UA-9988");
    consumer.process_event({"EV-02", "ORD-702", 599.00, "TAX-UA-9988"});

    std::cout << "\n--- Phase 3: Retry duplicate event test ---\n";
    consumer.process_event({"EV-02", "ORD-702", 599.00, "TAX-UA-9988"});
    
    return 0;
}
```
```ts
// ts
interface OrderPlacedEventV2 {
  eventId: string;
  orderId: string;
  amount: number;
  taxIdentifier?: string; // Optional field for zero-downtime evolution
}

class OutboxPublisher {
  async saveOrderWithOutbox(orderId: string, amount: number, taxId?: string): Promise<void> {
    console.log(`[DB Tx] Saving Order ${orderId} and writing Outbox event...`);
    // Atomically written in single DB transaction
  }
}

class TolerantBillingConsumer {
  private processedEvents = new Set<string>();

  handleEvent(event: OrderPlacedEventV2): void {
    if (this.processedEvents.has(event.eventId)) {
      console.log(`[TS Consumer] Duplicate event ${event.eventId} skipped.`);
      return;
    }

    console.log(`[TS Consumer] Handling Order=${event.orderId}, Amount=${event.amount}`);
    if (event.taxIdentifier) {
      console.log(`  -> Processing V2 with Tax ID: ${event.taxIdentifier}`);
    } else {
      console.log(`  -> Processing V1 fallback logic (no tax ID)`);
    }

    this.processedEvents.add(event.eventId);
  }
}

// Execution test
const publisher = new OutboxPublisher();
const consumer = new TolerantBillingConsumer();

publisher.saveOrderWithOutbox("ORD-3001", 89.90);
consumer.handleEvent({ eventId: "E-1", orderId: "ORD-3001", amount: 89.90 });
consumer.handleEvent({ eventId: "E-1", orderId: "ORD-3001", amount: 89.90 });
```
:::

---

## 3. Детальний порівняльний аналіз пропускної здатності та затримки

Розглянемо результати бенчмаркінгу продуктивності для обидвох підходів при високому навантаженні (10 000 запитів на секунду):

1. **Синхронний REST-потік**:
   - Середня затримка (RTT): 25 мс (включаючи TLS, HTTP-заголовки та серіалізацію JSON).
   - При збої мережі або перезапуску сервера затримка зростає до тайм-ауту у 5 000 мс.
   - Кількість одночасних потоків на відправнику зростає пропорційно затримці сервера (закон Літтла).

2. **Асинхронний Transactional Outbox потік**:
   - Затримка запису у БД продюсера: 1.2 мс (локальна транзакція `INSERT INTO outbox`).
   - Продюсер продовжує обробку трафіку з постійною швидкістю незалежно від стану споживачів.
   - Затримка доставки події споживачу (Consumer Lag): від 10 мс у нормальному стані до десятків хвилин під час деплою чи відновлення споживача.

### Стратегія обробки некоректних повідомлень (Dead Letter Queue — DLQ)
Якщо під час деплою нового споживача в коді розбирача виявляється баг, який викликає `Uncaught Error` для повідомлень певного типу, споживач не повинен застрягати у нескінченному циклі ретраїв (Poison Pill Message).

Схема обробки DLQ передбачає:
- Після N невдалих спроб обробки (наприклад, 3 ретраї з експоненційним запізненням), споживач пересилає оригінальне повідомлення у топік `orders-dlq` разом із заголовками винятку (`x-exception-message`, `x-failed-timestamp`).
- Зсув основного топіку просувається далі, відновлюючи обробку решти трафіку.
- Інженери аналізують вміст DLQ, виправляють баг у споживачі, розгортають версію `v2.1` та запускають утиліту `dlq-replay`, яка повертає повідомлення з DLQ назад у той самий топік.

---

## 4. Оптимізація пам'яті та потокобезпека в C та C++

При реалізації асинхронного розчеплення у високонавантажених C/C++ сервісах критичним вимогам є відсутність динамічних алокацій пам'яті на гарячому шляху (hot path) та гарантія потокобезпечності.

### 4.1. Внутрішня буферизація у C++20
У коді C++ використання `std::optional<std::string>` дозволяє уникнути виділення пам'яті у купі (heap allocation) для відсутніх полів, якщо застосовувати `std::string_view` або масиви фіксованого розміру `std::array<char, N>`.

При передачі подій між потоками обробника та мережевого IO використовують беззамкові кільцеві буфери (Lock-Free Ring Buffer) на базі `std::atomic<size_t>`. Це дозволяє Outbox-демону витягати події з логу БД і передавати їх у socket без блокування потоків виконання бізнес-транзакцій.

### 4.2. Гарантії пам'яті в C
У C-реалізації структура `OrderPlacedEvent` використовує статичні байтові буфери (`char order_id[32]`) та явний прапорець наявності поля `has_tax_identifier`. Це повністю виключає витоки пам'яті (memory leaks) при аварійному перезапуску процесів під час релізів і робить код придатним для вбудованих систем (наприклад, хабів розумного дому).

---

## 5. Повний аналіз відмовостійкості та відновлення при збоях (Failure Modes)

У практичній експлуатації асинхронного Outbox-контуру можливі 4 типи збоїв:

1. **Збій підключення до БД продюсера**: Транзакція скасовується (ROLLBACK). Клієнт отримує помилку `500`, жодного запису в Outbox не створюється. Стан бази та подій залишається строго узгодженим.
2. **Падіння Outbox Relay демона**: Події продовжують накопичуватися у таблиці `outbox_events`. Після рестарту демона він продовжує відправлення з останнього обробленого ID.
3. **Падіння брокера Kafka**: Outbox Relay отримує мережевий timeout при спробі публікації й повторює спроби з експоненційним запізненням (Backoff). База даних продюсера продовжує працювати без простоїв.
4. **Помилка десеріалізації на споживачі**: Некоректне повідомлення переводиться в топік `DLQ`, не зупиняючи обробку решти партиції.

---

## 6. Спостережність і моніторинг Outbox-контуру (Prometheus Metrics)

Для забезпечення контролю за асинхронним розчепленням у продакшені реалізують наступні метрики Prometheus:

1. `outbox_events_unprocessed_total` (gauge) — кількість записів у таблиці `outbox_events` зі статусом `PENDING`. Зростання цього показника свідчить про аварію Outbox Relay або проблеми з мережею до брокера.
2. `kafka_consumer_lag_records` (gauge) — кількість повідомлень у топіку, які ще не вичитані споживачем `BillingService`. Під час розгортання релізу споживача цей показник тимчасово зростає, а після старту контейнерів падає до нуля.
3. `dlq_messages_sent_total` (counter) — загальна кількість повідомлень, скинутих у Dead Letter Queue через помилки десеріалізації чи несумісність схем.

---

## 7. Інтеграційне тестування зчеплення у CI/CD (Testcontainers)

Щоб переконуватися у відсутності lockstep-зчеплення на етапі CI/CD, застосовують інтеграційне тестування з Testcontainers:

1. **Тест сумісності споживача**: CI-конвеєр піднімає контейнер Kafka і викачує попередньо записаний лог подій `OrderPlaced` трьох останніх версій.
2. **Перевірка Tolerant Reader**: Споживач обробляє пакет подій. Тест перевіряє, що жодна подія не викликала `panic` або скасування обробки.
3. **Перевірка ідемпотентності**: Одна й та сама подія відправляється двічі. Тест перевіряє, що стан моделі читання змінився лише один раз.

---

## 8. Практичний приклад конфігурації CDC Debezium для PostgreSQL Outbox

При використанні Change Data Capture (CDC) замість опитування таблиці Outbox SQL-запитами, Debezium зчитує лог WAL (Write-Ahead Logging) PostgreSQL.

Нижче наведено робочу конфігурацію Debezium Connector JSON:

```json
{
  "name": "outbox-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "postgres-db",
    "database.port": "5432",
    "database.user": "debezium",
    "database.password": "dbz_pass",
    "database.dbname": "orders_db",
    "database.server.name": "pg_orders",
    "table.include.list": "public.outbox_events",
    "tombstones.on.delete": "false",
    "transforms": "outbox",
    "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
    "transforms.outbox.table.fields.additional.placement": "event_type:header"
  }
}
```

Ця конфігурація перетворює кожен рядок, доданий у таблицю `outbox_events`, на подію Kafka у топіку `outbox.event.OrderPlaced` із автоматичним додаванням метаданих у заголовки Kafka. Це забезпечує мінімальну затримку доставки (< 5 мс) без створення додаткових Lock-блокувань бази даних.

---

## 9. Архітектурні сценарії очищення таблиці Outbox (Table Maintenance Strategy)

Накопичення записів у таблиці `outbox_events` без регулярної очистки призводить до роздуття табличних файлів бази даних (PostgreSQL Table Bloat) та сповільнення індексного пошуку.

Існує 3 тактики очищення:

1. **Delete-on-Publish**: Outbox Relay видаляє рядок з `outbox_events` одразу після отримання підтвердження (ACK) від Kafka.
   - *Перевага*: Таблиця Outbox залишається мінімального розміру (десятки рядків).
   - *Недолік*: Додаткове навантаження `DELETE` на транзакційний лог БД.
2. **Batch Purge Job**: Фонова задача о третій ночі видаляє оброблені події за запитом `DELETE FROM outbox_events WHERE created_at < NOW() - INTERVAL '3 days' AND status = 'PROCESSED'`.
   - *Перевага*: Відсутність накладного часу на `DELETE` у мить публікації.
   - *Недолік*: Потрібне регулярне виконання `VACUUM ANALYZE` для запобігання деградації продуктивності.
3. **Partition Truncation**: Таблиця `outbox_events` шардується за днями (Range Partitioning по даті). Наприкінці тижня застаріла партиція скидається атомарною командою `DROP TABLE outbox_events_2026_08_10`, що не вимагає жодних ресурсів на видалення окремих рядків.

---

## 10. Порівняння бінарних форматів серіалізації для розчеплення

Вибір бінарного формату серіалізації подій прямо визначає швидкість обробки та сумісність схем під час оновлення коду.

```
       Формат серіалізації         Швидкість декодування      Розмір бінарного пакета    Автоматична сумісність
------------------------------------------------------------------------------------------------------------------
1. JSON (Text Standard)             Низька (parsing overhead)  Великий (verbose keys)     Ручна (Tolerant Reader)
2. Protobuf (Binary Tags)           Висока (direct offset)     Маленький (varint tags)    Сувора (Tag-based)
3. Avro (Schema Registry)           Максимальна (no tags)      Мінімальний (raw bytes)    Повна (Schema Registry)
```

При використанні Protobuf або Avro розчеплення релізів стає математично гарантованим: бінарні декодери на рівні C/C++ двійкового парсингу пропускають невідомі теги за O(1) без виділення додаткової пам'яті в купі.

---

## 11. Механізм перепроведення подій (Event Log Replay Procedure)

У разі виявлення багу в бізнес-логіці `BillingService v2`, який зіпсував агреговані дані за останні 24 години, асинхронний подійний зв'язок дозволяє легко виконати процедуру відновлення (Replay Procedure):

1. **Фікс коду**: Команда виправляє баг і розгортає `BillingService v2.1`.
2. **Скидання зсуву (Offset Reset)**: За допомогою CLI-інструменту Kafka зсув групи споживачів скидається на 24 години назад:
   `kafka-consumer-groups --bootstrap-server kafka:9092 --group billing-group --reset-offsets --to-datetime 2026-08-17T00:00:00Z --execute`
3. **Регенеризація матеріалізованого представлення**: Споживач перечитує заново всі події з логу. Завдяки ідемпотентності та поблажливому читачу Read Model перераховується до коректного стану без потреби залучати команду відправника (`OrderService`).

---

## 12. Налаштування алертингу Prometheus для Dead Letter Queue

Для миттєвого виявлення отруйних повідомлень (Poison Pills) у продакшені налаштовують такі правила Prometheus Alertmanager:

```yaml
groups:
  - name: outbox_alerts
    rules:
      - alert: HighConsumerLag
        expr: kafka_consumer_lag_records{topic="orders"} > 5000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "BillingService consumer lag exceeds 5000 records"

      - alert: DeadLetterQueueNotEmpty
        expr: increase(dlq_messages_sent_total[1m]) > 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "Poison pill detected! Message sent to Dead Letter Queue"
```

---

## 13. Механіка кооперативного ребалансування у Kafka Consumer Groups

Під час розгортання оновленого споживача `BillingService v2` у Kubernetes за допомогою Rolling Update старий под v1 зупиняється, а новий под v2 реєструється у кластері Kafka.

У ранніх версіях Kafka це викликало процедуру **Eager Rebalance**, яка зупиняла обробку повідомлень усім подам групи (Stop-The-World pause).

Сучасна реалізація використовує **Cooperative Sticky Assignor**:
- Новий под v2 приєднується до групи без зупинки роботи інших працюючих подів.
- Перерозподіляються лише ті партиції, які належали зупиненому поду.
- Завдяки цьому реліз споживача проходить із нульовим перериванням обробки трафіку та без накопичення хибного лагу.
- Також налаштовується параметр `session.timeout.ms = 45000` та `max.poll.interval.ms = 300000`, щоб запобігти випадковим вильотам споживачів під час тривалої обробки важких пакетів подій у базі даних.
- Додатково впроваджується практика окремого фонового потоку `Heartbeat Thread`, який надсилає періодичні сигнали координатору групи незалежно від тривалості бізнес-транзакцій. Це повністю виключає хибне виключення споживачів зі складу активної когорти під час обробки пікових навантажень.
- Крім того, для запобігання втраті зв'язку між брокером та споживачами під час проведення регулярних релізів у конфігурації споживачів використовують алгоритми запобігання хибній інвалідації сесій (`keepalive`-сигнали). Це гарантує, що тимчасова зупинка обробника для проходження Garbage Collector (GC) або виділення додаткової пам'яті не призведе до викидання процесу із групи споживачів та не викличе повторного перерозподілу партицій між сусідніми подам.

---

## 14. Практичні інженерні висновки з реалізації

1. **Гарантія атомарності публікації**: Використання таблиці `outbox_events` гарантує, що не виникне розбіжності між станом бази даних та згенерованими подіями. Навіть якщо брокер Kafka або RabbitMQ повністю недоступний, запити клієнтів продовжують успішно зберігатися у БД, а події накопичуються в Outbox до моменту відновлення мережі.
2. **Типобезпечність та поблажливість (Tolerant Reader)**: У C++ використання `std::optional<std::string>` дозволяє на рівні системи типів виразити відсутність нового поля, запобігаючи неконтрольованим виняткам або прочитанню сміття з пам'яті. У мові C перевірка прапорця `has_tax_identifier` виконує аналогічну захисну функцію.
3. **Ліквідація нічних деплоїв**: Перехід від синхронного REST до асинхронного Outbox повністю знімає потребу у веденні спільних релізних календарів. Продюсери розгортаються, коли готова фіча, а споживачі адаптуються у своєму власному темпі розробки.

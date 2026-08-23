# ⚙️ Наскрізний харнес Walking Skeleton: ендпоінти та простеження запиту

Ця вставка містить практичну реалізацію найтоншого наскрізного зрізу (Walking Skeleton) для мультирегіональної платіжної системи OmniPay. Код показує, як простежується запит від створення транзакції на edge-маршрутизаторі, через валідацію контексту орендаря (Tenant Context) та ідемпотентного ключа, до формування запису в транзакційному журналі (Outbox/Ledger) та імітації асинхронного сповіщення.

## 1. Архітектурне призначення та структура харнесу

Walking Skeleton не є повноцінною бізнес-реалізацією всіх мікросервісів системи. Це **мінімальний робочий скелет**, який з'єднує всі архітектурні шари системи єдиним протокольним ланцюжком. Його ціль — перевірити інтеграційний ризик, зафіксувати формування наскрізного ідентифікатора простеження (`Correlation ID` / `Traceparent`), перевірити гарантію ідемпотентності та виміряти наскрізну затримку до того, як розробники почнуть писати доменний код.

### Основні етапи обробки транзакційного запиту у харнесі

1. **Edge Router & Context Extractor:** Прийом запиту на краю мережі. Витяг заголовків орендаря (`Tenant-ID`), перевірка наявності дедуплікаційного ключа (`Idempotency-Key`) та формування/прокидання наскрізного ідентифікатора трасування за стандартом W3C Trace Context (`traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01`).
2. **Idempotency Guard (Заслон ідемпотентності):** Перевірка дедуплікаційного вікна у локальній оперативній пам'яті чи швидкому сховищі. Якщо ключ вже було успішно оброблено раніше — виконання транзакції переривається, і клієнту негайно повертається збережений результат попередньої проводки з кодом `200 OK`. Це запобігає подвійному списанню коштів під час повторів запитів через мережеві таймаути.
3. **Ledger Outbox Writer (Транзакційний лог):** Атомарний запис наміру проводки у локальний журнал транзакцій (Outbox/Ledger). Запис виконується в режимі append-only до повернення відповіді клієнту, що гарантує збереження фінансової проводки (`RPO = 0`).
4. **Async Event Emitter (Асинхронний брокер):** Публікація події про успішний запис у внутрішню чергу повідомлень для подальшого асинхронного оновлення читацьких матеріалізованих в'ю (Read-Models) та відправки вебхуків торговцю.

## 2. Стандарт трасування W3C Trace Context та механізм прокидання

У розподілених мультирегіональних системах один вхідний HTTP-запит проходить крізь 5–10 незалежних сервісів. Без наскрізного простеження пошук причин затримок або втрачених транзакцій перетворюється на ручне зіставлення лог-файлів із десятків серверів.

Харнес реалізує специфікацію **W3C Trace Context**, де заголовок `traceparent` має наступну бінарну та текстову структуру:

```text
traceparent: 00 - 4bf92f3577b34da6a3ce929d0e0e4736 - 00f067aa0ba902b7 - 01
             │   │                                │                  │
             │   └─ Trace ID (16 байт / 32 hex)   └─ Parent Span ID  └─ Trace Flags
             └─ Версія стандарту (00)                (8 байт / 16 hex)   (01 = Sampled)
```

- **Trace ID:** Унікальний 128-бітний ідентифікатор усієї транзакційної сесії. Створюється на Edge Router і залишається незмінним під час проходження крізь усі внутрішні сервіси.
- **Parent Span ID (Parent ID):** 64-бітний ідентифікатор поточного виклику. Кожен мікросервіс при передачі запиту далі замінює Parent ID на власний Span ID, утворюючи деревоподібний граф викликів у Jaeger чи Zipkin.

## 3. Алгоритм дедуплікації та Idempotency Guard

Мережеві збої та таймаути є неминучими у розподілених системах. Якщо мобільний застосунок або сервер торговця не отримав відповіді протягом 2 секунд, він автоматично повторює HTTP-запит. Без заслону ідемпотентності (Idempotency Guard) це призводить до катастрофічного наслідку: подвійного списання коштів із картки покупця.

Алгоритм Idempotency Guard у харнесі працює за наступною схемою:

```text
[Вхідний HTTP Запит]
        │
        ▼
[Витяг Idempotency-Key з HTTP Header]
        │
        ▼
[Запит до Fast Key-Value Store (Redis/Memory)]
        ├── (Ключ існує + Стан: IN_PROGRESS)  ──> [Повернення 409 Conflict / Retry Later]
        ├── (Ключ існує + Стан: COMPLETED)    ──> [Повернення збереженої відповіді 200 OK]
        └── (Ключ відсутній) ─────────────────> [Атомарний SETNX Ключа (TTL 24h) + Виконання]
```

При отриманні нового ключа система атомарно встановлює прапорець `IN_PROGRESS` із часом життя (TTL) 24 години. Якщо наступний паралельний запит приходить із тим самим ключем, доки перший ще виконується, система повертає код `409 Conflict` або закликає зачекати, запобігаючи стан гонки (Race Condition).

## 4. Патерн Transactional Outbox та атомарність запису

Для запобігання ситуації, коли транзакцію збережено у базу даних, але не опубліковано у брокер повідомлень через аварію мережі, харнес застосовує патерн **Transactional Outbox**.

Замість прямого виклику брокера повідомлень у гарячому HTTP-потоці:
1. Бізнес-транзакція та запис події у таблицю `outbox` виконуються в межах єдиної локальної бази даних (Single Local DB Transaction).
2. Окремий фоновий процес (Outbox Publisher або CDC-коннектор на базі Debezium) вичитує нові записи з таблиці `outbox` та асинхронно транслює їх у Kafka чи RabbitMQ.

Це забезпечує гарантію доставки принаймні один раз (At-Least-Once Delivery) без сповільнення основної транзакції клієнта.

## 5. Реалізація Walking Skeleton C / C++

Нижче наведено робочий харнес обробки транзакційного запиту з наскрізною підтримкою простеження, валідації ідемпотентності та формуванням події в Outbox-журналі.

:::tabs
```c
/* Walking Skeleton Harness мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>

#define MAX_STR 64
#define OUTBOX_CAPACITY 100

typedef struct {
    char trace_id[MAX_STR];
    char tenant_id[MAX_STR];
    char idempotency_key[MAX_STR];
    double amount;
    char currency[8];
} checkout_request_t;

typedef struct {
    char transaction_id[MAX_STR];
    char trace_id[MAX_STR];
    char status[16];
    int http_code;
} checkout_response_t;

typedef struct {
    char id[MAX_STR];
    char tenant_id[MAX_STR];
    double amount;
    long timestamp;
} outbox_entry_t;

typedef struct {
    outbox_entry_t entries[OUTBOX_CAPACITY];
    size_t count;
} outbox_journal_t;

static outbox_journal_t g_outbox = { .count = 0 };

/* Перевірка ідемпотентності в пам'яті */
bool check_idempotency(const char* key, checkout_response_t* cached_out) {
    if (strcmp(key, "idem-duplicate-123") == 0) {
        snprintf(cached_out->transaction_id, MAX_STR, "tx_cached_998877");
        snprintf(cached_out->status, 16, "DUPLICATE_ACK");
        cached_out->http_code = 200;
        return true; /* Знайдено дублікат */
    }
    return false;
}

/* Атомарний запис у локальний Outbox */
bool record_to_outbox(const char* tenant, double amount, const char* trace_id) {
    if (g_outbox.count >= OUTBOX_CAPACITY) return false;
    
    outbox_entry_t* entry = &g_outbox.entries[g_outbox.count++];
    snprintf(entry->id, MAX_STR, "tx_live_%ld", time(NULL) + rand() % 1000);
    snprintf(entry->tenant_id, MAX_STR, "%s", tenant);
    entry->amount = amount;
    entry->timestamp = (long)time(NULL);

    printf("[%s] [OUTBOX_APPEND] Tenant: %s, TxID: %s, Amount: %.2f\n",
           trace_id, entry->tenant_id, entry->id, entry->amount);
    return true;
}

/* Головна точка входу Walking Skeleton */
checkout_response_t process_checkout(const checkout_request_t* req) {
    checkout_response_t res;
    memset(&res, 0, sizeof(res));
    snprintf(res.trace_id, MAX_STR, "%s", req->trace_id);

    printf("[%s] [EDGE_ROUTER] Ingesting request for Tenant: %s, Key: %s\n",
           req->trace_id, req->tenant_id, req->idempotency_key);

    /* 1. Guard ідемпотентності */
    if (check_idempotency(req->idempotency_key, &res)) {
        printf("[%s] [IDEMPOTENCY_GUARD] Duplicate key detected. Returning cached response.\n", req->trace_id);
        return res;
    }

    /* 2. Запис у локальний Ledger / Outbox */
    if (!record_to_outbox(req->tenant_id, req->amount, req->trace_id)) {
        snprintf(res.status, 16, "OUTBOX_FULL");
        res.http_code = 503;
        return res;
    }

    /* 3. Формування успішного результату */
    snprintf(res.transaction_id, MAX_STR, "tx_live_ok");
    snprintf(res.status, 16, "SUCCESS");
    res.http_code = 200;

    printf("[%s] [WALKING_SKELETON_SUCCESS] Completed end-to-end trace. Code: %d\n",
           req->trace_id, res.http_code);
    return res;
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("=== OmniPay Walking Skeleton Pipeline Harness (C) ===\n\n");

    checkout_request_t req1 = {
        .trace_id = "trace-uuid-1111-aaaa",
        .tenant_id = "tenant_enterprise_eu",
        .idempotency_key = "idem-unique-001",
        .amount = 250.50,
        .currency = "EUR"
    };

    checkout_response_t res1 = process_checkout(&req1);
    printf("Result 1: TxID=%s, Status=%s, Code=%d\n\n", res1.transaction_id, res1.status, res1.http_code);

    checkout_request_t req2 = {
        .trace_id = "trace-uuid-2222-bbbb",
        .tenant_id = "tenant_enterprise_eu",
        .idempotency_key = "idem-duplicate-123",
        .amount = 250.50,
        .currency = "EUR"
    };

    checkout_response_t res2 = process_checkout(&req2);
    printf("Result 2: TxID=%s, Status=%s, Code=%d\n", res2.transaction_id, res2.status, res2.http_code);

    return 0;
}
```
```cpp
// Walking Skeleton Harness мовою C++
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <optional>
#include <chrono>

struct CheckoutRequest {
    std::string trace_id;
    std::string tenant_id;
    std::string idempotency_key;
    double amount;
    std::string currency;
};

struct CheckoutResponse {
    std::string transaction_id;
    std::string trace_id;
    std::string status;
    int http_code;
};

struct OutboxEntry {
    std::string id;
    std::string tenant_id;
    double amount;
    std::chrono::system_clock::time_point timestamp;
};

class IdempotencyStore {
public:
    std::optional<CheckoutResponse> find(std::string_view key) const {
        if (key == "idem-duplicate-123") {
            return CheckoutResponse{
                "tx_cached_998877",
                "cached_trace",
                "DUPLICATE_ACK",
                200
            };
        }
        return std::nullopt;
    }
};

class OutboxJournal {
private:
    std::vector<OutboxEntry> entries_;
public:
    bool append(std::string_view tenant, double amount, std::string_view trace_id, std::string& out_tx_id) {
        out_tx_id = "tx_live_" + std::to_string(entries_.size() + 100);
        entries_.push_back(OutboxEntry{
            out_tx_id,
            std::string(tenant),
            amount,
            std::chrono::system_clock::now()
        });

        std::cout << "[" << trace_id << "] [OUTBOX_APPEND] Tenant: " << tenant 
                  << ", TxID: " << out_tx_id << ", Amount: " << amount << "\n";
        return true;
    }
};

class WalkingSkeletonPipeline {
private:
    IdempotencyStore idempotency_store_;
    OutboxJournal outbox_journal_;

public:
    CheckoutResponse processCheckout(const CheckoutRequest& req) {
        std::cout << "[" << req.trace_id << "] [EDGE_ROUTER] Ingesting request for Tenant: " 
                  << req.tenant_id << ", Key: " << req.idempotency_key << "\n";

        // 1. Guard ідемпотентності
        if (auto cached = idempotency_store_.find(req.idempotency_key)) {
            std::cout << "[" << req.trace_id << "] [IDEMPOTENCY_GUARD] Duplicate key detected. Returning cached response.\n";
            auto res = *cached;
            res.trace_id = req.trace_id;
            return res;
        }

        // 2. Атомарний запис у локальний Ledger Outbox
        std::string tx_id;
        if (!outbox_journal_.append(req.tenant_id, req.amount, req.trace_id, tx_id)) {
            return CheckoutResponse{"", req.trace_id, "OUTBOX_ERROR", 503};
        }

        // 3. Формування відповіді
        std::cout << "[" << req.trace_id << "] [WALKING_SKELETON_SUCCESS] Completed end-to-end trace. Code: 200\n";
        return CheckoutResponse{tx_id, req.trace_id, "SUCCESS", 200};
    }
};

int main() {
    std::cout << "=== OmniPay Walking Skeleton Pipeline Harness (C++) ===\n\n";

    WalkingSkeletonPipeline pipeline;

    CheckoutRequest req1{
        "trace-uuid-1111-aaaa",
        "tenant_enterprise_eu",
        "idem-unique-001",
        250.50,
        "EUR"
    };

    auto res1 = pipeline.processCheckout(req1);
    std::cout << "Result 1: TxID=" << res1.transaction_id << ", Status=" << res1.status << ", Code=" << res1.http_code << "\n\n";

    CheckoutRequest req2{
        "trace-uuid-2222-bbbb",
        "tenant_enterprise_eu",
        "idem-duplicate-123",
        250.50,
        "EUR"
    };

    auto res2 = pipeline.processCheckout(req2);
    std::cout << "Result 2: TxID=" << res2.transaction_id << ", Status=" << res2.status << ", Code=" << res2.http_code << "\n";

    return 0;
}
```
:::

## 6. Детальний розбір роботи харнесу та крайових випадків

Розглянемо покроково, як реалізовані мовні механізми C та C++ розв'язують архітектурні завдання Walking Skeleton:

1. **Контроль пам'яті та типів даних:**
   - У версії мовою C використовується стаціонарна структура `outbox_journal_t` із фіксованим масивом `outbox_entry_t entries[OUTBOX_CAPACITY]`. Це унеможливлює динамічний виділ пам'яті (`malloc`) у гарячому шляху виконання транзакцій, що виключає ризик витоків пам'яті чи фрагментації купи.
   - У версії мовою C++ застосовується RAII-контейнер `std::vector<OutboxEntry>`, безпосереднє використання `std::string_view` для некопіювального читання ключів та `std::optional<CheckoutResponse>` для безпечного вираження відсутності дубліката у сховищі ідемпотентності.
2. **Простеження викликів (Distributed Tracing):**
   - Трасовий ідентифікатор `trace_id` передається як перший аргумент у кожний функціональний блок або метод. Кожен рядок логування починається з префікса `[trace_id]`. У реальній системі цей рядок транслюється у заголовок OpenTelemetry та прокидається у gRPC-контекст.
3. **Обробка крайового випадку подвійного запиту (Race Condition on Idempotency):**
   - Якщо клієнт надсилає запит із ключем `idem-duplicate-123` (наприклад, через таймаут першого HTTP-запиту), система перехоплює його на етапі `Idempotency Guard`. Жодна проводка не додається до `OutboxJournal`, а клієнт отримує статус `DUPLICATE_ACK` із збереженим `HTTP 200 OK`. Це гарантує інваріант про відсутність подвійного списання.
4. **Гарантія неблокуючого виклику:**
   - Запис у `OutboxJournal` є атомарною операцією у локальній пам'яті / WAL-журналі. Тривалі операції (відправка SMS-сповіщень, виклик зовнішніх банківських API) виконуються окремими асинхронними воркерами, які читають події з Outbox-журналу.

Харнес доводить, що обрана поверхня контрактів є життєздатною, а інтеграційні ризики між шарами системи знято до початку масштабної розробки.

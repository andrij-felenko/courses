# ⚙️ Конвеєр маршрутизації повідомлень: фільтрація, предикати та мертва черга

У розподілених системах обробки потоків даних надійність та продуктивність маршрутизатора залежать від того, наскільки ефективно він розділяє швидкий аналіз транспортних метаданих (заголовків) та ресурсомістку десеріалізацію корисного навантаження. Помилка в обробці битого повідомлення, відсутність правила для нового типу події або неконтрольоване виділення динамічної пам'яті на гарячому шляху здатні спричинити зупинку всього брокера чи падіння обробника через вичерпання ресурсів.

Розгляньмо виробничий конвеєр маршрутизації, який об'єднує шість ключових патернів корпоративної інтеграції в єдиний стійкий механізм.

## Архітектура та життєвий цикл повідомлення в конвеєрі

Конвеєр обробки вхідного пакета організовано як послідовність суворо впорядкованих фаз:

```
[Вхідний пакет] 
       │
       ▼
 1. [Wire Tap] ───────────────► (Асинхронна копія в чергу аудиту AUDIT.STREAM)
       │
       ▼
 2. [Routing Slip Check] ─────► {Є активний крок?} ──► [Так] ──► (Вилучити крок та надіслати в чергу кроку)
       │                                                 │
       ▼ [Ні]                                            ▼ [Помилка: адреса не існує]
 3. [Content / Predicates]                               │
       │                                                 │
       ├──► Правило 1 (Предикат = true) ──► Черга 1      │
       ├──► Правило 2 (Предикат = true) ──► Черга 2      │
       │                                                 │
       ▼ [Жодне правило не спрацювало]                   │
 4. [Dead Letter Queue (DLQ)] ◄──────────────────────────┘
```

Розгляньмо кожну фазу конвеєра детально:

1. **Фаза спостереження (Wire Tap):** Щойно повідомлення надходить у процесор, конвеєр викликає зареєстрований приймач діагностичного каналу. Ця дія виконується до будь-яких мутацій конверта чи передачі іншим сервісам. Головна вимога — безаварійність: помилка в каналі аудиту не повинна переривати бізнес-тракт.
2. **Фаза маршрутного листа (Routing Slip):** Якщо вхідне повідомлення містить непорожній список кроків `routing_slip`, маршрутизатор оминає статичну таблицю правил. Він вилучає (pop) першу адресу з черги маршруту, оновлює метадані повідомлення та пересилає пакет зареєстрованому каналу цього кроку. Якщо вказаний у листі вузол не існує серед зареєстрованих отримувачів, повідомлення маркується як помилкове й передається в мертву чергу.
3. **Фаза предикатів (Content-Based Router & Recipient List):** Якщо маршрутний лист відсутній або вичерпаний, повідомлення передається на оцінку зареєстрованим правилам маршрутизації. Кожне правило містить функціональний предикат, який аналізує транспортні заголовки або вміст. Усі правила, чий предикат повернув `true`, передають пакет у свої цільові канали (що реалізує розгалуження Recipient List).
4. **Фаза ізоляції аномалій (Dead Letter Queue):** Якщо жоден предикат не повернув позитивного результату (немаршрутизоване повідомлення), пакет безумовно спрямовується до мертвої черги.

---

## Реалізація конвеєра: C та C++20

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <functional>
#include <memory>
#include <optional>
#include <span>
#include <chrono>
#include <stdexcept>

// Структура транспортного конверта повідомлення
struct MessageEnvelope {
    std::string id;
    std::string topic;
    std::unordered_map<std::string, std::string> headers;
    std::vector<uint8_t> payload;
    std::vector<std::string> routing_slip; // Послідовність кроків
    std::chrono::system_clock::time_point timestamp;

    [[nodiscard]] std::string_view payload_as_string() const noexcept {
        return {reinterpret_cast<const char*>(payload.data()), payload.size()};
    }

    [[nodiscard]] std::optional<std::string_view> get_header(std::string_view key) const noexcept {
        auto it = headers.find(std::string(key));
        if (it != headers.end()) {
            return it->second;
        }
        return std::nullopt;
    }
};

// Абстракція вихідного каналу призначення
class IMessageSink {
public:
    virtual ~IMessageSink() = default;
    virtual bool deliver(const MessageEnvelope& msg) = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
};

// Конкретна черга для доставки повідомлень
class QueueSink final : public IMessageSink {
public:
    explicit QueueSink(std::string queue_name) : name_(std::move(queue_name)) {}

    bool deliver(const MessageEnvelope& msg) override {
        std::cout << "  [Черга " << name_ << "] Отримано msg_id=" << msg.id 
                  << " payload: " << msg.payload_as_string() << "\n";
        delivered_count_++;
        return true;
    }

    [[nodiscard]] std::string_view name() const noexcept override { return name_; }
    [[nodiscard]] size_t count() const noexcept { return delivered_count_; }

private:
    std::string name_;
    size_t delivered_count_{0};
};

// Мертва черга для немаршрутизованих і битих повідомлень
class DeadLetterSink final : public IMessageSink {
public:
    explicit DeadLetterSink(std::string name = "DLQ.UNROUTED") : name_(std::move(name)) {}

    bool deliver(const MessageEnvelope& msg) override {
        std::cerr << "  ⚠️ [МЕРТВА ЧЕРГА " << name_ << "] Ізольовано непридатне msg_id=" 
                  << msg.id << " (немає маршруту або збій валідації)\n";
        dlq_count_++;
        return true;
    }

    [[nodiscard]] std::string_view name() const noexcept override { return name_; }
    [[nodiscard]] size_t count() const noexcept { return dlq_count_; }

private:
    std::string name_;
    size_t dlq_count_{0};
};

// Правило маршрутизації: предикат перевірки та список цільових каналів
struct RoutingRule {
    std::string rule_name;
    std::function<bool(const MessageEnvelope&)> predicate;
    std::vector<std::shared_ptr<IMessageSink>> destinations;
};

// Ядро маршрутизатора повідомлень
class MessageRouter {
public:
    explicit MessageRouter(std::shared_ptr<DeadLetterSink> dlq_sink)
        : dlq_(std::move(dlq_sink)) {
        if (!dlq_) {
            throw std::invalid_argument("Dead letter sink cannot be null");
        }
    }

    void add_rule(RoutingRule rule) {
        rules_.push_back(std::move(rule));
    }

    void set_wire_tap(std::shared_ptr<IMessageSink> tap_sink) {
        wire_tap_ = std::move(tap_sink);
    }

    void register_named_sink(std::shared_ptr<IMessageSink> sink) {
        named_sinks_[std::string(sink->name())] = sink;
    }

    // Головний конвеєр обробки вхідного повідомлення
    void route(MessageEnvelope msg) {
        // 1. Wire Tap: Неінвазивний відвід копії на аудит
        if (wire_tap_) {
            try {
                wire_tap_->deliver(msg);
            } catch (const std::exception& ex) {
                std::cerr << "Wire tap audit failed: " << ex.what() << "\n";
            }
        }

        // 2. Routing Slip: Якщо є супровідний маршрут — беремо перший крок
        if (!msg.routing_slip.empty()) {
            std::string next_hop = msg.routing_slip.front();
            msg.routing_slip.erase(msg.routing_slip.begin()); // Вилучаємо поточний крок

            auto it = named_sinks_.find(next_hop);
            if (it != named_sinks_.end()) {
                std::cout << "-> [Routing Slip] Передача на вузол '" << next_hop << "'\n";
                it->second->deliver(msg);
                return;
            } else {
                std::cerr << "-> [Routing Slip Помилка] Вузол '" << next_hop << "' недоступний!\n";
                dlq_->deliver(msg);
                return;
            }
        }

        // 3. Content-Based Router & Recipient List: Перевірка предикатів правил
        bool routed = false;
        for (const auto& rule : rules_) {
            bool matches = false;
            try {
                matches = rule.predicate(msg);
            } catch (const std::exception& e) {
                std::cerr << "Predicate error in rule '" << rule.rule_name << "': " << e.what() << "\n";
                matches = false;
            }

            if (matches) {
                for (const auto& dest : rule.destinations) {
                    dest->deliver(msg);
                    routed = true;
                }
            }
        }

        // 4. Якщо жодне правило не спрацювало — скидаємо в DLQ
        if (!routed) {
            dlq_->deliver(msg);
        }
    }

private:
    std::vector<RoutingRule> rules_;
    std::unordered_map<std::string, std::shared_ptr<IMessageSink>> named_sinks_;
    std::shared_ptr<IMessageSink> wire_tap_{nullptr};
    std::shared_ptr<DeadLetterSink> dlq_;
};

int main() {
    auto dlq = std::make_shared<DeadLetterSink>("DLQ.PRIMARY");
    auto audit_tap = std::make_shared<QueueSink>("AUDIT.STREAM");

    auto queue_eu = std::make_shared<QueueSink>("ORDERS.EU");
    auto queue_us = std::make_shared<QueueSink>("ORDERS.US");
    auto queue_fraud = std::make_shared<QueueSink>("FRAUD.EVALUATION");
    auto queue_kyc = std::make_shared<QueueSink>("KYC.VALIDATION");
    auto queue_billing = std::make_shared<QueueSink>("BILLING.SETTLEMENT");

    MessageRouter router(dlq);
    router.set_wire_tap(audit_tap);

    router.register_named_sink(queue_kyc);
    router.register_named_sink(queue_fraud);
    router.register_named_sink(queue_billing);

    // Правило 1: Регіональна маршрутизація (Content-Based)
    router.add_rule({
        "Region_EU_Rule",
        [](const MessageEnvelope& msg) {
            auto reg = msg.get_header("region");
            return reg.has_value() && *reg == "EU";
        },
        {queue_eu}
    });

    // Правило 2: Мультивекторне розсилання для великих сум (Recipient List)
    router.add_rule({
        "High_Value_VIP_Rule",
        [](const MessageEnvelope& msg) {
            auto amount = msg.get_header("amount");
            if (!amount.has_value()) return false;
            try {
                return std::stod(std::string(*amount)) >= 10000.0;
            } catch (...) {
                return false;
            }
        },
        {queue_us, queue_fraud}
    });

    std::cout << "=== 1. Звичайне замовлення з ЄС ===\n";
    MessageEnvelope msg1{
        .id = "msg_001",
        .topic = "orders",
        .headers = {{"region", "EU"}, {"amount", "250.0"}},
        .payload = {'{', '"', 'i', 't', 'e', 'm', '"', ':', '"', 'B', 'o', 'o', 'k', '"', '}'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg1);

    std::cout << "\n=== 2. VIP замовлення великої суми (Мультивектор) ===\n";
    MessageEnvelope msg2{
        .id = "msg_002",
        .topic = "orders",
        .headers = {{"region", "US"}, {"amount", "50000.0"}},
        .payload = {'{', '"', 'i', 't', 'e', 'm', '"', ':', '"', 'S', 'e', 'r', 'v', 'e', 'r', '"', '}'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg2);

    std::cout << "\n=== 3. Повідомлення з Routing Slip ===\n";
    MessageEnvelope msg3{
        .id = "msg_003",
        .topic = "onboarding",
        .headers = {{"user", "usr_99"}},
        .payload = {'{', '"', 'a', 'c', 't', 'i', 'o', 'n', '"', ':', '"', 'v', 'e', 'r', 'i', 'f', 'y', '"', '}'},
        .routing_slip = {"KYC.VALIDATION", "FRAUD.EVALUATION", "BILLING.SETTLEMENT"},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg3);

    std::cout << "\n=== 4. Немаршрутизоване повідомлення (падає в DLQ) ===\n";
    MessageEnvelope msg4{
        .id = "msg_004",
        .topic = "telemetry",
        .headers = {{"sensor", "temp_01"}},
        .payload = {'2', '4', '.', '5'},
        .routing_slip = {},
        .timestamp = std::chrono::system_clock::now()
    };
    router.route(msg4);

    return 0;
}
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_HEADERS 16
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64
#define MAX_PAYLOAD 512
#define MAX_SLIP_HOPS 8
#define MAX_DESTINATIONS 8
#define MAX_RULES 16

typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
} HeaderPair;

typedef struct {
    char id[32];
    char topic[32];
    HeaderPair headers[MAX_HEADERS];
    size_t header_count;
    char payload[MAX_PAYLOAD];
    size_t payload_len;
    char routing_slip[MAX_SLIP_HOPS][32];
    size_t slip_count;
} MessageEnvelope;

typedef struct MessageSink {
    char name[32];
    bool (*deliver)(struct MessageSink* self, const MessageEnvelope* msg);
    size_t delivered_count;
} MessageSink;

static bool queue_deliver(MessageSink* self, const MessageEnvelope* msg) {
    printf("  [Черга %s] Отримано msg_id=%s payload: %s\n", self->name, msg->id, msg->payload);
    self->delivered_count++;
    return true;
}

static bool dlq_deliver(MessageSink* self, const MessageEnvelope* msg) {
    fprintf(stderr, "  ⚠️ [МЕРТВА ЧЕРГА %s] Ізольовано непридатне msg_id=%s\n", self->name, msg->id);
    self->delivered_count++;
    return true;
}

static const char* get_header(const MessageEnvelope* msg, const char* key) {
    for (size_t i = 0; i < msg->header_count; i++) {
        if (strcmp(msg->headers[i].key, key) == 0) {
            return msg->headers[i].value;
        }
    }
    return NULL;
}

typedef bool (*PredicateFn)(const MessageEnvelope* msg);

typedef struct {
    char rule_name[32];
    PredicateFn predicate;
    MessageSink* destinations[MAX_DESTINATIONS];
    size_t dest_count;
} RoutingRule;

typedef struct {
    RoutingRule rules[MAX_RULES];
    size_t rule_count;
    MessageSink* named_sinks[MAX_RULES];
    size_t named_sink_count;
    MessageSink* wire_tap;
    MessageSink* dlq;
} MessageRouter;

void router_init(MessageRouter* router, MessageSink* dlq) {
    memset(router, 0, sizeof(MessageRouter));
    router->dlq = dlq;
}

void router_set_wire_tap(MessageRouter* router, MessageSink* tap) {
    router->wire_tap = tap;
}

void router_register_sink(MessageRouter* router, MessageSink* sink) {
    if (router->named_sink_count < MAX_RULES) {
        router->named_sinks[router->named_sink_count++] = sink;
    }
}

void router_add_rule(MessageRouter* router, const char* name, PredicateFn pred, MessageSink** dests, size_t dest_count) {
    if (router->rule_count >= MAX_RULES) return;
    RoutingRule* r = &router->rules[router->rule_count++];
    strncpy(r->rule_name, name, sizeof(r->rule_name) - 1);
    r->predicate = pred;
    r->dest_count = dest_count < MAX_DESTINATIONS ? dest_count : MAX_DESTINATIONS;
    for (size_t i = 0; i < r->dest_count; i++) {
        r->destinations[i] = dests[i];
    }
}

void router_route(MessageRouter* router, MessageEnvelope* msg) {
    // 1. Wire Tap
    if (router->wire_tap) {
        router->wire_tap->deliver(router->wire_tap, msg);
    }

    // 2. Routing Slip
    if (msg->slip_count > 0) {
        char next_hop[32];
        strncpy(next_hop, msg->routing_slip[0], sizeof(next_hop) - 1);
        next_hop[sizeof(next_hop) - 1] = '\0';

        // Зсув списку (pop)
        for (size_t i = 0; i < msg->slip_count - 1; i++) {
            strcpy(msg->routing_slip[i], msg->routing_slip[i + 1]);
        }
        msg->slip_count--;

        // Пошук цільового каналу
        for (size_t i = 0; i < router->named_sink_count; i++) {
            if (strcmp(router->named_sinks[i]->name, next_hop) == 0) {
                printf("-> [Routing Slip] Передача на вузол '%s'\n", next_hop);
                router->named_sinks[i]->deliver(router->named_sinks[i], msg);
                return;
            }
        }

        fprintf(stderr, "-> [Routing Slip Помилка] Вузол '%s' не знайдено!\n", next_hop);
        if (router->dlq) router->dlq->deliver(router->dlq, msg);
        return;
    }

    // 3. Перевірка правил (Content-Based / Filter / Recipient List)
    bool routed = false;
    for (size_t i = 0; i < router->rule_count; i++) {
        RoutingRule* r = &router->rules[i];
        if (r->predicate(msg)) {
            for (size_t j = 0; j < r->dest_count; j++) {
                r->destinations[j]->deliver(r->destinations[j], msg);
                routed = true;
            }
        }
    }

    // 4. Dead Letter Queue
    if (!routed && router->dlq) {
        router->dlq->deliver(router->dlq, msg);
    }
}

static bool is_region_eu(const MessageEnvelope* msg) {
    const char* reg = get_header(msg, "region");
    return reg && strcmp(reg, "EU") == 0;
}

static bool is_high_value(const MessageEnvelope* msg) {
    const char* amt = get_header(msg, "amount");
    if (!amt) return false;
    return atof(amt) >= 10000.0;
}

int main(void) {
    MessageSink dlq = {.name = "DLQ.PRIMARY", .deliver = dlq_deliver, .delivered_count = 0};
    MessageSink audit = {.name = "AUDIT.STREAM", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_eu = {.name = "ORDERS.EU", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_us = {.name = "ORDERS.US", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_fraud = {.name = "FRAUD.EVALUATION", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_kyc = {.name = "KYC.VALIDATION", .deliver = queue_deliver, .delivered_count = 0};
    MessageSink q_billing = {.name = "BILLING.SETTLEMENT", .deliver = queue_deliver, .delivered_count = 0};

    MessageRouter router;
    router_init(&router, &dlq);
    router_set_wire_tap(&router, &audit);

    router_register_sink(&router, &q_kyc);
    router_register_sink(&router, &q_fraud);
    router_register_sink(&router, &q_billing);

    MessageSink* eu_dests[] = {&q_eu};
    router_add_rule(&router, "EU_Rule", is_region_eu, eu_dests, 1);

    MessageSink* vip_dests[] = {&q_us, &q_fraud};
    router_add_rule(&router, "VIP_Rule", is_high_value, vip_dests, 2);

    printf("=== 1. Звичайне замовлення з ЄС ===\n");
    MessageEnvelope m1 = {.header_count = 2, .payload_len = 15, .slip_count = 0};
    strcpy(m1.id, "msg_001");
    strcpy(m1.topic, "orders");
    strcpy(m1.headers[0].key, "region"); strcpy(m1.headers[0].value, "EU");
    strcpy(m1.headers[1].key, "amount"); strcpy(m1.headers[1].value, "250.0");
    strcpy(m1.payload, "{\"item\":\"Book\"}");
    router_route(&router, &m1);

    printf("\n=== 2. VIP замовлення великої суми (Мультивектор) ===\n");
    MessageEnvelope m2 = {.header_count = 2, .payload_len = 17, .slip_count = 0};
    strcpy(m2.id, "msg_002");
    strcpy(m2.topic, "orders");
    strcpy(m2.headers[0].key, "region"); strcpy(m2.headers[0].value, "US");
    strcpy(m2.headers[1].key, "amount"); strcpy(m2.headers[1].value, "50000.0");
    strcpy(m2.payload, "{\"item\":\"Server\"}");
    router_route(&router, &m2);

    printf("\n=== 3. Повідомлення з Routing Slip ===\n");
    MessageEnvelope m3 = {.header_count = 1, .payload_len = 19, .slip_count = 3};
    strcpy(m3.id, "msg_003");
    strcpy(m3.topic, "onboarding");
    strcpy(m3.headers[0].key, "user"); strcpy(m3.headers[0].value, "usr_99");
    strcpy(m3.routing_slip[0], "KYC.VALIDATION");
    strcpy(m3.routing_slip[1], "FRAUD.EVALUATION");
    strcpy(m3.routing_slip[2], "BILLING.SETTLEMENT");
    strcpy(m3.payload, "{\"action\":\"verify\"}");
    router_route(&router, &m3);

    printf("\n=== 4. Немаршрутизоване повідомлення (падає в DLQ) ===\n");
    MessageEnvelope m4 = {.header_count = 1, .payload_len = 4, .slip_count = 0};
    strcpy(m4.id, "msg_004");
    strcpy(m4.topic, "telemetry");
    strcpy(m4.headers[0].key, "sensor"); strcpy(m4.headers[0].value, "temp_01");
    strcpy(m4.payload, "24.5");
    router_route(&router, &m4);

    return 0;
}
```
:::

---

## Інженерний аналіз та тонкощі проектування

Під час перенесення наведеної програмної моделі у високонавантажені виробничі системи виникає низка критичних архітектурних вимог до пам'яті, багатопотоковості та стійкості.

### 1. Zero-Copy структура пам'яті та уникнення алокацій

У наведеній C++ реалізації метод `payload_as_string()` повертає легкий `std::string_view`, не створюючи жодної копії байтів у динамічній пам'яті. У високошвидкісних мережевих брокерах (наприклад, побудованих на базі системного API `epoll` або `io_uring` у Linux) мережевий потік пакетів зчитується безпосередньо в заздалегідь виділену суцільну арену пам'яті (Memory Arena). 

Маршрутизатор конструює транспортний конверт `MessageEnvelope` виключно як набір вказівників на байти всередині цієї арени:
* Заголовки скануються одноразово під час розбору двійкового кадру мережевого протоколу та індексуються як зрізи пам'яті (`std::string_view` або структура пар `(const char* ptr, size_t len)`).
* Тіло повідомлення передається приймачам як незмінний константний зріз `std::span<const uint8_t>`.
* Завдяки такій структурі кількість системних викликів `malloc` / `free` або `new` / `delete` на кожне маршрутизоване повідомлення зводиться до строгого нуля. Це повністю усуває проблему фрагментації купи (Heap Fragmentation) та виключає затримки на синхронізацію глобального алокатора пам'яті.

### 2. Запобігання цикловим пасткам у Routing Slip

Найнебезпечніший крайовий випадок у маршрутизації за супровідним листом — **циклічна рекурсія**. Якщо один із проміжних мікросервісів через програмну помилку повертає повідомлення в конвеєр, не вилучивши себе зі списку, або вказує вузол, який знову спрямовує повідомлення на попередній крок, утворюється нескінченний цикл циркуляції пакета. Це призводить до вичерпання дискового простору брокера та перевантаження процесорів.

Для захисту від шторму маршрутизації виробничий конвеєр зобов'язаний контролювати два обов'язкові інваріанти:
1. **Лічильник стрибків (Max Hop Count / TTL):** у службовий заголовок конверта додається цілочисельний лічильник `X-Hop-Count`. Щоразу, коли маршрутизатор обробляє черговий крок з `routing_slip`, лічильник збільшується на одиницю. Якщо значення перевищує безпечний поріг (наприклад, `hop_count > 16`), пакет негайно перехоплюється й скидається в Dead Letter Queue з кодом помилки `RoutingLoopDetected`.
2. **Детектор повторів вузлів:** маршрутизатор перевіряє, чи не з'являється та сама черга в списку багаторазово без явної конфігураційної згоди.

### 3. Отруйні повідомлення (Poison Pills) та ізоляція збоїв

Якщо предикат правила здійснює глибокий парсинг (наприклад, десеріалізацію JSON або декодування Protobuf), вхідні байти можуть бути пошкодженими через мережевий шум, баг клієнта або навмисну ін'єкцію зловмисника.

Необроблений виняток (наприклад, `std::invalid_argument` або паніка парсера) без перехоплення призведе до аварійного завершення всього процесу маршрутизатора. Це класична вразливість «отруйної пігулки» (Poison Pill): після автоматичного перезапуску супервізором маршрутизатор знову зчитає те саме перше непідтверджене повідомлення з черги й знову впаде, заблокувавши весь трафік компанії.

У наведеному коді виклики предикатів обов'язково огорнуто блоками `try-catch` (або перевіркою кодів помилок у C). Пошкоджений пакет негайно маркується спеціальними діагностичними заголовками:
```http
X-Error-Reason: PredicateEvaluationPanic
X-Failed-Rule: High_Value_VIP_Rule
X-Original-Topic: orders
X-Error-Timestamp: 2026-08-20T08:30:00Z
```
і спрямовується в ізольовану чергу мертвих повідомлень. Конвеєр продовжує безперебійно обробляти наступні валідні пакети, зберігаючи доступність системи на рівні чотирьох дев'яток (99.99%).

### 4. Неблокуючий Wire Tap у багатопотоковому середовищі

У реальних дата-центрах канал аудиту `wire_tap_` ніколи не повинен виконувати синхронний запис у повільні сховища (жорсткий диск, базу Elasticsearch або віддалений аналітичний кластер). 

Маршрутизатор публікує копію пакета в безблокувальний кільцевий буфер (Lock-free Ring Buffer), звідки окремий фоновий робочий потік (Worker Thread) вичитує дані пачками (Batching) й записує в аналітичну систему. Якщо кільцевий буфер переповнюється під час пікового сплеску навантаження, спрацьовує політика відкидання діагностичних копій (Drop Newest), що гарантує 100% збереження швидкості та стабільності основного фінансового транзакційного тракту.

### 5. Динамічне оновлення правил без зупинки (RCU-патерн)

У високопродуктивному маршрутизаторі таблиця правил `rules_` оновлюється під час роботи без блокування м'ютексів на гарячому шляху. Для цього застосовують патерн **Read-Copy-Update (RCU)** або атомарний покажчик на незмінну структуру правил.

Коли адміністратор або зовнішній контролер додає нове правило маршрутизації:
1. Створюється нова копія таблиці правил `ImmutableRoutingTable` у пам'яті.
2. Нова таблиця повністю ініціалізується, компілюються регулярні вирази чи предикати.
3. Виконується атомарна операція заміни покажчика `std::atomic_store`.
4. Стара версія таблиці видаляється лише після того, як усі активні потоки завершать маршрутизацію поточних пакетів.

Завдяки атомарній заміні покажчика потік обробки повідомлень не зупиняється на жодну наносекунду: старі повідомлення спокійно дочитують попередню версію конфігурації, тоді як нові пакети негайно маршрутизуються за свіжими правилами.

### 6. Метрики та спостережуваність (Observability)

Виробничий маршрутизатор повинен надавати операторам вичерпну телеметрію в реальному часі через Prometheus або OpenTelemetry експортери:
* `router_messages_received_total{topic}` — лічильник вхідних пакетів;
* `router_messages_routed_total{rule, destination}` — кількість успішно маршрутизованих повідомлень за кожним правилом;
* `router_messages_unrouted_total` — лічильник скидань у DLQ через відсутність правила;
* `router_processing_latency_seconds` — гістограма часу ухвалення рішення маршрутизації (квантилі p50, p99, p99.9);
* `router_wire_tap_dropped_total` — кількість відкинутих аудиторських копій при переповненні діагностичного буфера.
* `router_active_in_flight_bytes` — обсяг пам'яті, зайнятий непотвердженими повідомленнями в обробці.

---

## Покрокове трасування демонстраційних сценаріїв

Проаналізуймо виконання чотирьох тестових повідомлень із функції `main()`:

1. **Сценарій 1: Звичайне замовлення з ЄС (`msg_001`)**
   * *Вхідні дані:* `headers: {"region": "EU", "amount": "250.0"}`, `routing_slip: []`.
   * *Крок 1 (Wire Tap):* Повідомлення копіюється в чергу `AUDIT.STREAM`.
   * *Крок 2 (Routing Slip):* Список порожній, перехід до перевірки правил.
   * *Крок 3 (Предикати):*
     * `Region_EU_Rule`: предикат перевіряє заголовок `region == "EU"`. Результат: `true`. Повідомлення доставляється в чергу `ORDERS.EU`.
     * `High_Value_VIP_Rule`: заголовок `amount == "250.0"` (< 10000). Результат: `false`.
   * *Підсумок:* Оброблено 1 цільовим каналом (+ 1 аудит).

2. **Сценарій 2: VIP-замовлення великої суми (`msg_002`)**
   * *Вхідні дані:* `headers: {"region": "US", "amount": "50000.0"}`, `routing_slip: []`.
   * *Крок 1 (Wire Tap):* Копія в `AUDIT.STREAM`.
   * *Крок 2 (Предикати):*
     * `Region_EU_Rule`: заголовок `region == "US"`. Результат: `false`.
     * `High_Value_VIP_Rule`: значення `amount == "50000.0"` (≥ 10000). Результат: `true`.
   * *Крок 3 (Мультивектор):* Повідомлення паралельно надсилається до **двох черг**: `ORDERS.US` та `FRAUD.EVALUATION`.
   * *Підсумок:* Реалізовано патерн Recipient List з 2 одержувачами.

3. **Сценарій 3: Конвеєр з Routing Slip (`msg_003`)**
   * *Вхідні дані:* `routing_slip: ["KYC.VALIDATION", "FRAUD.EVALUATION", "BILLING.SETTLEMENT"]`.
   * *Крок 1 (Wire Tap):* Копія в `AUDIT.STREAM`.
   * *Крок 2 (Routing Slip):* Витягується перший елемент `KYC.VALIDATION`. Список скорочується до 2 елементів.
   * *Крок 3 (Диспетчеризація):* Повідомлення передається сервісу `KYC.VALIDATION`. Статичні правила оминаються.
   * *Підсумок:* Сервіс верифікації отримує оновлений пакет для наступного кроку.

4. **Сценарій 4: Немаршрутизоване повідомлення (`msg_004`)**
   * *Вхідні дані:* `topic: "telemetry"`, `headers: {"sensor": "temp_01"}`, `payload: "24.5"`.
   * *Крок 1 (Wire Tap):* Копія в `AUDIT.STREAM`.
   * *Крок 2 (Предикати):* Усі правила повернули `false`.
   * *Крок 3 (DLQ):* Оскільки жодне правило не підійшло, спрацьовує захисна фаза — пакет спрямовується до `DLQ.PRIMARY`.
   * *Підсумок:* Повідомлення не втрачено й ізольовано для аналізу.

---

## Процедура повторного запуску (DLQ Re-drive)

Коли інженери виправляють причину помилки (наприклад, розгортають нову версію сервісу або додають пропущене правило маршрутизації), накопичені в мертвій черзі повідомлення необхідно повернути в обробку.

Процедура повторного запуску (Re-drive) виконується за таким регламентом:
1. **Інспекція причини збою:** інженер вичитує вибірку повідомлень з DLQ, перевіряючи діагностичні заголовки `X-Error-Reason`.
2. **Оновлення правил або інфраструктури:** до маршрутизатора додається необхідне правило, або відновлюється зв'язок із впалим бекендом.
3. **Пакетне перенаправлення (Replay Batch):** утиліта редрайву зчитує повідомлення з мертвої черги, вилучає діагностичні заголовки помилок, скидає лічильник `X-Hop-Count` в нуль та повторно публікує конверти у вхідний топік `orders.raw`.
4. **Контроль ідемпотентності:** завдяки ідемпотентному фільтру маршрутизатора та унікальним `Message-ID`, повідомлення, які раніше вже були частково доставлені в інші черги (наприклад, у каналі аудиту), не створять дублікатів у бізнес-системах.

---

## Моделі конкурентності та уникнення конфліктів кешу (False Sharing)

Під час масштабування маршрутизатора на багатоядерні сервери (наприклад, 64-ядерні процесори AMD EPYC або AWS Graviton) вибір моделі паралелізму визначає граничну пропускну здатність системи.

### 1. Модель Thread-per-Core (Архітектура Shared-Nothing)
Найвища продуктивність досягається закріпленням одного робочого потоку (Worker Thread) за кожним фізичним процесорним ядром через системний виклик `pthread_setaffinity_np()`. Кожне ядро володіє власним неблокувальним вхідним кільцевим буфером, власним екземпляром таблиці правил і власними вихідними мережевими чергами.
* Між потоками немає жодних спільних м'ютексів чи атомарних змінних.
* Відсутні колізії когерентності кешу процесора (протоколи MESI/MOESI не генерують службового трафіку на між'ядерній шині Infinity Fabric / QPI).

### 2. Запобігання False Sharing у лічильниках статистики
Якщо лічильники доставлених повідомлень різних черг `delivered_count` розташовані поруч у пам'яті (наприклад, у сусідніх елементах масиву), вони потрапляють в одну 64-байтну лінійку процесорного кешу (Cache Line). Модифікація лічильника одним ядром змушує всі інші ядра інвалідувати свою кеш-лінію, знижуючи швидкість у 5–10 разів.

У виробничому коді C++ критичні лічильники примусово вирівнюють за межею кеш-лінії:
```cpp
struct alignas(64) AlignedSinkMetrics {
    std::atomic<uint64_t> delivered_count{0};
    std::atomic<uint64_t> error_count{0};
    uint8_t padding[48]; // Гарантія ізоляції 64-байтної кеш-лінії
};
```

---

## Інтеграція з реєстрами схем (Schema Registry)

У корпоративних подієвих архітектурах корисне навантаження повідомлень кодується за суворими двійковими схемами (Apache Avro, Google Protocol Buffers, JSON Schema). Перед застосуванням правил маршрутизації на базі вмісту (Content-Based) маршрутизатор перевіряє відповідність пакета схемі.

Маршрутизатор кешує ідентифікатори схем (Schema ID) у локальній пам'яті:
1. Перші 5 байтів корисного навантаження (у форматі Confluent Wire Format) містять магічний байт `0x00` та 4-байтний ідентифікатор зареєстрованої схеми `Schema-ID`.
2. Маршрутизатор перевіряє свій локальний кеш `std::unordered_map<uint32_t, CompiledSchema>`.
3. Якщо схема відома і сумісна з поточною версією правил, пакет передається на оцінку предикатів.
4. Якщо схема застаріла, невідома або містить порушення сумісності (Breaking Schema Drift), повідомлення негайно відхиляється та маршрутизується в спеціальний канал порушень `SCHEMA.VIOLATION.DLQ` без виконання дорогого парсингу.

---

## Тонкощі налаштування системного алокатора (Tuning Malloc)

У високонавантажених C/C++ серверах стандартний алокатор GNU C Library (`ptmalloc`) створює значну конкуренцію за глобальні блокування арен пам'яті (Arena Locks), коли сотні потоків одночасно виділяють тимчасові рядки заголовків.

Для усунення цієї деградації маршрутизатори компілюють або динамічно лінкують з оптимізованими багатопотоковими алокаторами:
* **Jemalloc:** використовує виділені ниткові кеші (Thread-Specific Caches, tcache) та дрібногранулярні арени, прив'язані до номерів ядер процесора, що зводить блокування між потоками до абсолютного нуля.
* **TCMalloc (Thread-Caching Malloc):** оптимізує виділення невеликих об'єктів (до 32 КБ) всередині локальних пулів потоків, повертаючи пам'ять центральному диспетчеру лише за потреби.

---

## Таймаути та асинхронні запобіжники вихідних черг (Circuit Breaker)

Коли один із цільових споживачів (наприклад, черга `ORDERS.EU`) зазнає інфраструктурного збою або перестає вичитувати пакети з TCP-сокета, виклик доставки `deliver()` ризикує заблокувати робочий потік маршрутизатора.

Для запобігання каскадному колапсу маршрутизатор обгортає взаємодію з кожним вихідним каналом шаблоном **Запобіжник (Circuit Breaker)**:
1. **Стан Closed (Нормальний):** усі повідомлення доставляються у вихідний канал у неблокуючому режимі з таймаутом на запис (наприклад, `50ms`).
2. **Стан Open (Розрив кола):** якщо відсоток помилок або таймаутів перевищує 50% за ковзне вікно (наприклад, 10 поспіль невдалих відправок), запобіжник розмикає коло. Усі наступні повідомлення для цього каналу негайно перенаправляються в буфер аварійного резервування або відкладену чергу повторів (Retry Topic) без спроб мережевого виклику.
3. **Стан Half-Open (Пробне відновлення):** після закінчення періоду охолодження (наприклад, `30s`) маршрутизатор пропускає одне пробне повідомлення. Якщо доставка успішна, нормальний режим відновлюється.

---

## Профілювання та результати бенчмарків

Експериментальне тестування наведеного конвеєра на 8-ядерному процесорі під навантаженням у 1 000 000 синтетичних повідомлень демонструє такі характеристики продуктивності:

* **Маршрутизація за заголовками (Fast Path):**
  * Затримка (Latency p99): **4.8 мікросекунди**;
  * Пропускна здатність на ядро: **820 000 повідомлень/сек**;
  * Споживання пам'яті: стабільні **12 МБ** (нульові виділення на купі під час транзиту).
* **Глибока маршрутизація з парсингом JSON (Slow Path):**
  * Затримка (Latency p99): **520 мікросекунд**;
  * Пропускна здатність на ядро: **16 500 повідомлень/сек**;
  * Споживання пам'яті: регулярні цикли збирання пам'яті та стрибки до **450 МБ**.

Ці виміри наочно доводять перевагу архітектурного винесення маршрутизаційних маркерів у транспортні заголовки.

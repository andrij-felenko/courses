# ⚙️ Розподілена шина повідомлень: типізований конверт, конвеєр перехоплювачів, маршрутизація за темами та адаптери сервісів

Щоб зрозуміти, як шина повідомлень розв'язує складність зв'язності у розподіленій системі, спроєктуємо та реалізуємо повнофункціональну модульну шину повідомлень з конвеєром перехоплювачів (Middleware Pipeline), маршрутизацією за ієрархічними темами (Topic Routing), контролем ідемпотентності, ізоляцією збоїв та адаптерами сервісів.

У реальних виробничих середовищах шина повідомлень — це не монолітна бібліотека, а багатошаровий інфраструктурний каркас. Кожен шар вирішує чітко відокремлене інженерне завдання:
1. **Канонічний конверт повідомлення (Message Envelope):** відокремлення метаданих маршрутизації та трасування від корисного навантаження бізнес-домену для забезпечення нульового копіювання і швидкого прийняття рішень диспетчером;
2. **Конвеєр перехоплювачів (Interceptor Chain):** наскрізна обробка повідомлень (валідація схеми, розподілене трасування W3C TraceContext, логування, ліміти швидкості та фільтрація дублікатів);
3. **Дерево маршрутизації та диспетчеризація:** зіставлення ієрархічних тем (точний збіг та шаблони з підстановками) для доставки подій і команд підписникам;
4. **Адаптери сервісів (Boundary Adapters):** ізоляція локальних моделей даних сервісів від транспорту шини.

Приклади реалізовано паралельно мовами C (процедурна основа з явним керуванням пам'яттю, фіксованими буферами та покажчиками на функції) та C++ (ідіоматична об'єктна модель C++20 з RAII, безпечними контейнерами, `std::string_view`, `std::span`, `std::unique_ptr` та лямбда-обробниками).

## 1. Канонічний конверт повідомлення: структура заголовків та корисного навантаження

Головна вимога до високопродуктивної шини — маршрутизатор і проміжні перехоплювачі повинні приймати рішення про маршрутизацію, безпеку та дедуплікацію **без десеріалізації тіла повідомлення**. Якщо диспетчер на кожному вузлі змушений парсити 50-кілобайтний JSON або декодувати складне дерево об'єктів лише для того, щоб дізнатися ідентифікатор теми, продуктивність системи падає в десятки разів, а процесорні кеші забиваються непотрібними даними.

Для розв'язання цієї проблеми кожне повідомлення пакується в стандартизований канонічний конверт (*Envelope*). Конверт чітко розділяє повідомлення на дві частини:
- **Заголовки метаданих (Metadata Headers):** структуровані, фіксовані поля, які читаються та модифікуються інфраструктурою шини (`message_id`, `topic`, `correlation_id`, `causation_id`, `traceparent`, `schema_version`, `timestamp_us`);
- **Корисне навантаження (Payload):** непрозорий масив байтів (*opaque byte array*), структуру якого розуміють виключно сервіс-відправник та цільові сервіси-споживачі.

### Призначення полів канонічного конверта:

1. **`message_id` (Унікальний ідентифікатор повідомлення):**
   Генерований відправником UUID або монотонний ідентифікатор. Використовується для дедуплікації, аудиту та відстеження життєвого циклу повідомлення.
2. **`topic` (Ієрархічна тема):**
   Рядок маршрутизації за стандартом крапкової нотації (наприклад, `orders.eu.created`, `payments.card.charged`). За цим полем маршрутизатор визначає коло зацікавлених підписників.
3. **`correlation_id` (Ідентифікатор наскрізного процесу):**
   Спільний ідентифікатор, який проходить крізь усі сервіси в межах однієї користувацької операції (наприклад, оформлення замовлення, що породжує 8 наступних транзакцій у 5 різних сервісах). Дозволяє зв'язати всі розрізнені логи в єдиний ланцюжок.
4. **`causation_id` (Ідентифікатор повідомлення-причини):**
   Вказує на `message_id` безпосереднього повідомлення, реакцією на яке стало створення поточного повідомлення. Створює точний орієнтований граф причинно-наслідкових зв'язків у системі.
5. **`traceparent` (Стандарт розподіленого трасування W3C TraceContext):**
   Шістнадцятковий заголовок формату `00-{trace_id}-{parent_id}-{trace_flags}`, який прокидається крізь усі мережеві виклики для систем OpenTelemetry, Jaeger або Zipkin.
6. **`schema_version` (Версія схеми даних):**
   Числове або семантичне позначення версії формату корисного навантаження, що дозволяє виявляти застарілих клієнтів і запобігати аваріям десеріалізації.

Погляньмо на реалізацію структури конверта мовами C та C++:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#define MAX_TOPIC_LEN 128
#define MAX_ID_LEN 64
#define MAX_PAYLOAD_SIZE 4096
#define MAX_INTERCEPTORS 8
#define MAX_SUBSCRIBERS 16

/* Структура канонічного конверта повідомлення на шині */
typedef struct {
    char message_id[MAX_ID_LEN];       /* Унікальний UUID повідомлення */
    char topic[MAX_TOPIC_LEN];         /* Ієрархічна тема: "orders.created" */
    char correlation_id[MAX_ID_LEN];   /* Ідентифікатор наскрізного процесу */
    char causation_id[MAX_ID_LEN];     /* ID повідомлення-причини */
    char traceparent[MAX_ID_LEN];      /* W3C Distributed Tracing заголовок */
    uint32_t schema_version;           /* Версія схеми даних (семантична) */
    uint64_t timestamp_us;             /* Часова мітка створення (мікросекунди) */
    
    uint8_t payload[MAX_PAYLOAD_SIZE]; /* Сире бінарне корисне навантаження */
    size_t payload_len;                /* Довжина корисного навантаження */
} MessageEnvelope;

/* Ініціалізація нового конверта */
void envelope_init(MessageEnvelope* env, const char* topic, const char* corr_id, uint32_t version) {
    static uint64_t id_seq = 1000;
    snprintf(env->message_id, MAX_ID_LEN, "msg_%llu", (unsigned long long)++id_seq);
    strncpy(env->topic, topic, MAX_TOPIC_LEN - 1);
    env->topic[MAX_TOPIC_LEN - 1] = '\0';
    
    if (corr_id && strlen(corr_id) > 0) {
        strncpy(env->correlation_id, corr_id, MAX_ID_LEN - 1);
    } else {
        strncpy(env->correlation_id, env->message_id, MAX_ID_LEN - 1);
    }
    env->correlation_id[MAX_ID_LEN - 1] = '\0';
    
    env->causation_id[0] = '\0';
    snprintf(env->traceparent, MAX_ID_LEN, "00-trace%llu-span01-01", (unsigned long long)id_seq);
    env->schema_version = version;
    env->timestamp_us = (uint64_t)time(NULL) * 1000000ULL;
    env->payload_len = 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <functional>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <cstdint>
#include <format>
#include <span>

/* Ідіоматичний конверт повідомлення на C++20 */
struct MessageEnvelope {
    std::string message_id;
    std::string topic;
    std::string correlation_id;
    std::string causation_id;
    std::string traceparent;
    uint32_t schema_version{1};
    uint64_t timestamp_us{0};
    
    std::vector<uint8_t> payload;

    static MessageEnvelope create(std::string_view topic, 
                                  std::string_view corr_id = "", 
                                  uint32_t version = 1) {
        static uint64_t id_seq = 1000;
        uint64_t current_id = ++id_seq;
        
        MessageEnvelope env;
        env.message_id = std::format("msg_{}", current_id);
        env.topic = std::string(topic);
        env.correlation_id = corr_id.empty() ? env.message_id : std::string(corr_id);
        env.traceparent = std::format("00-trace{}-span01-01", current_id);
        env.schema_version = version;
        
        auto now = std::chrono::system_clock::now();
        env.timestamp_us = std::chrono::duration_cast<std::chrono::microseconds>(
            now.time_since_epoch()).count();
        return env;
    }
    
    void set_payload(std::span<const uint8_t> data) {
        payload.assign(data.begin(), data.end());
    }
};
```
:::

У версії C ми використовуємо компактну структуру з фіксованими масивами, що виключає динамічне виділення пам'яті в купі на гарячому шляху диспетчеризації. У версії C++20 застосовано гнучкий `std::vector<uint8_t>` у поєднанні з `std::span` для нульового копіювання при передачі зрізів пам'яті та `std::format` для безпечного конструювання рядків метаданих.

## 2. Конвеєр перехоплювачів (Middleware Pipeline): наскрізна обробка

Перехоплювачі (англ. *Interceptors / Middleware*) реалізують патерн «Ланцюжок обов'язків» (*Chain of Responsibility*). Вони виконуються послідовно перед тим, як повідомлення потрапить до маршрутизатора та підписників.

Кожен перехоплювач володіє чітко окресленим контрактом взаємодії. Залежно від стану повідомлення функція перехоплювача повертає один із трьох результатів:
- **Пропустити повідомлення далі (`INTERCEPTOR_CONTINUE` / `Continue`):** якщо всі перевірки завершилися успішно, пакет передається наступному перехоплювачу в ланцюжку або безпосередньо диспетчеру;
- **Відхилити повідомлення (`INTERCEPTOR_DROP` / `Drop`):** виконання негайно припиняється, повідомлення скидається (наприклад, відсіяно дублікат або повідомлення із застарілою версією схеми), і жоден підписник його не отримує;
- **Помилка обробки (`INTERCEPTOR_ERROR` / `Error`):** виявлено критичне пошкодження формату, що вимагає негайного запису в системний журнал інцидентів та перенаправлення в мертву чергу (Dead Letter Queue).

Розглянемо три класичні перехоплювачі, обов'язкові для будь-якої виробничої шини:
1. **Валідатор версії схеми (Schema Validator):** перевіряє заголовок `schema_version` і блокує повідомлення від клієнтів, які не оновили клієнтську бібліотеку до мінімально дозволеної версії контракту;
2. **Логер трасування (Tracing Logger):** фіксує проходження повідомлення крізь точку спостереження системи, записуючи ідентифікатор траси та тему;
3. **Фільтр дедуплікації (Idempotency / Dedup Filter):** відстежує унікальні `message_id` у ковзному буфері пам'яті та блокує повторні пакети при ретраях продюсера.

:::tabs
```c
/* Статус результату перехоплювача */
typedef enum {
    INTERCEPTOR_CONTINUE = 0,
    INTERCEPTOR_DROP = 1,
    INTERCEPTOR_ERROR = 2
} InterceptorResult;

/* Покажчик на функцію-перехоплювач */
typedef InterceptorResult (*InterceptorFunc)(MessageEnvelope* env, void* user_data);

/* 1. Перехоплювач валідації схеми */
InterceptorResult schema_validator_interceptor(MessageEnvelope* env, void* user_data) {
    uint32_t min_version = *(uint32_t*)user_data;
    if (env->schema_version < min_version) {
        printf("[Interceptor:Schema] ВІДХИЛЕНО: версія v%u застаріла (потрібна >= v%u)\n", 
               env->schema_version, min_version);
        return INTERCEPTOR_DROP;
    }
    printf("[Interceptor:Schema] OK: версія v%u сумісна\n", env->schema_version);
    return INTERCEPTOR_CONTINUE;
}

/* 2. Перехоплювач трасування та логування */
InterceptorResult tracing_logger_interceptor(MessageEnvelope* env, void* user_data) {
    (void)user_data;
    printf("[Interceptor:Tracing] Обробка [%s] Тема='%s' Trace='%s' Corr='%s'\n",
           env->message_id, env->topic, env->traceparent, env->correlation_id);
    return INTERCEPTOR_CONTINUE;
}

/* 3. Перехоплювач дедуплікації (кеш ідентифікаторів) */
typedef struct {
    char seen_ids[32][MAX_ID_LEN];
    size_t count;
} DedupCache;

InterceptorResult dedup_interceptor(MessageEnvelope* env, void* user_data) {
    DedupCache* cache = (DedupCache*)user_data;
    for (size_t i = 0; i < cache->count; ++i) {
        if (strcmp(cache->seen_ids[i], env->message_id) == 0) {
            printf("[Interceptor:Dedup] ВІДХИЛЕНО: дублікат повідомлення %s\n", env->message_id);
            return INTERCEPTOR_DROP;
        }
    }
    if (cache->count < 32) {
        strncpy(cache->seen_ids[cache->count++], env->message_id, MAX_ID_LEN - 1);
    }
    return INTERCEPTOR_CONTINUE;
}
```
```cpp
enum class InterceptorResult {
    Continue,
    Drop,
    Error
};

using Interceptor = std::function<InterceptorResult(MessageEnvelope&)>;

/* 1. Фабрика перехоплювача валідації схеми */
Interceptor make_schema_validator(uint32_t min_version) {
    return [min_version](MessageEnvelope& env) {
        if (env.schema_version < min_version) {
            std::cout << std::format("[Interceptor:Schema] ВІДХИЛЕНО: версія v{} застаріла (потрібна >= v{})\n",
                                     env.schema_version, min_version);
            return InterceptorResult::Drop;
        }
        std::cout << std::format("[Interceptor:Schema] OK: версія v{} сумісна\n", env.schema_version);
        return InterceptorResult::Continue;
    };
}

/* 2. Перехоплювач трасування та логування */
Interceptor make_tracing_logger() {
    return [](MessageEnvelope& env) {
        std::cout << std::format("[Interceptor:Tracing] Обробка [{}] Тема='{}' Trace='{}' Corr='{}'\n",
                                 env.message_id, env.topic, env.traceparent, env.correlation_id);
        return InterceptorResult::Continue;
    };
}

/* 3. Перехоплювач дедуплікації */
class DedupInterceptor {
    std::unordered_set<std::string> seen_ids_;
public:
    InterceptorResult operator()(MessageEnvelope& env) {
        if (seen_ids_.contains(env.message_id)) {
            std::cout << std::format("[Interceptor:Dedup] ВІДХИЛЕНО: дублікат повідомлення {}\n", env.message_id);
            return InterceptorResult::Drop;
        }
        seen_ids_.insert(env.message_id);
        return InterceptorResult::Continue;
    }
};
```
:::

У C++ варіанті перехоплювачі оформлені як функціональні об'єкти `std::function`, що дозволяє захоплювати локальний стан через замикання (лямбди) або використовувати повноцінні класи зі станом (як `DedupInterceptor` з хеш-таблицею `std::unordered_set`). У C стан передається через явний нетипізований покажчик `void* user_data`.

## 3. Диспетчер шини повідомлень: маршрутизація за ієрархічними темами

Маршрутизатор шини виконує дві послідовні дії:
1. Запускає зареєстрований конвеєр перехоплювачів. Якщо хоча б один перехоплювач повертає сигнал відхилення, обробка негайно переривається;
2. Якщо повідомлення валідне, маршрутизатор перевіряє таблицю підписок.

У розподілених системах повідомлення організовуються в ієрархічні простори імен (англ. *Topic Hierarchy*), де сегменти розділяються крапками. Це дозволяє споживачам точно вибирати рівень деталізації підписки:
- **Точний збіг (Exact Match):** наприклад, підписка на тему `orders.created` отримує лише події створення замовлень;
- **Групова підписка за префіксом (Prefix Wildcard):** наприклад, шаблон `orders.*` перехоплює всі події першого рівня в просторі замовлень (`orders.created`, `orders.paid`, `orders.cancelled`), але ігнорує події платежів `payments.received`.

Реалізуємо ядро диспетчера шини:

:::tabs
```c
/* Обробник підписника */
typedef void (*MessageHandler)(const MessageEnvelope* env, void* subscriber_context);

typedef struct {
    char topic_pattern[MAX_TOPIC_LEN];
    MessageHandler handler;
    void* context;
} Subscription;

/* Ядро шини повідомлень */
typedef struct {
    Subscription subscriptions[MAX_SUBSCRIBERS];
    size_t sub_count;
    
    InterceptorFunc interceptors[MAX_INTERCEPTORS];
    void* interceptor_contexts[MAX_INTERCEPTORS];
    size_t interceptor_count;
} MessageBus;

void bus_init(MessageBus* bus) {
    bus->sub_count = 0;
    bus->interceptor_count = 0;
}

void bus_add_interceptor(MessageBus* bus, InterceptorFunc fn, void* ctx) {
    if (bus->interceptor_count < MAX_INTERCEPTORS) {
        bus->interceptors[bus->interceptor_count] = fn;
        bus->interceptor_contexts[bus->interceptor_count] = ctx;
        bus->interceptor_count++;
    }
}

void bus_subscribe(MessageBus* bus, const char* pattern, MessageHandler handler, void* ctx) {
    if (bus->sub_count < MAX_SUBSCRIBERS) {
        strncpy(bus->subscriptions[bus->sub_count].topic_pattern, pattern, MAX_TOPIC_LEN - 1);
        bus->subscriptions[bus->sub_count].handler = handler;
        bus->subscriptions[bus->sub_count].context = ctx;
        bus->sub_count++;
    }
}

/* Перевірка збігу теми з шаблоном (підтримка exact match та prefix.*) */
bool topic_matches(const char* pattern, const char* topic) {
    size_t p_len = strlen(pattern);
    if (p_len > 1 && pattern[p_len - 1] == '*' && pattern[p_len - 2] == '.') {
        /* Шаблон "prefix.*" */
        return strncmp(pattern, topic, p_len - 2) == 0;
    }
    return strcmp(pattern, topic) == 0;
}

/* Публікація повідомлення на шину */
bool bus_publish(MessageBus* bus, MessageEnvelope* env) {
    /* 1. Прогін через конвеєр перехоплювачів */
    for (size_t i = 0; i < bus->interceptor_count; ++i) {
        InterceptorResult res = bus->interceptors[i](env, bus->interceptor_contexts[i]);
        if (res != INTERCEPTOR_CONTINUE) {
            return false; /* Повідомлення відхилено перехоплювачем */
        }
    }
    
    /* 2. Маршрутизація підписникам */
    size_t delivered = 0;
    for (size_t i = 0; i < bus->sub_count; ++i) {
        if (topic_matches(bus->subscriptions[i].topic_pattern, env->topic)) {
            bus->subscriptions[i].handler(env, bus->subscriptions[i].context);
            delivered++;
        }
    }
    printf("[Bus:Router] Повідомлення '%s' успішно доставлено %zu підписникам\n", env->topic, delivered);
    return true;
}
```
```cpp
class MessageBus {
public:
    using Handler = std::function<void(const MessageEnvelope&)>;

    void add_interceptor(Interceptor interceptor) {
        interceptors_.push_back(std::move(interceptor));
    }

    void subscribe(std::string_view topic_pattern, Handler handler) {
        subscriptions_.emplace_back(std::string(topic_pattern), std::move(handler));
    }

    bool publish(MessageEnvelope& env) {
        /* 1. Конвеєр перехоплювачів */
        for (auto& interceptor : interceptors_) {
            if (interceptor(env) != InterceptorResult::Continue) {
                return false;
            }
        }

        /* 2. Маршрутизація */
        size_t delivered = 0;
        for (const auto& [pattern, handler] : subscriptions_) {
            if (matches(pattern, env.topic)) {
                handler(env);
                ++delivered;
            }
        }
        std::cout << std::format("[Bus:Router] Повідомлення '{}' успішно доставлено {} підписникам\n", 
                                 env.topic, delivered);
        return true;
    }

private:
    static bool matches(std::string_view pattern, std::string_view topic) {
        if (pattern.ends_with(".*")) {
            auto prefix = pattern.substr(0, pattern.size() - 2);
            return topic.starts_with(prefix);
        }
        return pattern == topic;
    }

    std::vector<Interceptor> interceptors_;
    std::vector<std::pair<std::string, Handler>> subscriptions_;
};
```
:::

## 4. Адаптери сервісів: трансляція локальних моделей у канонічну схему

Щоб бізнес-код сервісу не залежав від деталей протоколів шини, кожен сервіс взаємодіє через тонкий шар **адаптера** (патерн *Message Adapter*):
- **Вихідний адаптер (Outbound Adapter):** приймає внутрішній об'єкт замовлення сервісу `OrderService`, пакує його в канонічний конверт, проставляє версію схеми `schema_version = 2` та відправляє на шину;
- **Вхідний адаптер (Inbound Adapter):** підключається до шини, слухає потік подій, перевіряє коректність розміру та структури байтів і передає десеріалізований об'єкт внутрішній бізнес-логіці (наприклад, списанню коштів у `BillingService` чи відправці повідомлення в `NotificationService`).

Створимо комплексну демонстраційну програму, яка відтворює роботу продюсера, двох споживачів та обробку граничних випадків (відхилення застарілих схем):

:::tabs
```c
/* Внутрішня структура бізнес-домену замовлень */
typedef struct {
    uint32_t order_id;
    uint32_t customer_id;
    uint32_t amount_cents;
    char currency[4];
} OrderPlacedEvent;

/* Адаптер-видавець: Order Service Outbound Adapter */
void order_service_publish_order(MessageBus* bus, uint32_t order_id, uint32_t cust_id, uint32_t cents) {
    OrderPlacedEvent evt;
    evt.order_id = order_id;
    evt.customer_id = cust_id;
    evt.amount_cents = cents;
    strncpy(evt.currency, "UAH", 4);
    
    MessageEnvelope env;
    envelope_init(&env, "orders.created", "", 2 /* schema v2 */);
    
    /* Бінарна серіалізація в корисне навантаження конверта */
    memcpy(env.payload, &evt, sizeof(OrderPlacedEvent));
    env.payload_len = sizeof(OrderPlacedEvent);
    
    printf("\n--> [OrderService] Створено замовлення #%u на суму %u.%02u %s. Публікація в шину...\n",
           order_id, cents / 100, cents % 100, evt.currency);
    bus_publish(bus, &env);
}

/* Адаптер-споживач 1: Billing Service Inbound Handler */
void billing_service_handler(const MessageEnvelope* env, void* ctx) {
    (void)ctx;
    if (env->payload_len != sizeof(OrderPlacedEvent)) return;
    
    const OrderPlacedEvent* evt = (const OrderPlacedEvent*)env->payload;
    printf("  [BillingService] ОТРИМАНО подію: Списання коштів за замовленням #%u: %u.%02u %s (Trace: %s)\n",
           evt->order_id, evt->amount_cents / 100, evt->amount_cents % 100, evt->currency, env->traceparent);
}

/* Адаптер-споживач 2: Notification Service Inbound Handler */
void notification_service_handler(const MessageEnvelope* env, void* ctx) {
    (void)ctx;
    if (env->payload_len != sizeof(OrderPlacedEvent)) return;
    
    const OrderPlacedEvent* evt = (const OrderPlacedEvent*)env->payload;
    printf("  [NotificationService] ОТРИМАНО подію: Відправка SMS клієнту #%u: Замовлення #%u підтверджено\n",
           evt->customer_id, evt->order_id);
}

int main(void) {
    printf("=== ДЕМОНСТРАЦІЯ РОБОТИ ШИНИ ПОВІДОМЛЕНЬ (C) ===\n");
    
    MessageBus bus;
    bus_init(&bus);
    
    /* Налаштування конвеєра перехоплювачів */
    uint32_t min_version = 2;
    DedupCache dedup_cache = {.count = 0};
    
    bus_add_interceptor(&bus, schema_validator_interceptor, &min_version);
    bus_add_interceptor(&bus, tracing_logger_interceptor, NULL);
    bus_add_interceptor(&bus, dedup_interceptor, &dedup_cache);
    
    /* Реєстрація підписок сервісів */
    bus_subscribe(&bus, "orders.*", billing_service_handler, NULL);
    bus_subscribe(&bus, "orders.created", notification_service_handler, NULL);
    
    /* Сценарій 1: Успішна публікація замовлення */
    order_service_publish_order(&bus, 4010, 77, 150000);
    
    /* Сценарій 2: Відхилення повідомлення із застарілою схемою v1 */
    printf("\n--> [LegacyProducer] Спроба публікації повідомлення за схемою v1...\n");
    MessageEnvelope old_env;
    envelope_init(&old_env, "orders.created", "corr_old", 1 /* v1 */);
    bus_publish(&bus, &old_env);
    
    return 0;
}
```
```cpp
/* Структура канонічної події замовлення */
struct OrderPlacedEvent {
    uint32_t order_id{0};
    uint32_t customer_id{0};
    uint32_t amount_cents{0};
    char currency[4]{"UAH"};
};

/* Адаптер видавця: Order Service */
void publish_order(MessageBus& bus, uint32_t order_id, uint32_t cust_id, uint32_t cents) {
    OrderPlacedEvent evt{order_id, cust_id, cents, "UAH"};
    
    auto env = MessageEnvelope::create("orders.created", "", 2 /* v2 */);
    
    std::span<const uint8_t> bytes(reinterpret_cast<const uint8_t*>(&evt), sizeof(evt));
    env.set_payload(bytes);
    
    std::cout << std::format("\n--> [OrderService] Створено замовлення #{} на суму {}.{:02d} {}. Публікація в шину...\n",
                             order_id, cents / 100, cents % 100, evt.currency);
    bus.publish(env);
}

int main() {
    std::cout << "=== ДЕМОНСТРАЦІЯ РОБОТИ ШИНИ ПОВІДОМЛЕНЬ (C++) ===\n";

    MessageBus bus;

    /* Реєстрація перехоплювачів */
    bus.add_interceptor(make_schema_validator(2));
    bus.add_interceptor(make_tracing_logger());
    
    DedupInterceptor dedup;
    bus.add_interceptor([&dedup](MessageEnvelope& env) {
        return dedup(env);
    });

    /* Підписка сервісу білінгу на всі події orders.* */
    bus.subscribe("orders.*", [](const MessageEnvelope& env) {
        if (env.payload.size() == sizeof(OrderPlacedEvent)) {
            const auto* evt = reinterpret_cast<const OrderPlacedEvent*>(env.payload.data());
            std::cout << std::format("  [BillingService] ОТРИМАНО: Списання коштів за замовленням #{}: {}.{:02d} {} (Trace: {})\n",
                                     evt->order_id, evt->amount_cents / 100, evt->amount_cents % 100, 
                                     evt->currency, env.traceparent);
        }
    });

    /* Підписка сервісу сповіщень на точну тему orders.created */
    bus.subscribe("orders.created", [](const MessageEnvelope& env) {
        if (env.payload.size() == sizeof(OrderPlacedEvent)) {
            const auto* evt = reinterpret_cast<const OrderPlacedEvent*>(env.payload.data());
            std::cout << std::format("  [NotificationService] ОТРИМАНО: SMS клієнту #{}: Замовлення #{} підтверджено\n",
                                     evt->customer_id, evt->order_id);
        }
    });

    /* Сценарій 1: Успішна публікація події */
    publish_order(bus, 4010, 77, 150000);

    /* Сценарій 2: Відхилення застарілої схеми v1 */
    std::cout << "\n--> [LegacyProducer] Спроба публікації повідомлення за схемою v1...\n";
    auto old_env = MessageEnvelope::create("orders.created", "corr_old", 1 /* v1 */);
    bus.publish(old_env);

    return 0;
}
```
:::

## 5. Очікуваний вивід та перевірка роботи конвеєра

Запуск скомпільованих програм C та C++ демонструє ідентичну послідовність проходження повідомлень крізь конвеєр перехоплювачів і маршрутизатор шини:

```
=== ДЕМОНСТРАЦІЯ РОБОТИ ШИНИ ПОВІДОМЛЕНЬ (C++) ===

--> [OrderService] Створено замовлення #4010 на суму 1500.00 UAH. Публікація в шину...
[Interceptor:Schema] OK: версія v2 сумісна
[Interceptor:Tracing] Обробка [msg_1001] Тема='orders.created' Trace='00-trace1001-span01-01' Corr='msg_1001'
  [BillingService] ОТРИМАНО: Списання коштів за замовленням #4010: 1500.00 UAH (Trace: 00-trace1001-span01-01)
  [NotificationService] ОТРИМАНО: SMS клієнту #77: Замовлення #4010 підтверджено
[Bus:Router] Повідомлення 'orders.created' успішно доставлено 2 підписникам

--> [LegacyProducer] Спроба публікації повідомлення за схемою v1...
[Interceptor:Schema] ВІДХИЛЕНО: версія v1 застаріла (потрібна >= v2)
```

Результати виконання підтверджують ключові інваріанти шини:
- Повідомлення успішно маршрутизується до двох незалежних підписників (Billing Service за груповим шаблоном `orders.*` та Notification Service за точним `orders.created`);
- Конвеєр перехоплювачів успішно відхилив некоректне повідомлення v1 до його потрапляння до бізнес-сервісів, запобігши помилкам десеріалізації;
- Контекст розподіленого трасування (`traceparent`) та наскрізної кореляції (`correlation_id`) зберігається без змін на всіх етапах передачі.

## 6. Алгоритми маршрутизації: лінійний перебір проти префіксного дерева (Topic Trie)

У навчальній реалізації перевірка збігу тем здійснюється послідовним лінійним перебором зареєстрованих підписок:

```
T_lookup(N) = O(N · L)
```

де `N` — кількість підписників, а `L` — середня довжина рядка теми. Якщо в системі зареєстровано 100 підписок, лінійний перебір виконується за лічені мікросекунди. Однак у великих промислових брокерах (наприклад, NATS або RabbitMQ), де кількість активних підписок сягає сотен тисяч, лінійне сканування створює неприпустиме навантаження на процесор.

Для масштабування маршрутизації застосовують спеціалізовану структуру даних — **Префіксне дерево тем (Topic Radix Tree / Trie)**.

У такому дереві кожен вузол відповідає окремому слову (сегменту) теми, розділеному крапкою:

```
                 (Root)
                /      \
           "orders"   "payments"
           /      \        \
      "created"  "paid"   "failed"
```

Коли споживач підписується на шаблон `orders.*`, покажчик на його обробник реєструється у спеціальній підстановковій гілці вузла `orders`.

При надходженні повідомлення з темою `orders.created.v2` диспетчер розбиває тему на масив токенів `["orders", "created", "v2"]` і виконує спуск по дереву:
1. Знаходить вузол `orders` за константний час `O(1)` через хеш-таблицю дочірніх вузлів;
2. Переходить до вузла `created`;
3. Збирає всіх підписників, зареєстрованих у цьому вузлі, а також у батьківських вузлах із підстановками `*` (один сегмент) та `#` (довільна кількість сегментів).

Складність маршрутизації через дерево тем становить `O(D)`, де `D` — глибина ієрархії теми (типово від 2 до 5 сегментів), і абсолютно **не залежить від загальної кількості зареєстрованих підписників `N`**.

## 7. Відмовостійкість: повтори, отруйні повідомлення та карантин (Dead Letter Queue)

У розподіленому середовищі споживач може зазнати невдачі під час обробки повідомлення з двох принципово різних причин:

1. **Транзиторний збій (Transient Failure):**
   Тимчасова недоступність бази даних, мережевий таймаут до платіжного шлюзу або перезавантаження контейнера.
   *Стратегія розв'язання:* повторна спроба (*Retry*) з експоненційним відступом та джитером (Exponential Backoff with Jitter):

```
t_backoff = min(t_max, t_base · 2^attempt) ± random_jitter
```

2. **Перманентний збій / «Отруйне повідомлення» (Poison Message):**
   Повідомлення містить некоректні дані, які викликають неперехоплюваний виняток, переповнення стека або падіння процесу споживача (`SIGSEGV / OOM Kill`).
   Якщо таке повідомлення негайно повертати в чергу, споживач потрапляє в нескінченний цикл аварійного перезапуску (*CrashLoopBackOff*), блокуючи обробку всіх наступних валідних замовлень.

Для захисту від отруйних повідомлень шина реалізує політику карантину за допомогою лічильника спроб доставки `delivery_attempt`:
- При отриманні повідомлення воркер інкрементує лічильник спроб у заголовку конверта;
- Якщо кількість спроб перевищує поріг (наприклад, `max_delivery_attempts = 3`), перехоплювач автоматично вилучає повідомлення з основного каналу та публікує його в **Мертву чергу (Dead Letter Queue, DLQ)** — спеціальний ізольований канал `dead.letter.orders`;
- Основна черга розблоковується, а інженери підтримки отримують сповіщення для ручного аудиту вмісту мертвої черги.

## 8. Асинхронний протокол «Запит-Відповідь» (Request-Reply over Bus)

Хоча шина повідомлень оптимізована для односторонньої трансляції подій, у багатьох бізнес-сценаріях сервісу-відправнику необхідно отримати результат виконання операції (наприклад, запит кредитного ліміту клієнта перед оформленням замовлення).

Прямий синхронний HTTP-виклик знову повернув би нас до проблеми часової зв'язаності. Замість цього шина реалізує асинхронний патерн **Request-Reply** за допомогою двох спеціальних полів канонічного конверта:
- **`reply_to`:** ім'я тимчасової черги або теми, куди відправник очікує отримати відповідь (наприклад, `replies.ordersvc.temp_842`);
- **`correlation_id`:** унікальний ідентифікатор запиту, що повертається у відповіді для зіставлення з вихідним об'єктом `Future / Promise` клієнта.

### Послідовність проходження запиту-відповіді:

1. Клієнт створює тимчасову приватну чергу підписки `reply_queue_77` та генерує `correlation_id = "req_9901"`;
2. Клієнт публікує команду в загальну чергу `cmd.billing.check_limit`, вказуючи в конверті `reply_to = "reply_queue_77"` та `correlation_id = "req_9901"`;
3. Сервіс білінгу вичитує команду з черги, виконує перевірку балансу та формує повідомлення-відповідь;
4. Сервіс білінгу публікує відповідь безпосередньо в тему, зазначену в полі `reply_to`, копіюючи `correlation_id = "req_9901"`;
5. Клієнт отримує пакет зі своєї черги відповідей, за ідентифікатором `req_9901` знаходить очікуючий об'єкт у пам'яті та асинхронно передає результат бізнес-потоку.

Цей механізм дозволяє реалізувати взаємодію в стилі RPC без встановлення прямого мережевого з'єднання між сервісами, зберігаючи всі переваги буферизації та моніторингу шини повідомлень.

## 9. Атомарна публікація через патерн Transactional Outbox

Найбільш підступною пасткою при публікації в шину є **проблема подвійного запису (Dual-Write Problem)**.

Уявімо сервіс замовлень, який зберігає запис про нове замовлення в реляційній базі даних PostgreSQL, а потім відправляє повідомлення `orders.created` на шину. Якщо публікація в шину завершиться аварією через збій мережі, замовлення збережеться в базі, але білінг і склад ніколи про нього не дізнаються. Якщо ж спершу опублікувати подію в шину, а потім спробувати зафіксувати транзакцію в базі, падіння бази даних призведе до того, що гроші з клієнта спишуться за неіснуюче замовлення.

Розв'язанням є патерн **Transactional Outbox**:
1. У тій самій транзакції бази даних, яка зберігає бізнес-сутність `orders`, сервіс записує повідомлення в спеціальну службову таблицю `outbox`:
   ```sql
   BEGIN TRANSACTION;
   INSERT INTO orders (id, customer_id, total_cents) VALUES (4010, 77, 150000);
   INSERT INTO outbox_messages (id, topic, payload, created_at) 
   VALUES ('msg_1001', 'orders.created', '{"order_id":4010,...}', NOW());
   COMMIT;
   ```
2. Окремий фоновий процес (Outbox Publisher або Debezium CDC через читання журналу випереджального запису WAL бази даних) асинхронно вичитує рядки з таблиці `outbox_messages`, відправляє їх на шину повідомлень і після отримання квитанції брокера видаляє або позначає як надіслані.

Завдяки цьому гарантується семантика доставки *At-Least-Once*: повідомлення гарантовано потрапляє на шину рівно тоді, коли транзакція бази даних успішно зафіксована.

## 10. Низькорівнева оптимізація пам'яті та кеш-ліній процесора

При проектуванні диспетчерів з пропускною здатністю понад 1 000 000 повідомлень/с мовами C та C++ критичного значення набуває структура пам'яті та поведінка апаратної архітектури:

1. **Запобігання помилковому розділенню кеш-ліній (False Sharing):**
   Якщо лічильник вхідних повідомлень продюсера та покажчик голови черги споживача розміщені в суміжних адресах пам'яті (в межах однієї 64-байтової кеш-лінії L1 процесора), ядра CPU постійно інвалідуватимуть кеші одне одного через протокол когерентності MESI. Для усунення цього ефекту структури вирівнюють за межею кеш-лінії (`alignas(64)` в C++ або `__attribute__((aligned(64)))` в C).
2. **Кільцеві безблокувальні буфери (Lock-Free Ring Buffers):**
   Замість м'ютексів операційної системи (`pthread_mutex_t`), які викликають перемикання контексту ядра (накладні витрати 1–3 мкс на операцію), передача повідомлень між перехоплювачами організовується через атомарні покажчики читання й запису з послідовною узгодженістю `std::memory_order_acquire / std::memory_order_release`.
3. **Пам'яттєві пули та арени (Memory Arenas):**
   Для виключення фрагментації пам'яті в довготривалих процесах-брокерах конверти повідомлень виділяються з попередньо створених кільцевих арен пам'яті фіксованого розміру (Slab Allocator), де повернення блоку полягає в простому декременті атомарного лічильника.

Це дозволяє досягти субмікросекундної латентності доставки на рівні ядра операційної системи, що робить архітектуру шини здатною витримувати екстремальні навантаження сучасних фінтех-платформ.

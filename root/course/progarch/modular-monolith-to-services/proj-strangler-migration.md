# ⚙️ Практична реалізація конвеєра Strangler Fig: від шва в коді до подвійного запису

Виділення мікросервісу з модульного моноліта без зупинки роботи системи вимагає чіткої інженерної реалізації на трьох рівнях:
1. **Створення шва в коді (Branch by Abstraction):** заміна прямого домену або виклику бази даних абстрактним інтерфейсом-обгорткою.
2. **Маршрутизатор канарейки (Canary Router & Shadow Read):** розщеплення трафіку між сталим монолітним кодом та новим мережевим викликом із порівнянням результатів.
3. **Подвійний запис (Dual Write):** безпечне оновлення даних в обох системах із фоновою реконсиляцією та обробкою мережевих збоїв.

Нижче наведено реалізацію цієї механіки для компонента обробки телеметрії пристроїв розумного дому. Приклад показує, як внутрішній виклик функції еволюціонує в канарейковий мережевий виклик до нового мікросервісу без зміни клієнтського коду.

## Архітектурний шаблон виділення шва

```
        Клієнтський код (Контролер / Обробник)
                       │
                       ▼
          [ Абстракція / Фасад ]  (Branch by Abstraction)
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ Старий модуль ]            [ Новий HTTP/gRPC Клієнт ]
 (у пам'яті моноліта)          (до мікросервісу)
```

## Покрокова механіка виконання запиту

Під час міграції кожен запит до компонента проходить скрізь систему роутингу за наступним алгоритмом:

- **Крок 1 (Отримання контексту):** Вхідний запит містить ідентифікатор пристрою (`device_id`) та дані вимірювань.
- **Крок 2 (Обчислення канарейкового бакета):** Маршрутизатор обчислює хеш або залишок від ділення `device_id % 100`. Це забезпечує детермінований роутинг: один і той самий пристрій під час канарейкового розгортання завжди потрапляє в одну й ту саму систему.
- **Крок 3 (Перевірка порогового відсотка):** Якщо бакет менший за `canary_percent` (наприклад `5%`), запит спрямовується до нового мікросервісу. Інакше запит обробляється старій реалізації моноліта.
- **Крок 4 (Shadow Write / Тіньове виконання):** Якщо ввімкнено тіньовий режим (`shadow_read_enabled`), запит виконується у новій системі, але одночасно викликає й старий модуль для звірки результатів. Помилки старої системи в тіньовому режимі не впливають на користувача, але записуються у лог розходжень.

---

## Детальний аналіз пам'яті та продуктивності абстракцій

Виділення шва в коді вносить мінімальну накладну витрату (Overhead) на виклик функції:
- **У мові C:** Виклик через вказівник на функцію у таблиці `telemetry_provider_t` додає непряму адресацію (`indirect call`), що коштує лише 1–2 наносекунди CPU-часу.
- **У мові C++:** Віртуальний виклик через vtable додає одну додаткову розіменовку вказівника на vptr. Оскільки обробка телеметрії зазвичай передбачає I/O або роботу з мережею, накладні витрати на vtable є абсолютно знехтовно малими порівняно з користю від чистої декомпозиції коду.

Для забезпечення потокобезпечності (Thread Safety) при розгалуженні запитів у багатопотоковому моноліті значення `canary_percent` оновлюється атомарно (атомарні вказівники або `std::atomic<int>`), що дозволяє змінювати частку канарейкового трафіку в реальному часі без блокувань (Lock-Free Hot Reload).

---

## Реалізація конвеєра

:::tabs
```c
/* C: Виділення шва та канарейковий маршрутизатор з подвійним записом */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Модель телеметрії пристрою */
typedef struct {
    long device_id;
    double temperature;
    double humidity;
    long timestamp;
} telemetry_payload_t;

/* Результат обробки */
typedef struct {
    bool success;
    int status_code;
    char error_msg[64];
} process_result_t;

/* 1. Інтерфейс (шов у коді) через вказівники на функції */
typedef struct telemetry_provider {
    process_result_t (*process)(struct telemetry_provider *self, const telemetry_payload_t *data);
    void (*destroy)(struct telemetry_provider *self);
    void *ctx;
} telemetry_provider_t;

/* --- Стара реалізація (внутрішній модуль моноліта) --- */
typedef struct {
    char db_connection_str[128];
} legacy_monolith_ctx_t;

static process_result_t legacy_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    legacy_monolith_ctx_t *ctx = (legacy_monolith_ctx_t *)self->ctx;
    process_result_t res = { .success = true, .status_code = 200, .error_msg = "" };
    
    /* Симуляція запису в спільну монолітну БД */
    printf("[LEGACY MONOLITH] Writing to DB (%s): Device=%ld, Temp=%.1f C\n",
           ctx->db_connection_str, data->device_id, data->temperature);
    return res;
}

static void legacy_destroy(telemetry_provider_t *self) {
    if (self) {
        free(self->ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_legacy(const char *db_conn) {
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    legacy_monolith_ctx_t *ctx = (legacy_monolith_ctx_t *)malloc(sizeof(legacy_monolith_ctx_t));
    strncpy(ctx->db_connection_str, db_conn, sizeof(ctx->db_connection_str) - 1);
    
    p->process = legacy_process;
    p->destroy = legacy_destroy;
    p->ctx = ctx;
    return p;
}

/* --- Нова реалізація (HTTP/gRPC клієнт до мікросервісу) --- */
typedef struct {
    char service_endpoint[128];
    int timeout_ms;
} remote_service_ctx_t;

static process_result_t remote_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    remote_service_ctx_t *ctx = (remote_service_ctx_t *)self->ctx;
    process_result_t res = { .success = true, .status_code = 201, .error_msg = "" };
    
    /* Симуляція мережевого RPC-виклику до нового сервісу */
    printf("[NEW MICROSERVICE] POST %s (timeout=%dms): Device=%ld, Temp=%.1f C\n",
           ctx->service_endpoint, ctx->timeout_ms, data->device_id, data->temperature);
    return res;
}

static void remote_destroy(telemetry_provider_t *self) {
    if (self) {
        free(self->ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_remote(const char *endpoint, int timeout_ms) {
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    remote_service_ctx_t *ctx = (remote_service_ctx_t *)malloc(sizeof(remote_service_ctx_t));
    strncpy(ctx->service_endpoint, endpoint, sizeof(ctx->service_endpoint) - 1);
    ctx->timeout_ms = timeout_ms;
    
    p->process = remote_process;
    p->destroy = remote_destroy;
    p->ctx = ctx;
    return p;
}

/* --- Strangler Router: Канарейка + Shadow Read + Dual Write --- */
typedef struct {
    telemetry_provider_t *legacy;
    telemetry_provider_t *remote;
    int canary_percent; /* 0..100 */
    bool shadow_read_enabled;
} strangler_router_ctx_t;

static process_result_t strangler_process(telemetry_provider_t *self, const telemetry_payload_t *data) {
    strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)self->ctx;
    
    /* Проста детермінована перевірка канарейки на основі device_id */
    int bucket = (int)(data->device_id % 100);
    bool use_new_service = (bucket < ctx->canary_percent);
    
    if (use_new_service) {
        printf("[ROUTER] Routing Device %ld -> NEW SERVICE (Canary bucket %d < %d%%)\n",
               data->device_id, bucket, ctx->canary_percent);
        process_result_t res = ctx->remote->process(ctx->remote, data);
        
        /* Shadow write/read у старову систему для верифікації якщо увімкнено */
        if (ctx->shadow_read_enabled) {
            printf("[ROUTER] Performing Shadow Write to Legacy for verification...\n");
            ctx->legacy->process(ctx->legacy, data);
        }
        return res;
    } else {
        printf("[ROUTER] Routing Device %ld -> LEGACY MONOLITH (Canary bucket %d >= %d%%)\n",
               data->device_id, bucket, ctx->canary_percent);
        return ctx->legacy->process(ctx->legacy, data);
    }
}

static void strangler_destroy(telemetry_provider_t *self) {
    if (self) {
        strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)self->ctx;
        if (ctx->legacy) ctx->legacy->destroy(ctx->legacy);
        if (ctx->remote) ctx->remote->destroy(ctx->remote);
        free(ctx);
        free(self);
    }
}

telemetry_provider_t *telemetry_provider_create_strangler(
    telemetry_provider_t *legacy,
    telemetry_provider_t *remote,
    int canary_percent,
    bool shadow_read) 
{
    telemetry_provider_t *p = (telemetry_provider_t *)malloc(sizeof(telemetry_provider_t));
    strangler_router_ctx_t *ctx = (strangler_router_ctx_t *)malloc(sizeof(strangler_router_ctx_t));
    ctx->legacy = legacy;
    ctx->remote = remote;
    ctx->canary_percent = canary_percent;
    ctx->shadow_read_enabled = shadow_read;
    
    p->process = strangler_process;
    p->destroy = strangler_destroy;
    p->ctx = ctx;
    return p;
}

int main(void) {
    printf("=== STRANGLER MIGRATION DEMO ===\n");
    
    telemetry_provider_t *legacy = telemetry_provider_create_legacy("postgres://localhost:5432/monolith");
    telemetry_provider_t *remote = telemetry_provider_create_remote("http://telemetry-service.internal/api/v1", 200);
    
    /* Налаштовуємо роутер: 20% трафіку на новий сервіс, з увімкненим shadow-записом */
    telemetry_provider_t *router = telemetry_provider_create_strangler(legacy, remote, 20, true);
    
    telemetry_payload_t batch[] = {
        { .device_id = 105, .temperature = 22.4, .humidity = 45.0, .timestamp = 1700000001 }, /* 5% < 20% -> NEW */
        { .device_id = 142, .temperature = 19.8, .humidity = 50.1, .timestamp = 1700000002 }, /* 42% >= 20% -> LEGACY */
        { .device_id = 119, .temperature = 25.1, .humidity = 40.2, .timestamp = 1700000003 }  /* 19% < 20% -> NEW */
    };
    
    for (size_t i = 0; i < sizeof(batch)/sizeof(batch[0]); i++) {
        router->process(router, &batch[i]);
    }
    
    router->destroy(router);
    return 0;
}
```
```cpp
// C++17: Ідіоматична реалізація Branch by Abstraction та Strangler Router (RAII, Polymorphism, std::expected)
#include <iostream>
#include <memory>
#include <string>
#include <string_view>
#include <vector>
#include <variant>
#include <system_error>

struct TelemetryPayload {
    long device_id;
    double temperature;
    double humidity;
    long timestamp;
};

struct ProcessError {
    int status_code;
    std::string message;
};

// Простий аналог std::expected для демонстрації обробки помилок без винятків
template <typename T, typename E>
class Expected {
    std::variant<T, E> data_;
public:
    Expected(T val) : data_(std::move(val)) {}
    Expected(E err) : data_(std::move(err)) {}
    
    bool has_value() const { return std::holds_alternative<T>(data_); }
    const T& value() const { return std::get<T>(data_); }
    const E& error() const { return std::get<E>(data_); }
};

// 1. Абстрактний інтерфейс шва (Branch by Abstraction)
class ITelemetryProvider {
public:
    virtual ~ITelemetryProvider() = default;
    virtual Expected<bool, ProcessError> process(const TelemetryPayload& data) = 0;
};

// --- Стара монолітна реалізація ---
class LegacyMonolithProvider final : public ITelemetryProvider {
    std::string db_connection_str_;
public:
    explicit LegacyMonolithProvider(std::string db_conn)
        : db_connection_str_(std::move(db_conn)) {}
        
    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        std::cout << "[LEGACY MONOLITH] Direct DB write (" << db_connection_str_ 
                  << "): Device=" << data.device_id << ", Temp=" << data.temperature << " C\n";
        return true;
    }
};

// --- Нова мікросервісна реалізація ---
class RemoteServiceProvider final : public ITelemetryProvider {
    std::string service_endpoint_;
    int timeout_ms_;
public:
    RemoteServiceProvider(std::string endpoint, int timeout_ms)
        : service_endpoint_(std::move(endpoint)), timeout_ms_(timeout_ms) {}
        
    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        std::cout << "[NEW MICROSERVICE] RPC POST " << service_endpoint_ 
                  << " (timeout=" << timeout_ms_ << "ms): Device=" << data.device_id 
                  << ", Temp=" << data.temperature << " C\n";
        return true;
    }
};

// --- Strangler Router з підтримкою Canary та Shadow Write ---
class StranglerRouter final : public ITelemetryProvider {
    std::unique_ptr<ITelemetryProvider> legacy_;
    std::unique_ptr<ITelemetryProvider> remote_;
    int canary_percent_;
    bool shadow_read_enabled_;
public:
    StranglerRouter(std::unique_ptr<ITelemetryProvider> legacy,
                    std::unique_ptr<ITelemetryProvider> remote,
                    int canary_percent,
                    bool shadow_read)
        : legacy_(std::move(legacy)),
          remote_(std::move(remote)),
          canary_percent_(canary_percent),
          shadow_read_enabled_(shadow_read) {}

    Expected<bool, ProcessError> process(const TelemetryPayload& data) override {
        int bucket = static_cast<int>(data.device_id % 100);
        bool use_new_service = (bucket < canary_percent_);

        if (use_new_service) {
            std::cout << "[ROUTER] Device " << data.device_id 
                      << " -> NEW SERVICE (Canary bucket " << bucket << " < " << canary_percent_ << "%)\n";
            auto result = remote_->process(data);
            
            if (shadow_read_enabled_ && result.has_value()) {
                std::cout << "[ROUTER] Executing Shadow Write to Legacy for reconciliation verification...\n";
                [[maybe_unused]] auto shadow_res = legacy_->process(data);
            }
            return result;
        } else {
            std::cout << "[ROUTER] Device " << data.device_id 
                      << " -> LEGACY MONOLITH (Canary bucket " << bucket << " >= " << canary_percent_ << "%)\n";
            return legacy_->process(data);
        }
    }
};

int main() {
    std::cout << "=== STRANGLER MIGRATION DEMO (C++17) ===\n";
    
    auto legacy = std::make_unique<LegacyMonolithProvider>("postgres://localhost:5432/monolith");
    auto remote = std::make_unique<RemoteServiceProvider>("http://telemetry-service.internal/api/v1", 200);
    
    // Створюємо роутер: 20% канарейка, увімкнений shadow write
    auto router = std::make_unique<StranglerRouter>(std::move(legacy), std::move(remote), 20, true);
    
    std::vector<TelemetryPayload> batch = {
        {105, 22.4, 45.0, 1700000001}, // 5% -> NEW
        {142, 19.8, 50.1, 1700000002}, // 42% -> LEGACY
        {119, 25.1, 40.2, 1700000003}  // 19% -> NEW
    };
    
    for (const auto& item : batch) {
        auto res = router->process(item);
        if (!res.has_value()) {
            std::cerr << "Processing failed: " << res.error().message << "\n";
        }
    }
    
    return 0; // RAII автоматично звільняє всі ресурси
}
```
:::

---

## Аналіз крайніх випадків та підводних каменів

Під час експлуатації канарейкового маршрутизатора у продакшні інженер натрапляє на кілька важливих крайніх випадків:

1. **Мережеві таймаути та повтори (Circuit Breaker Integration):** На відміну від монолітного виклику в пам'яті, мережевий виклик `RemoteServiceProvider` може зависнути через втрату пакетів у мережі. Маршрутизатор мусить містити обгортку Circuit Breaker із жорстким таймаутом (наприклад `200ms`). Якщо мікросервіс не відповідає вчасно, роутер повинен миттєво відкотитися до виконання `legacy_->process()` для даного запиту.
2. **Конфлікти ідентифікаторів при подвійному записі:** Якщо обидві системи генерують власні первинні ключі у базах даних (наприклад, через послідовності `AUTO_INCREMENT`), записи розсіхронізуються. Рішення — генерація UUIDv4 або монотонних ідентифікаторів Snowflake ID у клієнтському коді до виклику будь-якого з провайдерів.
3. **Обробка помилок у тіньовому режимі:** Тіньовий запис (Shadow Write) мусить виконуватися асинхронно у фоновому пулі потоків або через неблокуючий I/O. Помилка або таймаут тіньового запису не повинні повертати код помилки користувачеві, чий основний запит пройшов успішно.
4. **Простежуваність (Trace Propagation):** При переході запиту від монолітного роутера до `RemoteServiceProvider` обов'язково прокидається заголовок `traceparent` (OpenTelemetry), що дозволяє бачити єдиний спан у системах distributed tracing (Jaeger, Zipkin).
5. **Динамічне масштабування пулу потоків фонової реконсиляції:** При високих показниках RPS тіньові читання можуть створювати підвищений тиск на чергу I/O. Реконсилятор повинен мати вбудовану тактику відкидання навантаження (Load Shedding): якщо черга фонових перевірок заповнена на 80%, тіньові запити тимчасово пропускаються.

---

## Покроковий алгоритм розгортання у продакшн

- **Фаза 0 (Моноліт):** Клієнти викликають `LegacyMonolithProvider` напряму без використання маршрутизаторів.
- **Фаза 1 (Впровадження шва):** Код переводиться на абстрактний інтерфейс `ITelemetryProvider`, створюється `StranglerRouter` із конфігураційним значенням `canary_percent = 0`. Системна поведінка залишається повністю незмінною.
- **Фаза 2 (Shadow Write / Dark Launch):** Параметр `canary_percent` зберігається на рівні `0`, але вмикається дублювання запитів на `RemoteServiceProvider` у фоновому асинхронному режимі (без впливу на результат для клієнта). Автоматичний реконсилятор порівнює записи та збирає метрики відхилень.
- **Фаза 3 (Canary Migration):** Параметр `canary_percent` поступово збільшується: `1% -> 5% -> 25% -> 50% -> 100%`. Вся обробка поступово переходить на новий мікросервіс з моніторингом латентності.
- **Фаза 4 (Очищення та декомпресія):** Клас `StranglerRouter` та застаріла реалізація `LegacyMonolithProvider` повністю видаляються з кодової бази моноліта. Клієнти підключаються безпосередньо до `RemoteServiceProvider`.

# ⚙️ Реалізація причинного шлюзу read-model з очікуванням версії

У цій роботі реалізовано повноцінний промисловий шлюз запитів (Query Gateway) для розподілених систем із розділенням відповідальності команд і запитів (CQRS). Він забезпечує гарантію «читання власних записів» (Read-Your-Own-Writes) через механізм версійних токенів та неблокувального очікування на умовних змінних (Condition Variables), усуваючи аномалії застарілого читання без надмірного навантаження на первинну базу даних.

## Архітектурний дизайн та компоненти шлюзу

У класичній схемі CQRS запит на читання або спрямовується до денормалізованого сховища (де він ризикує повернути застарілий стан), або до первинної транзакційної бази (що руйнує масштабованість контуру запису). Пропонований шлюз виступає інтелектуальним арбітром: він оцінює поточний лаг реплікації та динамічно вибирає найбільш ефективну стратегію обслуговування запиту.

Шлюз складається з чотирьох взаємопов'язаних компонентів:
1. **Реєстр ватерліній (`WatermarkRegistry`):** потокобезпечна структура даних, яка відстежує останню зафіксовану версію для кожного агрегату чи партиції та керує чергою потоків, що очікують настання певної версії.
2. **Командний обробник (`CommandHandler`):** фіксує бізнес-мутацію у сховищі запису, генерує монотонний номер версії (`VersionToken`) та відправляє подію до черги.
3. **Обробник проєкцій (`ProjectionWorker`):** вичитує події з черги, оновлює денормалізоване представлення в базі читання та просуває ватерлінію в реєстрі, пробуджуючи очікуючі потоки.
4. **Шлюз запитів (`QueryGateway`):** приймає клієнтський запит із заголовком `X-Required-Version`, порівнює його з поточною ватерлінією та або повертає дані негайно, або переходить у режим очікування з жорстким таймаутом, після чого виконує аварійне перемикання на первинну базу (Primary Fallback).

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <shared_mutex>
#include <condition_variable>
#include <chrono>
#include <optional>
#include <expected>
#include <thread>
#include <vector>

namespace cqrs {

using Version = uint64_t;
using EntityId = std::string;

// Структура представлення сутності для читання
struct OrderView {
    EntityId order_id;
    std::string customer_id;
    std::string status;
    int64_t total_cents{0};
    Version version{0};
};

// Перелік можливих помилок виконання запиту
enum class GatewayError {
    Timeout,
    NotFound,
    PrimaryUnavailable,
    InternalError
};

// Реєстр ватерліній та синхронізація очікування версій
class WatermarkRegistry {
public:
    void update_watermark(const EntityId& id, Version new_version) {
        std::unique_lock lock(mutex_);
        auto& current = watermarks_[id];
        if (new_version > current) {
            current = new_version;
            // Пробуджуємо всі потоки, що чекають оновлення цієї або меншої версії
            cv_.notify_all();
        }
    }

    [[nodiscard]] Version get_watermark(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = watermarks_.find(id);
        return (it != watermarks_.end()) ? it->second : 0;
    }

    [[nodiscard]] bool wait_for_version(
        const EntityId& id,
        Version required_version,
        std::chrono::milliseconds timeout
    ) {
        std::unique_lock lock(mutex_);
        return cv_.wait_for(lock, timeout, [&] {
            auto it = watermarks_.find(id);
            return (it != watermarks_.end()) && (it->second >= required_version);
        });
    }

private:
    mutable std::shared_mutex mutex_;
    std::condition_variable_any cv_;
    std::unordered_map<EntityId, Version> watermarks_;
};

// Сховище моделі читання (Read Model Store)
class ReadModelStore {
public:
    void upsert(OrderView view) {
        std::unique_lock lock(mutex_);
        store_[view.order_id] = std::move(view);
    }

    [[nodiscard]] std::optional<OrderView> find(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = store_.find(id);
        if (it != store_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<EntityId, OrderView> store_;
};

// Первинне транзакційне сховище (Write Model Primary Database)
class PrimaryWriteStore {
public:
    void save(OrderView order) {
        std::unique_lock lock(mutex_);
        primary_db_[order.order_id] = std::move(order);
    }

    [[nodiscard]] std::optional<OrderView> fetch_direct(const EntityId& id) const {
        std::shared_lock lock(mutex_);
        auto it = primary_db_.find(id);
        if (it != primary_db_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

private:
    mutable std::shared_mutex mutex_;
    std::unordered_map<EntityId, OrderView> primary_db_;
};

// Шлюз запитів на читання з контролем контракту причинності
class CausalQueryGateway {
public:
    CausalQueryGateway(
        std::shared_ptr<WatermarkRegistry> registry,
        std::shared_ptr<ReadModelStore> read_store,
        std::shared_ptr<PrimaryWriteStore> write_store
    ) : registry_(std::move(registry)),
        read_store_(std::move(read_store)),
        write_store_(std::move(write_store)) {}

    [[nodiscard]] std::expected<OrderView, GatewayError> get_order(
        const EntityId& id,
        std::optional<Version> required_version,
        std::chrono::milliseconds wait_budget = std::chrono::milliseconds(50)
    ) {
        if (required_version.has_value()) {
            const Version req_v = *required_version;
            const Version current_v = registry_->get_watermark(id);

            if (current_v < req_v) {
                // Входимо в кероване очікування наздоганяння проєкції
                const bool caught_up = registry_->wait_for_version(id, req_v, wait_budget);
                if (!caught_up) {
                    // Бюджет часу вичерпано: перемикаємося на первинну базу (Primary Fallback)
                    auto direct_res = write_store_->fetch_direct(id);
                    if (direct_res.has_value()) {
                        return *direct_res;
                    }
                    return std::unexpected(GatewayError::Timeout);
                }
            }
        }

        // Швидкий шлях: читання з денормалізованого представлення
        auto view = read_store_->find(id);
        if (view.has_value()) {
            return *view;
        }

        // Аварійний шлях: якщо сутність щойно створена і відсутня в моделі читання
        auto fallback = write_store_->fetch_direct(id);
        if (fallback.has_value()) {
            return *fallback;
        }

        return std::unexpected(GatewayError::NotFound);
    }

private:
    std::shared_ptr<WatermarkRegistry> registry_;
    std::shared_ptr<ReadModelStore> read_store_;
    std::shared_ptr<PrimaryWriteStore> write_store_;
};

} // namespace cqrs
```
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <pthread.h>
#include <time.h>
#include <errno.h>

#define MAX_ID_LEN 64
#define MAX_STATUS_LEN 32
#define HASH_TABLE_SIZE 1024

typedef uint64_t version_t;

typedef struct {
    char order_id[MAX_ID_LEN];
    char customer_id[MAX_ID_LEN];
    char status[MAX_STATUS_LEN];
    int64_t total_cents;
    version_t version;
} order_view_t;

typedef struct watermark_node {
    char entity_id[MAX_ID_LEN];
    version_t version;
    struct watermark_node* next;
} watermark_node_t;

typedef struct {
    watermark_node_t* buckets[HASH_TABLE_SIZE];
    pthread_mutex_t lock;
    pthread_cond_t cv;
} watermark_registry_t;

static unsigned int hash_str(const char* str) {
    unsigned int hash = 5381;
    int c;
    while ((c = *str++)) {
        hash = ((hash << 5) + hash) + c;
    }
    return hash % HASH_TABLE_SIZE;
}

void watermark_registry_init(watermark_registry_t* reg) {
    memset(reg->buckets, 0, sizeof(reg->buckets));
    pthread_mutex_init(&reg->lock, NULL);
    pthread_cond_init(&reg->cv, NULL);
}

void watermark_registry_update(watermark_registry_t* reg, const char* id, version_t v) {
    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    
    watermark_node_t* cur = reg->buckets[idx];
    while (cur) {
        if (strcmp(cur->entity_id, id) == 0) {
            if (v > cur->version) {
                cur->version = v;
                pthread_cond_broadcast(&reg->cv);
            }
            pthread_mutex_unlock(&reg->lock);
            return;
        }
        cur = cur->next;
    }
    
    watermark_node_t* node = (watermark_node_t*)malloc(sizeof(watermark_node_t));
    strncpy(node->entity_id, id, MAX_ID_LEN - 1);
    node->entity_id[MAX_ID_LEN - 1] = '\0';
    node->version = v;
    node->next = reg->buckets[idx];
    reg->buckets[idx] = node;
    
    pthread_cond_broadcast(&reg->cv);
    pthread_mutex_unlock(&reg->lock);
}

version_t watermark_registry_get(watermark_registry_t* reg, const char* id) {
    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    watermark_node_t* cur = reg->buckets[idx];
    while (cur) {
        if (strcmp(cur->entity_id, id) == 0) {
            version_t v = cur->version;
            pthread_mutex_unlock(&reg->lock);
            return v;
        }
        cur = cur->next;
    }
    pthread_mutex_unlock(&reg->lock);
    return 0;
}

bool watermark_registry_wait(watermark_registry_t* reg, const char* id, version_t req_v, int timeout_ms) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_ms / 1000;
    ts.tv_nsec += (timeout_ms % 1000) * 1000000;
    if (ts.tv_nsec >= 1000000000) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1000000000;
    }

    unsigned int idx = hash_str(id);
    pthread_mutex_lock(&reg->lock);
    while (true) {
        watermark_node_t* cur = reg->buckets[idx];
        version_t cur_v = 0;
        while (cur) {
            if (strcmp(cur->entity_id, id) == 0) {
                cur_v = cur->version;
                break;
            }
            cur = cur->next;
        }
        if (cur_v >= req_v) {
            pthread_mutex_unlock(&reg->lock);
            return true;
        }
        int rc = pthread_cond_timedwait(&reg->cv, &reg->lock, &ts);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&reg->lock);
            return false;
        }
    }
}
```
:::

## Покроковий розбір життєвого циклу запиту

Механізм роботи шлюзу гарантує захист від стану гонитви завдяки чіткому розділенню фаз:

1. **Фаза валідації контракту:** коли запит надходить до шлюзу, перевіряється наявність параметра `required_version`. Якщо клієнт не вимагає конкретної версії (звичайний аналітичний або публічний запит), шлюз безпосередньо звертається до `ReadModelStore`, витрачаючи менше ніж 1 мілісекунду.
2. **Фаза перевірки ватерлінії:** шлюз виконує атомарне зчитування поточної зафіксованої версії через `get_watermark()`. Завдяки використанню `std::shared_mutex` паралельні операції читання ватерліній не блокують одна одну.
3. **Фаза синхронного очікування:** якщо `current_v < req_v`, потік реєструє предикат у `wait_for_version()`. Потік звільняє блокування м'ютекса та переходить у стан сну ядра ОС. Коли обробник проєкцій фіксує нову пачку подій, виклик `notify_all()` (або `pthread_cond_broadcast()`) перевіряє предикат. Якщо версія досягнута, потік прокидається з відновленим блокуванням.
4. **Фаза аварійного перемикання (Fallback):** якщо виділений бюджет часу (наприклад, 50 мс) вичерпано, а подія все ще стоїть у черзі брокера через перевантаження або мережевий лаг, шлюз не повертає помилку `404`, а прозоро перенаправляє запит до `PrimaryWriteStore`.

## Обробка крайових випадків та багатопотокових пасток

Під час експлуатації такого шлюзу під високим навантаженням необхідно враховувати три критичні інженерні аспекти:

### 1. Захист від хибних пробуджень (Spurious Wakeups)
Операційна система може пробудити потік з умовної змінної навіть за відсутності виклику `notify`. У наведеній C++ реалізації лямбда-предикат у `cv_.wait_for` автоматично перевіряє умову `it->second >= required_version` у циклі. У C-версії для цього реалізовано явний цикл `while (cur_v < req_v)` навколо `pthread_cond_timedwait`.

### 2. Запобігання ефекту громової отари (Thundering Herd)
Якщо сотні клієнтських з'єднань одночасно очікують оновлення популярної сутності (наприклад, статусу масштабного розпродажу), одиничний виклик `notify_all()` пробудить усі 100 потоків одночасно. Щоб уникнути сплеску навантаження на процесор, у високонавантажених системах реєстр ватерліній розбивають на кілька незалежних кошиків (Buckets), кожен з яких має власну умовну змінну.

### 3. Очищення застарілих ватерліній (Pruning & Memory Leaks)
Якщо система обробляє мільйони унікальних замовлень на добу, таблиця `watermarks_` зростатиме нескінченно. Для запобігання витоку пам'яті реєстр доповнюють фоновим процесом очищення (TTL Pruning): записи про сутності, до яких не було звернень понад 60 секунд і чий лаг дорівнює нулю, безпечно видаляються з хеш-таблиці.

## Масштабування від одного вузла до кластера: розподілені ватерлінії

Наведена реалізація використовує пам'ять одного процесу, що ідеально підходить для архітектури з локальними воркерами або Sidecar-проксі. Проте коли шлюз читання горизонтально масштабується на десятки вузлів за балансувальником навантаження (L7 Load Balancer), виникає потреба в розподіленій координації ватерліній.

У розподіленому кластері застосовують одну з двох моделей:
1. **Зберігання ватерліній у розподіленій пам'яті (Redis / KeyDB / NATS KV):**
   Обробник проєкцій після фіксації пачки оновлює лічильник версії в Redis за допомогою атомарної команди `HSET entity:watermarks ORD-7714 1042`. Шлюзи читання підписуються на потік оновлень через Redis Pub/Sub або перевіряють значення локально з кешуванням на 5–10 мс.
2. **Маршрутизація сесій за агрегатом (Sticky Routing / Consistent Hashing):**
   Балансувальник запитів скеровує всі операції читання та запису для конкретного користувача `USER-42` на той самий вузол шлюзу читання на основі хешу ідентифікатора. Це дозволяє зберегти блискавичну швидкість локальної синхронізації в оперативній пам'яті (`O(1)` доступ) без накладних витрат на мережевий консенсус.

## Оцінка навантаження на пул потоків ядра

При використанні синхронних блокувань на умовних змінних кожен очікуючий запит утримує окремий потік ОС (OS Thread). За стека потоку за замовчуванням у 8 МБ (типове значення в Linux) утримання 10 000 одночасних очікуючих з'єднань потребувало б 80 ГБ оперативної пам'яті.

Щоб запобігти вичерпанню пам'яті у високонавантажених сервісах:
- Розмір стека робочих потоків шлюзу обмежують до 256–512 КБ (`pthread_attr_setstacksize`).
- Для масштабування понад 100 000 конкурентних з'єднань блокуючі виклики замінюють на неблокувальні асинхронні корутини (C++20 Coroutines із `std::suspend_always` або Tokio tasks у Rust / epoll event loop), де очікування перетворюється на реєстрацію зворотного виклику (callback) без прив'язки до фізичного потоку ядра.

## Верифікація поведінки та приклад тесту

Наведений нижче тестовий сценарій імітує реальну затримку конвеєра реплікації (20 мс) і демонструє успішне виконання контракту «Read-Your-Own-Writes»:

```cpp
int main() {
    auto registry = std::make_shared<cqrs::WatermarkRegistry>();
    auto read_store = std::make_shared<cqrs::ReadModelStore>();
    auto write_store = std::make_shared<cqrs::PrimaryWriteStore>();

    cqrs::CausalQueryGateway gateway(registry, read_store, write_store);

    const std::string order_id = "ORD-7714";

    // 1. Командний потік: запис у первинну базу з версією 1042
    cqrs::OrderView fresh_order{order_id, "USER-42", "PAID", 12500, 1042};
    write_store->save(fresh_order);

    // 2. Фоновий потік проєктора: імітація затримки обробки черги (20 мс)
    std::thread projector_thread([&]() {
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
        read_store->upsert(fresh_order);
        registry->update_watermark(order_id, 1042);
    });

    // 3. Клієнтський потік: негайний запит із вимогою версії 1042
    auto start_time = std::chrono::steady_clock::now();
    auto result = gateway.get_order(order_id, 1042, std::chrono::milliseconds(100));
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::steady_clock::now() - start_time
    ).count();

    projector_thread.join();

    if (result.has_value()) {
        std::cout << "[SUCCESS] Отримано замовлення: " << result->order_id 
                  << ", статус: " << result->status 
                  << ", версія: " << result->version 
                  << ", час очікування: " << duration << " мс\n";
    }

    return 0;
}
```

Така архітектура дозволяє зберегти всі переваги асинхронного масштабування моделей читання, гарантуючи водночас 100% строгість виконання бізнес-інваріантів для критичних користувацьких сценаріїв.

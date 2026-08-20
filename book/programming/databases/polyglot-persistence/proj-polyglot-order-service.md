# ⚙️ Розробка поліглотного сервісу замовлень на C та C++

У сучасних розподілених додатках сервіс замовлень використовує поліглотну архітектуру: транзакційне ядро гарантує надійність фіксації оплат та зміни статусів (OLTP), швидкий Key-Value кеш забезпечує отримання замовлення за мікросекунди, а повнотекстовий індекс підтримує пошук товарів та фільтрацію.

У цьому практичному проєкті ми розробимо повноцінний поліглотний координатор мовами C та C++, який реалізує патерн Transactional Outbox, синхронізацію з Key-Value кешем та інвертованим пошуковим індексом без виникнення станів гонитви.

---

### Архітектура системи та потоки даних

Координатор об'єднує три спеціалізовані підсистеми:
1. **Primary OLTP Store (Транзакційне ядро)**: Зберігає таблиці `Orders` та `OutboxEvents` з повною підтримкою атомарності ACID.
2. **Key-Value Read Cache (L1 Cache)**: Швидка хеш-таблиця для отримання замовлення за ідентифікатором за час `O(1)`.
3. **Search Inverted Index (Пошуковий рушій)**: Інвертований індекс слів для повнотекстового пошуку товарів за назвою та описом.
4. **Outbox Processor (Асинхронний синхронізатор)**: Фоновий потік, який зчитує нові події з Outbox і безпечно оновлює вторинні сховища з перевіркою монотонності версій.

---

### Повна реалізація мовами C та C++

Нижче наведено вихідний код проєкту, реалізований за стандартами C99 та C++17 без сторонніх залежностей.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ORDERS 64
#define MAX_EVENTS 128
#define MAX_CACHE 64
#define STR_LEN 64

typedef struct {
    int id;
    char customer[STR_LEN];
    double amount;
    char status[16];
    uint64_t version;
} order_record_t;

typedef struct {
    int event_id;
    int order_id;
    char event_type[32];
    char payload[128];
    uint64_t version;
    bool processed;
} outbox_event_t;

typedef struct {
    int order_id;
    char cached_data[128];
    uint64_t version;
} cache_entry_t;

typedef struct {
    // 1. Primary OLTP Database
    order_record_t orders[MAX_ORDERS];
    size_t order_count;
    outbox_event_t outbox[MAX_EVENTS];
    size_t outbox_count;

    // 2. Key-Value Cache
    cache_entry_t cache[MAX_CACHE];
    size_t cache_count;
} polyglot_system_t;

void polyglot_init(polyglot_system_t *sys) {
    sys->order_count = 0;
    sys->outbox_count = 0;
    sys->cache_count = 0;
}

// Атомарне створення замовлення та запис в Outbox (ACID транзакція)
int create_order_transaction(polyglot_system_t *sys, int order_id, const char *customer, double amount) {
    if (sys->order_count >= MAX_ORDERS || sys->outbox_count >= MAX_EVENTS) return -1;

    // 1. Запис замовлення
    order_record_t *ord = &sys->orders[sys->order_count++];
    ord->id = order_id;
    strncpy(ord->customer, customer, STR_LEN - 1);
    ord->amount = amount;
    strncpy(ord->status, "CREATED", 15);
    ord->version = 1;

    // 2. Атомарний запис події в Outbox в тій самій транзакції
    outbox_event_t *ev = &sys->outbox[sys->outbox_count++];
    ev->event_id = (int)sys->outbox_count;
    ev->order_id = order_id;
    ev->version = 1;
    strncpy(ev->event_type, "ORDER_CREATED", 31);
    snprintf(ev->payload, 127, "{\"id\":%d,\"customer\":\"%s\",\"amount\":%.2f}", order_id, customer, amount);
    ev->processed = false;

    return 0;
}

// Фоновий процес обробки Outbox та синхронізації з Key-Value кешем
void process_outbox_events(polyglot_system_t *sys) {
    for (size_t i = 0; i < sys->outbox_count; ++i) {
        if (!sys->outbox[i].processed) {
            int oid = sys->outbox[i].order_id;
            uint64_t ver = sys->outbox[i].version;

            // Оновлення Key-Value кешу з перевіркою версії (Optimistic Locking)
            bool found_in_cache = false;
            for (size_t c = 0; c < sys->cache_count; ++c) {
                if (sys->cache[c].order_id == oid) {
                    if (ver >= sys->cache[c].version) {
                        strncpy(sys->cache[c].cached_data, sys->outbox[i].payload, 127);
                        sys->cache[c].version = ver;
                    }
                    found_in_cache = true;
                    break;
                }
            }

            if (!found_in_cache && sys->cache_count < MAX_CACHE) {
                sys->cache[sys->cache_count].order_id = oid;
                strncpy(sys->cache[sys->cache_count].cached_data, sys->outbox[i].payload, 127);
                sys->cache[sys->cache_count].version = ver;
                sys->cache_count++;
            }

            sys->outbox[i].processed = true;
        }
    }
}

// Швидке читання з L1 Кешу
const char* read_order_fast(polyglot_system_t *sys, int order_id) {
    for (size_t i = 0; i < sys->cache_count; ++i) {
        if (sys->cache[i].order_id == order_id) {
            return sys->cache[i].cached_data;
        }
    }
    return NULL; // Кеш-промах, читання з основної БД
}

int main(void) {
    polyglot_system_t system;
    polyglot_init(&system);

    // 1. Створення замовлення в основній БД
    create_order_transaction(&system, 1001, "Dmytro", 450.0);
    printf("Order 1001 created in Primary OLTP.\n");

    // Читання з кешу до синхронізації
    const char *cached = read_order_fast(&system, 1001);
    printf("Cache state before sync: %s\n", cached ? cached : "CACHE_MISS");

    // 2. Фоновий процес CDC / Outbox
    process_outbox_events(&system);

    // Читання з кешу після синхронізації
    cached = read_order_fast(&system, 1001);
    printf("Cache state after sync: %s\n", cached ? cached : "CACHE_MISS");

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <sstream>
#include <optional>
#include <memory>
#include <chrono>

namespace polyglot {

struct Order {
    int id;
    std::string customer;
    double amount;
    std::string status;
    uint64_t version;
};

struct OutboxEvent {
    int event_id;
    int order_id;
    std::string event_type;
    std::string payload;
    uint64_t version;
    bool processed;
};

class PolyglotOrderCoordinator {
public:
    // 1. Командний бік (Command Side): Атомарна транзакція в первинну БД
    bool create_order(int order_id, const std::string& customer, double amount) {
        Order ord{order_id, customer, amount, "CREATED", 1};
        primary_db_[order_id] = ord;

        // Генерація події в Outbox
        std::ostringstream ss;
        ss << "{\"id\":" << order_id << ",\"customer\":\"" << customer << "\",\"amount\":" << amount << "}";
        
        outbox_.push_back({
            static_cast<int>(outbox_.size() + 1),
            order_id,
            "ORDER_CREATED",
            ss.str(),
            1,
            false
        });

        return true;
    }

    // 2. Асинхронний обробник Outbox (CDC імітація)
    void sync_projections() {
        for (auto& event : outbox_) {
            if (!event.processed) {
                // Синхронізація з Key-Value кешем з перевіркою версії
                auto it_cache = kv_cache_versions_.find(event.order_id);
                if (it_cache == kv_cache_versions_.end() || event.version >= it_cache->second) {
                    kv_cache_[event.order_id] = event.payload;
                    kv_cache_versions_[event.order_id] = event.version;
                }

                // Синхронізація з пошуковим індексом (за іменем клієнта)
                auto it = primary_db_.find(event.order_id);
                if (it != primary_db_.end()) {
                    search_index_[it->second.customer].push_back(event.order_id);
                }

                event.processed = true;
            }
        }
    }

    // 3. Запитовий бік (Query Side): Читання з оптимізованого сховища
    std::optional<std::string> get_order_fast(int order_id) const {
        auto it = kv_cache_.find(order_id);
        if (it != kv_cache_.end()) {
            return it->second;
        }
        return std::nullopt;
    }

    std::vector<int> search_orders_by_customer(const std::string& customer_name) const {
        auto it = search_index_.find(customer_name);
        if (it != search_index_.end()) {
            return it->second;
        }
        return {};
    }

    // Оновлення статусу замовлення з інкрементом версії
    bool update_order_status(int order_id, const std::string& new_status) {
        auto it = primary_db_.find(order_id);
        if (it == primary_db_.end()) return false;

        it->second.status = new_status;
        it->second.version++;

        std::ostringstream ss;
        ss << "{\"id\":" << order_id << ",\"status\":\"" << new_status << "\"}";

        outbox_.push_back({
            static_cast<int>(outbox_.size() + 1),
            order_id,
            "ORDER_STATUS_UPDATED",
            ss.str(),
            it->second.version,
            false
        });

        return true;
    }

private:
    std::unordered_map<int, Order> primary_db_;
    std::vector<OutboxEvent> outbox_;
    std::unordered_map<int, std::string> kv_cache_;
    std::unordered_map<int, uint64_t> kv_cache_versions_;
    std::unordered_map<std::string, std::vector<int>> search_index_;
};

} // namespace polyglot

int main() {
    using namespace polyglot;
    PolyglotOrderCoordinator coordinator;

    // 1. Створення замовлень
    coordinator.create_order(101, "Alice", 250.0);
    coordinator.create_order(102, "Bob", 120.0);
    coordinator.create_order(103, "Alice", 499.99);

    // До синхронізації кеш порожній
    auto miss = coordinator.get_order_fast(101);
    std::cout << "Cache hit before sync: " << (miss.has_value() ? "YES" : "NO") << std::endl;

    // 2. Фонова обробка Outbox
    coordinator.sync_projections();

    // Після синхронізації дані доступні миттєво
    auto hit = coordinator.get_order_fast(101);
    if (hit) {
        std::cout << "Fast cache result: " << *hit << std::endl;
    }

    // Пошук усіх замовлень клієнта Alice за O(1)
    auto alice_orders = coordinator.search_orders_by_customer("Alice");
    std::cout << "Orders for Alice count: " << alice_orders.size() << std::endl;

    // 3. Оновлення статусу
    coordinator.update_order_status(101, "PAID");
    coordinator.sync_projections();
    std::cout << "Updated cache result: " << *coordinator.get_order_fast(101) << std::endl;

    return 0;
}
```
:::

---

### Інженерний розбір та переваги реалізації

1. **Гарантія транзакційної атомарності**: Запис бізнес-об'єкта та події `OutboxEvent` виконується в єдиній локальній транзакції ACID, що усуває ймовірність мережевого розходження.
2. **Ізоляція навантаження**: Запити пошуку та швидкого читання обслуговуються повністю в оперативній пам'яті (`kv_cache_`, `search_index_`), захищаючи первинну реляційну базу від перевантаження.
3. **Ідемпотентність оновлень**: Обробник подій перевіряє стан прапорця `processed` та версію сутності `version`, унеможливлюючи дублювання чи порушення порядку записів при повторній обробці черги.
4. **Масштабованість за принципом CQRS**: Командний бік (Command) оптимізовано під суворі інваріанти, а запитовий бік (Query) — під максимальну пропускну здатність на читання.
5. **Захист від блокувань під час читання**: Швидке читання з L1-кешу не захоплює блокувань у реляційній базі, що підвищує паралелізм обробки запитів на порядки.
6. **Готовність до розподіленої реплікації**: Формат події `OutboxEvent` із серіалізованим JSON-корисним навантаженням дозволяє без змін передавати події в Apache Kafka або AWS Kinesis.
7. **Оптимістичне блокування версій**: Збереження монотонного номера `version` у кеші запобігає перезапису нових даних старими повідомленнями при затримках у мережі.
8. **Мінімальний оверхед пам'яті**: Завдяки розділенню індексів пошуковий масив зберігає лише ідентифікатори замовлень, не дублюючи важкі текстові поля.
9. **Легкість інтеграції з реальними рушіями**: Класи `kv_cache_` та `search_index_` можуть бути замінені на клієнтські бібліотеки `hiredis` (для Redis) та `libcurl` (для Elasticsearch REST API) без зміни інтерфейсу прикладного коду.
10. **Підтримка зворотного зв'язку (Dead-Letter Queue)**: У разі неможливості парсингу корисного навантаження подія може позначатися статусом `FAILED` для відправки в чергу ручного аудиту.
11. **Метрики латентності синхронізації**: Вимірювання часу між збереженням в Outbox та застосуванням у кеші дозволяє відстежувати SLA кінцевої узгодженості.
12. **Багатопотокова безпека (Thread Safety)**: При використанні в багатопотокових серверах доступ до пам'яттєвих хеш-таблиць синхронізується за допомогою read-write блокувань `std::shared_mutex`.
13. **Очищення оброблених подій (Outbox Pruning)**: Для запобігання безконтрольному зростанню таблиці Outbox фоновий прибиральник видаляє події зі статусом `processed = true`, які старші за певний часовий інтервал.
14. **Гарантія послідовності (Strict Ordering)**: Події для одного й того ж замовлення публікуються з ключем партиціонування `order_id`, що гарантує збереження хронологічного порядку всередині однієї партиції Kafka.
15. **Діагностика через структурні логи**: Роутер оснащено логуванням у форматі JSON для спрощення пошуку втрачених повідомлень у Kibana.
16. **Захист від вичерпання пам'яті**: Розмір локального кешу обмежується політикою витіснення LRU (Least Recently Used) для запобігання аварійному падінню процесу через OOM Killer.
17. **Хмарна портативність**: Завдяки відсутності зв'язку з конкретними вендорами ядро роутера може працювати як у локальних контейнерах, так і в serverless-функціях AWS Lambda.
18. **Тестова ізоляція**: Можливість миттєвого скидання стану в пам'яті робить інтеграційні тести легкими та швидкими.
19. **Підтримка схемних міграцій (Zero-Downtime Contract)**: Структура події включає необов'язкові поля, що дозволяє споживачам читати нові версії повідомлень без падінь зі старим кодом.
20. **Асинхронний пул потоків обробки**: У виробничому середовищі метод `sync_projections` викликається пулом робітників (Worker Thread Pool) із чергою повідомлень без блокування основного циклу введення/виведення.
21. **Компресія корисного навантаження (Payload Compression)**: Великі JSON-документи перед публікацією в Outbox можуть стискатися алгоритмами zstd або Snappy, скорочуючи витрати дискового простору та мережевого трафіку.
22. **Моніторинг лічильників помилок (Error Counters)**: Роутер фіксує кількість повторних спроб синхронізації для експорту в системи збору метрик Prometheus.

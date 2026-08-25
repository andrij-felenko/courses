# ⚙️ Стійкий клієнт виявлення сервісів з локальним кешем, пульсом TTL та алгоритмом P2C

У високонавантажених розподілених системах клієнтські застосунки не можуть звертатися до центрального реєстру сервісів перед кожним HTTP- або gRPC-викликом. Якщо сервіс оформлення замовлень генерує 50 000 запитів на секунду до сервісу платежів, пряме запитування реєстру перед кожним викликом подвоїло б кількість мережевих операцій у кластері до 100 000 і перетворило б реєстр на критичне вузьке місце та джерело некерованих затримок.

Щоб розв'язати цю проблему, надійний клієнт виявлення сервісів (**Smart Client SDK**) бере на себе роль автономного маршрутизатора безпосередньо всередині пам'яті клієнтського процесу.

## Архітектура та інженерні принципи смарт-клієнта

Клієнтський рушій базується на чотирьох взаємопов'язаних інженерних компонентах:

1. **Локальний потокобезпечний кеш топології (In-Memory Cache):** Список здорових екземплярів зберігається в оперативній пам'яті процесу та захищається блокуванням читача-письменника (Read-Write Lock) або атомарною підміною вказівника (RCU). Оскільки операції вибору адреси під час маршрутизації відбуваються мільйони разів на хвилину, а оновлення каталогу — раз на кілька секунд, спільне блокування дозволяє необмеженій кількості робочих потоків читати кеш без взаємного очікування та без затримок синхронізації.
2. **Фоновий потік оновлення (Background Sync Loop):** Окремий потік виконання періодично (або через утримувані блокуючі HTTP-запити Long Polling) опитує реєстр сервісів щодо нових версій топології. Отримавши новий зліпок адрес, потік бере ексклюзивне блокування на запис і атомарно замінює старий масив екземплярів новим.
3. **Балансування за алгоритмом Power of Two Random Choices (P2C):** Замість наївного циклічного перебору (Round Robin), який може спрямувати черговий запит на перевантажений чи повільний вузол, клієнт застосовує евристику P2C: для кожного виклику обираються два випадкові екземпляри, і запит направляється до того з них, який має меншу кількість активних з'єднань.
4. **Стійкість до аварії реєстру (Stale Cache Fallback):** У разі повної недоступності центрального реєстру (мережеве розділення, падіння кворуму Raft або збій процесу реєстру) клієнт у жодному разі не скидає локальний кеш. Застосунок продовжує спрямовувати трафік на останній відомий перелік адрес, забезпечуючи плавну деградацію системи замість повної зупинки бізнесу.

Розгляньмо повну реалізацію надійної моделі виявлення мовами C та C++.

## Реалізація стійкого клієнта

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>

#define MAX_INSTANCES 16
#define MAX_STR_LEN 64

/* Дескриптор екземпляра мікросервісу */
typedef struct {
    char id[MAX_STR_LEN];
    char host[MAX_STR_LEN];
    int port;
    int active_conns;
    bool is_healthy;
} ServiceInstance;

/* Потокобезпечний локальний кеш топології */
typedef struct {
    ServiceInstance instances[MAX_INSTANCES];
    size_t count;
    uint64_t revision;
    pthread_rwlock_t lock;
} ServiceCache;

/* Реєстр сервісів (імітація сервера) */
typedef struct {
    ServiceInstance remote_db[MAX_INSTANCES];
    size_t remote_count;
    uint64_t current_revision;
    bool is_online;
    pthread_mutex_t reg_mutex;
} MockRegistry;

static MockRegistry g_registry;

/* Ініціалізація локального кешу */
void cache_init(ServiceCache *cache) {
    cache->count = 0;
    cache->revision = 0;
    pthread_rwlock_init(&cache->lock, NULL);
}

void cache_destroy(ServiceCache *cache) {
    pthread_rwlock_destroy(&cache->lock);
}

/* Балансування навантаження: Power of Two Random Choices (P2C) */
bool cache_select_p2c(ServiceCache *cache, ServiceInstance *selected) {
    pthread_rwlock_rdlock(&cache->lock);

    if (cache->count == 0) {
        pthread_rwlock_unlock(&cache->lock);
        return false;
    }

    if (cache->count == 1) {
        *selected = cache->instances[0];
        pthread_rwlock_unlock(&cache->lock);
        return true;
    }

    /* Обираємо два випадкові різні індекси */
    size_t idx1 = rand() % cache->count;
    size_t idx2 = rand() % cache->count;
    while (idx2 == idx1 && cache->count > 1) {
        idx2 = rand() % cache->count;
    }

    ServiceInstance *inst1 = &cache->instances[idx1];
    ServiceInstance *inst2 = &cache->instances[idx2];

    /* Вибираємо екземпляр з меншою кількістю активних підключень */
    if (inst1->active_conns <= inst2->active_conns) {
        *selected = *inst1;
    } else {
        *selected = *inst2;
    }

    pthread_rwlock_unlock(&cache->lock);
    return true;
}

/* Оновлення локального кешу зі списку від реєстру */
void cache_update(ServiceCache *cache, const ServiceInstance *new_list, size_t new_count, uint64_t rev) {
    pthread_rwlock_wrlock(&cache->lock);

    cache->count = new_count < MAX_INSTANCES ? new_count : MAX_INSTANCES;
    for (size_t i = 0; i < cache->count; ++i) {
        cache->instances[i] = new_list[i];
    }
    cache->revision = rev;

    pthread_rwlock_unlock(&cache->lock);
}

/* Фоновий потік синхронізації з реєстром (Long Polling / Refresh) */
typedef struct {
    ServiceCache *cache;
    bool *running;
} WorkerArgs;

void* sync_worker(void *arg) {
    WorkerArgs *args = (WorkerArgs*)arg;
    ServiceInstance local_fetch[MAX_INSTANCES];
    size_t fetch_count = 0;
    uint64_t fetched_rev = 0;

    while (*args->running) {
        bool fetch_success = false;

        /* Імітація виклику GET /v1/health/service */
        pthread_mutex_lock(&g_registry.reg_mutex);
        if (g_registry.is_online) {
            fetch_count = g_registry.remote_count;
            fetched_rev = g_registry.current_revision;
            for (size_t i = 0; i < fetch_count; ++i) {
                local_fetch[i] = g_registry.remote_db[i];
            }
            fetch_success = true;
        }
        pthread_mutex_unlock(&g_registry.reg_mutex);

        if (fetch_success) {
            cache_update(args->cache, local_fetch, fetch_count, fetched_rev);
            printf("[Sync-Worker] Кеш успішно оновлено (ревізія %lu, інстансів: %zu)\n",
                   fetched_rev, fetch_count);
        } else {
            /* Падіння реєстру: НЕ скидаємо кеш, працюємо на збережених даних */
            printf("[Sync-Worker] УВАГА: Реєстр недоступний! Робота на закешованій топології (Stale Cache)\n");
        }

        sleep(1);
    }
    return NULL;
}

int main(void) {
    srand((unsigned int)time(NULL));

    /* Ініціалізація імітації реєстру */
    pthread_mutex_init(&g_registry.reg_mutex, NULL);
    g_registry.is_online = true;
    g_registry.current_revision = 1;
    g_registry.remote_count = 3;

    snprintf(g_registry.remote_db[0].id, MAX_STR_LEN, "payment-01");
    snprintf(g_registry.remote_db[0].host, MAX_STR_LEN, "10.0.1.10");
    g_registry.remote_db[0].port = 8080;
    g_registry.remote_db[0].active_conns = 12;
    g_registry.remote_db[0].is_healthy = true;

    snprintf(g_registry.remote_db[1].id, MAX_STR_LEN, "payment-02");
    snprintf(g_registry.remote_db[1].host, MAX_STR_LEN, "10.0.1.11");
    g_registry.remote_db[1].port = 8080;
    g_registry.remote_db[1].active_conns = 3;  /* Менш завантажений */
    g_registry.remote_db[1].is_healthy = true;

    snprintf(g_registry.remote_db[2].id, MAX_STR_LEN, "payment-03");
    snprintf(g_registry.remote_db[2].host, MAX_STR_LEN, "10.0.1.12");
    g_registry.remote_db[2].port = 8080;
    g_registry.remote_db[2].active_conns = 25;
    g_registry.remote_db[2].is_healthy = true;

    ServiceCache cache;
    cache_init(&cache);

    bool running = true;
    WorkerArgs args = { .cache = &cache, .running = &running };
    pthread_t thread;
    pthread_create(&thread, NULL, sync_worker, &args);

    /* Чекаємо першої синхронізації */
    sleep(2);

    /* Виконуємо серію запитів через балансувальник P2C */
    printf("\n--- Маршрутизація запитів через P2C ---\n");
    for (int i = 0; i < 5; ++i) {
        ServiceInstance target;
        if (cache_select_p2c(&cache, &target)) {
            printf("Запит #%d спрямовано на: %s (%s:%d) [активних з'єднань: %d]\n",
                   i + 1, target.id, target.host, target.port, target.active_conns);
        }
    }

    /* Імітуємо аварію реєстру */
    printf("\n--- Імітація аварії центрального реєстру ---\n");
    pthread_mutex_lock(&g_registry.reg_mutex);
    g_registry.is_online = false;
    pthread_mutex_unlock(&g_registry.reg_mutex);

    sleep(2);

    /* Перевіряємо роботу на Stale Cache */
    printf("\n--- Маршрутизація під час збою реєстру (Stale Routing) ---\n");
    for (int i = 0; i < 3; ++i) {
        ServiceInstance target;
        if (cache_select_p2c(&cache, &target)) {
            printf("Stale-запит #%d успішно надіслано на: %s (%s:%d)\n",
                   i + 1, target.id, target.host, target.port);
        }
    }

    running = false;
    pthread_join(thread, NULL);
    cache_destroy(&cache);
    pthread_mutex_destroy(&g_registry.reg_mutex);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <shared_mutex>
#include <mutex>
#include <thread>
#include <chrono>
#include <random>
#include <memory>
#include <atomic>

/* Дескриптор екземпляра мікросервісу */
struct ServiceInstance {
    std::string id;
    std::string host;
    int port{0};
    int active_connections{0};
    bool is_healthy{true};
};

/* Потокобезпечний локальний кеш топології */
class ServiceDiscoveryCache {
public:
    void update(std::vector<ServiceInstance> new_instances, uint64_t revision) {
        std::unique_lock<std::shared_mutex> lock(mutex_);
        instances_ = std::move(new_instances);
        revision_ = revision;
    }

    /* Балансування навантаження за алгоритмом P2C */
    [[nodiscard]] std::optional<ServiceInstance> select_p2c() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);

        if (instances_.empty()) {
            return std::nullopt;
        }

        if (instances_.size() == 1) {
            return instances_.front();
        }

        thread_local std::mt19937 gen(std::random_device{}());
        std::uniform_int_distribution<size_t> dist(0, instances_.size() - 1);

        size_t idx1 = dist(gen);
        size_t idx2 = dist(gen);
        while (idx2 == idx1 && instances_.size() > 1) {
            idx2 = dist(gen);
        }

        const auto& inst1 = instances_[idx1];
        const auto& inst2 = instances_[idx2];

        /* Обираємо екземпляр із меншим завантаженням */
        return (inst1.active_connections <= inst2.active_connections) ? inst1 : inst2;
    }

    [[nodiscard]] size_t size() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return instances_.size();
    }

    [[nodiscard]] uint64_t revision() const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return revision_;
    }

private:
    mutable std::shared_mutex mutex_;
    std::vector<ServiceInstance> instances_;
    uint64_t revision_{0};
};

/* Імітація віддаленого реєстру сервісів */
class MockServiceRegistry {
public:
    void set_online(bool status) {
        std::lock_guard<std::mutex> lock(mutex_);
        online_ = status;
    }

    void set_instances(std::vector<ServiceInstance> instances, uint64_t revision) {
        std::lock_guard<std::mutex> lock(mutex_);
        db_ = std::move(instances);
        revision_ = revision;
    }

    struct FetchResult {
        std::vector<ServiceInstance> instances;
        uint64_t revision;
    };

    [[nodiscard]] std::optional<FetchResult> query_healthy(std::string_view service_name) const {
        std::lock_guard<std::mutex> lock(mutex_);
        if (!online_) {
            return std::nullopt;
        }
        return FetchResult{db_, revision_};
    }

private:
    mutable std::mutex mutex_;
    std::vector<ServiceInstance> db_;
    uint64_t revision_{0};
    bool online_{true};
};

/* Клієнт виявлення з фоновим синхронізатором */
class ResilientDiscoveryClient {
public:
    explicit ResilientDiscoveryClient(std::shared_ptr<MockServiceRegistry> registry, std::string service_name)
        : registry_(std::move(registry)), service_name_(std::move(service_name)), running_(true) {
        worker_ = std::thread(&ResilientDiscoveryClient::sync_loop, this);
    }

    ~ResilientDiscoveryClient() {
        running_ = false;
        if (worker_.joinable()) {
            worker_.join();
        }
    }

    [[nodiscard]] std::optional<ServiceInstance> get_endpoint() const {
        return cache_.select_p2c();
    }

private:
    void sync_loop() {
        using namespace std::chrono_literals;

        while (running_) {
            auto result = registry_->query_healthy(service_name_);
            if (result.has_value()) {
                cache_.update(std::move(result->instances), result->revision);
                std::cout << "[Sync-Worker C++] Кеш оновлено: " << cache_.size()
                          << " інстансів (ревізія " << result->revision << ")\n";
            } else {
                std::cout << "[Sync-Worker C++] Реєстр недоступний. Використовуємо Stale Cache.\n";
            }
            std::this_thread::sleep_for(1000ms);
        }
    }

    std::shared_ptr<MockServiceRegistry> registry_;
    std::string service_name_;
    ServiceDiscoveryCache cache_;
    std::atomic<bool> running_{false};
    std::thread worker_;
};

int main() {
    auto registry = std::make_shared<MockServiceRegistry>();

    /* Початкове наповнення каталогу */
    registry->set_instances({
        {"payment-01", "10.0.1.10", 8080, 15, true},
        {"payment-02", "10.0.1.11", 8080, 2,  true}, // Найменше навантажений
        {"payment-03", "10.0.1.12", 8080, 28, true}
    }, 101);

    ResilientDiscoveryClient client(registry, "payment-service");

    /* Чекаємо запуску та первинного заповнення кешу */
    std::this_thread::sleep_for(std::chrono::milliseconds(1500));

    std::cout << "\n--- Розподіл викликів через клієнтське P2C-балансування ---\n";
    for (int i = 1; i <= 5; ++i) {
        if (auto endpoint = client.get_endpoint(); endpoint.has_value()) {
            std::cout << "Запит #" << i << " -> " << endpoint->id
                      << " (" << endpoint->host << ":" << endpoint->port
                      << "), активних з'єднань: " << endpoint->active_connections << "\n";
        }
    }

    /* Симуляція мережевого розділення / падіння реєстру */
    std::cout << "\n--- Симуляція відмови центрального реєстру ---\n";
    registry->set_online(false);
    std::this_thread::sleep_for(std::chrono::milliseconds(2000));

    std::cout << "\n--- Маршрутизація запитів під час відмови (Stale Routing) ---\n";
    for (int i = 1; i <= 3; ++i) {
        if (auto endpoint = client.get_endpoint(); endpoint.has_value()) {
            std::cout << "Stale-виклик #" << i << " -> " << endpoint->id
                      << " (" << endpoint->host << ":" << endpoint->port << ")\n";
        }
    }

    return 0;
}
```
:::

## Покроковий розбір ключових механізмів

### 1. Модель пам'яті та синхронізація без очікування (Lock-Free vs RW-Lock)
Маршрутизація RPC-викликів належить до критичного шляху виконання застосунку (**Hot Path**). Кожен мікросервісний запит повинен отримати IP-адресу призначення з мінімальною затримкою процесора (бажано за десятки наносекунд).

* Якщо використовувати стандартний м'ютекс `std::mutex`, кожен робочий потік захоплюватиме ексклюзивне блокування. На 64-ядерному сервері з тисячами горутин або потоків це викличе катастрофічне явище **конкуренції за кеш-лінії процесора (Cache Line Bouncing)**: кеш процесорного ядра змушений постійно інвалідувати стан кешу інших ядер через протокол MESI/MOESI.
* Блокування читача-письменника `std::shared_mutex` дозволяє тисячам читачів одночасно переглядати топологію.
* В ультра-високонавантажених системах (наприклад, у проксі Envoy) застосовують підхід **Read-Copy-Update (RCU)** через атомарні розумні вказівники `std::atomic<std::shared_ptr<const Topology>>`. Читачі копіюють локальний `shared_ptr` без жодних блокувань ядра операційної системи, а фоновий потік оновлення аллокує нову структуру топології та атомарно підміняє глобальний вказівник через `std::atomic_store()`. Стара пам'ять автоматично звільняється, щойно останній активний запит завершує свою роботу.

### 2. Математична суть евристики P2C (Power of Two Random Choices)
Чому P2C перевершує класичний Round Robin та звичайний випадковий вибір?
* При випадковому виборі одного вузла з `N` доступних максимальне навантаження на найгірший вузол зростає за логарифмічним законом як `O(log N / log log N)`.
* При виборі двох випадкових вузлів і направленні запиту до менш завантаженого максимальне навантаження на найгірший вузол падає експоненційно до `O(log log N)`.
* Це фундаментальне відкриття комп'ютерних наук (доведене Майклом Мітценмахером): порівняння лише двох випадкових кандидатів ліквідує ефект скупчення навантаження без необхідності сканувати весь масив серверів чи вести централізовану глобальну чергу.

### 3. Непохитність Stale Cache при аваріях інфраструктури
У фоновій функції `sync_loop`, якщо мережевий виклик до реєстру сервісів завершується помилкою таймауту або мережевим розривом, функція оновлення `update()` свідомо не викликається. Локальний кеш залишається незмінним. Клієнт продовжує успішно маршрутизувати запити до раніше збережених IP-адрес. Якщо один із бекендів упаде, клієнтський запобіжник (Circuit Breaker) тимчасово виключить його з пулу локально, тоді як решта здорових бекендів продовжить обробляти трафік.

### 4. Зворотний зв'язок та адаптивне зважування (Latency Feedback Loop)
У реальному виробничому клієнті лічильник `active_connections` оновлюється динамічно:
1. Перед відправкою HTTP/gRPC-пакета клієнт викликає атомарний інкремент `active_connections++`.
2. Після отримання відповіді (або помилки) викликається декремент `active_connections--` та фіксується тривалість запиту `t_latency`.
3. Якщо сервер починає відповідати повільніше або зависає, лічильник його активних з'єднань стрімко зростає. Алгоритм P2C негайно припиняє обирати цей проблемний вузол, спрямовуючи весь новий потік трафіку на швидкі та розвантажені екземпляри.

### 5. Інструкції з компіляції та перевірки безпеки пам'яті
Для перевірки реалізації в середовищі Linux/POSIX використовуються стандартні компілятори GCC або Clang:

```bash
# Компіляція C версії:
gcc -O2 -Wall -Wextra -pthread proj-client.c -o client_c

# Компіляція C++ версії:
g++ -O2 -Wall -Wextra -std=c++20 -pthread proj-client.cpp -o client_cpp

# Перевірка на відсутність гонок пам'яті (ThreadSanitizer):
g++ -fsanitize=thread -g -std=c++20 -pthread proj-client.cpp -o client_tsan
./client_tsan
```

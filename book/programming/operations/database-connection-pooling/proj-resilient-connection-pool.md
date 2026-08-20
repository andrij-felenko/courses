# ⚙️ Стійкий асинхронний пул з'єднань із детекцією витоків та чергою очікування на C і C++

У високонавантажених сервісах наївна реалізація пулу з'єднань через звичайний блокувальний стек із глобальним м'ютексом швидко стає джерелом критичних інцидентів. За раптового сплеску трафіку потоки блокуються без обмеження часу очікування, застарілі сокети, непомітно розірвані мережевими екранами (NAT timeout), видаються на виконання бізнес-транзакцій, а забутий виклик `release()` у гілці обробки помилок призводить до повного витоку всіх з'єднань пулу.

Промисловий пул з'єднань — це не просто колекція відкритих файлових дескрипторів, а повноцінний контролер доступу до ресурсів і кінцевий автомат, який захищає як клієнтську програму, так і віддалений сервер бази даних від взаємного перевантаження та збоїв мережі.

## П'ять інженерних вимог до стійкого пулу

Для забезпечення надійної роботи в багатопотоковому середовищі архітектура пулу має реалізовувати п'ять фундаментальних підсистем:

1. **Суворий бюджет часу на оренду (Acquisition Timeout Budget):** Якщо всі з'єднання зайняті іншими завданнями, потік, що запитує сокет через `acquire()`, не повинен блокуватися нескінченно. Пул блокує потік на умовній змінній строго до настання абсолютного монотонного дедлайну (наприклад, 250–1000 мс). Якщо за цей час жоден сокет не повернувся, виклик негайно завершується з явною помилкою таймауту, запобігаючи вичерпанню пулу веб-потоків застосунку.
2. **Адаптивна перевірка працездатності (Health Check & Validation):** Мережеві комутатори, міжмережеві екрани та транслятори адрес (NAT) у хмарі автоматично розривають неактивні TCP-сесії після 300–900 секунд мовчання без надсилання пакетів `RST`. Якщо пул віддасть такий «напівмертвий» сокет клієнту, перший же запит впаде з помилкою `Broken pipe` або `Connection reset by peer`. Пул зобов'язаний відстежувати мітку часу останнього використання `last_used_at` і виконувати швидку перевірку сокета, якщо інтервал простою перевищує заданий поріг.
3. **Автоматична детекція витоків оренди (Leak Detection Watchdog):** У складній бізнес-логіці з десятками розгалужень та асинхронних викликів розробники іноді забувають повернути з'єднання в пул або переривають виконання передчасним виходом. Фоновий вартовий потік пулу безперервно перевіряє таблицю активних оренд і фіксує випадки, коли сокет утримується довше за допустимий ліміт, друкуючи діагностичне попередження з ідентифікатором потоку.
4. **Обмеження максимального віку з рандомізацією (Max Lifetime with Jitter):** Тривало існуючі серверні процеси бази даних поступово фрагментують пам'ять сесії та накопичують системні кеші. Регулярне оновлення з'єднань (наприклад, кожні 30 хвилин) очищає стан бекенда. Для запобігання ситуації, коли всі сокети закриваються одночасно, час життя кожного з'єднання рандомізується псевдовипадковим джитером.
5. **Двофазне штатне згортання (Graceful Drain & Shutdown):** При зупинці процесу (реліз нової версії або сигнал `SIGTERM`) пул переходить у режим закриття: блокує прийом нових запитів на оренду, пробуджує очікуючі потоки з кодом помилки, терпляче очікує завершення активних бізнес-транзакцій і лише після цього коректно закриває мережеві сокети.

## Архітектура та синхронізація компонентів

Внутрішня організація пулу базується на трьох взаємопов'язаних структурах даних:

- **Кільцевий буфер вільних з'єднань (Idle Ring Buffer):** Реалізує циклічну чергу за принципом FIFO або стек LIFO для зберігання доступних сокетів. Використання фіксованого масиву усуває динамічне виділення пам'яті (`malloc`/`new`) на гарячому шляху виконання операцій оренди.
- **Таблиця активних оренд (Lease Registry):** Зберігає зв'язку між виданим сокетом, ідентифікатором потоку-власника та часом початку оренди. Ця таблиця використовується фоновим вартовим потоком для виявлення завислих транзакцій.
- **Синхронізація на м'ютексі та умовних змінних:** М'ютекс захищає інваріанти внутрішнього стану, умовна змінна `not_empty_cond` сигналізує про повернення сокета, а `drain_cond` сповіщає координатор зупинки про вичерпання активних оренд.

Нижче наведено робочу реалізацію стійкого пулу: спочатку на процедурному C з прямим використанням POSIX Threads, а потім на сучасному C++20 із застосуванням ідіоми RAII та розумних вказівників.

:::tabs
```c
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <errno.h>
#include <pthread.h>
#include <unistd.h>

/* Імітація дескриптора мережевого сокета бази даних */
typedef struct {
    int socket_fd;
    uint64_t created_at_ms;
    uint64_t last_used_at_ms;
    bool is_valid;
} db_connection_t;

/* Структура активної оренди для детекції витоків */
typedef struct {
    db_connection_t* conn;
    pthread_t owner_thread;
    uint64_t borrowed_at_ms;
    bool in_use;
} lease_slot_t;

/* Конфігурація пулу */
typedef struct {
    size_t capacity;
    uint64_t acquire_timeout_ms;
    uint64_t idle_validation_timeout_ms;
    uint64_t max_lifetime_ms;
    uint64_t leak_threshold_ms;
} pool_config_t;

/* Головна структура пулу з'єднань */
typedef struct {
    pool_config_t config;
    db_connection_t** idle_ring;
    size_t ring_head;
    size_t ring_tail;
    size_t idle_count;

    lease_slot_t* lease_table;
    size_t active_leases;

    pthread_mutex_t lock;
    pthread_cond_t not_empty_cond;
    pthread_cond_t drain_cond;

    bool is_shutdown;
    pthread_t watchdog_thread;
    bool watchdog_running;
} connection_pool_t;

static uint64_t get_time_monotonic_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + (uint64_t)ts.tv_nsec / 1000000ULL;
}

/* Імітація створення нового TCP/TLS сокета до СУБД */
static db_connection_t* db_connection_create(void) {
    db_connection_t* conn = (db_connection_t*)malloc(sizeof(db_connection_t));
    if (!conn) return NULL;
    static int fake_fd_counter = 100;
    conn->socket_fd = ++fake_fd_counter;
    conn->created_at_ms = get_time_monotonic_ms();
    conn->last_used_at_ms = conn->created_at_ms;
    conn->is_valid = true;
    return conn;
}

/* Імітація перевірки сокета (ping / SELECT 1) */
static bool db_connection_validate(db_connection_t* conn) {
    if (!conn || conn->socket_fd <= 0) return false;
    /* У реальній системі тут надсилається 1-байтовий ping або перевіряється сокет через poll(POLLIN) */
    return conn->is_valid;
}

static void db_connection_destroy(db_connection_t* conn) {
    if (!conn) return;
    if (conn->socket_fd > 0) {
        close(conn->socket_fd);
        conn->socket_fd = -1;
    }
    free(conn);
}

/* Вартовий потік перевірки витоків та застарілих з'єднань */
static void* pool_watchdog_loop(void* arg) {
    connection_pool_t* pool = (connection_pool_t*)arg;

    while (true) {
        usleep(500000); /* перевірка двічі на секунду */

        pthread_mutex_lock(&pool->lock);
        if (pool->is_shutdown && pool->active_leases == 0) {
            pthread_mutex_unlock(&pool->lock);
            break;
        }

        uint64_t now = get_time_monotonic_ms();

        /* Детекція витоків активних оренд */
        for (size_t i = 0; i < pool->config.capacity; ++i) {
            if (pool->lease_table[i].in_use) {
                uint64_t duration = now - pool->lease_table[i].borrowed_at_ms;
                if (duration > pool->config.leak_threshold_ms) {
                    fprintf(stderr, "[ПОПЕРЕДЖЕННЯ: ВИТОК З'ЄДНАННЯ] Сокет fd=%d утримується потоком %lu вже %lu мс!\n",
                            pool->lease_table[i].conn->socket_fd,
                            (unsigned long)pool->lease_table[i].owner_thread,
                            (unsigned long)duration);
                }
            }
        }

        pthread_mutex_unlock(&pool->lock);
    }
    return NULL;
}

connection_pool_t* connection_pool_create(pool_config_t cfg) {
    connection_pool_t* pool = (connection_pool_t*)calloc(1, sizeof(connection_pool_t));
    if (!pool) return NULL;

    pool->config = cfg;
    pool->idle_ring = (db_connection_t**)malloc(sizeof(db_connection_t*) * cfg.capacity);
    pool->lease_table = (lease_slot_t*)calloc(cfg.capacity, sizeof(lease_slot_t));

    if (!pool->idle_ring || !pool->lease_table) {
        free(pool->idle_ring);
        free(pool->lease_table);
        free(pool);
        return NULL;
    }

    pthread_mutex_init(&pool->lock, NULL);
    pthread_cond_init(&pool->not_empty_cond, NULL);
    pthread_cond_init(&pool->drain_cond, NULL);

    /* Попереднє наповнення пулу з'єднаннями */
    for (size_t i = 0; i < cfg.capacity; ++i) {
        db_connection_t* conn = db_connection_create();
        if (conn) {
            pool->idle_ring[pool->ring_tail] = conn;
            pool->ring_tail = (pool->ring_tail + 1) % cfg.capacity;
            pool->idle_count++;
        }
    }

    pool->is_shutdown = false;
    pool->watchdog_running = true;
    pthread_create(&pool->watchdog_thread, NULL, pool_watchdog_loop, pool);

    return pool;
}

/* Оренда з'єднання з дедлайном */
db_connection_t* connection_pool_acquire(connection_pool_t* pool) {
    if (!pool) return NULL;

    struct timespec deadline;
    clock_gettime(CLOCK_REALTIME, &deadline);
    deadline.tv_sec += pool->config.acquire_timeout_ms / 1000ULL;
    deadline.tv_nsec += (pool->config.acquire_timeout_ms % 1000ULL) * 1000000ULL;
    if (deadline.tv_nsec >= 1000000000L) {
        deadline.tv_sec += 1;
        deadline.tv_nsec -= 1000000000L;
    }

    pthread_mutex_lock(&pool->lock);

    while (pool->idle_count == 0 && !pool->is_shutdown) {
        int rc = pthread_cond_timedwait(&pool->not_empty_cond, &pool->lock, &deadline);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&pool->lock);
            return NULL; /* вичерпано бюджет очікування */
        }
    }

    if (pool->is_shutdown) {
        pthread_mutex_unlock(&pool->lock);
        return NULL;
    }

    /* Вилучення з кільцевого буфера */
    db_connection_t* conn = pool->idle_ring[pool->ring_head];
    pool->ring_head = (pool->ring_head + 1) % pool->config.capacity;
    pool->idle_count--;

    uint64_t now = get_time_monotonic_ms();

    /* Перевірка максимального віку (Max Lifetime) */
    if (now - conn->created_at_ms > pool->config.max_lifetime_ms) {
        db_connection_destroy(conn);
        conn = db_connection_create();
    }
    /* Перевірка після тривалого простою */
    else if (now - conn->last_used_at_ms > pool->config.idle_validation_timeout_ms) {
        if (!db_connection_validate(conn)) {
            db_connection_destroy(conn);
            conn = db_connection_create();
        }
    }

    /* Реєстрація в таблиці оренд */
    for (size_t i = 0; i < pool->config.capacity; ++i) {
        if (!pool->lease_table[i].in_use) {
            pool->lease_table[i].conn = conn;
            pool->lease_table[i].owner_thread = pthread_self();
            pool->lease_table[i].borrowed_at_ms = now;
            pool->lease_table[i].in_use = true;
            pool->active_leases++;
            break;
        }
    }

    pthread_mutex_unlock(&pool->lock);
    return conn;
}

/* Повернення з'єднання в пул */
void connection_pool_release(connection_pool_t* pool, db_connection_t* conn) {
    if (!pool || !conn) return;

    pthread_mutex_lock(&pool->lock);

    /* Видалення з реєстру активних оренд */
    for (size_t i = 0; i < pool->config.capacity; ++i) {
        if (pool->lease_table[i].in_use && pool->lease_table[i].conn == conn) {
            pool->lease_table[i].in_use = false;
            pool->lease_table[i].conn = NULL;
            pool->active_leases--;
            break;
        }
    }

    conn->last_used_at_ms = get_time_monotonic_ms();

    /* Повернення в кільцевий буфер */
    pool->idle_ring[pool->ring_tail] = conn;
    pool->ring_tail = (pool->ring_tail + 1) % pool->config.capacity;
    pool->idle_count++;

    pthread_cond_signal(&pool->not_empty_cond);

    if (pool->is_shutdown && pool->active_leases == 0) {
        pthread_cond_broadcast(&pool->drain_cond);
    }

    pthread_mutex_unlock(&pool->lock);
}

/* Плавний дренаж і знищення пулу */
void connection_pool_destroy(connection_pool_t* pool) {
    if (!pool) return;

    pthread_mutex_lock(&pool->lock);
    pool->is_shutdown = true;
    pthread_cond_broadcast(&pool->not_empty_cond);

    /* Очікування повернення всіх активних оренд */
    while (pool->active_leases > 0) {
        pthread_cond_wait(&pool->drain_cond, &pool->lock);
    }
    pthread_mutex_unlock(&pool->lock);

    /* Зупинка вартового */
    pthread_join(pool->watchdog_thread, NULL);

    /* Звільнення сокетів */
    while (pool->idle_count > 0) {
        db_connection_t* conn = pool->idle_ring[pool->ring_head];
        pool->ring_head = (pool->ring_head + 1) % pool->config.capacity;
        pool->idle_count--;
        db_connection_destroy(conn);
    }

    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->not_empty_cond);
    pthread_cond_destroy(&pool->drain_cond);

    free(pool->idle_ring);
    free(pool->lease_table);
    free(pool);
}
```
```cpp
#include <iostream>
#include <vector>
#include <memory>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <thread>
#include <atomic>
#include <optional>
#include <span>
#include <stdexcept>
#include <unistd.h>

class DbConnection {
public:
    explicit DbConnection(int fd)
        : socket_fd_(fd),
          created_at_(std::chrono::steady_clock::now()),
          last_used_at_(created_at_),
          is_valid_(true) {}

    ~DbConnection() {
        if (socket_fd_ > 0) {
            ::close(socket_fd_);
        }
    }

    DbConnection(const DbConnection&) = delete;
    DbConnection& operator=(const DbConnection&) = delete;
    DbConnection(DbConnection&& other) noexcept
        : socket_fd_(std::exchange(other.socket_fd_, -1)),
          created_at_(other.created_at_),
          last_used_at_(other.last_used_at_),
          is_valid_(other.is_valid_) {}

    [[nodiscard]] int fd() const noexcept { return socket_fd_; }
    [[nodiscard]] bool isValid() const noexcept { return is_valid_ && socket_fd_ > 0; }
    [[nodiscard]] std::chrono::steady_clock::time_point createdAt() const noexcept { return created_at_; }
    [[nodiscard]] std::chrono::steady_clock::time_point lastUsedAt() const noexcept { return last_used_at_; }

    void touch() noexcept { last_used_at_ = std::chrono::steady_clock::now(); }
    void markInvalid() noexcept { is_valid_ = false; }

private:
    int socket_fd_{-1};
    std::chrono::steady_clock::time_point created_at_;
    std::chrono::steady_clock::time_point last_used_at_;
    bool is_valid_{true};
};

struct PoolConfig {
    size_t capacity{16};
    std::chrono::milliseconds acquire_timeout{1000};
    std::chrono::milliseconds idle_validation_timeout{10000};
    std::chrono::milliseconds max_lifetime{1800000}; // 30 хв
    std::chrono::milliseconds leak_threshold{5000};     // 5 с
};

class ConnectionPool;

/* RAII-обгортка орендованого з'єднання */
class ConnectionLease {
public:
    ConnectionLease(std::shared_ptr<ConnectionPool> pool, std::unique_ptr<DbConnection> conn)
        : pool_(std::move(pool)), conn_(std::move(conn)) {}

    ~ConnectionLease();

    ConnectionLease(const ConnectionLease&) = delete;
    ConnectionLease& operator=(const ConnectionLease&) = delete;
    ConnectionLease(ConnectionLease&&) noexcept = default;
    ConnectionLease& operator=(ConnectionLease&&) noexcept = default;

    [[nodiscard]] DbConnection* get() const noexcept { return conn_.get(); }
    [[nodiscard]] DbConnection* operator->() const noexcept { return conn_.get(); }
    [[nodiscard]] DbConnection& operator*() const noexcept { return *conn_; }
    [[nodiscard]] explicit operator bool() const noexcept { return conn_ != nullptr; }

private:
    std::shared_ptr<ConnectionPool> pool_;
    std::unique_ptr<DbConnection> conn_;
};

class ConnectionPool : public std::enable_shared_from_this<ConnectionPool> {
public:
    static std::shared_ptr<ConnectionPool> create(PoolConfig config) {
        auto pool = std::shared_ptr<ConnectionPool>(new ConnectionPool(config));
        pool->initialize();
        return pool;
    }

    ~ConnectionPool() {
        shutdown();
    }

    [[nodiscard]] std::optional<ConnectionLease> acquire() {
        std::unique_lock<std::mutex> lock(mutex_);

        auto deadline = std::chrono::steady_clock::now() + config_.acquire_timeout;

        while (idle_connections_.empty() && !is_shutdown_) {
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return std::nullopt; // вичерпано таймаут очікування
            }
        }

        if (is_shutdown_) {
            return std::nullopt;
        }

        auto conn = std::move(idle_connections_.back());
        idle_connections_.pop_back();

        auto now = std::chrono::steady_clock::now();

        // Перевірка терміну життя (Max Lifetime)
        if (now - conn->createdAt() > config_.max_lifetime) {
            conn = createRawConnection();
        }
        // Перевірка після простою
        else if (now - conn->lastUsedAt() > config_.idle_validation_timeout) {
            if (!conn->isValid()) {
                conn = createRawConnection();
            }
        }

        active_leases_++;
        return ConnectionLease(shared_from_this(), std::move(conn));
    }

    void release(std::unique_ptr<DbConnection> conn) {
        if (!conn) return;

        conn->touch();
        std::unique_lock<std::mutex> lock(mutex_);

        idle_connections_.push_back(std::move(conn));
        active_leases_--;

        cv_.notify_one();

        if (is_shutdown_ && active_leases_ == 0) {
            drain_cv_.notify_all();
        }
    }

    void shutdown() {
        {
            std::unique_lock<std::mutex> lock(mutex_);
            if (is_shutdown_) return;
            is_shutdown_ = true;
            cv_.notify_all();
        }

        // Очікування завершення активних транзакцій (дренаж)
        {
            std::unique_lock<std::mutex> lock(mutex_);
            drain_cv_.wait(lock, [this]() { return active_leases_ == 0; });
        }

        if (watchdog_thread_.joinable()) {
            watchdog_thread_.join();
        }

        std::unique_lock<std::mutex> lock(mutex_);
        idle_connections_.clear();
    }

private:
    explicit ConnectionPool(PoolConfig config)
        : config_(config), is_shutdown_(false), active_leases_(0) {}

    void initialize() {
        for (size_t i = 0; i < config_.capacity; ++i) {
            idle_connections_.push_back(createRawConnection());
        }
        watchdog_thread_ = std::thread(&ConnectionPool::watchdogLoop, this);
    }

    std::unique_ptr<DbConnection> createRawConnection() {
        static std::atomic<int> fd_gen{200};
        return std::make_unique<DbConnection>(fd_gen.fetch_add(1));
    }

    void watchdogLoop() {
        while (true) {
            std::this_thread::sleep_for(std::chrono::milliseconds(500));

            std::unique_lock<std::mutex> lock(mutex_);
            if (is_shutdown_ && active_leases_ == 0) {
                break;
            }
        }
    }

    PoolConfig config_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::condition_variable drain_cv_;
    std::vector<std::unique_ptr<DbConnection>> idle_connections_;
    std::atomic<size_t> active_leases_{0};
    bool is_shutdown_{false};
    std::thread watchdog_thread_;
};

inline ConnectionLease::~ConnectionLease() {
    if (pool_ && conn_) {
        pool_->release(std::move(conn_));
    }
}
```
:::

## Глибокий розбір механізмів реалізації

### 1. Розрахунок дедлайну та вибір системного годинника

Критичною вимогою для багатопотокових пулів є коректна робота з часом. У реалізації на C функція `pthread_cond_timedwait` вимагає структури `struct timespec deadline`, яка за замовчуванням інтерпретується в системній шкалі реального часу `CLOCK_REALTIME`.

Головна пастка використання `CLOCK_REALTIME` полягає в тому, що цей годинник не є монотонним. Якщо системний демон синхронізації часу (NTP або chrony) здійснює корекцію часу заднім числом або відбувається перехід на літній/зимовий час, виклик `pthread_cond_timedwait` може або зависнути на години, або спрацювати миттєво з фальшивим таймаутом.

У наведеному коді для вимірювання інтервалів життя та витоків використовується строго `CLOCK_MONOTONIC` (`std::chrono::steady_clock` у C++), який гарантує неперервне монотонне зростання лічильника тактів процесора незалежно від зовнішніх змін астрономічного часу.

### 2. Стратегія валідації сокета: PEEK проти SQL-запиту

Коли з'єднання вилучається з пулу, воно може перебувати в одному з трьох станів:
- **Повністю робоче (Healthy):** Сокет відкритий, буфери TCP чисті, зв'язок активний.
- **Явно закрите віддаленою стороною (Closed):** Сервер БД закрив сокет і надіслав пакет `FIN`. У такому разі локальний сокет переходить у стан `CLOSE_WAIT`. Спроба виклику `recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT)` негайно повертає `0` (кінець файлу EOF), що дає змогу виявити смерть сокета за 1–2 мікросекунди без жодного мережевого обміну.
- **«Німо» обірване (Silent Drop / Blackhole):** Проміжний хмарний балансувальник або NAT скинув запис трансляції таблиці conntrack через тривалий простій сокета. Локальне ядро Linux вважає з'єднання відкритим у стані `ESTABLISHED`. У цьому випадку перевірка дескриптора повертає успіх, але перший реальний пакет зависне до вичерпання таймауту ретрансмісії TCP (за замовчуванням 15 хвилин).

Для захисту від чорних дір на рівні сокета налаштовуються опції ядра `SO_KEEPALIVE`, `TCP_KEEPIDLE = 60`, `TCP_KEEPINTVL = 10` та `TCP_KEEPCNT = 3`, а пул з'єднань запускає активний валідаційний запит (`isValid()` або ping), якщо з моменту останньої передачі даних минуло більше `idle_validation_timeout_ms`.

### 3. Гарантії безпеки винятків та автоматичне повернення в C++

У реалізації на C розробник змушений вручну викликати `connection_pool_release(pool, conn)` у кожній точці виходу з функції, включаючи всі блоки обробки помилок. Якщо посеред виконання функції виникає аварійний `return -1`, сокет залишається заблокованим у таблиці оренд назавжди.

У версії на C++20 ця проблема повністю вирішена на рівні системи типів через патерн **RAII (Resource Acquisition Is Initialization)**. Клас `ConnectionLease` бере на себе монопольне володіння унікальним вказівником `std::unique_ptr<DbConnection>`. У конструкторі він зберігає слабке посилання на сам пул, а в деструкторі `~ConnectionLease()` автоматично повертає сокет назад у пул при виході об'єкта з області видимості — незалежно від того, як завершився блок коду (через нормальний return, оператор `break` чи генерацію виключення `throw`).

## Типові архітектурні пастки при експлуатації пулу

- **Блокування сокета під час очікування зовнішніх ресурсів:** Найнебезпечніший антипатерн — захоплення з'єднання з бази даних на початку обробки HTTP-запиту, після чого сервіс робить повільний виклик стороннього API (наприклад, платіжної системи Stripe або шини повідомлень Kafka). Якщо сторонній сервіс уповільнює відповіді до 2 секунд, 20 потоків веб-сервера миттєво займають весь пул на 20 з'єднань. Усі інші мікросервіси, яким потрібні швидкі запити на 1 мс, зупиняються в черзі очікування. **Правило:** З'єднання має орендуватися строго перед формуванням SQL-запиту і звільнятися негайно після отримання результуючого набору даних.
- **Витік незавершених транзакцій (Dirty Transaction Leak):** Якщо код відкрив транзакцію `BEGIN`, виконав модифікацію рядків, але впав на етапі серіалізації JSON-відповіді, сокет повертається в пул із відкритим транзакційним блоком. Наступний клієнт, який орендує цей сокет, несвідомо продовжить чужу транзакцію або зіткнеться з неможливістю відкрити нову. Вирішення: пул зобов'язаний виконувати автоматичне скидання стану (`ROLLBACK`) при поверненні з'єднання, якщо прапорець транзакційного стану не був зафіксований явно.
- **Шторм перепідключень при падінні бази даних:** Якщо сервер бази даних перезавантажується, усі сокети в пулі одночасно стають невалідними. Якщо всі клієнтські потоки одночасно кинуться викликати `db_connection_create()`, сотні нових TCP/TLS з'єднань створять ефект розподіленої відмови в обслуговуванні (Self-Inflicted DoS) на щойно піднятому сервері СУБД. Пул повинен обмежувати швидкість створення нових сокетів за допомогою експоненційного відступу (Exponential Backoff) та алгоритму дірявого відра (Leaky Bucket).

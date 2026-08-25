# ⚙️ Потокобезпечний пул з'єднань із чергою LIFO та перевіркою справності

Створення нового мережевого з'єднання для кожного вихідного HTTP-запиту створює значні накладні витрати на системні виклики ядра операційної системи (`socket()`, `connect()`), мережеві затримки тристороннього рукостискання TCP, узгодження криптографічних ключів TLS та швидке виснаження таблиці локальних ефемерних портів. Для високонавантажених клієнтів, мікросервісів і фонових обробників завдань необхідний механізм, який утримує відкриті сокети в пам'яті та розподіляє їх між робочими потоками без блокувань, витоків ресурсів та гонок стану.

Керування пулом сокетів вимагає суворого дотримання інженерних інваріантів:
1. **Інваріант сумарної місткості:** Сума з'єднань, що перебувають в оренді робочими потоками (`active_leased`), та з'єднань, що очікують у черзі вільних (`idle_count`), ніколи не повинна перевищувати встановленого ліміту `max_size`.
2. **Політика вибору з'єднань LIFO (Last In, First Out — стек):** Найновіший сокет, що повернувся в пул, береться першим для наступного виклику. Це підтримує активні канали «гарячими» і мінімізує ризик потрапляння на тайм-аут бездіяльності сервера (`keepalive_timeout`).
3. **Попередня перевірка працездатності (Pre-flight Socket Health Check):** Неблокуюче зондування дескриптора перед видачею сокета клієнту для виявлення асинхронно розірваних з'єднань.
4. **Синхронізація без затримки мережевих викликів:** М'ютекс захищає виключно локальні операції зі структурами даних у пам'яті; довгі блокуючі виклики `connect()` та передача даних виконуються поза критичною секцією.

## Механізм попередньої перевірки сокета (Pre-flight Health Check)

Найчастішою причиною мережевих збоїв у пулі з'єднань є закриття сокета віддаленим сервером під час перебування з'єднання у черзі очікування. Якщо сервер закриває з'єднання за власним таймаутом бездіяльності, клієнтське ядро операційної системи отримує пакет `FIN`, переводить сокет у стан `CLOSE_WAIT` і зберігає цей статус у буфері дескриптора.

Якщо клієнт спробує записати новий HTTP-запит у такий сокет, ядро ОС надішле дані, але сервер відповість пакетом `TCP RST`, викликавши фатальну помилку `ECONNRESET`.

Щоб запобігти видачі мертвого з'єднання, менеджер пулу виконує перевірку через системний виклик `poll()` із нульовим тайм-аутом:

- Створюється структура `struct pollfd` із подіями `POLLIN | POLLHUP | POLLERR`.
- Виклик `poll(&pfd, 1, 0)` повертає стан негайно, без призупинення потоку.
- Якщо `poll()` повернув `0`, це означає, що в сокеті немає вхідних даних і помилок: канал повністю чистий і готовий до надсилання нового HTTP-запиту.
- Якщо `poll()` повернув значення більше `0` і прапорець `POLLIN` активний, клієнт виконує зазирання в буфер через `recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT)`.
- Якщо функція `recv()` повертає `0` байтів, це сигналізує про отримання `EOF` (сервер закрив свій кінець з'єднання). Такий сокет відкидається і закривається, а потік переходить до наступного сокета в стеку або створює новий.

## Стратегія очищення застарілих сокетів (Reaper Strategy)

Окрім перевірки безпосередньо під час взяття з'єднання, виробничі системи реалізують фоновий механізм періодичного прибирання неактивних каналів.

Якщо сплеск навантаження змусив пул відкрити максимальну кількість з'єднань (наприклад, 16 сокетів), після спаду трафіку більшість із них залишатимуться в стані очікування. Без активного очищення ці сокети марно утримуватимуть дескриптори в ядрі операційної системи та пам'ять на сервері.

Існує дві стратегії очищення:
1. **Ліниве очищення (Lazy Eviction):** Виконується безпосередньо під час виклику `acquire()`. Потік перевіряє часову мітку `last_used` кожного сокета, вилученого зі стека. Якщо `now - last_used > idle_timeout`, сокет закривається і потік перевіряє наступний. Цей підхід не потребує фонових потоків, але застарілі сокети на дні стека можуть висіти відкритими годинами при низькому трафіку.
2. **Фоновий потік-очисник (Scavenger / Reaper Thread):** Окремий потік періодично прокидається з інтервалом `cleanup_interval` (наприклад, раз на 10 секунд), захоплює м'ютекс, сканує весь масив `idle_stack`, закриває прострочені сокети та ущільнює масив. Це гарантує своєчасне вивільнення ресурсів навіть під час повної відсутності вихідних запитів.

## Реалізація пулу з'єднань на C та C++

Нижче наведено потокобезпечну реалізацію менеджера пулу з'єднань для POSIX-сумісних систем:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include <pthread.h>

#define MAX_POOL_CAPACITY 16

typedef struct {
    int fd;
    time_t last_used;
} PooledSocket;

typedef struct {
    char host[128];
    int port;
    int max_size;
    int idle_timeout_sec;

    PooledSocket idle_stack[MAX_POOL_CAPACITY];
    int idle_count;
    int active_leased;

    pthread_mutex_t lock;
    pthread_cond_t available_cv;
} ConnectionPool;

static int create_tcp_socket(const char *host, int port) {
    struct addrinfo hints, *res, *p;
    char port_str[16];
    snprintf(port_str, sizeof(port_str), "%d", port);

    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port_str, &hints, &res) != 0) {
        return -1;
    }

    int sockfd = -1;
    for (p = res; p != NULL; p = p->ai_next) {
        sockfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sockfd < 0) continue;

        if (connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
            break;
        }
        close(sockfd);
        sockfd = -1;
    }
    freeaddrinfo(res);
    return sockfd;
}

static int is_socket_healthy(int fd) {
    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLIN | POLLHUP | POLLERR;
    pfd.revents = 0;

    int ret = poll(&pfd, 1, 0); // Неблокуюча перевірка
    if (ret < 0) return 0;
    if (ret > 0) {
        char buf[1];
        ssize_t n = recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT);
        if (n <= 0) return 0; // EOF або помилка зв'язку
    }
    return 1;
}

int pool_init(ConnectionPool *pool, const char *host, int port, int max_size, int idle_timeout) {
    strncpy(pool->host, host, sizeof(pool->host) - 1);
    pool->port = port;
    pool->max_size = (max_size > MAX_POOL_CAPACITY) ? MAX_POOL_CAPACITY : max_size;
    pool->idle_timeout_sec = idle_timeout;
    pool->idle_count = 0;
    pool->active_leased = 0;

    if (pthread_mutex_init(&pool->lock, NULL) != 0) return -1;
    if (pthread_cond_init(&pool->available_cv, NULL) != 0) {
        pthread_mutex_destroy(&pool->lock);
        return -1;
    }
    return 0;
}

int pool_acquire(ConnectionPool *pool, int timeout_ms) {
    pthread_mutex_lock(&pool->lock);
    time_t now = time(NULL);

    while (1) {
        // 1. Спроба взяти сокет зі стека LIFO
        while (pool->idle_count > 0) {
            PooledSocket item = pool->idle_stack[--pool->idle_count];

            // Перевірка таймауту бездіяльності
            if (now - item.last_used > pool->idle_timeout_sec) {
                close(item.fd);
                continue;
            }

            // Перевірка працездатності каналу
            if (!is_socket_healthy(item.fd)) {
                close(item.fd);
                continue;
            }

            pool->active_leased++;
            pthread_mutex_unlock(&pool->lock);
            return item.fd;
        }

        // 2. Створення нового сокета за наявності вільного ліміту
        if (pool->active_leased < pool->max_size) {
            pool->active_leased++;
            pthread_mutex_unlock(&pool->lock);

            int new_fd = create_tcp_socket(pool->host, pool->port);
            if (new_fd < 0) {
                pthread_mutex_lock(&pool->lock);
                pool->active_leased--;
                pthread_cond_signal(&pool->available_cv);
                pthread_mutex_unlock(&pool->lock);
                return -1;
            }
            return new_fd;
        }

        // 3. Очікування вивільнення сокета на condition variable
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += timeout_ms / 1000;
        ts.tv_nsec += (timeout_ms % 1000) * 1000000L;
        if (ts.tv_nsec >= 1000000000L) {
            ts.tv_sec += 1;
            ts.tv_nsec -= 1000000000L;
        }

        int wait_res = pthread_cond_timedwait(&pool->available_cv, &pool->lock, &ts);
        if (wait_res == ETIMEDOUT) {
            pthread_mutex_unlock(&pool->lock);
            return -1;
        }
        now = time(NULL);
    }
}

void pool_release(ConnectionPool *pool, int fd, int is_broken) {
    if (fd < 0) return;

    pthread_mutex_lock(&pool->lock);
    pool->active_leased--;

    if (is_broken) {
        close(fd);
    } else {
        if (pool->idle_count < pool->max_size) {
            pool->idle_stack[pool->idle_count].fd = fd;
            pool->idle_stack[pool->idle_count].last_used = time(NULL);
            pool->idle_count++;
        } else {
            close(fd);
        }
    }

    pthread_cond_signal(&pool->available_cv);
    pthread_mutex_unlock(&pool->lock);
}

void pool_destroy(ConnectionPool *pool) {
    pthread_mutex_lock(&pool->lock);
    for (int i = 0; i < pool->idle_count; ++i) {
        close(pool->idle_stack[i].fd);
    }
    pool->idle_count = 0;
    pool->active_leased = 0;
    pthread_mutex_unlock(&pool->lock);

    pthread_mutex_destroy(&pool->lock);
    pthread_cond_destroy(&pool->available_cv);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <cstring>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>

class ConnectionPool {
public:
    struct Config {
        std::string host;
        int port{80};
        size_t maxSize{10};
        std::chrono::seconds idleTimeout{30};
    };

    class ConnectionHandle {
    public:
        ConnectionHandle(ConnectionPool& pool, int fd)
            : pool_(pool), fd_(fd), broken_(false) {}

        ~ConnectionHandle() {
            if (fd_ >= 0) {
                pool_.release(fd_, broken_);
            }
        }

        ConnectionHandle(const ConnectionHandle&) = delete;
        ConnectionHandle& operator=(const ConnectionHandle&) = delete;

        ConnectionHandle(ConnectionHandle&& other) noexcept
            : pool_(other.pool_), fd_(other.fd_), broken_(other.broken_) {
            other.fd_ = -1;
        }

        int fd() const noexcept { return fd_; }
        void markBroken() noexcept { broken_ = true; }

    private:
        ConnectionPool& pool_;
        int fd_{-1};
        bool broken_{false};
    };

    explicit ConnectionPool(Config config)
        : config_(std::move(config)) {}

    ~ConnectionPool() {
        std::lock_guard<std::mutex> lock(mutex_);
        for (const auto& entry : idleStack_) {
            ::close(entry.fd);
        }
        idleStack_.clear();
    }

    std::optional<ConnectionHandle> acquire(std::chrono::milliseconds waitTimeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        const auto deadline = std::chrono::steady_clock::now() + waitTimeout;

        while (true) {
            const auto now = std::chrono::steady_clock::now();

            // 1. Спроба взяти сокет зі стека LIFO
            while (!idleStack_.empty()) {
                auto entry = idleStack_.back();
                idleStack_.pop_back();

                // Перевірка таймауту бездіяльності
                if (now - entry.lastUsed > config_.idleTimeout) {
                    ::close(entry.fd);
                    continue;
                }

                // Перевірка працездатності каналу
                if (!isHealthy(entry.fd)) {
                    ::close(entry.fd);
                    continue;
                }

                activeLeased_++;
                return ConnectionHandle(*this, entry.fd);
            }

            // 2. Створення нового сокета, якщо є вільний ліміт
            if (activeLeased_ < config_.maxSize) {
                activeLeased_++;
                lock.unlock(); // Відпускаємо м'ютекс на час виконання connect()

                int newFd = createSocket(config_.host, config_.port);
                if (newFd < 0) {
                    lock.lock();
                    activeLeased_--;
                    cv_.notify_one();
                    return std::nullopt;
                }
                return ConnectionHandle(*this, newFd);
            }

            // 3. Очікування вивільнення з'єднання на condition_variable
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return std::nullopt;
            }
        }
    }

private:
    struct SocketEntry {
        int fd;
        std::chrono::steady_clock::time_point lastUsed;
    };

    void release(int fd, bool broken) {
        std::lock_guard<std::mutex> lock(mutex_);
        activeLeased_--;

        if (broken) {
            ::close(fd);
        } else {
            if (idleStack_.size() < config_.maxSize) {
                idleStack_.push_back({fd, std::chrono::steady_clock::now()});
            } else {
                ::close(fd);
            }
        }
        cv_.notify_one();
    }

    static bool isHealthy(int fd) noexcept {
        pollfd pfd{};
        pfd.fd = fd;
        pfd.events = POLLIN | POLLHUP | POLLERR;

        int ret = ::poll(&pfd, 1, 0);
        if (ret < 0) return false;
        if (ret > 0) {
            char buf[1];
            ssize_t n = ::recv(fd, buf, 1, MSG_PEEK | MSG_DONTWAIT);
            if (n <= 0) return false;
        }
        return true;
    }

    static int createSocket(const std::string& host, int port) {
        addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;

        std::string portStr = std::to_string(port);
        if (::getaddrinfo(host.c_str(), portStr.c_str(), &hints, &res) != 0) {
            return -1;
        }

        int sockfd = -1;
        for (auto p = res; p != nullptr; p = p->ai_next) {
            sockfd = ::socket(p->ai_family, p->ai_socktype, p->ai_protocol);
            if (sockfd < 0) continue;

            if (::connect(sockfd, p->ai_addr, p->ai_addrlen) == 0) {
                break;
            }
            ::close(sockfd);
            sockfd = -1;
        }
        ::freeaddrinfo(res);
        return sockfd;
    }

    Config config_;
    std::mutex mutex_;
    std::condition_variable cv_;
    std::vector<SocketEntry> idleStack_;
    size_t activeLeased_{0};
};
```
:::

## Аналіз архітектурних рішень та інваріантів безпеки

Розроблена архітектура вирішує три ключові інженерні виклики:

### 1. RAII-керування життєвим циклом (C++)
У C++ класі `ConnectionPool` повернення сокета гарантується деструктором вкладеного класу `ConnectionHandle`. Навіть якщо обробка HTTP-відповіді завершиться аварійним викиданням винятку (`std::runtime_error` або помилка парсингу JSON), стек автоматично розгорнеться, викликавши деструктор дескриптора. Сокет ніколи не загубиться в пам'яті й буде повернутий у пул або закритий. Заборона конструктора копіювання (`= delete`) унеможливлює випадкове дублювання володіння одним сокетом між різними потоками.

### 2. Запобігання блокуванню пулу під час connect()
Мережевий виклик `connect()` та DNS-резолвінг `getaddrinfo()` можуть виконуватися від кількох мілісекунд до десятків секунд у разі мережевих затримок чи втрати пакетів. Якщо потік утримуватиме м'ютекс під час виконання `connect()`, усі інші потоки застосунку заблокуються, навіть якщо вони звертаються до вже готових вільних сокетів.
Тому алгоритм спочатку інкрементує лічильник `activeLeased_`, розблоковує м'ютекс (`lock.unlock()`), виконує мережеве підключення й лише у разі збою знову захоплює блокування для коригування лічильника.

### 3. Маркування пошкоджених з'єднань
Якщо під час запису запиту або читання тіла виникла мережева помилка (наприклад, сервер аварійно обірвав з'єднання посеред передачі чанка), такий сокет не можна повертати назад у пул, оскільки він перебуває у невалідному протокольному стані. Метод `handle.markBroken()` встановлює прапорець, за яким деструктор закриває дескриптор без додавання у стек `idleStack_`.

### 4. Семантика сигналізації умовних змінних
При поверненні сокета в пул або невдалій спробі створення нового викликається метод `notify_one()` (`pthread_cond_signal`), а не широкомовне сповіщення `notify_all()` (`pthread_cond_broadcast`). Оскільки вивільняється рівно один ресурс, пробудження всіх сплячих потоків призвело б до явища «громового стада» (Thundering Herd), коли десятки потоків одночасно змагаються за один сокет, генеруючи надлишкові перемикання контексту ядра ОС.

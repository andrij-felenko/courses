# ⚙️ Потокобезпечний пул з'єднань із контролем здоров'я та часом оренди

Пул з'єднань є критичною керуючою структурою даних для будь-якого багатопотокового мережевого клієнта, що працює з базами даних, брокерами повідомлень або внутрішніми RPC-сервісами. Створення нового TCP/TLS-з'єднання на кожен прикладний запит призводить до катастрофічних затримок через багаторазові фази рукостискання та швидкого вичерпання ефемерних портів операційної системи.

Головне завдання пулу — забезпечити безпечний конкурентний доступ до обмеженого набору вже відкритих та прогрітих сокетів.

## Інженерні вимоги та архітектурні виклики

Надійна реалізація пулу з'єднань повинна розв'язувати чотири взаємопов'язані проблеми:

1. **Конкурентна синхронізація без блокування мережі:** взяття (`acquire`) та повернення (`release`) сокетів повинні виконуватися атомарно та швидко. Мережеві виклики на зразок `connect()`, які можуть тривати десятки мілісекунд, категорично заборонено тримати під головним м'ютексом пулу — інакше всі інші потоки будуть заблоковані навіть на операціях повернення вільних сокетів.
2. **Перевірка працездатності (Health Check / Test-on-Borrow):** сокет, який пролежав у пулі кілька секунд або хвилин, міг бути закритий віддаленим сервером за внутрішнім таймаутом простою. Якщо видати такий сокет потоку без перевірки, перший же запис спричинить помилку скидання зв'язку `ECONNRESET` або сигнал аварійної зупинки `SIGPIPE`.
3. **Обмеження часу життя (Max Lifetime та Idle Timeout):** тривале утримання одного й того самого з'єднання призводить до накопичення витоків пам'яті на стороні сервера та ігнорування оновлень DNS-записів (наприклад, при перемиканні резервного вузла бази даних). Пул зобов'язаний автоматично оновлювати застарілі сокети.
4. **Гарантія безпечного повернення (RAII-оренда):** сокет не повинен загубитися в разі виникнення помилки, передчасного повернення з функції або генерації винятку в прикладному коді.

## Механізм перевірки стану сокета без вичитування даних

Для перевірки стану сокета перед його видачею клієнту пул виконує неблокуюче підглядання через системний виклик `recv` із прапорцями `MSG_PEEK | MSG_DONTWAIT`:

:::tabs
```c
char probe;
ssize_t res = recv(fd, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
if (res == 0) {
    // Віддалений сервер надіслав FIN (сокет закритий)
} else if (res < 0) {
    if (errno == EAGAIN || errno == EWOULDBLOCK) {
        // Буфер прийому чистий, помилок немає — сокет повністю готовий до роботи
    } else {
        // Сокет пошкоджено (наприклад, отримано RST або зламано маршрут)
    }
} else {
    // У буфері є незчитані дані від попереднього запиту — сокет забруднений
}
```
```cpp
char probe;
ssize_t res = ::recv(fd, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
if (res == 0) {
    // Віддалений сервер надіслав FIN (сокет закритий)
} else if (res < 0) {
    if (errno == EAGAIN || errno == EWOULDBLOCK) {
        // Буфер прийому чистий, помилок немає — сокет повністю готовий до роботи
    } else {
        // Сокет пошкоджено (наприклад, отримано RST або зламано маршрут)
    }
} else {
    // У буфері є незчитані дані від попереднього запиту — сокет забруднений
}
```
:::

- Прапорець `MSG_PEEK` копіює дані з приймального буфера ядра без їхнього фактичного видалення з черги, не спотворюючи протокольний потік.
- Прапорець `MSG_DONTWAIT` змушує виклик негайно повернутися без блокування потоку, якщо буфер прийому порожній.

## Повна реалізація пулу з'єднань

Нижче наведено повноцінну реалізацію багатопотокового пулу з підтримкою LIFO-стека вільних з'єднань, обмеженням максимальної місткості, перевіркою таймаутів та безпечним дренажем при зупинці.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <pthread.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <fcntl.h>

typedef struct {
    int fd;
    time_t created_at;
    time_t last_used_at;
} PooledConnection;

typedef struct {
    char host[128];
    int port;
    int max_capacity;
    int max_idle_sec;
    int max_life_sec;

    PooledConnection **idle_stack;
    int idle_count;
    int active_count;

    pthread_mutex_t lock;
    pthread_cond_t cond;
    int is_shutdown;
} ConnectionPool;

static int connect_to_host(const char *host, int port) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    if (inet_pton(AF_INET, host, &addr.sin_addr) <= 0) {
        close(fd);
        return -1;
    }

    if (connect(fd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(fd);
        return -1;
    }
    return fd;
}

static int is_connection_alive(int fd) {
    char probe;
    ssize_t r = recv(fd, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
    if (r == 0) return 0; // Отримано FIN від сервера
    if (r < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) return 1; // Буфер чистий, з'єднання живе
        return 0; // Апаратна помилка або RST
    }
    return 0; // Неочікувані залишковий трафік
}

ConnectionPool* pool_create(const char *host, int port, int capacity, int max_idle, int max_life) {
    ConnectionPool *p = (ConnectionPool*)calloc(1, sizeof(ConnectionPool));
    if (!p) return NULL;

    strncpy(p->host, host, sizeof(p->host) - 1);
    p->port = port;
    p->max_capacity = capacity;
    p->max_idle_sec = max_idle;
    p->max_life_sec = max_life;

    p->idle_stack = (PooledConnection**)malloc(sizeof(PooledConnection*) * capacity);
    p->idle_count = 0;
    p->active_count = 0;
    p->is_shutdown = 0;

    pthread_mutex_init(&p->lock, NULL);
    pthread_cond_init(&p->cond, NULL);
    return p;
}

PooledConnection* pool_acquire(ConnectionPool *p, int timeout_sec) {
    pthread_mutex_lock(&p->lock);
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += timeout_sec;

    while (1) {
        if (p->is_shutdown) {
            pthread_mutex_unlock(&p->lock);
            return NULL;
        }

        // 1. Спроба взяти готове з'єднання з вершини стека (LIFO)
        time_t now = time(NULL);
        while (p->idle_count > 0) {
            PooledConnection *conn = p->idle_stack[--p->idle_count];
            
            // Перевірка перевищення лімітів часу
            int expired = ((now - conn->last_used_at) > p->max_idle_sec) ||
                          ((now - conn->created_at) > p->max_life_sec);

            if (!expired && is_connection_alive(conn->fd)) {
                p->active_count++;
                pthread_mutex_unlock(&p->lock);
                return conn;
            }

            // З'єднання застаріло або закрите сервером — знищуємо
            close(conn->fd);
            free(conn);
        }

        // 2. Якщо вільних немає, але ліміт ємності не вичерпано — створюємо новий сокет
        if (p->active_count < p->max_capacity) {
            p->active_count++;
            pthread_mutex_unlock(&p->lock);

            // Мережевий виклик connect виконується ПОЗА блокуванням м'ютекса
            int fd = connect_to_host(p->host, p->port);
            if (fd < 0) {
                pthread_mutex_lock(&p->lock);
                p->active_count--;
                pthread_cond_signal(&p->cond);
                pthread_mutex_unlock(&p->lock);
                return NULL;
            }

            PooledConnection *conn = (PooledConnection*)malloc(sizeof(PooledConnection));
            conn->fd = fd;
            conn->created_at = time(NULL);
            conn->last_used_at = conn->created_at;
            return conn;
        }

        // 3. Усі слоти зайняті — очікуємо звільнення іншим потоком
        int rc = pthread_cond_timedwait(&p->cond, &p->lock, &ts);
        if (rc == ETIMEDOUT) {
            pthread_mutex_unlock(&p->lock);
            return NULL;
        }
    }
}

void pool_release(ConnectionPool *p, PooledConnection *conn, int is_broken) {
    if (!conn) return;

    pthread_mutex_lock(&p->lock);
    p->active_count--;

    time_t now = time(NULL);
    int expired = ((now - conn->created_at) > p->max_life_sec);

    if (is_broken || expired || p->is_shutdown || !is_connection_alive(conn->fd)) {
        close(conn->fd);
        free(conn);
    } else {
        conn->last_used_at = now;
        p->idle_stack[p->idle_count++] = conn;
    }

    pthread_cond_signal(&p->cond);
    pthread_mutex_unlock(&p->lock);
}

void pool_destroy(ConnectionPool *p) {
    if (!p) return;

    pthread_mutex_lock(&p->lock);
    p->is_shutdown = 1;
    pthread_cond_broadcast(&p->cond);

    for (int i = 0; i < p->idle_count; ++i) {
        close(p->idle_stack[i]->fd);
        free(p->idle_stack[i]);
    }
    p->idle_count = 0;
    pthread_mutex_unlock(&p->lock);

    pthread_mutex_destroy(&p->lock);
    pthread_cond_destroy(&p->cond);
    free(p->idle_stack);
    free(p);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <memory>
#include <chrono>
#include <mutex>
#include <condition_variable>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

class ConnectionPool;

class SocketConnection {
public:
    explicit SocketConnection(int fd) 
        : fd_(fd), createdAt_(Clock::now()), lastUsedAt_(createdAt_) {}

    ~SocketConnection() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    SocketConnection(const SocketConnection&) = delete;
    SocketConnection& operator=(const SocketConnection&) = delete;

    int nativeHandle() const noexcept { return fd_; }

    bool isAlive() const noexcept {
        if (fd_ < 0) return false;
        char probe;
        ssize_t r = ::recv(fd_, &probe, 1, MSG_PEEK | MSG_DONTWAIT);
        if (r == 0) return false; // Сервер надіслав FIN
        if (r < 0) {
            return (errno == EAGAIN || errno == EWOULDBLOCK);
        }
        return false; // Залишковий трафік
    }

    void touch() noexcept { lastUsedAt_ = Clock::now(); }

    using Clock = std::chrono::steady_clock;
    Clock::time_point createdAt() const noexcept { return createdAt_; }
    Clock::time_point lastUsedAt() const noexcept { return lastUsedAt_; }

private:
    int fd_{-1};
    Clock::time_point createdAt_;
    Clock::time_point lastUsedAt_;
};

class ConnectionLease {
public:
    ConnectionLease(std::shared_ptr<ConnectionPool> pool, std::unique_ptr<SocketConnection> conn)
        : pool_(std::move(pool)), conn_(std::move(conn)) {}

    ~ConnectionLease();

    ConnectionLease(ConnectionLease&&) noexcept = default;
    ConnectionLease& operator=(ConnectionLease&&) noexcept = default;

    SocketConnection* operator->() noexcept { return conn_.get(); }
    SocketConnection& operator*() noexcept { return *conn_; }
    int fd() const noexcept { return conn_ ? conn_->nativeHandle() : -1; }

    void markBroken() noexcept { isBroken_ = true; }

private:
    std::shared_ptr<ConnectionPool> pool_;
    std::unique_ptr<SocketConnection> conn_;
    bool isBroken_{false};
};

class ConnectionPool : public std::enable_shared_from_this<ConnectionPool> {
public:
    struct Config {
        std::string host;
        int port{80};
        size_t maxCapacity{16};
        std::chrono::seconds maxIdleTime{30};
        std::chrono::seconds maxLifetime{300};
    };

    explicit ConnectionPool(Config config) : config_(std::move(config)) {}

    ~ConnectionPool() {
        shutdown();
    }

    std::unique_ptr<ConnectionLease> acquire(std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        auto deadline = std::chrono::steady_clock::now() + timeout;

        while (!isShutdown_) {
            auto now = std::chrono::steady_clock::now();

            // 1. Отримання валідного з'єднання з вершини LIFO-стека
            while (!idleStack_.empty()) {
                auto conn = std::move(idleStack_.back());
                idleStack_.pop_back();

                bool expired = ((now - conn->lastUsedAt()) > config_.maxIdleTime) ||
                               ((now - conn->createdAt()) > config_.maxLifetime);

                if (!expired && conn->isAlive()) {
                    ++activeCount_;
                    return std::make_unique<ConnectionLease>(shared_from_this(), std::move(conn));
                }
                // Застарілий або мертвий сокет знищується деструктором unique_ptr
            }

            // 2. Створення нового з'єднання, якщо ліміт активних не вичерпано
            if (activeCount_ < config_.maxCapacity) {
                ++activeCount_;
                lock.unlock(); // Звільняємо м'ютекс на час повільного мережевого виклику

                auto rawConn = openRawSocket();
                if (!rawConn) {
                    lock.lock();
                    --activeCount_;
                    cv_.notify_one();
                    return nullptr;
                }

                return std::make_unique<ConnectionLease>(shared_from_this(), std::move(rawConn));
            }

            // 3. Очікування на умовній змінній
            if (cv_.wait_until(lock, deadline) == std::cv_status::timeout) {
                return nullptr;
            }
        }
        return nullptr;
    }

    void release(std::unique_ptr<SocketConnection> conn, bool isBroken) {
        if (!conn) return;

        std::lock_guard<std::mutex> lock(mutex_);
        --activeCount_;

        auto now = std::chrono::steady_clock::now();
        bool expired = (now - conn->createdAt()) > config_.maxLifetime;

        if (!isBroken && !expired && !isShutdown_ && conn->isAlive()) {
            conn->touch();
            idleStack_.push_back(std::move(conn));
        }

        cv_.notify_one();
    }

    void shutdown() {
        std::lock_guard<std::mutex> lock(mutex_);
        isShutdown_ = true;
        idleStack_.clear();
        cv_.notify_all();
    }

private:
    std::unique_ptr<SocketConnection> openRawSocket() {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return nullptr;

        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(config_.port));
        if (::inet_pton(AF_INET, config_.host.c_str(), &addr.sin_addr) <= 0) {
            ::close(fd);
            return nullptr;
        }

        if (::connect(fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
            ::close(fd);
            return nullptr;
        }

        return std::make_unique<SocketConnection>(fd);
    }

    Config config_;
    std::vector<std::unique_ptr<SocketConnection>> idleStack_;
    size_t activeCount_{0};
    bool isShutdown_{false};
    std::mutex mutex_;
    std::condition_variable cv_;
};

inline ConnectionLease::~ConnectionLease() {
    if (pool_ && conn_) {
        pool_->release(std::move(conn_), isBroken_);
    }
}
```
:::

## Детальний розбір реалізації та пасток

### 1. Чому LIFO-стек переважає FIFO-чергу

У реалізації черги вільних з'єднань використано масив-стек (`idle_stack`), з якого сокети вибираються з кінця (`pop_back()`), а повертаються на вершину (`push_back()`).

У разі зміни навантаження на систему (наприклад, у нічний час частота запитів падає вдесятеро):
- Верхні один-два сокети безперервно беруться, використовуються та повертаються, залишаючись теплими.
- Решта сокетів на дні стека лишаються недоторканими. Вони перевищують ліміт `maxIdleTime` і автоматично закриваються при першій спробі вилучення з пулу або під час фонової перевірки.
- Якби використовувалася черга FIFO, кожен новий запит брав би найстаріший сокет, постійно підтримуючи всі сокети пулу в ледь живому стані й унеможливлюючи вивільнення зайвої пам'яті.

### 2. Двоетапне створення з'єднання без утримання блокування

Ключовим моментом методу `acquire` є виклик `lock.unlock()` перед викликом `connect_to_host()` / `openRawSocket()`.

Якщо мережа відчуває затримки або віддалений вузол тимчасово не відповідає, виклик `connect()` може заблокуватися на 1–2 секунди (або до 75 секунд за стандартного таймауту TCP SYN). Якби м'ютекс залишався заблокованим, жоден інший потік застосунку не зміг би:
- Повернути вже опрацьований робочий сокет назад у пул.
- Отримати вже готове вільне з'єднання зі стека.
- Перевірити статус завершення пулу під час виклику `shutdown()`.

Збільшення лічильника `active_count` перед розблокуванням резервує слот ємності, гарантуючи, що сумарна кількість сокетів не перевищить `max_capacity`.

### 3. Автоматичний захист від витоків через RAII

Клас `ConnectionLease` у версії на C++ реалізує ідіому «Захоплення ресурсу є ініціалізація» (англ. *Resource Acquisition Is Initialization*, RAII).

Якщо в процесі виконання прикладного коду станеться апаратний збій, функція достроково завершиться через `return` або буде згенеровано виняток `std::runtime_error`, деструктор `~ConnectionLease()` викликається гарантовано під час розгортання стека (англ. *stack unwinding*). Деструктор передає сокет назад у пул, виключаючи «зависання» лічильника активних з'єднань і гарантуючи пробудження потоків у черзі очікування.

### 4. Проблема громового стада та справедливість сповіщень

Під час звільнення з'єднання у функції `pool_release()` використовується виклик `pthread_cond_signal()` (`cv_.notify_one()`), а не `pthread_cond_broadcast()` (`cv_.notify_all()`).

Виклик `broadcast` розбудив би всі заблоковані потоки одночасно («громове стадо», англ. *Thundering Herd Problem*). Усі потоки кинулися б захоплювати м'ютекс, створюючи надмірну конкуренцію за лінії кешу процесора (cache-line bouncing), після чого рівно один потік забрав би вивільнений слот, а решта знову заснули б. Виклик `signal` будить рівно один потік, мінімізуючи накладні витрати ядра на планування.

Натомість під час аварійної або планової зупинки у функції `pool_destroy()` / `shutdown()` використання `broadcast` / `notify_all()` є обов'язковим, оскільки всі потоки, що чекають на черзі, повинні негайно отримати статус `is_shutdown = true` та розблокуватися без зависання.

### 5. Інструментальна верифікація та тестування на витоки

Надійність багатопотокового пулу з'єднань обов'язково верифікується під динамічними аналізаторами:
- **ThreadSanitizer (`-fsanitize=thread`):** виявляє стан гонитви при конкурентній зміні `active_count` та масиву `idle_stack`.
- **AddressSanitizer (`-fsanitize=address`) та Valgrind:** контролюють відсутність витоків пам'яті та дескрипторів сокетів після виклику `pool_destroy()`.

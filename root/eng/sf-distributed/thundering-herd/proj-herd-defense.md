# ⚙️ Інженерний захист від штормів перепідключення: клієнтський джитер та серверний сокет-шардинг

Практична реалізація захисту від гримучої отари вимагає симетричних інженерних заходів на обох кінцях з'єднання: клієнт повинен рандомізувати інтервали між спробами з'єднання за допомогою алгоритму Decorrelated Jitter, а сервер — шардувати черги слухання між ядрами процесора через `SO_REUSEPORT` та відсікати надлишкові сплески вхідним токенним лімітером.

## Анатомія клієнтського захисту: Decorrelated Jitter та керування станом

Клієнтський рівень є першою лінією оборони проти фазової синхронізації. Коли тисячі екземплярів мобільних додатків або мікросервісів втрачають зв'язок із бекендом, стандартний детермінований цикл повторів неминуче перетворює їх на когерентну отару.

Для усунення кореляції між клієнтами алгоритм Decorrelated Jitter розраховує тривалість паузи перед наступною спробою не від початкового моменту аварії чи фіксованого номера кроку, а від фактично витриманого попереднього інтервалу сну `prev_backoff`. Наступне значення обирається рівномірно з випадкового відрізка:

```
sleep_time = uniform(base_interval, prev_backoff · 3)
```

Такий підхід забезпечує три критичні властивості:
1. **Швидке розсіювання фази:** Навіть якщо група клієнтів одночасно отримала однаковий початковий інтервал `base`, на наступній ітерації їхні інтервали очікування рівномірно розподіляться у трикратно розширеному діапазоні `[base, 3 · base]`.
2. **Плавне експоненційне зростання:** Середнє значення затримки на кожному кроці збільшується в `1.5` раза, що гарантує спадання сумарного навантаження на відновлюваний сервер.
3. **Захист від переповнення та стеля:** Затримка обмежується константою `max_backoff`, щоб запобігти безкінечному засинанню клієнтів при тривалих аваріях.

### Інженерні тонкощі вибору джерела часу та ентропії
Під час реалізації клієнтських таймерів критично важливо використовувати монотонні таймери ядра (`CLOCK_MONOTONIC` у C або `std::chrono::steady_clock` у C++). Використання системного астрономічного годинника (`CLOCK_REALTIME` або `std::chrono::system_clock`) є грубою помилкою: якщо демон синхронізації часу NTP здійснить ступінчасте коригування годинника назад під час аварії, клієнтські потоки можуть заснути на години або, навпаки, прокинутися миттєво всі разом, створивши штучну гримучу отару.

Також важливо забезпечити незалежну ініціалізацію генератора псевдовипадкових чисел для кожного процесу або потоку (комбінація PID процесу, адреси потоку та монотонного часу), щоб клоновані через `fork()` процеси не генерували однакові послідовності затримок.

Нижче наведено паралельні реалізації клієнтського менеджера з'єднань мовами C (стандарт C11) та C++ (сучасний стандарт C++20 з використанням RAII, концептів та типу `std::expected`):

:::tabs
```c
/* C11 implementation: client connection loop with decorrelated jitter */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

typedef struct {
    double base_sec;
    double max_sec;
    double prev_backoff_sec;
    unsigned int seed;
} JitterBackoff;

void jitter_init(JitterBackoff *jb, double base_sec, double max_sec) {
    jb->base_sec = base_sec;
    jb->max_sec = max_sec;
    jb->prev_backoff_sec = base_sec;
    jb->seed = (unsigned int)(time(NULL) ^ getpid());
}

double jitter_next(JitterBackoff *jb) {
    double low = jb->base_sec;
    double high = jb->prev_backoff_sec * 3.0;
    if (high < low) {
        high = low;
    }
    
    /* Uniform random in [low, high] */
    double r = (double)rand_r(&jb->seed) / (double)RAND_MAX;
    double sleep_time = low + r * (high - low);
    
    if (sleep_time > jb->max_sec) {
        sleep_time = jb->max_sec;
    }
    
    jb->prev_backoff_sec = sleep_time;
    return sleep_time;
}

int connect_with_herd_protection(const char *ip, int port, int max_attempts) {
    JitterBackoff backoff;
    jitter_init(&backoff, 0.5, 30.0); /* base 500ms, max 30s */
    
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    if (inet_pton(AF_INET, ip, &server_addr.sin_addr) <= 0) {
        return -1;
    }

    for (int attempt = 1; attempt <= max_attempts; ++attempt) {
        int sock_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (sock_fd < 0) {
            return -1;
        }

        if (connect(sock_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) == 0) {
            printf("[Client] Connected on attempt %d\n", attempt);
            return sock_fd;
        }

        close(sock_fd);
        double delay = jitter_next(&backoff);
        printf("[Client] Attempt %d failed. Jittered sleep: %.3f s\n", attempt, delay);
        
        struct timespec ts;
        ts.tv_sec = (time_t)delay;
        ts.tv_nsec = (long)((delay - (time_t)delay) * 1e9);
        nanosleep(&ts, NULL);
    }

    return -1; /* Exceeded max attempts */
}
```
```cpp
// C++20 implementation: modern RAII connection manager with Decorrelated Jitter
#include <iostream>
#include <chrono>
#include <random>
#include <thread>
#include <expected>
#include <system_error>
#include <string_view>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>

class SocketHandle {
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() { reset(); }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

private:
    int fd_{-1};
};

class DecorrelatedJitterBackoff {
public:
    DecorrelatedJitterBackoff(std::chrono::milliseconds base,
                              std::chrono::milliseconds max)
        : base_(base), max_(max), prev_(base),
          rng_(std::random_device{}()) {}

    std::chrono::milliseconds next() {
        const auto low = base_.count();
        const auto high = std::max(low, prev_.count() * 3);
        
        std::uniform_int_distribution<long long> dist(low, high);
        const auto sleep_ms = std::min(max_.count(), dist(rng_));
        
        prev_ = std::chrono::milliseconds(sleep_ms);
        return prev_;
    }

private:
    std::chrono::milliseconds base_;
    std::chrono::milliseconds max_;
    std::chrono::milliseconds prev_;
    std::mt19937_64 rng_;
};

class ResilientClient {
public:
    ResilientClient(std::string_view host, int port)
        : host_(host), port_(port),
          backoff_(std::chrono::milliseconds(500), std::chrono::seconds(30)) {}

    std::expected<SocketHandle, std::error_code> connect(int max_attempts) {
        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port_);
        if (::inet_pton(AF_INET, host_.data(), &addr.sin_addr) <= 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        for (int attempt = 1; attempt <= max_attempts; ++attempt) {
            SocketHandle sock(::socket(AF_INET, SOCK_STREAM, 0));
            if (!sock.valid()) {
                return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
            }

            if (::connect(sock.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) == 0) {
                std::cout << "[Client C++] Connected successfully on attempt " << attempt << "\n";
                return sock;
            }

            const auto delay = backoff_.next();
            std::cout << "[Client C++] Attempt " << attempt << " failed. Sleeping "
                      << delay.count() << " ms\n";
            std::this_thread::sleep_for(delay);
        }

        return std::unexpected(std::make_error_code(std::errc::timed_out));
    }

private:
    std::string_view host_;
    int port_;
    DecorrelatedJitterBackoff backoff_;
};
```
:::

## Серверний сокет-шардинг: SO_REUSEPORT, EPOLLEXCLUSIVE та Token Bucket

На серверному боці шлюзу головна інженерна проблема полягає в тому, як розподілити вхідний потік з'єднань між десятками ядер процесора без виникнення точок синхронізації та блокувань.

### Механізм SO_REUSEPORT у ядрі Linux
Класична архітектура з одним слухаючим сокетом змушує всі робочі потоки конкурувати за один файловий дескриптор. Коли приходить пакет TCP SYN, ядро Linux змушене блокувати чергу `accept_queue` сокета, що під високим навантаженням викликає шторм блокувань у спін-локах ядра (`slock-spinning`).

Опція `SO_REUSEPORT` докорінно змінює цю схему:
1. Кожен робочий потік або процес створює власний незалежний слухаючий сокет і прив'язує його до одного й того самого порту.
2. Ядро створює масив слухаючих сокетів `sock*` для даного порту.
3. Коли надходить вхідний пакет TCP SYN, мережевий стек ядра обчислює хеш-функцію від 4-кортежу заголовків IP/TCP (`hash(src_ip, src_port, dst_ip, dst_port)`) і спрямовує з'єднання в індивідуальну чергу строго одного конкретного сокета.
4. Конкуренція між потоками за чергу повністю ліквідується.
5. Для складних сценаріїв балансування (наприклад, з урахуванням локальності пам'яті NUMA-вузлів або завантаженості потоків) ядро підтримує завантаження користувацьких програм eBPF через опцію `SO_ATTACH_REUSEPORT_EBPF`, що дозволяє спрямовувати пакети на найменш завантажені ядра процесора.

### Робота з epoll у режимі EPOLLEXCLUSIVE
Для запобігання ситуації, коли кілька потоків очікують подій у спільних дескрипторах `epoll`, прапорець `EPOLLEXCLUSIVE` гарантує семантику «пробудити строго одного» (англ. *wake-one*). Оскільки сокет налаштовано в неблокуючому крайовому режимі (`EPOLLET`), воркер зобов'язаний вичитувати з'єднання у неперервному циклі `while(true)` через виклик `accept4()` до моменту повернення помилки `EAGAIN` або `EWOULDBLOCK`.

### Вхідне обмеження: Lock-Free Token Bucket
Якщо кількість вхідних запитів перевищує розрахункову місткість ядра, серверний воркер повинен миттєво скидати зайві підключення без виділення пам'яті під стан сесії чи виконання криптографії TLS. Для цього використовується атомарний токенний бакет на базі неблокуючих операцій `compare_exchange_weak`.

Нижче наведено паралельні реалізації багатопотокового сервера мовами C (C11 з POSIX Threads) та C++ (C++20 з використанням `std::atomic` та `std::stop_token`):

:::tabs
```c
/* C11 server worker with SO_REUSEPORT and Token Bucket rate limiter */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <time.h>
#include <pthread.h>

#define MAX_EVENTS 64
#define PORT 8080

typedef struct {
    double capacity;
    double tokens;
    double refill_rate;
    struct timespec last_refill;
    pthread_mutex_t lock;
} TokenBucket;

void tb_init(TokenBucket *tb, double capacity, double rate) {
    tb->capacity = capacity;
    tb->tokens = capacity;
    tb->refill_rate = rate;
    clock_gettime(CLOCK_MONOTONIC, &tb->last_refill);
    pthread_mutex_init(&tb->lock, NULL);
}

bool tb_consume(TokenBucket *tb) {
    pthread_mutex_lock(&tb->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - tb->last_refill.tv_sec) +
                     (now.tv_nsec - tb->last_refill.tv_nsec) / 1e9;
    tb->last_refill = now;

    tb->tokens += elapsed * tb->refill_rate;
    if (tb->tokens > tb->capacity) {
        tb->tokens = tb->capacity;
    }

    bool allowed = false;
    if (tb->tokens >= 1.0) {
        tb->tokens -= 1.0;
        allowed = true;
    }
    pthread_mutex_unlock(&tb->lock);
    return allowed;
}

int create_reuseport_listener(int port) {
    int listen_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
    if (listen_fd < 0) return -1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(port);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        close(listen_fd);
        return -1;
    }

    if (listen(listen_fd, 4096) < 0) {
        close(listen_fd);
        return -1;
    }

    return listen_fd;
}
```
```cpp
// C++20 server worker using SO_REUSEPORT, EPOLLEXCLUSIVE and atomic Token Bucket
#include <iostream>
#include <atomic>
#include <chrono>
#include <thread>
#include <vector>
#include <cstring>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>

class AtomicTokenBucket {
public:
    AtomicTokenBucket(double capacity, double refill_rate)
        : capacity_(capacity), refill_rate_(refill_rate),
          tokens_(capacity),
          last_update_(std::chrono::steady_clock::now().time_since_epoch().count()) {}

    bool try_consume() {
        const auto now = std::chrono::steady_clock::now().time_since_epoch().count();
        auto last = last_update_.load(std::memory_order_relaxed);

        while (true) {
            const double elapsed = static_cast<double>(now - last) / 1e9;
            double current = tokens_.load(std::memory_order_relaxed);
            double updated = std::min(capacity_, current + elapsed * refill_rate_);

            if (updated < 1.0) {
                return false; // Admission rejected: rate limit exceeded
            }

            if (tokens_.compare_exchange_weak(current, updated - 1.0,
                                             std::memory_order_release,
                                             std::memory_order_relaxed)) {
                last_update_.store(now, std::memory_order_relaxed);
                return true;
            }
        }
    }

private:
    const double capacity_;
    const double refill_rate_;
    std::atomic<double> tokens_;
    std::atomic<long long> last_update_;
};

class ReusePortServerWorker {
public:
    ReusePortServerWorker(int id, int port, AtomicTokenBucket& limiter)
        : worker_id_(id), port_(port), limiter_(limiter) {}

    void run(std::stop_token stop_tok) {
        int listen_fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
        if (listen_fd < 0) return;

        int opt = 1;
        ::setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        ::setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));

        struct sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);

        if (::bind(listen_fd, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0 ||
            ::listen(listen_fd, 4096) < 0) {
            ::close(listen_fd);
            return;
        }

        int epoll_fd = ::epoll_create1(0);
        struct epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET | EPOLLEXCLUSIVE;
        ev.data.fd = listen_fd;
        ::epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

        struct epoll_event events[64];
        while (!stop_tok.stop_requested()) {
            int nfds = ::epoll_wait(epoll_fd, events, 64, 200);
            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == listen_fd) {
                    while (true) {
                        struct sockaddr_in client_addr{};
                        socklen_t client_len = sizeof(client_addr);
                        int client_fd = ::accept4(listen_fd,
                                                  reinterpret_cast<struct sockaddr*>(&client_addr),
                                                  &client_len, SOCK_NONBLOCK);
                        if (client_fd < 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                            break;
                        }

                        if (!limiter_.try_consume()) {
                            // Швидке скидання з'єднання при перевантаженні (Herd Protection)
                            ::close(client_fd);
                            continue;
                        }

                        // Обробка дозволеного з'єднання
                        ::close(client_fd);
                    }
                }
            }
        }

        ::close(epoll_fd);
        ::close(listen_fd);
    }

private:
    int worker_id_;
    int port_;
    AtomicTokenBucket& limiter_;
};
```
:::

## Тестування та перевірка стійкості під навантаженням

Для перевірки ефективності розроблених рішень застосовують стенди синтетичного навантаження, які моделюють миттєвий шторм перепідключень. 

Утиліта генерації навантаження (наприклад, `vegeta` або спеціалізований скрипт на базі `k6`/`locust`) запускає 50 000 паралельних віртуальних користувачів, які в одну мілісекунду ініціюють TCP-з'єднання.

Під час тестування відстежують три ключові системні метрики:
- **Частота перемикання контекстів ядра (`cs/s` утиліти `vmstat 1`):** При правильному шардингу через `SO_REUSEPORT` та `EPOLLEXCLUSIVE` кількість перемикань контексту залишається пропорційною кількості активних ядер і не перевищує 50 000 на секунду, тоді як у наївній схемі стрибає вище 1 500 000 на секунду.
- **Скидання пакетів у сокетних чергах:** Відсутність зростання значень `TCPExtListenOverflows` та `TCPExtListenDrops` у виводі `netstat -s`.
- **Корисна пропускна здатність (Goodput):** Частка успішно оброблених з'єднань залишається на рівні 100% від встановленого ліміту токенного бакета без сплесків затримки по 99-му перцентилю.

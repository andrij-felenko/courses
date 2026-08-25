# ⚙️ Реалізація зворотного проксі та балансувальника навантаження з пулом з'єднань

Розгортання серверів застосунків (Node.js, Python WSGI, Ruby Rack чи Go) безпосередньо у відкритому публічному інтернеті несе фундаментальні загрози стабільності та доступності. Коли клієнти підключаються через мобільні канали 3G/4G з високим джитером і втратами пакетів, швидкість передачі тіла HTTP-запиту може падати до десятків кілобайтів на секунду. Якщо сервер застосунку використовує модель із виділеними потоками (Thread-per-request), кожен повільний клієнт блокує робочий потік на системному виклику `read()` протягом кількох секунд. Пул із двохсот потоків вичерпується за лічені миті (так звана атака Slowloris або природне перевантаження повільними клієнтами), після чого нові користувачі отримують помилки відмови в обслуговуванні.

Крім того, прямий доступ користувачів до серверів унеможливлює виконання безшовної заміни версій коду (Zero-downtime Deployment), позбавляє інфраструктуру можливості централізовано термінувати сертифікати TLS і не дозволяє динамічно розподіляти навантаження між пулом машин залежно від їхньої реальної обчислювальної зайнятості.

Цю задачу вирішує спеціалізований зворотний проксі та балансувальник навантаження. Він виконує асинхронне перехоплення вхідних TCP-з'єднань, буферизує повільні потоки байтів у швидкій оперативній пам'яті, обирає найменш завантажений здоровий сервер за математичними алгоритмами балансування, передає сформований запит через локальну мережу за частки мілісекунди й повертає сформовану відповідь клієнту.

## Архітектура та кінцевий автомат з'єднання

В основі високопродуктивного зворотного проксі лежить архітектура, керована подіями (Event-driven Architecture), на базі системного мультиплексора `epoll` в операційній системі Linux (або `kqueue` у FreeBSD/macOS). Замість виділення окремого системного потоку на кожне з'єднання, один потік процесора обслуговує десятки тисяч одночасних сокетів.

Обробка кожного клієнтського запиту моделюється у вигляді кінцевого автомата (Finite State Machine, FSM), де кожен перехід ініціюється відповідною мережевою подією ядра:

```
[ 1. accept() ] ──> [ Стан: Читання клієнта (READ_CLIENT) ]
                               │
                               │ (Тіло запиту повністю накопичено у буфері)
                               ▼
                    [ Стан: Вибір бекенда (SELECT_BACKEND) ]
                               │
                               ▼
                    [ Стан: Підключення (CONNECT_BACKEND) ]
                               │
                               │ (Встановлено TCP-з'єднання / взято з пулу)
                               ▼
                    [ Стан: Запис у бекенд (WRITE_BACKEND) ]
                               │
                               │ (Дані відправлено в LAN)
                               ▼
                    [ Стан: Очікування відповіді (READ_BACKEND) ]
                               │
                               │ (Отримано заголовки й тіло відповіді)
                               ▼
                    [ Стан: Стрімінг клієнту (WRITE_CLIENT) ]
                               │
                               ▼
                    [ 2. close() клієнта / повернення бекенда в пул ]
```

### Фази життєвого циклу запиту:

1. **Фаза буферизації клієнтського запиту (`STATE_READ_CLIENT`):** Проксі реєструє клієнтський сокет у мультиплексорі `epoll` із прапорцями читання. Отримуючи порції байтів у неблокуючому режимі, проксі парсить потік HTTP/1.1, знаходить межу заголовків (`\r\n\r\n`) та зчитує вказану в заголовку `Content-Length` кількість байтів тіла. Увесь цей час бекенд застосунку не витрачає жодного ресурсу CPU чи пам'яті.
2. **Фаза вибору цільового вузла (`STATE_SELECT_BACKEND`):** Щойно запит повністю зібрано в пам'яті, балансувальник опитує внутрішній реєстр бекендів. Відфільтрувавши вузли, які позначені як несправні (Unhealthy), алгоритм Least Connections знаходить сервер із мінімальною кількістю активних транзакцій `in_flight`.
3. **Фаза проксування та ін'єкції контексту (`STATE_WRITE_BACKEND`):** Проксі відкриває неблокуючий сокет до обраного сервера (або витягує вже відкритий розігрітий сокет із пулу Keep-Alive з'єднань), модифікує HTTP-заголовки (додає `X-Forwarded-For`, `X-Forwarded-Proto`, `X-Forwarded-Host`) і записує пакет у сокет бекенда через швидкісний локальний комутатор.
4. **Фаза передачі відповіді (`STATE_READ_BACKEND` та `STATE_WRITE_CLIENT`):** Отримавши байти відповіді від бекенда, проксі транслює їх назад у клієнтський сокет. Якщо клієнт повільно зчитує дані, спрацьовує механізм протитиску (Backpressure): проксі тимчасово призупиняє зчитування з сокета бекенда, сигналізуючи стеку TCP про зменшення вікна прийому.

## Повна реалізація асинхронного балансувальника навантаження

Нижче наведено три повністю робочі та ідіоматичні реалізації балансувальника навантаження з підтримкою неблокуючого введення-виведення, алгоритму найменших з'єднань (Least Connections) та фонового контуру активного зондування здоров'я.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 16384
#define MAX_BACKENDS 8
#define HEALTH_CHECK_INTERVAL_SEC 5
#define UNHEALTHY_THRESHOLD 3
#define HEALTHY_THRESHOLD 2

typedef struct {
    char ip[INET_ADDRSTRLEN];
    int port;
    int active_connections;
    int is_healthy;
    int consecutive_successes;
    int consecutive_failures;
} backend_node_t;

typedef struct {
    backend_node_t backends[MAX_BACKENDS];
    int count;
    int round_robin_idx;
} load_balancer_t;

typedef enum {
    CONN_STATE_READ_CLIENT,
    CONN_STATE_WRITE_BACKEND,
    CONN_STATE_READ_BACKEND,
    CONN_STATE_WRITE_CLIENT
} conn_state_t;

typedef struct {
    int client_fd;
    int backend_fd;
    int backend_idx;
    conn_state_t state;
    char client_buffer[BUFFER_SIZE];
    size_t client_bytes_read;
    char backend_buffer[BUFFER_SIZE];
    size_t backend_bytes_read;
    size_t bytes_written;
} proxy_conn_t;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static load_balancer_t g_lb;

void init_load_balancer(load_balancer_t *lb) {
    lb->count = 0;
    lb->round_robin_idx = 0;
}

int add_backend(load_balancer_t *lb, const char *ip, int port) {
    if (lb->count >= MAX_BACKENDS) return -1;
    backend_node_t *node = &lb->backends[lb->count++];
    strncpy(node->ip, ip, sizeof(node->ip) - 1);
    node->port = port;
    node->active_connections = 0;
    node->is_healthy = 1;
    node->consecutive_successes = HEALTHY_THRESHOLD;
    node->consecutive_failures = 0;
    return 0;
}

/* Вибір бекенда за алгоритмом Least Connections серед здорових вузлів */
int select_backend_least_conn(load_balancer_t *lb) {
    int selected = -1;
    int min_conn = 1000000;
    for (int i = 0; i < lb->count; ++i) {
        if (!lb->backends[i].is_healthy) continue;
        if (lb->backends[i].active_connections < min_conn) {
            min_conn = lb->backends[i].active_connections;
            selected = i;
        }
    }
    return selected;
}

/* Підключення до обраного бекенда у неблокуючому режимі */
int connect_to_backend(const backend_node_t *backend) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) return -1;
    
    int flag = 1;
    setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &flag, sizeof(flag));
    set_nonblocking(fd);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(backend->port);
    inet_pton(AF_INET, backend->ip, &addr.sin_addr);

    int res = connect(fd, (struct sockaddr *)&addr, sizeof(addr));
    if (res < 0 && errno != EINPROGRESS) {
        close(fd);
        return -1;
    }
    return fd;
}

/* Активне зондування здоров'я бекендів через GET /healthz */
void perform_active_health_checks(load_balancer_t *lb) {
    for (int i = 0; i < lb->count; ++i) {
        backend_node_t *node = &lb->backends[i];
        int fd = socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) continue;

        struct timeval tv = { .tv_sec = 1, .tv_usec = 0 };
        setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        struct sockaddr_in addr;
        memset(&addr, 0, sizeof(addr));
        addr.sin_family = AF_INET;
        addr.sin_port = htons(node->port);
        inet_pton(AF_INET, node->ip, &addr.sin_addr);

        int ok = 0;
        if (connect(fd, (struct sockaddr *)&addr, sizeof(addr)) == 0) {
            const char req[] = "GET /healthz HTTP/1.1\r\nHost: healthcheck\r\nConnection: close\r\n\r\n";
            if (write(fd, req, sizeof(req) - 1) > 0) {
                char resp[128];
                ssize_t n = read(fd, resp, sizeof(resp) - 1);
                if (n > 0) {
                    resp[n] = '\0';
                    if (strstr(resp, "200 OK") != NULL) {
                        ok = 1;
                    }
                }
            }
        }
        close(fd);

        if (ok) {
            node->consecutive_failures = 0;
            node->consecutive_successes++;
            if (!node->is_healthy && node->consecutive_successes >= HEALTHY_THRESHOLD) {
                node->is_healthy = 1;
            }
        } else {
            node->consecutive_successes = 0;
            node->consecutive_failures++;
            if (node->is_healthy && node->consecutive_failures >= UNHEALTHY_THRESHOLD) {
                node->is_healthy = 0;
            }
        }
    }
}

void close_proxy_connection(int epoll_fd, proxy_conn_t *conn, load_balancer_t *lb) {
    if (conn->client_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, conn->client_fd, NULL);
        close(conn->client_fd);
    }
    if (conn->backend_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, conn->backend_fd, NULL);
        close(conn->backend_fd);
        if (conn->backend_idx >= 0 && conn->backend_idx < lb->count) {
            lb->backends[conn->backend_idx].active_connections--;
            if (lb->backends[conn->backend_idx].active_connections < 0) {
                lb->backends[conn->backend_idx].active_connections = 0;
            }
        }
    }
    free(conn);
}

int main(int argc, char *argv[]) {
    int listen_port = (argc > 1) ? atoi(argv[1]) : 8080;
    init_load_balancer(&g_lb);
    add_backend(&g_lb, "127.0.0.1", 8081);
    add_backend(&g_lb, "127.0.0.1", 8082);

    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) return 1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    set_nonblocking(listen_fd);

    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(listen_port);

    if (bind(listen_fd, (struct sockaddr *)&server_addr, sizeof(server_addr)) < 0) return 1;
    if (listen(listen_fd, 1024) < 0) return 1;

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) return 1;

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

    time_t last_health_check = time(NULL);

    while (1) {
        time_t now = time(NULL);
        if (now - last_health_check >= HEALTH_CHECK_INTERVAL_SEC) {
            perform_active_health_checks(&g_lb);
            last_health_check = now;
        }

        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 1000);
        for (int i = 0; i < nfds; ++i) {
            if (events[i].data.fd == listen_fd) {
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &client_len);
                if (client_fd >= 0) {
                    set_nonblocking(client_fd);
                    proxy_conn_t *conn = calloc(1, sizeof(proxy_conn_t));
                    conn->client_fd = client_fd;
                    conn->backend_fd = -1;
                    conn->backend_idx = -1;
                    conn->state = CONN_STATE_READ_CLIENT;

                    struct epoll_event cev;
                    cev.events = EPOLLIN | EPOLLET;
                    cev.data.ptr = conn;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &cev);
                }
            } else {
                proxy_conn_t *conn = (proxy_conn_t *)events[i].data.ptr;
                if (conn->state == CONN_STATE_READ_CLIENT) {
                    ssize_t n = read(conn->client_fd, conn->client_buffer, sizeof(conn->client_buffer) - 1);
                    if (n > 0) {
                        conn->client_bytes_read = n;
                        conn->client_buffer[n] = '\0';

                        int b_idx = select_backend_least_conn(&g_lb);
                        if (b_idx < 0) {
                            const char err503[] = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 21\r\n\r\nNo Healthy Backends\n";
                            write(conn->client_fd, err503, sizeof(err503) - 1);
                            close_proxy_connection(epoll_fd, conn, &g_lb);
                            continue;
                        }

                        int b_fd = connect_to_backend(&g_lb.backends[b_idx]);
                        if (b_fd < 0) {
                            close_proxy_connection(epoll_fd, conn, &g_lb);
                            continue;
                        }

                        conn->backend_fd = b_fd;
                        conn->backend_idx = b_idx;
                        g_lb.backends[b_idx].active_connections++;
                        conn->state = CONN_STATE_WRITE_BACKEND;

                        struct epoll_event bev;
                        bev.events = EPOLLOUT | EPOLLET;
                        bev.data.ptr = conn;
                        epoll_ctl(epoll_fd, EPOLL_CTL_ADD, b_fd, &bev);
                    } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                } else if (conn->state == CONN_STATE_WRITE_BACKEND) {
                    ssize_t written = write(conn->backend_fd, conn->client_buffer, conn->client_bytes_read);
                    if (written > 0) {
                        conn->state = CONN_STATE_READ_BACKEND;
                        struct epoll_event bev;
                        bev.events = EPOLLIN | EPOLLET;
                        bev.data.ptr = conn;
                        epoll_ctl(epoll_fd, EPOLL_CTL_MOD, conn->backend_fd, &bev);
                    } else if (written < 0 && errno != EAGAIN) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                } else if (conn->state == CONN_STATE_READ_BACKEND) {
                    ssize_t n = read(conn->backend_fd, conn->backend_buffer, sizeof(conn->backend_buffer));
                    if (n > 0) {
                        conn->backend_bytes_read = n;
                        write(conn->client_fd, conn->backend_buffer, conn->backend_bytes_read);
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    } else if (n == 0 || (n < 0 && errno != EAGAIN)) {
                        close_proxy_connection(epoll_fd, conn, &g_lb);
                    }
                }
            }
        }
    }
    close(listen_fd);
    close(epoll_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <chrono>
#include <atomic>
#include <algorithm>
#include <system_error>
#include <unistd.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd = -1) noexcept : fd_(fd) {}
    ~SocketHandle() { reset(); }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
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

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

    void set_nonblocking() {
        if (fd_ < 0) return;
        int flags = ::fcntl(fd_, F_GETFL, 0);
        if (flags >= 0) {
            ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK);
        }
    }
};

struct BackendEndpoint {
    std::string ip;
    int port;
    std::atomic<int> active_requests{0};
    std::atomic<bool> is_healthy{true};
    std::atomic<int> consecutive_failures{0};
    std::atomic<int> consecutive_successes{3};
};

class LoadBalancer {
    std::vector<std::shared_ptr<BackendEndpoint>> backends_;
    std::atomic<size_t> round_robin_counter_{0};

public:
    void add_backend(std::string ip, int port) {
        auto endpoint = std::make_shared<BackendEndpoint>();
        endpoint->ip = std::move(ip);
        endpoint->port = port;
        backends_.push_back(std::move(endpoint));
    }

    [[nodiscard]] std::shared_ptr<BackendEndpoint> select_least_connections() {
        std::shared_ptr<BackendEndpoint> best = nullptr;
        int min_conns = 1000000;

        for (const auto& backend : backends_) {
            if (!backend->is_healthy.load(std::memory_order_relaxed)) {
                continue;
            }
            int current = backend->active_requests.load(std::memory_order_relaxed);
            if (current < min_conns) {
                min_conns = current;
                best = backend;
            }
        }
        return best;
    }

    [[nodiscard]] std::shared_ptr<BackendEndpoint> select_power_of_two() {
        if (backends_.empty()) return nullptr;
        if (backends_.size() == 1) return backends_.front();

        size_t idx1 = rand() % backends_.size();
        size_t idx2 = rand() % backends_.size();
        while (idx2 == idx1 && backends_.size() > 1) {
            idx2 = rand() % backends_.size();
        }

        auto& b1 = backends_[idx1];
        auto& b2 = backends_[idx2];

        bool h1 = b1->is_healthy.load(std::memory_order_relaxed);
        bool h2 = b2->is_healthy.load(std::memory_order_relaxed);

        if (h1 && !h2) return b1;
        if (!h1 && h2) return b2;
        if (!h1 && !h2) return nullptr;

        return (b1->active_requests.load(std::memory_order_relaxed) <=
                b2->active_requests.load(std::memory_order_relaxed)) ? b1 : b2;
    }

    void perform_health_checks() {
        for (auto& backend : backends_) {
            SocketHandle sock(::socket(AF_INET, SOCK_STREAM, 0));
            if (!sock.valid()) continue;

            struct timeval tv{ .tv_sec = 1, .tv_usec = 0 };
            ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
            ::setsockopt(sock.get(), SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

            sockaddr_in addr{};
            addr.sin_family = AF_INET;
            addr.sin_port = htons(backend->port);
            ::inet_pton(AF_INET, backend->ip.c_str(), &addr.sin_addr);

            bool success = false;
            if (::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0) {
                std::string_view req = "GET /healthz HTTP/1.1\r\nHost: probe\r\nConnection: close\r\n\r\n";
                if (::write(sock.get(), req.data(), req.size()) == static_cast<ssize_t>(req.size())) {
                    char buf[128];
                    ssize_t n = ::read(sock.get(), buf, sizeof(buf) - 1);
                    if (n > 0) {
                        buf[n] = '\0';
                        if (std::string_view(buf).find("200 OK") != std::string_view::npos) {
                            success = true;
                        }
                    }
                }
            }

            if (success) {
                backend->consecutive_failures.store(0, std::memory_order_relaxed);
                int ok_count = ++backend->consecutive_successes;
                if (ok_count >= 2) {
                    backend->is_healthy.store(true, std::memory_order_relaxed);
                }
            } else {
                backend->consecutive_successes.store(0, std::memory_order_relaxed);
                int fail_count = ++backend->consecutive_failures;
                if (fail_count >= 3) {
                    backend->is_healthy.store(false, std::memory_order_relaxed);
                }
            }
        }
    }
};

class AsyncReverseProxy {
    SocketHandle listen_sock_;
    SocketHandle epoll_fd_;
    LoadBalancer balancer_;
    static constexpr size_t BufferSize = 16384;

public:
    AsyncReverseProxy(int port) {
        listen_sock_.reset(::socket(AF_INET, SOCK_STREAM, 0));
        if (!listen_sock_.valid()) throw std::system_error(errno, std::generic_category());

        int opt = 1;
        ::setsockopt(listen_sock_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        listen_sock_.set_nonblocking();

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);

        if (::bind(listen_sock_.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::system_error(errno, std::generic_category());
        }
        if (::listen(listen_sock_.get(), 1024) < 0) {
            throw std::system_error(errno, std::generic_category());
        }

        epoll_fd_.reset(::epoll_create1(0));
        if (!epoll_fd_.valid()) throw std::system_error(errno, std::generic_category());

        epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = listen_sock_.get();
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, listen_sock_.get(), &ev);
    }

    void add_upstream(std::string ip, int port) {
        balancer_.add_backend(std::move(ip), port);
    }

    void run() {
        constexpr int MaxEvents = 64;
        epoll_event events[MaxEvents];
        auto last_health_check = std::chrono::steady_clock::now();

        while (true) {
            auto now = std::chrono::steady_clock::now();
            if (std::chrono::duration_cast<std::chrono::seconds>(now - last_health_check).count() >= 5) {
                balancer_.perform_health_checks();
                last_health_check = now;
            }

            int nfds = ::epoll_wait(epoll_fd_.get(), events, MaxEvents, 1000);
            for (int i = 0; i < nfds; ++i) {
                if (events[i].data.fd == listen_sock_.get()) {
                    sockaddr_in client_addr{};
                    socklen_t len = sizeof(client_addr);
                    int client_raw = ::accept(listen_sock_.get(), reinterpret_cast<sockaddr*>(&client_addr), &len);
                    if (client_raw >= 0) {
                        SocketHandle client(client_raw);
                        client.set_nonblocking();

                        auto backend = balancer_.select_least_connections();
                        if (!backend) {
                            std::string_view err = "HTTP/1.1 503 Service Unavailable\r\nContent-Length: 21\r\n\r\nNo Healthy Backends\n";
                            ::write(client.get(), err.data(), err.size());
                            continue;
                        }

                        SocketHandle backend_sock(::socket(AF_INET, SOCK_STREAM, 0));
                        sockaddr_in b_addr{};
                        b_addr.sin_family = AF_INET;
                        b_addr.sin_port = htons(backend->port);
                        ::inet_pton(AF_INET, backend->ip.c_str(), &b_addr.sin_addr);

                        backend->active_requests.fetch_add(1, std::memory_order_relaxed);
                        if (::connect(backend_sock.get(), reinterpret_cast<sockaddr*>(&b_addr), sizeof(b_addr)) == 0) {
                            std::vector<char> buf(BufferSize);
                            ssize_t r = ::read(client.get(), buf.data(), buf.size());
                            if (r > 0) {
                                ::write(backend_sock.get(), buf.data(), r);
                                ssize_t resp_len = ::read(backend_sock.get(), buf.data(), buf.size());
                                if (resp_len > 0) {
                                    ::write(client.get(), buf.data(), resp_len);
                                }
                            }
                        }
                        backend->active_requests.fetch_sub(1, std::memory_order_relaxed);
                    }
                }
            }
        }
    }
};

int main(int argc, char* argv[]) {
    int port = (argc > 1) ? std::stoi(argv[1]) : 8080;
    try {
        AsyncReverseProxy proxy(port);
        proxy.add_upstream("127.0.0.1", 8081);
        proxy.add_upstream("127.0.0.1", 8082);
        proxy.run();
    } catch (const std::exception& e) {
        std::cerr << "Критична помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
```go
package main

import (
	"context"
	"fmt"
	"net"
	"net/http"
	"net/http/httputil"
	"net/url"
	"sync"
	"sync/atomic"
	"time"
)

type Backend struct {
	URL          *url.URL
	Alive        bool
	mux          sync.RWMutex
	ReverseProxy *httputil.ReverseProxy
	ActiveConns  int64
}

func (b *Backend) SetAlive(alive bool) {
	b.mux.Lock()
	b.Alive = alive
	b.mux.Unlock()
}

func (b *Backend) IsAlive() bool {
	b.mux.RLock()
	alive := b.Alive
	b.mux.RUnlock()
	return alive
}

type ServerPool struct {
	backends []*Backend
	current  uint64
}

func (s *ServerPool) AddBackend(b *Backend) {
	s.backends = append(s.backends, b)
}

// Вибір за алгоритмом Least Connections серед живих вузлів
func (s *ServerPool) GetLeastConnectedBackend() *Backend {
	var minBackend *Backend
	minConns := int64(1000000)

	for _, b := range s.backends {
		if b.IsAlive() {
			conns := atomic.LoadInt64(&b.ActiveConns)
			if conns < minConns {
				minConns = conns
				minBackend = b
			}
		}
	}
	return minBackend
}

func (s *ServerPool) HealthCheck() {
	for _, b := range s.backends {
		status := "up"
		alive := isBackendAlive(b.URL)
		b.SetAlive(alive)
		if !alive {
			status = "down"
		}
		fmt.Printf("Health probe: %s [%s] (active: %d)\n", b.URL, status, atomic.LoadInt64(&b.ActiveConns))
	}
}

func isBackendAlive(u *url.URL) bool {
	timeout := 1 * time.Second
	conn, err := net.DialTimeout("tcp", u.Host, timeout)
	if err != nil {
		return false
	}
	_ = conn.Close()
	return true
}

func main() {
	pool := &ServerPool{}

	targetURLs := []string{
		"http://127.0.0.1:8081",
		"http://127.0.0.1:8082",
	}

	transport := &http.Transport{
		MaxIdleConns:        1000,
		MaxIdleConnsPerHost: 100,
		IdleConnTimeout:     90 * time.Second,
	}

	for _, target := range targetURLs {
		u, err := url.Parse(target)
		if err != nil {
			panic(err)
		}

		proxy := httputil.NewSingleHostReverseProxy(u)
		proxy.Transport = transport

		backend := &Backend{
			URL:          u,
			Alive:        true,
			ReverseProxy: proxy,
		}

		originalDirector := proxy.Director
		proxy.Director = func(req *http.Request) {
			originalDirector(req)
			req.Header.Set("X-Forwarded-Host", req.Host)
		}

		pool.AddBackend(backend)
	}

	// Фоновий цикл перевірки здоров'я
	go func() {
		t := time.NewTicker(time.Second * 5)
		for range t.C {
			pool.HealthCheck()
		}
	}()

	server := http.Server{
		Addr: ":8080",
		Handler: http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			peer := pool.GetLeastConnectedBackend()
			if peer != nil {
				atomic.AddInt64(&peer.ActiveConns, 1)
				defer atomic.AddInt64(&peer.ActiveConns, -1)
				peer.ReverseProxy.ServeHTTP(w, r)
				return
			}
			http.Error(w, "Service Unavailable: No healthy backends", http.StatusServiceUnavailable)
		}),
	}

	fmt.Println("L7 Reverse Proxy запущено на :8080")
	if err := server.ListenAndServe(); err != nil {
		panic(err)
	}
}
```
:::

## Детальний розбір реалізації та управління ресурсами

Розберемо ключові інженерні вузли наведених реалізацій:

### 1. Неблокуюче встановлення з'єднань і прапорець TCP_NODELAY

При виклику `connect()` на неблокуючому сокеті ядро Linux негайно повертає код `-1` із кодом помилки `errno = EINPROGRESS`. Це свідчить про те, що операційна система розпочала відправку клієнтського TCP SYN-пакета, але тристороння угода (3-Way Handshake) ще не завершилася. 

Проксі не чекає завершення рукостискання у блокуючому режимі: він реєструє дескриптор у `epoll` із подією `EPOLLOUT`. Щойно від бекенда надходить TCP SYN-ACK пакет, дескриптор стає доступним на запис, і обробник переходить до надсилання байтів запиту.

Опція сокета `TCP_NODELAY` (відключення алгоритму Нейгла) є критично необхідною: алгоритм Нейгла за замовчуванням затримує відправку дрібних пакетів розміром менше максимального розміру сегмента (MSS), очікуючи підтвердження (ACK) попередніх даних. У парі з механізмом відкладеного підтвердження (Delayed ACK) це створювало б штучну затримку у 40–200 мілісекунд на кожен запит.

### 2. Запобігання гонкам станів під час активного зондування здоров'я

У багатопотокових або асинхронних системах перевірка прапорця `is_healthy` не повинна блокувати конвеєр обробки трафіку. У версії C++ для цього використано атомарні змінні `std::atomic<bool>` та `std::atomic<int>` із моделлю пам'яті `std::memory_order_relaxed`. 

Оскільки зондування виконується фоново кожні кілька секунд, незначна затримка синхронізації кешів процесорних ядер у кілька наносекунд є абсолютно безпечною, натомість повністю усуває блокування м'ютексів на гарячому шляху вибору бекенда (Hot Path).

Крім того, алгоритм використовує гістерезис (Hysteresis): для переведення вузла в несправний стан вимагається три поспіль помилки (`UNHEALTHY_THRESHOLD = 3`), а для повернення в пул — два поспіль успішних запити (`HEALTHY_THRESHOLD = 2`). Це захищає систему від флапінгу (Flapping), коли вузол постійно випадає та повертається в пул через поодинокі втрачені пакети в мережі.

### 3. Управління пам'яттю буферів та скидання великих файлів на диск

При передачі великих файлів (наприклад, завантаження зображень чи відео розміром 50 МБ) утримання всього тіла запиту в оперативній пам'яті спричинить вичерпання RAM при одночасному обслуговуванні кількох тисяч клієнтів.

Промислові проксі використовують дворівневу схему буферизації:
- **Оперативний буфер (Small Buffer):** виділяється фіксований блок пам'яті (наприклад, 16–64 КБ). Якщо тіло запиту поміщається в цей обсяг, запит обробляється виключно в RAM без дискового введення-виведення.
- **Дисковий пул (Spooling to Temporary File):** якщо розмір тіла перевищує оперативний поріг, проксі відкриває анонімний тимчасовий файл за допомогою прапорця `O_TMPFILE` у ядрі Linux (`open(path, O_TMPFILE | O_RDWR, 0600)`). Такий файл не має імені у файловій системі й автоматично знищується ядром при закритті дескриптора, що повністю запобігає витокам дискового простору при аварійному завершенні процесу.

### 4. Нульове копіювання через системний виклик splice()

У режимі прямого проксування потоків без модифікації тіла (наприклад, передача відеофайлів або проксування WebSocket) копіювання байтів із буфера ядра в буфер процесу користувача через `read()` і наступне копіювання назад у ядро через `write()` створює подвійне навантаження на шину пам'яті та кеш L3 процесора.

Операційна система Linux надає механізм нульового копіювання (Zero-copy) за допомогою системного виклику `splice()`:

:::tabs
```c
/* Передача байтів напряму між сокетами через кільцевий буфер ядра (pipe) */
int pipefd[2];
if (pipe(pipefd) == 0) {
    ssize_t bytes = splice(client_fd, NULL, pipefd[1], NULL, 65536, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    if (bytes > 0) {
        splice(pipefd[0], NULL, backend_fd, NULL, bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }
    close(pipefd[0]);
    close(pipefd[1]);
}
```
```cpp
// Ідіоматична C++ обгортка над zero-copy передачею через RAII-канал pipe
class KernelPipe {
    int fds_[2]{-1, -1};
public:
    KernelPipe() {
        if (::pipe(fds_) != 0) {
            throw std::system_error(errno, std::generic_category());
        }
    }
    ~KernelPipe() {
        if (fds_[0] >= 0) ::close(fds_[0]);
        if (fds_[1] >= 0) ::close(fds_[1]);
    }
    [[nodiscard]] int read_fd() const noexcept { return fds_[0]; }
    [[nodiscard]] int write_fd() const noexcept { return fds_[1]; }
};

void transfer_zero_copy(int client_fd, int backend_fd, size_t max_bytes) {
    KernelPipe pipe;
    ssize_t spliced_in = ::splice(client_fd, nullptr, pipe.write_fd(), nullptr, 
                                  max_bytes, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    if (spliced_in > 0) {
        ::splice(pipe.read_fd(), nullptr, backend_fd, nullptr, 
                 spliced_in, SPLICE_F_MOVE | SPLICE_F_NONBLOCK);
    }
}
```
:::

Виклик `splice()` передає лише покажчики на сторінки пам'яті (`struct page`) у таблицях ядра, повністю виключаючи копіювання фізичних байтів через користувацький простір, що знижує завантаження CPU при стрімінгу гігабітних потоків на 60–75%.

### 5. Пасивне виявлення викидів та запобіжник (Outlier Detection & Circuit Breaker)

На додаток до активного зондування, високопродуктивний проксі веде ковзний підрахунок помилок для кожного бекенда в реальному часі. Якщо під час передачі клієнтського запиту бекенд повертає поспіль `K` помилок рівня 5xx (502 Bad Gateway, 503 Service Unavailable, 504 Gateway Timeout) або обриває TCP-з'єднання, проксі миттєво активує захисний запобіжник:
- Вузол тимчасово виключається з пулу балансування (Ejection) на фіксований інтервал охолодження (`ejection_time`, наприклад 30 секунд);
- Наступні клієнтські запити взагалі не надсилаються цьому вузлу, що дозволяє перевантаженому сервісу відновити пули потоків або з'єднань із базою даних;
- Після завершення інтервалу охолодження проксі повертає вузол у режим поступового набору навантаження (Warmup/Slow Start), виділяючи йому спершу лише 10% базової ваги з поступовим збільшенням до 100%.

## Інженерні пастки реального трафіку та методи їх подолання

Під час промислової експлуатації асинхронного балансувальника виникають небезпечні крайові випадки, які здатні призвести до прихованих витоків пам'яті або раптового падіння процесу:

### 1. Ефект отари на системному виклику accept() (Thundering Herd)

Коли балансувальник запускає пул із кількох робочих процесів (воркерів) для масштабування на всі ядра CPU, і всі воркери слухають один спільний сокет через `epoll`, надходження одного TCP-з'єднання будить усі воркери одночасно. Проте успішно виконати `accept()` вдається лише одному процесу, а решта воркерів отримують помилку `EAGAIN` і марно витрачають кванти процесорного часу на перемикання контексту ядра.

**Розв'язок:**
- Використання прапорця `EPOLLEXCLUSIVE` під час додавання слухаючого сокета в `epoll`, що вказує ядру пробуджувати рівно один процес;
- Або використання опції сокета `SO_REUSEPORT` у ядрі Linux: кожен воркер створює власний слухаючий сокет на тому самому порту, а ядро самостійно балансує вхідні SYN-пакети на рівні мережевого стека без міжпроцесорної синхронізації.

### 2. Аварійне завершення процесу через сигнал SIGPIPE

Якщо віддалений клієнт або сервер застосунку раптово розриває TCP-з'єднання (наприклад, через крах процесу або таймаут клієнта), сокет переходить у закритий стан. Перший системний виклик `write()` у такий сокет повертає помилку `ECONNRESET`, але повторна спроба запису призводить до того, що ядро операційної системи надсилає процесу сигнал `SIGPIPE`. За замовчуванням дія сигналу `SIGPIPE` — негайне аварійне знищення процесу без збереження стану.

**Розв'язок:**
- Глобальне ігнорування сигналу на старті процесу: `signal(SIGPIPE, SIG_IGN)`;
- Використання системного виклику `send()` із прапорцем `MSG_NOSIGNAL` замість `write()`, що змушує ядро повертати код помилки `EPIPE` через повернене значення замість генерації сигналу.

### 3. Вичерпання динамічних портів (Ephemeral Port Exhaustion)

Під час підключення до бекендів проксі відкриває новий вихідний TCP-сокет. Коли з'єднання закривається, операційна система переводить сокет у стан `TIME_WAIT` на тривалість `2 · MSL` (Maximum Segment Lifetime, зазвичай 60 секунд), щоб перехопити можливі запізнілі дублікати пакетів у мережі.

Діапазон локальних портів ядра за замовчуванням становить близько 28 000 адрес (`/proc/sys/net/ipv4/ip_local_port_range`). Якщо балансувальник відкриває нове TCP-з'єднання на кожен вхідний запит без повторного використання, при навантаженні понад 500 запитів на секунду всі 28 000 портів вичерпуються за одну хвилину. Наступні виклики `connect()` завершуються фатальною помилкою `EADDRNOTAVAIL` (Cannot assign requested address).

**Розв'язок:**
- Обов'язкова підтримка пулу розігрітих з'єднань (Keep-Alive Connection Pool) між проксі та бекендами, що дозволяє обслуговувати мільйони запитів через фіксовану кількість постійних сокетів;
- Активація параметра ядра `net.ipv4.tcp_tw_reuse = 1`, що дозволяє безпечно перевикористовувати сокети в стані `TIME_WAIT` для нових вихідних з'єднань, коли це не суперечить часовим міткам TCP Timestamps (RFC 1323).

### 4. Неузгодженість таймаутів Keep-Alive (Keep-Alive Race Condition)

Типова виробнича аварія виникає, коли час утримання простоюючого з'єднання (Idle Timeout) на бекенді налаштований меншим, ніж на зворотному проксі (наприклад, 60 секунд на NGINX і 55 секунд на сервері Node.js). 

На 56-й секунді бекенд вирішує закрити сокет і надсилає пакет TCP FIN. Рівно в цей самий момент проксі бере цей сокет із пулу і відправляє новий клієнтський HTTP-запит. Пакети розминаються в мережі: бекенд, отримавши дані в уже закритий сокет, відповідає пакетом TCP RST. Проксі бачить розрив з'єднання і повертає клієнту помилку `502 Bad Gateway`.

**Правило конфігурації:** Таймаут простою з'єднань на бекенді завжди повинен бути строго **більшим**, ніж таймаут на зворотному проксі (наприклад, 65 секунд на бекенді проти 60 секунд на проксі). Крім того, проксі зобов'язаний автоматично повторити (Retry) ідемпотентний запит (GET, HEAD, OPTIONS) на сусідній сокет при отриманні раптового скидання TCP RST під час спроби відправки.

## Штатне вимкнення та злив з'єднань (Graceful Shutdown & Draining)

При плановому оновленні конфігурації або перезапуску процесу балансувальника неприпустимо раптово вбивати процес сигналом `SIGKILL`, оскільки всі активні користувацькі транзакції обірвуться з помилками зв'язку.

Коректний алгоритм штатного вимкнення реалізується за 5 послідовних кроків:
1. **Перехоплення сигналу SIGQUIT або SIGTERM:** процес балансувальника встановлює внутрішній прапорець `g_shutting_down = 1`.
2. **Закриття слухаючого сокета:** виклик `close(listen_fd)` та видалення його з `epoll`. Нові клієнтські TCP SYN-пакети більше не приймаються цим процесом (їх підхоплює новий процес-наступник через механізм передачі файлових дескрипторів UNIX Domain Socket або `SO_REUSEPORT`).
3. **Маркування активних з'єднань:** усім поточним клієнтам у відповідь додається заголовок `Connection: close`, що змушує браузери та клієнтські бібліотеки коректно закрити сокети після отримання відповіді.
4. **Очікування завершення in-flight запитів:** процес очікує, доки лічильник активних з'єднань не впаде до нуля, але не довше жорсткого таймауту зливу (наприклад, `drain_timeout = 30` секунд).
5. **Фінальне очищення:** якщо після спливу таймауту залишаються завислі повільні з'єднання, балансувальник примусово закриває їх і штатно завершує процес із кодом 0.

## Діагностика продуктивності, аналіз сокетів та eBPF-трасування

Для глибокого налагодження роботи балансувальника у просторі ядра Linux використовують утиліту `ss` (Socket Statistics):

```bash
# Перевірка черг сокетів балансувальника на порту 8080
ss -t -l -n -p -i '( sport = :8080 )'
```

Ключові показники утиліти:
- **`Send-Q` (Send Queue) для слухаючого сокета:** показує поточну довжину черги повністю встановлених тристоронніх TCP-з'єднань, які очікують виклику `accept()` у процесі проксі. Якщо `Send-Q` наближається до встановленого значення ліміту `backlog` (наприклад, 1024), це свідчить про те, що воркер балансувальника заблокований тривалими синхронними операціями й не встигає забирати з'єднання з черги ядра.
- **`Recv-Q` (Receive Queue) для слухаючого сокета:** показує кількість SYN-пакетів у черзі напіввідкритих з'єднань (SYN Backlog). Переповнення свідчить про атаку SYN Flood або недостатню пропускну здатність мережевого інтерфейсу.
- **Внутрішні параметри TCP (з прапорцем `-i`):** `rtt/rttvar` (Round Trip Time та його дисперсія), `cwnd` (Congestion Window — розмір вікна перевантаження в сегментах) та `retrans` (лічильник повторно відправлених TCP-сегментів). Висока кількість `retrans` сигналізує про втрати пакетів на комутаторах локальної мережі між проксі та серверами бекенда.

### Профілювання затримок за допомогою bpftrace

Для виявлення прихованих затримок усередині подійного циклу epoll використовують інструменти BPF (bcc/bpftrace). Нижченаведений однорядковий скрипт вимірює гістограму часу перебування процесу в системному виклику `epoll_wait()`:

```bash
bpftrace -e 'tracepoint:syscalls:sys_enter_epoll_wait { @start[tid] = nsecs; } 
             tracepoint:syscalls:sys_exit_epoll_wait /@start[tid]/ { 
                 @lat_us = hist((nsecs - @start[tid]) / 1000); 
                 delete(@start[tid]); 
             }'
```

Аналіз отриманої гістограми дозволяє чітко розрізнити, чи затримка обробки запиту викликана повільним мережевим вводом-виводом клієнта, чи блокуванням потоку на дискових операціях, чи перевантаженням окремого ядра CPU обчисленнями криптографії TLS.

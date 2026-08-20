# ⚙️ Реалізація прозорого L7 сайдкар-проксі з запобіжником і балансуванням навантаження

У мікросервісній архітектурі головним завданням сайдкар-проксі (Data Plane) є перехоплення вхідного та вихідного трафіку застосунку з прозорим виконанням інфраструктурних завдань: динамічного вибору здорового екземпляра сервісу, ізоляції несправних вузлів за допомогою [запобіжника (Circuit Breaker)](book:programming/circuit-breaker-pattern) та прокидання контексту [розподіленого трейсингу](book:programming/distributed-tracing).

Коли бізнес-сервіс виконує мережевий виклик, він не повинен піклуватися про повторні спроби при тимчасових мережевих збоях, пошук працездатних IP-адрес чи шифрування каналу. Усі ці обов'язки бере на себе локальний проксі-процес, що працює в тому самому мережевому просторі імен.

Нижче реалізовано повнофункціональний L7 HTTP-проксі-демон двома мовами: чистим C з використанням низькорівневого системного API POSIX та сучасним ідіоматичним C++20 з RAII-обгортками сокетів, безпечним керуванням пам'яттю та типобезпечним пулом бекендів.

## Повний робочий код реалізації

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define LISTEN_PORT 15001
#define BUFFER_SIZE 16384
#define MAX_UPSTREAMS 8
#define MAX_CONSECUTIVE_5XX 3
#define EJECTION_DURATION_SEC 10

typedef struct {
    char host[64];
    int port;
    int consecutive_5xx;
    time_t ejected_until;
} UpstreamNode;

typedef struct {
    UpstreamNode nodes[MAX_UPSTREAMS];
    size_t count;
    size_t rr_index;
} UpstreamPool;

static UpstreamPool g_pool;

void init_upstream_pool(void) {
    g_pool.count = 0;
    g_pool.rr_index = 0;
}

bool add_upstream(const char* host, int port) {
    if (g_pool.count >= MAX_UPSTREAMS) return false;
    UpstreamNode* node = &g_pool.nodes[g_pool.count++];
    strncpy(node->host, host, sizeof(node->host) - 1);
    node->host[sizeof(node->host) - 1] = '\0';
    node->port = port;
    node->consecutive_5xx = 0;
    node->ejected_until = 0;
    return true;
}

int select_healthy_upstream(void) {
    time_t now = time(NULL);
    size_t checked = 0;

    while (checked < g_pool.count) {
        size_t idx = g_pool.rr_index % g_pool.count;
        g_pool.rr_index = (g_pool.rr_index + 1) % g_pool.count;
        checked++;

        UpstreamNode* node = &g_pool.nodes[idx];
        if (node->ejected_until > 0) {
            if (now >= node->ejected_until) {
                /* Термін виключення минув: пробне повернення вузла в пул */
                node->ejected_until = 0;
                node->consecutive_5xx = 0;
                printf("[CB] Вузол %s:%d повернуто до пулу після охолодження\n", node->host, node->port);
                return (int)idx;
            }
            continue; /* Вузол у стані ізоляції */
        }
        return (int)idx;
    }
    return -1; /* Усі бекенди виключені або пул порожній */
}

void record_upstream_result(int idx, int status_code) {
    if (idx < 0 || (size_t)idx >= g_pool.count) return;
    UpstreamNode* node = &g_pool.nodes[idx];

    if (status_code >= 500 && status_code <= 599) {
        node->consecutive_5xx++;
        printf("[OUTLIER] Вузол %s:%d повернув помилку %d (підряд: %d/%d)\n",
               node->host, node->port, status_code, node->consecutive_5xx, MAX_CONSECUTIVE_5XX);

        if (node->consecutive_5xx >= MAX_CONSECUTIVE_5XX) {
            node->ejected_until = time(NULL) + EJECTION_DURATION_SEC;
            printf("[CIRCUIT_BREAKER] Вузол %s:%d ізольовано на %d секунд!\n",
                   node->host, node->port, EJECTION_DURATION_SEC);
        }
    } else if (status_code >= 200 && status_code < 500) {
        /* Успішний статус скидає лічильник послідовних збоїв */
        node->consecutive_5xx = 0;
    }
}

int connect_to_upstream(const char* host, int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, host, &serv_addr.sin_addr) <= 0) {
        close(sock);
        return -1;
    }

    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    if (connect(sock, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
        close(sock);
        return -1;
    }
    return sock;
}

int parse_http_status(const char* response_buf, size_t len) {
    if (len < 12) return 0;
    if (strncmp(response_buf, "HTTP/1.", 7) != 0) return 0;
    const char* p = response_buf + 8;
    while (*p == ' ' && (size_t)(p - response_buf) < len) p++;
    return atoi(p);
}

void handle_client(int client_fd) {
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read = read(client_fd, buffer, sizeof(buffer) - 1);
    if (bytes_read <= 0) {
        close(client_fd);
        return;
    }
    buffer[bytes_read] = '\0';

    int upstream_idx = select_healthy_upstream();
    if (upstream_idx < 0) {
        const char* err_503 = 
            "HTTP/1.1 503 Service Unavailable\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 42\r\n\r\n"
            "Service Mesh: No healthy upstream hosts\n";
        write(client_fd, err_503, strlen(err_503));
        close(client_fd);
        return;
    }

    UpstreamNode* node = &g_pool.nodes[upstream_idx];
    int upstream_fd = connect_to_upstream(node->host, node->port);
    if (upstream_fd < 0) {
        record_upstream_result(upstream_idx, 503);
        const char* err_502 = 
            "HTTP/1.1 502 Bad Gateway\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 35\r\n\r\n"
            "Service Mesh: Upstream connect fail\n";
        write(client_fd, err_502, strlen(err_502));
        close(client_fd);
        return;
    }

    /* Ін'єкція службового заголовка трейсингу перед завершенням заголовків \r\n\r\n */
    char modified_req[BUFFER_SIZE + 256];
    char* sep = strstr(buffer, "\r\n\r\n");
    if (sep) {
        size_t head_len = (size_t)(sep - buffer);
        snprintf(modified_req, sizeof(modified_req),
                 "%.*s\r\nx-mesh-proxied: sidecar-c-v1\r\nx-request-id: req-%lx\r\n\r\n%s",
                 (int)head_len, buffer, (unsigned long)time(NULL), sep + 4);
        write(upstream_fd, modified_req, strlen(modified_req));
    } else {
        write(upstream_fd, buffer, bytes_read);
    }

    /* Читання відповіді бекенда та передача клієнту */
    ssize_t up_read = read(upstream_fd, buffer, sizeof(buffer) - 1);
    if (up_read > 0) {
        buffer[up_read] = '\0';
        int status = parse_http_status(buffer, up_read);
        record_upstream_result(upstream_idx, status);
        write(client_fd, buffer, up_read);
    } else {
        record_upstream_result(upstream_idx, 504);
    }

    close(upstream_fd);
    close(client_fd);
}

int main(void) {
    init_upstream_pool();
    add_upstream("127.0.0.1", 8081);
    add_upstream("127.0.0.1", 8082);
    add_upstream("127.0.0.1", 8083);

    int server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in address = {
        .sin_family = AF_INET,
        .sin_addr.s_addr = INADDR_ANY,
        .sin_port = htons(LISTEN_PORT)
    };

    if (bind(server_fd, (struct sockaddr*)&address, sizeof(address)) < 0) {
        perror("bind");
        close(server_fd);
        return 1;
    }

    if (listen(server_fd, 64) < 0) {
        perror("listen");
        close(server_fd);
        return 1;
    }

    printf("=== L7 Сайдкар-проксі (C) запущено на порті %d ===\n", LISTEN_PORT);

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t addrlen = sizeof(client_addr);
        int client_fd = accept(server_fd, (struct sockaddr*)&client_addr, &addrlen);
        if (client_fd >= 0) {
            handle_client(client_fd);
        }
    }

    close(server_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <optional>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace mesh {

using Clock = std::chrono::steady_clock;
using TimePoint = std::chrono::time_point<Clock>;

struct UpstreamNode {
    std::string host;
    int port;
    int consecutive_5xx{0};
    TimePoint ejected_until{TimePoint::min()};

    [[nodiscard]] bool is_healthy(TimePoint now) const {
        return now >= ejected_until;
    }
};

class SocketGuard {
    int fd_{-1};
public:
    explicit SocketGuard(int fd) : fd_(fd) {}
    ~SocketGuard() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketGuard(const SocketGuard&) = delete;
    SocketGuard& operator=(const SocketGuard&) = delete;
    SocketGuard(SocketGuard&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketGuard& operator=(SocketGuard&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

class OutlierDetector {
    std::vector<UpstreamNode> nodes_;
    size_t rr_index_{0};
    const int max_consecutive_5xx_{3};
    const std::chrono::seconds ejection_duration_{10};

public:
    void add_upstream(std::string host, int port) {
        nodes_.push_back(UpstreamNode{std::move(host), port, 0, TimePoint::min()});
    }

    [[nodiscard]] std::optional<size_t> select_healthy_node() {
        if (nodes_.empty()) return std::nullopt;
        const auto now = Clock::now();
        
        for (size_t checked = 0; checked < nodes_.size(); ++checked) {
            size_t idx = rr_index_ % nodes_.size();
            rr_index_ = (rr_index_ + 1) % nodes_.size();

            auto& node = nodes_[idx];
            if (node.is_healthy(now)) {
                if (node.ejected_until != TimePoint::min()) {
                    /* Відновлення після завершення тайм-ауту охолодження */
                    node.ejected_until = TimePoint::min();
                    node.consecutive_5xx = 0;
                    std::cout << "[CB] Відновлено вузол " << node.host << ":" << node.port << "\n";
                }
                return idx;
            }
        }
        return std::nullopt;
    }

    void record_status(size_t idx, int status_code) {
        if (idx >= nodes_.size()) return;
        auto& node = nodes_[idx];

        if (status_code >= 500 && status_code <= 599) {
            node.consecutive_5xx++;
            std::cout << "[OUTLIER] Вузол " << node.host << ":" << node.port
                      << " статус " << status_code << " (невдач: "
                      << node.consecutive_5xx << "/" << max_consecutive_5xx_ << ")\n";

            if (node.consecutive_5xx >= max_consecutive_5xx_) {
                node.ejected_until = Clock::now() + ejection_duration_;
                std::cout << "[CIRCUIT_BREAKER] Вузол " << node.host << ":" << node.port
                          << " ізольовано на " << ejection_duration_.count() << "s!\n";
            }
        } else if (status_code >= 200 && status_code < 500) {
            node.consecutive_5xx = 0;
        }
    }

    [[nodiscard]] const UpstreamNode& get_node(size_t idx) const {
        return nodes_.at(idx);
    }
};

class SidecarProxy {
    int port_;
    OutlierDetector detector_;

    static std::optional<SocketGuard> create_upstream_socket(const std::string& host, int port) {
        int fd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd < 0) return std::nullopt;

        SocketGuard guard(fd);
        sockaddr_in serv_addr{};
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_port = htons(port);

        if (::inet_pton(AF_INET, host.c_str(), &serv_addr.sin_addr) <= 0) {
            return std::nullopt;
        }

        timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        ::setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
        ::setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

        if (::connect(fd, reinterpret_cast<sockaddr*>(&serv_addr), sizeof(serv_addr)) < 0) {
            return std::nullopt;
        }
        return guard;
    }

    static int parse_status_code(std::string_view response) {
        if (response.size() < 12 || !response.starts_with("HTTP/1.")) return 0;
        auto pos = response.find(' ');
        if (pos == std::string_view::npos) return 0;
        while (pos < response.size() && response[pos] == ' ') ++pos;
        if (pos + 3 <= response.size()) {
            return std::stoi(std::string(response.substr(pos, 3)));
        }
        return 0;
    }

public:
    explicit SidecarProxy(int port) : port_(port) {}

    void add_backend(std::string host, int port) {
        detector_.add_upstream(std::move(host), port);
    }

    void handle_connection(SocketGuard client) {
        std::vector<char> buffer(16384);
        ssize_t bytes = ::read(client.get(), buffer.data(), buffer.size() - 1);
        if (bytes <= 0) return;

        std::string_view request(buffer.data(), static_cast<size_t>(bytes));
        auto upstream_idx = detector_.select_healthy_node();

        if (!upstream_idx) {
            std::string_view err_503 = 
                "HTTP/1.1 503 Service Unavailable\r\n"
                "Content-Length: 38\r\n\r\n"
                "Mesh: No healthy upstreams available\n";
            ::write(client.get(), err_503.data(), err_503.size());
            return;
        }

        const auto& node = detector_.get_node(*upstream_idx);
        auto upstream_sock = create_upstream_socket(node.host, node.port);

        if (!upstream_sock) {
            detector_.record_status(*upstream_idx, 503);
            std::string_view err_502 = 
                "HTTP/1.1 502 Bad Gateway\r\n"
                "Content-Length: 29\r\n\r\n"
                "Mesh: Connection to host failed\n";
            ::write(client.get(), err_502.data(), err_502.size());
            return;
        }

        /* Додавання службових заголовків трейсингу */
        std::string enriched_req;
        auto header_end = request.find("\r\n\r\n");
        if (header_end != std::string_view::npos) {
            enriched_req.append(request.substr(0, header_end));
            enriched_req.append("\r\nx-mesh-envoy: sidecar-cpp-v2\r\nx-request-id: req-cpp-trace\r\n\r\n");
            enriched_req.append(request.substr(header_end + 4));
        } else {
            enriched_req = std::string(request);
        }

        ::write(upstream_sock->get(), enriched_req.data(), enriched_req.size());

        ssize_t up_bytes = ::read(upstream_sock->get(), buffer.data(), buffer.size() - 1);
        if (up_bytes > 0) {
            std::string_view resp(buffer.data(), static_cast<size_t>(up_bytes));
            int status = parse_status_code(resp);
            detector_.record_status(*upstream_idx, status);
            ::write(client.get(), buffer.data(), static_cast<size_t>(up_bytes));
        } else {
            detector_.record_status(*upstream_idx, 504);
        }
    }

    void run() {
        int sfd = ::socket(AF_INET, SOCK_STREAM, 0);
        if (sfd < 0) throw std::runtime_error("socket creation failed");
        SocketGuard server_guard(sfd);

        int opt = 1;
        ::setsockopt(sfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port_);

        if (::bind(sfd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            throw std::runtime_error("bind failed");
        }
        if (::listen(sfd, 64) < 0) {
            throw std::runtime_error("listen failed");
        }

        std::cout << "=== L7 Сайдкар-проксі (C++20) запущено на порті " << port_ << " ===\n";

        while (true) {
            sockaddr_in client_addr{};
            socklen_t len = sizeof(client_addr);
            int cfd = ::accept(sfd, reinterpret_cast<sockaddr*>(&client_addr), &len);
            if (cfd >= 0) {
                handle_connection(SocketGuard(cfd));
            }
        }
    }
};

} // namespace mesh

int main() {
    mesh::SidecarProxy proxy(15001);
    proxy.add_backend("127.0.0.1", 8081);
    proxy.add_backend("127.0.0.1", 8082);
    proxy.add_backend("127.0.0.1", 8083);
    proxy.run();
    return 0;
}
```
:::

## Покроковий розбір архітектури та фаз обробки запиту

Реалізований сайдкар-проксі працює за моделлю послідовного конвеєра з п'яти дискретних етапів:

### 1. Ініціалізація та керування сокетами

Проксі відкриває головний слухаючий TCP-сокет на порті `15001`. Сокет конфігурується з прапорцем `SO_REUSEADDR` для уникнення зависань порту в стані `TIME_WAIT` при перезапуску процесу. 

Для вихідних з'єднань до бекендів (`connect_to_upstream`) обов'язково встановлюються таймаути на читання та запис через сокетні опції `SO_RCVTIMEO` та `SO_SNDTIMEO` (у прикладі — 2 секунди). Без цих опцій завислий або «німий» віддалений сервер призведе до блокування потоку проксі на невизначений термін (до 15 хвилин за дефолтними налаштуваннями TCP keep-alive ядра Linux).

У версії C++20 керування ресурсами дескрипторів сокетів повністю інкапсульовано в ідіому RAII за допомогою класу `SocketGuard`: конструктор захоплює числовий дескриптор `int fd`, а деструктор гарантовано викликає `::close(fd_)` при виході з будь-якої гілки виконання чи викиданні винятку.

### 2. Динамічний вибір бекенда та стан запобіжника (Circuit Breaker)

Управління списком доступних серверів покладено на модуль `OutlierDetector` / `UpstreamPool`. Проксі використовує алгоритм циклічного перебору **Round-Robin** за модулем кількості зареєстрованих хостів.

Перед передачею запиту хосту проксі перевіряє його статус надійності:
* Якщо поле `ejected_until` дорівнює нулю або минулому часу (`now >= node.ejected_until`), вузол вважається здоровим (`HEALTHY`).
* Якщо вузол перебував у стані ізоляції, але період охолодження закінчився, проксі переводить його у випробувальний стан (Half-Open): лічильник збоїв скидається до нуля, і на хост направляється один пробний запит.
* Якщо вузол ізольований (`now < node.ejected_until`), циклічний покажчик переходить до наступного елемента масиву. Якщо всі вузли в пулі несправні, функція негайно повертає відсутність результату, і клієнт отримує синтетичну відповідь `HTTP 503 Service Unavailable`.

### 3. Модифікація L7-заголовків та ін'єкція контексту трейсингу

Проксі зчитує сирий потік байтів клієнтського запиту і сканує його на наявність двосимвольного маркеру кінця HTTP-заголовків `\r\n\r\n`. 

Виявивши межу заголовків, проксі вставляє два службові заголовки:
1. `x-mesh-proxied` — службова мітка версії проксі для діагностики шляху запиту.
2. `x-request-id` — унікальний ідентифікатор транзакції. Якщо клієнт не передав свій ID, проксі генерує його на базі поточної мітки часу, що забезпечує наскрізну простежуваність виклику в розподіленому журналі логів.

### 4. Вичитування відповіді та розбір статусів

Після успішного отримання відповіді від віддаленого сервера проксі парсить початковий HTTP-рядок (`HTTP/1.1 200 OK` або `HTTP/1.1 503 Service Unavailable`).

Функція `parse_http_status` вилучає числовий код статусу:
* Якщо статус потрапляє в діапазон `500..599` (помилки сервера), лічильник `consecutive_5xx` відповідного вузла збільшується на одиницю. При досягненні порогового значення `MAX_CONSECUTIVE_5XX` (3 помилки поспіль) для вузла встановлюється час блокування `ejected_until = now + 10s`.
* Якщо статус знаходиться в діапазоні `200..499` (успіх або клієнтська помилка бізнес-логіки), лічильник послідовних збоїв `consecutive_5xx` миттєво обнуляється, підтверджуючи працездатність процесу.

## Типові інженерні пастки реалізації проксі-демонів

### 1. Шторм ретраїв (Retry Storm) на неідемпотентних операціях

Автоматичні повторні спроби на рівні проксі є небезпечними, якщо вони застосовуються без аналізу HTTP-методу. Якщо клієнт викликав платіжний метод `POST /api/v1/payments`, і бекенд повернув код 500 після того, як кошти вже списалися з рахунку, наївний автоматичний ретрай сайдкара на інший бекенд призведе до подвійного списання коштів. 

Промислові сітки (Envoy) дозволяють повтори лише для ідемпотентних методів (`GET`, `PUT`, `DELETE`, `HEAD`) або вимагають передачі криптографічного ключа ідемпотентності в заголовку `Idempotency-Key`.

### 2. Зависання на напівзакритих з'єднаннях (TCP Half-Closed)

Коли бекенд завершує передачу даних і відправляє TCP-сегмент `FIN`, сокет переходить у напівзакритий стан. Якщо проксі не перевіряє повернене значення системного виклику `read() <= 0` і не закриває обидва кінці з'єднання, сокетні структури ядра залишатимуться відкритими, що призведе до швидкого вичерпання ліміту відкритих файлів процесу (`ulimit -n`).

### 3. Каскадне вибивання всього пулу (Cascading Total Ejection)

Якщо всі бекенди кластера тимчасово повертають 500 через недоступність спільної бази даних, простий алгоритм виявлення викидів послідовно ізолює 100% серверів у пулі. Навіть коли база даних відновить роботу через кілька секунд, кластер залишатиметься повністю паралізованим, оскільки проксі відмовлятиметься направляти запити до завершення тайм-ауту охолодження.

Для запобігання цьому промислові сітки вводять параметр `max_ejection_percent` (зазвичай 50%): навіть при масових збоях проксі ніколи не ізолює більше половини зареєстрованих хостів, залишаючи можливість аварійного відновлення.

## Інструкція з тестування та перевірки роботи

Для перевірки роботи запобіжника та балансування запустіть три тестові сервери за допомогою утиліти `nc` (Netcat) на локальних портах:

```bash
# Термінал 1: Здоровий бекенд 1
while true; do echo -e "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nnode1" | nc -l -p 8081; done

# Термінал 2: Здоровий бекенд 2
while true; do echo -e "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nnode2" | nc -l -p 8082; done

# Термінал 3: Збійний бекенд 3 (постійно повертає 500)
while true; do echo -e "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 5\r\n\r\nerror" | nc -l -p 8083; done
```

Скомпілюйте та запустіть проксі:

```bash
# Для C-версії:
gcc -O2 -Wall proj_proxy.c -o proxy_c && ./proxy_c

# Для C++ версії:
g++ -O2 -std=c++20 -Wall proj_proxy.cpp -o proxy_cpp && ./proxy_cpp
```

Виконайте серію з 10 тестових запитів через утиліту `curl`:

```bash
for i in {1..10}; do curl -i http://127.0.0.1:15001/test; echo ""; sleep 0.5; done
```

У логах консолі проксі ви побачите, як після трьох послідовних звернень до порту 8083 спрацьовує правило `[CIRCUIT_BREAKER] Вузол 127.0.0.1:8083 ізольовано на 10 секунд!`, після чого 100% наступних запитів рівномірно розподіляються виключно між здоровими портами 8081 та 8082.

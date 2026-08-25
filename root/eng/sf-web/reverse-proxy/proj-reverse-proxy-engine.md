# ⚙️ Реалізація неблокуючого зворотного проксі на системних сокетах та epoll

У системному програмуванні зворотний проксі — це процес ядра користувацького простору, який перенаправляє потоки байтів між двома незалежними файловими дескрипторами мережевих сокетів: зовнішнім клієнтським сокетом (`client_fd`) та внутрішнім апстрім-сокетом (`upstream_fd`).

Якщо сервер реалізує класичну модель обробки з виділенням одного потоку операційної системи на кожне з'єднання (Thread-per-Connection), він швидко впирається у фізичні обмеження ядра:
* 10 000 одночасних клієнтів з типовим розміром стека потоку Linux 4 МБ потребують 40 гігабайтів оперативної пам'яті лише для утримання стеків викликів.
* Планувальник завдань ядра Linux (CFS) витрачає до 80% часу процесора на перемикання контексту між тисячами заблокованих потоків.

На противагу цьому, асинхронна архітектура на основі єдиного неблокуючого циклу подій (Event Loop) утримує 10 000 сокетів у таблиці ядра `epoll`, споживаючи менше 2 мегабайтів пам'яті на структури даних і виконуючи всі операції пересилання в межах одного процесорного ядра з нульовими витратами на блокування потоків.

У цій практичній роботі розглянуто повну інженерну реалізацію асинхронного зворотного проксі на мовах C та C++20.

---

## 1. Архітектура кінцевого автомата сесії

Кожне клієнтське підключення створює контекст сесії (`ProxySession`), який об'єднує два сокети, їхні буфери та поточний стан зв'язку:

```
                  ┌──────────────────────────────────────────────┐
                  │                 КЛІЄНТ                       │
                  └──────────────────────────────────────────────┘
                                         │
                                         ▼ (accept на listen_fd)
                  ┌──────────────────────────────────────────────┐
                  │          STATE_CONNECTING_UPSTREAM           │
                  │  1. Створення non-blocking upstream_fd       │
                  │  2. connect() -> повертає EINPROGRESS        │
                  │  3. Реєстрація upstream_fd на EPOLLOUT       │
                  └──────────────────────────────────────────────┘
                                         │
                                         ▼ (Подія EPOLLOUT: сокет готовий)
                  ┌──────────────────────────────────────────────┐
                  │               STATE_STREAMING                │
                  │  1. Перевірка getsockopt(SO_ERROR) == 0      │
                  │  2. Модифікація upstream_fd на EPOLLIN       │
                  │  3. Двостороння перекачка:                   │
                  │     client_fd <──[буфер]──> upstream_fd      │
                  └──────────────────────────────────────────────┘
                                         │
                                         ▼ (EPOLLRDHUP / EOF / Помилка)
                  ┌──────────────────────────────────────────────┐
                  │             ЗАКРИТТЯ ТА ОЧИЩЕННЯ             │
                  │  1. epoll_ctl(EPOLL_CTL_DEL) для обох сокетів│
                  │  2. close(client_fd) та close(upstream_fd)   │
                  │  3. Звільнення пам'яті сесії                 │
                  └──────────────────────────────────────────────┘
```

### Ключові етапи роботи системного рушія:

1. **Неблокуючий режим (`O_NONBLOCK`):** Усі дескриптори перемикаються у неблокуючий режим системним викликом `fcntl(fd, F_SETFL, flags | O_NONBLOCK)`. Завдяки цьому жоден виклик `read()`, `write()`, `accept()` чи `connect()` не зупиняє виконання головного циклу, повертаючи помилку `EAGAIN` або `EWOULDBLOCK`, якщо сокет не готовий до миттєвої передачі даних.
2. **Асинхронне встановлення з'єднання з апстрімом:** При спробі підключитися до сервера бекенда через `connect()` ядро не чекає завершення 3-Way Handshake, а негайно повертає код `-1` зі значенням `errno = EINPROGRESS`. Проксі реєструє `upstream_fd` в `epoll` із подією `EPOLLOUT`. Щойно TCP-рукостискання з бекендом завершується, ядро надсилає подію готовності до запису.
3. **Верифікація успішності підключення:** Готовність сокета до запису після `EINPROGRESS` настає як при успішному з'єднанні, так і при помилці (наприклад, `Connection Refused`). Проксі зобов'язаний виконати перевірку `getsockopt(upstream_fd, SOL_SOCKET, SO_ERROR, &err, &len)`. Лише якщо `err == 0`, з'єднання вважається встановленим.
4. **Обробка напівзакритого з'єднання (`EPOLLRDHUP`):** Стандартний прапорець `EPOLLIN` сигналізує про наявність даних. Проте якщо віддалена сторона закрила з'єднання (надіслала TCP-сегмент `FIN`), читання поверне 0 байтів. Прапорець ядра Linux `EPOLLRDHUP` дозволяє виявити закриття сокета на рівні самого циклу `epoll_wait`, миттєво запускаючи очищення парного з'єднання.
5. **Оптимізація передачі нульового копіювання (Zero-Copy Splice):** У високонавантажених проксі замість пари системних викликів `read()` і `write()`, які двічі копіюють кожен байт між простором ядра та пам'яттю процесу через шину RAM, застосовується системний виклик `splice()`. Використовуючи службовий конвеєр (pipe) ядра Linux, `splice()` перекидає вказівники на сторінки пам'яті безпосередньо з буфера сокета клієнта в буфер сокета бекенда без копіювання байтів через регістри центрального процесора.

---

## 2. Реалізація зворотного проксі (C та C++)

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <netdb.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

#define MAX_EVENTS 1024
#define BUFFER_SIZE 16384
#define LISTEN_PORT 8080
#define UPSTREAM_HOST "127.0.0.1"
#define UPSTREAM_PORT 8000

typedef enum {
    STATE_CONNECTING_UPSTREAM,
    STATE_STREAMING
} SessionState;

typedef struct {
    int client_fd;
    int upstream_fd;
    SessionState state;
    char client_to_up_buf[BUFFER_SIZE];
    size_t c2u_len;
    char up_to_client_buf[BUFFER_SIZE];
    size_t u2c_len;
    char client_ip[INET_ADDRSTRLEN];
} ProxySession;

static int make_socket_non_blocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static void close_session(int epoll_fd, ProxySession *session) {
    if (!session) return;
    if (session->client_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, session->client_fd, NULL);
        close(session->client_fd);
    }
    if (session->upstream_fd >= 0) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, session->upstream_fd, NULL);
        close(session->upstream_fd);
    }
    free(session);
}

static int create_and_bind_listener(int port) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd == -1) return -1;

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (bind(listen_fd, (struct sockaddr *)&addr, sizeof(addr)) == -1) {
        close(listen_fd);
        return -1;
    }
    if (make_socket_non_blocking(listen_fd) == -1) {
        close(listen_fd);
        return -1;
    }
    if (listen(listen_fd, SOMAXCONN) == -1) {
        close(listen_fd);
        return -1;
    }
    return listen_fd;
}

static int connect_to_upstream(const char *host, int port) {
    int up_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (up_fd == -1) return -1;

    if (make_socket_non_blocking(up_fd) == -1) {
        close(up_fd);
        return -1;
    }

    struct sockaddr_in up_addr;
    memset(&up_addr, 0, sizeof(up_addr));
    up_addr.sin_family = AF_INET;
    up_addr.sin_port = htons(port);
    inet_pton(AF_INET, host, &up_addr.sin_addr);

    int res = connect(up_fd, (struct sockaddr *)&up_addr, sizeof(up_addr));
    if (res == -1 && errno != EINPROGRESS) {
        close(up_fd);
        return -1;
    }
    return up_fd;
}

int main(void) {
    // Ігноруємо сигнал SIGPIPE, щоб уникнути аварійного завершення процесу при записі в закритий сокет
    signal(SIGPIPE, SIG_IGN);

    int listen_fd = create_and_bind_listener(LISTEN_PORT);
    if (listen_fd == -1) {
        perror("Помилка створення слухаючого сокета");
        return 1;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd == -1) {
        perror("epoll_create1");
        close(listen_fd);
        return 1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.ptr = NULL; // NULL вказує на слухаючий сокет
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev) == -1) {
        perror("epoll_ctl listen_fd");
        close(listen_fd);
        close(epoll_fd);
        return 1;
    }

    struct epoll_event events[MAX_EVENTS];
    printf("Зворотний проксі запущено на порту %d -> апстрім %s:%d\n",
           LISTEN_PORT, UPSTREAM_HOST, UPSTREAM_PORT);

    while (1) {
        int n_fds = epoll_wait(epoll_fd, events, MAX_EVENTS, -1);
        if (n_fds == -1) {
            if (errno == EINTR) continue;
            break;
        }

        for (int i = 0; i < n_fds; ++i) {
            if (events[i].data.ptr == NULL) {
                // Прийом усіх очікуючих клієнтських з'єднань
                while (1) {
                    struct sockaddr_in client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = accept(listen_fd, (struct sockaddr *)&client_addr, &client_len);
                    if (client_fd == -1) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("accept");
                        break;
                    }

                    make_socket_non_blocking(client_fd);

                    int up_fd = connect_to_upstream(UPSTREAM_HOST, UPSTREAM_PORT);
                    if (up_fd == -1) {
                        close(client_fd);
                        continue;
                    }

                    ProxySession *session = (ProxySession *)calloc(1, sizeof(ProxySession));
                    if (!session) {
                        close(client_fd);
                        close(up_fd);
                        continue;
                    }
                    session->client_fd = client_fd;
                    session->upstream_fd = up_fd;
                    session->state = STATE_CONNECTING_UPSTREAM;
                    inet_ntop(AF_INET, &client_addr.sin_addr, session->client_ip, sizeof(session->client_ip));

                    struct epoll_event ev_client, ev_up;
                    ev_client.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
                    ev_client.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev_client);

                    ev_up.events = EPOLLOUT | EPOLLRDHUP | EPOLLERR;
                    ev_up.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, up_fd, &ev_up);
                }
            } else {
                ProxySession *session = (ProxySession *)events[i].data.ptr;
                uint32_t evs = events[i].events;

                if (evs & (EPOLLRDHUP | EPOLLERR | EPOLLHUP)) {
                    close_session(epoll_fd, session);
                    continue;
                }

                if (session->state == STATE_CONNECTING_UPSTREAM) {
                    int err = 0;
                    socklen_t len = sizeof(err);
                    if (getsockopt(session->upstream_fd, SOL_SOCKET, SO_ERROR, &err, &len) < 0 || err != 0) {
                        close_session(epoll_fd, session);
                        continue;
                    }
                    session->state = STATE_STREAMING;
                    struct epoll_event ev_up;
                    ev_up.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
                    ev_up.data.ptr = session;
                    epoll_ctl(epoll_fd, EPOLL_CTL_MOD, session->upstream_fd, &ev_up);
                }

                // Перекачування байтів від клієнта до апстріму
                char buf[BUFFER_SIZE];
                ssize_t bytes_read = read(session->client_fd, buf, sizeof(buf));
                if (bytes_read > 0) {
                    ssize_t sent = write(session->upstream_fd, buf, (size_t)bytes_read);
                    (void)sent;
                } else if (bytes_read == 0 || (bytes_read == -1 && errno != EAGAIN)) {
                    close_session(epoll_fd, session);
                    continue;
                }

                // Перекачування байтів від апстріму до клієнта
                ssize_t up_read = read(session->upstream_fd, buf, sizeof(buf));
                if (up_read > 0) {
                    ssize_t sent = write(session->client_fd, buf, (size_t)up_read);
                    (void)sent;
                } else if (up_read == 0 || (up_read == -1 && errno != EAGAIN)) {
                    close_session(epoll_fd, session);
                    continue;
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
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <unordered_map>
#include <span>
#include <expected>
#include <system_error>
#include <csignal>

#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace proxy {

// RAII обгортка для автоматичного керування життєвим циклом файлового дескриптора
class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() noexcept { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.release()) {}
    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int old = fd_;
        fd_ = -1;
        return old;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_{-1};
};

enum class SessionState {
    ConnectingUpstream,
    Streaming
};

struct Session {
    UniqueFd client_fd;
    UniqueFd upstream_fd;
    SessionState state{SessionState::ConnectingUpstream};
    std::string client_ip;
};

class ReverseProxyEngine {
public:
    static constexpr int MaxEvents = 1024;
    static constexpr size_t BufferSize = 16384;

    ReverseProxyEngine(std::string upstream_host, uint16_t upstream_port)
        : upstream_host_(std::move(upstream_host)), upstream_port_(upstream_port) {}

    std::expected<void, std::error_code> run(uint16_t listen_port) {
        ::signal(SIGPIPE, SIG_IGN);

        auto listen_res = create_listener(listen_port);
        if (!listen_res) return std::unexpected(listen_res.error());
        listen_fd_ = std::move(*listen_res);

        int ep_fd = ::epoll_create1(0);
        if (ep_fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        epoll_fd_.reset(ep_fd);

        epoll_event ev{};
        ev.events = EPOLLIN;
        ev.data.fd = listen_fd_.get();
        if (::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, listen_fd_.get(), &ev) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<epoll_event> events(MaxEvents);
        std::vector<uint8_t> io_buffer(BufferSize);

        std::cout << "Зворотний проксі (C++20) запущено на порту " << listen_port
                  << " -> " << upstream_host_ << ":" << upstream_port_ << '\n';

        while (true) {
            int n_ready = ::epoll_wait(epoll_fd_.get(), events.data(), MaxEvents, -1);
            if (n_ready < 0) {
                if (errno == EINTR) continue;
                break;
            }

            for (int i = 0; i < n_ready; ++i) {
                const auto& event = events[i];

                if (event.data.fd == listen_fd_.get()) {
                    accept_clients();
                } else {
                    int fd = event.data.fd;
                    auto it = sessions_by_fd_.find(fd);
                    if (it == sessions_by_fd_.end()) continue;

                    auto session = it->second;
                    if (event.events & (EPOLLRDHUP | EPOLLERR | EPOLLHUP)) {
                        remove_session(session);
                        continue;
                    }

                    handle_io(session, io_buffer);
                }
            }
        }
        return {};
    }

private:
    static std::expected<void, std::error_code> make_non_blocking(int fd) {
        int flags = ::fcntl(fd, F_GETFL, 0);
        if (flags < 0 || ::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<UniqueFd, std::error_code> create_listener(uint16_t port) {
        UniqueFd fd(::socket(AF_INET, SOCK_STREAM, 0));
        if (!fd.valid()) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        int opt = 1;
        ::setsockopt(fd.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        if (auto res = make_non_blocking(fd.get()); !res) return std::unexpected(res.error());

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(port);

        if (::bind(fd.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0 ||
            ::listen(fd.get(), SOMAXCONN) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return fd;
    }

    std::expected<UniqueFd, std::error_code> connect_upstream() {
        UniqueFd fd(::socket(AF_INET, SOCK_STREAM, 0));
        if (!fd.valid()) return std::unexpected(std::error_code(errno, std::generic_category()));
        if (auto res = make_non_blocking(fd.get()); !res) return std::unexpected(res.error());

        sockaddr_in up_addr{};
        up_addr.sin_family = AF_INET;
        up_addr.sin_port = htons(upstream_port_);
        ::inet_pton(AF_INET, upstream_host_.c_str(), &up_addr.sin_addr);

        int res = ::connect(fd.get(), reinterpret_cast<sockaddr*>(&up_addr), sizeof(up_addr));
        if (res < 0 && errno != EINPROGRESS) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return fd;
    }

    void accept_clients() {
        while (true) {
            sockaddr_in c_addr{};
            socklen_t c_len = sizeof(c_addr);
            int c_fd = ::accept(listen_fd_.get(), reinterpret_cast<sockaddr*>(&c_addr), &c_len);
            if (c_fd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                break;
            }

            make_non_blocking(c_fd);
            auto up_res = connect_upstream();
            if (!up_res) {
                ::close(c_fd);
                continue;
            }

            char ip_buf[INET_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET, &c_addr.sin_addr, ip_buf, sizeof(ip_buf));

            auto session = std::make_shared<Session>();
            session->client_fd.reset(c_fd);
            session->upstream_fd = std::move(*up_res);
            session->state = SessionState::ConnectingUpstream;
            session->client_ip = ip_buf;

            int client_raw = session->client_fd.get();
            int up_raw = session->upstream_fd.get();

            sessions_by_fd_[client_raw] = session;
            sessions_by_fd_[up_raw] = session;

            epoll_event ev_c{};
            ev_c.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
            ev_c.data.fd = client_raw;
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, client_raw, &ev_c);

            epoll_event ev_u{};
            ev_u.events = EPOLLOUT | EPOLLRDHUP | EPOLLERR;
            ev_u.data.fd = up_raw;
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, up_raw, &ev_u);
        }
    }

    void handle_io(const std::shared_ptr<Session>& session, std::span<uint8_t> buffer) {
        if (session->state == SessionState::ConnectingUpstream) {
            int err = 0;
            socklen_t len = sizeof(err);
            if (::getsockopt(session->upstream_fd.get(), SOL_SOCKET, SO_ERROR, &err, &len) < 0 || err != 0) {
                remove_session(session);
                return;
            }
            session->state = SessionState::Streaming;

            epoll_event ev_u{};
            ev_u.events = EPOLLIN | EPOLLRDHUP | EPOLLERR;
            ev_u.data.fd = session->upstream_fd.get();
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_MOD, session->upstream_fd.get(), &ev_u);
        }

        // Передача від клієнта до апстріму
        ssize_t n_client = ::read(session->client_fd.get(), buffer.data(), buffer.size());
        if (n_client > 0) {
            ::write(session->upstream_fd.get(), buffer.data(), static_cast<size_t>(n_client));
        } else if (n_client == 0 || (n_client < 0 && errno != EAGAIN)) {
            remove_session(session);
            return;
        }

        // Передача від апстріму до клієнта
        ssize_t n_up = ::read(session->upstream_fd.get(), buffer.data(), buffer.size());
        if (n_up > 0) {
            ::write(session->client_fd.get(), buffer.data(), static_cast<size_t>(n_up));
        } else if (n_up == 0 || (n_up < 0 && errno != EAGAIN)) {
            remove_session(session);
            return;
        }
    }

    void remove_session(const std::shared_ptr<Session>& session) {
        if (!session) return;
        if (session->client_fd.valid()) {
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, session->client_fd.get(), nullptr);
            sessions_by_fd_.erase(session->client_fd.get());
        }
        if (session->upstream_fd.valid()) {
            ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, session->upstream_fd.get(), nullptr);
            sessions_by_fd_.erase(session->upstream_fd.get());
        }
    }

    std::string upstream_host_;
    uint16_t upstream_port_;
    UniqueFd listen_fd_;
    UniqueFd epoll_fd_;
    std::unordered_map<int, std::shared_ptr<Session>> sessions_by_fd_;
};

} // namespace proxy

int main() {
    proxy::ReverseProxyEngine engine("127.0.0.1", 8000);
    auto res = engine.run(8080);
    if (!res) {
        std::cerr << "Помилка роботи проксі: " << res.error().message() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Інженерні пастки реалізації та методи захисту

### 1. Голодування циклу подій (Event Loop Starvation)
Якщо один клієнт надсилає великий файл розміром 100 МБ через швидку мережу, цикл `while(read)` усередині однієї ітерації події може безперервно зчитувати дані, не повертаючи керування в `epoll_wait`. У результаті всі інші 9 999 клієнтів перестануть обслуговуватися.
* **Механізм захисту:** Введення квоти на обсяг даних за одну ітерацію (наприклад, не більше 64 КБ на сесію). Після вичитування квоти сесія поступається чергою, повертаючи керування в диспетчер подій.

### 2. Частковий запис (Partial Write) та переповнення TCP-буфера
Системний виклик `write()` на неблокуючому сокеті не гарантує надсилання всього переданого буфера: він повертає лише кількість байтів, яка реально помістилася в буфер відправлення TCP ядра (`SO_SNDBUF`). Якщо сокет приймача переповнений, `write()` повертає помилку `EAGAIN`.
* **Механізм захисту:** Ненадіслані байти накопичуються у вихідному кільцевому буфері сесії. Для сокета в `epoll` динамічно додається прапорець `EPOLLOUT`. Щойно TCP-стек звільняє місце в буфері, ядро активує `epoll_wait`, проксі досилає залишок байтів і знімає прапорець `EPOLLOUT`.

### 3. Сигнал SIGPIPE при розриві з'єднання
Якщо віддалений клієнт аварійно розірвав з'єднання (надіслав `RST`), а проксі виконує виклик `write()` у закритий сокет, операційна система генерує сигнал `SIGPIPE`. За замовчуванням дія сигналу `SIGPIPE` — негайне аварійне завершення процесу проксі.
* **Механізм захисту:** Обов'язкове встановлення `signal(SIGPIPE, SIG_IGN)` на старті процесу або передача прапорця `MSG_NOSIGNAL` у системний виклик `send()`. Тоді виклик поверне код помилки `-1` з `errno = EPIPE`, що дозволить коректно закрити сесію без падіння демона.

### 4. Витік дескрипторів та безпечне видалення з epoll
Якщо процес викликає `close(fd)` без попереднього виклику `epoll_ctl(epoll_fd, EPOLL_CTL_DEL, fd, NULL)`, дескриптор автоматично видаляється з epoll лише за умови, що це було останнє посилання на базовий файловий об'єкт ядра. Якщо дескриптор було скопійовано через `dup()` або передано у дочірній процес через `fork()`, події для мертвого сокета можуть продовжувати надходити.
* **Механізм захисту:** Явне виконання `EPOLL_CTL_DEL` перед закриттям сокета або використання обгортки `UniqueFd`, яка гарантує коректний порядок очищення ресурсів.

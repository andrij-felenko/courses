# Практикум: виробничий координатор коректного завершення

Мережевий сервер, що одночасно обслуговує тисячі підключень клієнтів, не може припинити виконання миттєво. Якщо процес зупинити грубо через аварійне переривання або типову дію сигналу `SIGTERM`, клієнти отримають раптовий розрив TCP-сесії аварійним пакетом `RST` замість коректного закриття `FIN`, незавершені транзакції у базі даних залишаться в невизначеному стані, а буферизовані дані в оперативній пам'яті буде втрачено.

Мета цього проєкту — розробити повнофункціональний, виробничий мережевий координатор коректного завершення (*graceful shutdown*) на базі неблокуючого мультиплексування `epoll` в операційній системі Linux. Координатор повинен бездоганно перехоплювати системні сигнали `SIGTERM` та `SIGINT` через дескриптор `signalfd`, миттєво відсікати прийом нових підключень, надавати активним клієнтам регламентоване часове вікно на завершення передачі даних (*connection draining*), контролювати жорсткий дедлайн за допомогою монотонного таймера `timerfd` і гарантувати безпечне звільнення системних ресурсів.

## Архітектурний дизайн координатора

Координатор побудовано як детермінований автомат скінченних станів (*finite state machine*, FSM), інтегрований у єдиний головний цикл обробки подій (*event loop*). Така архітектура повністю усуває використання ненадійних користувацьких функцій-обробників сигналів, виключаючи будь-які ризики взаємних блокувань у пам'яті (*deadlocks*) або порушення асинхронно-сигнальної безпеки (*async-signal safety*).

```
   [ Ядро Linux: SIGTERM / SIGINT ]
                  │
                  ▼
         [ signalfd (sfd) ] ──(read event)──► [ epoll_wait() ]
                                                      │
                                                      ▼
 ┌────────────────────────────────────────────────────────────────────────┐
 │                    АВТОМАТ СТАНІВ КООРДИНАТОРА                         │
 │                                                                        │
 │   STATE_RUNNING                                                        │
 │        │                                                               │
 │        ├─► [ Отримано сигнал зупинки ]                                 │
 │        ▼                                                               │
 │   STATE_STOPPING                                                       │
 │        │  • epoll_ctl(EPOLL_CTL_DEL, listen_fd) [прийом закрито]       │
 │        │  • arm_watchdog_timer(timer_fd, 5.0s)  [запуск дедлайну]      │
 │        ▼                                                               │
 │   STATE_DRAINING                                                       │
 │        │  • Розсилання службових сповіщень активним клієнтам           │
 │        │  • Очікування завершення передачі даних (read == 0 / EOF)     │
 │        │                                                               │
 │        ├──► [ Усі клієнти від'єдналися до таймауту ] ──► STATE_DONE   │
 │        │                                                    │          │
 │        └──► [ Спрацював timer_fd (5.0s) ] ──────────────► STATE_TIMEOUT│
 │                                                             │          │
 │                                                             ▼          │
 │                                                      [ cleanup & exit ]│
 └────────────────────────────────────────────────────────────────────────┘
```

Життєвий цикл процесу розбито на чотири взаємовиключні фази:

1. **Фаза активного виконання (`STATE_RUNNING`):** Сервер прослуховує вхідний сокет `listen_fd`, реєструє нові клієнтські з'єднання в дереві `epoll` та виконує штатну обробку прикладних запитів.
2. **Фаза перехоплення та відсікання (`STATE_STOPPING`):** При надходженні сигналу ядро записує структуру `signalfd_siginfo` у дескриптор `sfd`. Головний цикл прокидається, негайно вилучає `listen_fd` із дерева `epoll` і закриває його. Нові клієнти більше не можуть під'єднатися (отримують помилку `ECONNREFUSED` на рівні TCP), а балансувальник навантаження фіксує зупинку сервісу.
3. **Фаза дренування робіт (`STATE_DRAINING`):** Сервер продовжує обслуговувати поточні підключення. Одночасно запускається наглядач `timerfd` із таймаутом безпеки (5 секунд). Клієнтам, які надсилають запити, повертається статус завершення сесії `Connection: close`.
4. **Фаза очищення (`STATE_DONE` або `STATE_TIMEOUT`):** Якщо всі клієнти штатно закрили з'єднання, сервер скидає буфери, звільняє дескриптори та повертає ядру код `0`. Якщо таймер безпеки вичерпано, координатор примусово закриває завислі з'єднання, фіксує аварійне попередження у журналі та виходить із кодом `1`, запобігаючи невідворотному знищенню процесу системним сигналом `SIGKILL`.

## Реалізація координатора на C та C++

У системному програмуванні критично розуміти обидві парадигми: пряме керування дескрипторами ядра за допомогою стандартних викликів POSIX C та ідіоматичний сучасний C++20 із застосуванням RAII-обгорток, об'єктно-орієнтованого автомата станів, типу `std::expected` та безпечного управління часом.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 1024
#define SHUTDOWN_TIMEOUT_SEC 5

typedef enum {
    STATE_RUNNING,
    STATE_STOPPING,
    STATE_DRAINING,
    STATE_DONE,
    STATE_TIMEOUT
} server_state_t;

typedef struct {
    int fd;
    char remote_addr[INET_ADDRSTRLEN];
    int remote_port;
} client_conn_t;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

static int create_signalfd(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);

    /* Блокуємо сигнали для всіх потоків процесу */
    if (sigprocmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("sigprocmask");
        return -1;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return -1;
    }
    return sfd;
}

static int create_timerfd(void) {
    int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    if (tfd == -1) {
        perror("timerfd_create");
        return -1;
    }
    return tfd;
}

static int arm_timer(int tfd, int seconds) {
    struct itimerspec its;
    memset(&its, 0, sizeof(its));
    its.it_value.tv_sec = seconds;
    its.it_value.tv_nsec = 0;
    return timerfd_settime(tfd, 0, &its, NULL);
}

static int create_listen_socket(int port) {
    int fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd == -1) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);

    if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, SOMAXCONN) == -1) {
        perror("listen");
        close(fd);
        return -1;
    }
    return fd;
}

int main(int argc, char *argv[]) {
    int port = 8080;
    if (argc > 1) port = atoi(argv[1]);

    printf("[SERVER] Ініціалізація координатора завершення на порту %d...\n", port);

    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) {
        perror("epoll_create1");
        return 1;
    }

    int sig_fd = create_signalfd();
    int timer_fd = create_timerfd();
    int listen_fd = create_listen_socket(port);

    if (sig_fd == -1 || timer_fd == -1 || listen_fd == -1) {
        fprintf(stderr, "[SERVER] Критична помилка ініціалізації дескрипторів\n");
        return 1;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sig_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, sig_fd, &ev);

    ev.events = EPOLLIN;
    ev.data.fd = timer_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, timer_fd, &ev);

    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    client_conn_t clients[MAX_EVENTS];
    for (int i = 0; i < MAX_EVENTS; ++i) clients[i].fd = -1;
    int active_clients = 0;

    server_state_t state = STATE_RUNNING;
    struct epoll_event events[MAX_EVENTS];

    printf("[SERVER] Головний цикл запущено (PID: %d). Очікування з'єднань...\n", getpid());

    while (state != STATE_DONE && state != STATE_TIMEOUT) {
        int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (nfds == -1) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        for (int i = 0; i < nfds; ++i) {
            int cur_fd = events[i].data.fd;

            /* Подія 1: Надходження системного сигналу через signalfd */
            if (cur_fd == sig_fd) {
                struct signalfd_siginfo fdsi;
                ssize_t s = read(sig_fd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    printf("\n[SERVER] Отримано сигнал %d (%s) від PID %d\n",
                           fdsi.ssi_signo,
                           fdsi.ssi_signo == SIGTERM ? "SIGTERM" : "SIGINT",
                           fdsi.ssi_pid);

                    if (state == STATE_RUNNING) {
                        printf("[SERVER] Перехід у режим STOPPING: відсікання нових клієнтів...\n");
                        state = STATE_STOPPING;

                        /* Закриваємо вхідний сокет, щоб не приймати нові з'єднання */
                        epoll_ctl(epfd, EPOLL_CTL_DEL, listen_fd, NULL);
                        close(listen_fd);
                        listen_fd = -1;

                        printf("[SERVER] Запуск таймера дренування на %d секунд...\n", SHUTDOWN_TIMEOUT_SEC);
                        arm_timer(timer_fd, SHUTDOWN_TIMEOUT_SEC);
                        state = STATE_DRAINING;

                        if (active_clients == 0) {
                            printf("[SERVER] Немає активних клієнтів. Завершення миттєве.\n");
                            state = STATE_DONE;
                            break;
                        } else {
                            printf("[SERVER] Очікування завершення %d активних клієнтів...\n", active_clients);
                        }
                    } else if (state == STATE_DRAINING) {
                        printf("[SERVER] Повторний сигнал переривання! Екстрене форсоване завершення.\n");
                        state = STATE_TIMEOUT;
                        break;
                    }
                }
            }
            /* Подія 2: Спрацював сторожовий таймер дедлайну */
            else if (cur_fd == timer_fd) {
                uint64_t expirations;
                read(timer_fd, &expirations, sizeof(expirations));
                printf("[SERVER] ПОМИЛКА: Вичерпано ліміт часу дренування (%d c)!\n", SHUTDOWN_TIMEOUT_SEC);
                printf("[SERVER] Примусове закриття %d завислих клієнтів перед аварійним виходом.\n", active_clients);
                state = STATE_TIMEOUT;
                break;
            }
            /* Подія 3: Новий клієнт під час штатної роботи */
            else if (cur_fd == listen_fd) {
                struct sockaddr_in client_addr;
                socklen_t client_len = sizeof(client_addr);
                int client_fd = accept4(listen_fd, (struct sockaddr*)&client_addr, &client_len,
                                        SOCK_NONBLOCK | SOCK_CLOEXEC);
                if (client_fd != -1) {
                    if (active_clients < MAX_EVENTS) {
                        ev.events = EPOLLIN | EPOLLRDHUP;
                        ev.data.fd = client_fd;
                        epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev);

                        for (int k = 0; k < MAX_EVENTS; ++k) {
                            if (clients[k].fd == -1) {
                                clients[k].fd = client_fd;
                                inet_ntop(AF_INET, &client_addr.sin_addr, clients[k].remote_addr, sizeof(clients[k].remote_addr));
                                clients[k].remote_port = ntohs(client_addr.sin_port);
                                break;
                            }
                        }
                        active_clients++;
                        printf("[CLIENT] Під'єднано нового клієнта (FD: %d, всього: %d)\n", client_fd, active_clients);
                    } else {
                        /* Переповнення черги з'єднань */
                        close(client_fd);
                    }
                }
            }
            /* Подія 4: Передача даних або закриття з'єднання клієнтом */
            else {
                char buf[BUFFER_SIZE];
                ssize_t bytes_read = read(cur_fd, buf, sizeof(buf) - 1);

                if (bytes_read > 0) {
                    buf[bytes_read] = '\0';
                    /* Ехо-відповідь клієнту */
                    const char *resp_prefix = (state == STATE_DRAINING) ? "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n" : "OK: ";
                    write(cur_fd, resp_prefix, strlen(resp_prefix));
                    write(cur_fd, buf, bytes_read);

                    if (state == STATE_DRAINING) {
                        /* Під час дренування відправляємо відповідь і закриваємо запис */
                        shutdown(cur_fd, SHUT_WR);
                    }
                } else {
                    /* read == 0 (EOF) або помилка читання */
                    epoll_ctl(epfd, EPOLL_CTL_DEL, cur_fd, NULL);
                    close(cur_fd);

                    for (int k = 0; k < MAX_EVENTS; ++k) {
                        if (clients[k].fd == cur_fd) {
                            clients[k].fd = -1;
                            break;
                        }
                    }
                    active_clients--;
                    printf("[CLIENT] Клієнт від'єднався (FD: %d, лишилося: %d)\n", cur_fd, active_clients);

                    if (state == STATE_DRAINING && active_clients == 0) {
                        printf("[SERVER] Усі клієнтські сесії успішно дреновано.\n");
                        state = STATE_DONE;
                        break;
                    }
                }
            }
        }
    }

    /* Фаза остаточного вивільнення ресурсів */
    printf("[SERVER] Фаза прибирання: звільнення дескрипторів та скидання буферів...\n");
    for (int i = 0; i < MAX_EVENTS; ++i) {
        if (clients[i].fd != -1) {
            close(clients[i].fd);
            clients[i].fd = -1;
        }
    }

    if (listen_fd != -1) close(listen_fd);
    close(sig_fd);
    close(timer_fd);
    close(epfd);
    fflush(stdout);

    if (state == STATE_DONE) {
        printf("[SERVER] Коректне завершення виконано успішно. Код виходу 0.\n");
        return 0;
    } else {
        fprintf(stderr, "[SERVER] Завершення перервано за таймаутом/форсовано. Код виходу 1.\n");
        return 1;
    }
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
#include <expected>
#include <span>
#include <array>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/signalfd.h>
#include <sys/timerfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace net {

/* RAII-обгортка над файловим дескриптором ядра */
class UniqueFd {
public:
    constexpr UniqueFd() noexcept : fd_(-1) {}
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
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
        int tmp = fd_;
        fd_ = -1;
        return tmp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }

private:
    int fd_;
};

enum class ServerState {
    Running,
    Stopping,
    Draining,
    Done,
    Timeout
};

class GracefulServer {
public:
    explicit GracefulServer(int port, std::chrono::seconds drain_timeout = std::chrono::seconds(5))
        : port_(port), timeout_duration_(drain_timeout), state_(ServerState::Running) {}

    [[nodiscard]] bool initialize() {
        epoll_fd_.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!epoll_fd_.valid()) {
            std::perror("epoll_create1");
            return false;
        }

        auto sfd = setup_signalfd();
        if (!sfd) return false;
        signal_fd_ = std::move(*sfd);

        auto tfd = setup_timerfd();
        if (!tfd) return false;
        timer_fd_ = std::move(*tfd);

        auto lfd = setup_listen_socket();
        if (!lfd) return false;
        listen_fd_ = std::move(*lfd);

        add_to_epoll(signal_fd_.get(), EPOLLIN);
        add_to_epoll(timer_fd_.get(), EPOLLIN);
        add_to_epoll(listen_fd_.get(), EPOLLIN);

        std::cout << "[CPP-SERVER] Ініціалізація завершена. Порт: " << port_
                  << ", PID: " << ::getpid() << '\n';
        return true;
    }

    int run() {
        constexpr size_t max_events = 64;
        std::array<epoll_event, max_events> events{};
        std::array<char, 1024> buffer{};

        while (state_ != ServerState::Done && state_ != ServerState::Timeout) {
            int nfds = ::epoll_wait(epoll_fd_.get(), events.data(), max_events, -1);
            if (nfds == -1) {
                if (errno == EINTR) continue;
                std::perror("epoll_wait");
                break;
            }

            for (int i = 0; i < nfds; ++i) {
                int current_fd = events[i].data.fd;

                if (current_fd == signal_fd_.get()) {
                    handle_signal_event();
                } else if (current_fd == timer_fd_.get()) {
                    handle_timer_timeout();
                } else if (current_fd == listen_fd_.get()) {
                    handle_new_connection();
                } else {
                    handle_client_io(current_fd, buffer);
                }
            }
        }

        return perform_final_cleanup();
    }

private:
    std::expected<UniqueFd, int> setup_signalfd() {
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGTERM);
        sigaddset(&mask, SIGINT);

        if (::pthread_sigmask(SIG_BLOCK, &mask, nullptr) != 0) {
            std::perror("pthread_sigmask");
            return std::unexpected(errno);
        }

        int fd = ::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
        if (fd == -1) {
            std::perror("signalfd");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    std::expected<UniqueFd, int> setup_timerfd() {
        int fd = ::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
        if (fd == -1) {
            std::perror("timerfd_create");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    std::expected<UniqueFd, int> setup_listen_socket() {
        int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
        if (fd == -1) {
            std::perror("socket");
            return std::unexpected(errno);
        }

        int opt = 1;
        ::setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
        addr.sin_port = htons(port_);

        if (::bind(fd, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == -1) {
            std::perror("bind");
            return std::unexpected(errno);
        }

        if (::listen(fd, SOMAXCONN) == -1) {
            std::perror("listen");
            return std::unexpected(errno);
        }
        return UniqueFd(fd);
    }

    void add_to_epoll(int fd, uint32_t events_mask) {
        epoll_event ev{};
        ev.events = events_mask;
        ev.data.fd = fd;
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_ADD, fd, &ev);
    }

    void remove_from_epoll(int fd) {
        ::epoll_ctl(epoll_fd_.get(), EPOLL_CTL_DEL, fd, nullptr);
    }

    void arm_drain_watchdog() {
        itimerspec its{};
        its.it_value.tv_sec = timeout_duration_.count();
        its.it_value.tv_nsec = 0;
        ::timerfd_settime(timer_fd_.get(), 0, &its, nullptr);
    }

    void handle_signal_event() {
        signalfd_siginfo fdsi{};
        ssize_t s = ::read(signal_fd_.get(), &fdsi, sizeof(fdsi));
        if (s != sizeof(fdsi)) return;

        std::cout << "\n[CPP-SERVER] Отримано сигнал " << fdsi.ssi_signo
                  << " від процесу PID " << fdsi.ssi_pid << '\n';

        if (state_ == ServerState::Running) {
            std::cout << "[CPP-SERVER] Початок дренування. Зупинка прийому нових з'єднань...\n";
            state_ = ServerState::Stopping;

            remove_from_epoll(listen_fd_.get());
            listen_fd_.reset(); // Закриття сокету прослуховування

            arm_drain_watchdog();
            state_ = ServerState::Draining;

            if (active_connections_.empty()) {
                std::cout << "[CPP-SERVER] Немає активних сесій. Миттєвий вихід.\n";
                state_ = ServerState::Done;
            } else {
                std::cout << "[CPP-SERVER] Очікування завершення "
                          << active_connections_.size() << " активних з'єднань...\n";
            }
        } else if (state_ == ServerState::Draining) {
            std::cout << "[CPP-SERVER] Повторний сигнал! Форсоване переривання.\n";
            state_ = ServerState::Timeout;
        }
    }

    void handle_timer_timeout() {
        uint64_t expirations = 0;
        ::read(timer_fd_.get(), &expirations, sizeof(expirations));
        std::cerr << "[CPP-SERVER] Таймаут дренування вичерпано! Аварійний скид.\n";
        state_ = ServerState::Timeout;
    }

    void handle_new_connection() {
        sockaddr_in client_addr{};
        socklen_t len = sizeof(client_addr);
        int client_raw = ::accept4(listen_fd_.get(),
                                   reinterpret_cast<sockaddr*>(&client_addr),
                                   &len, SOCK_NONBLOCK | SOCK_CLOEXEC);
        if (client_raw >= 0) {
            add_to_epoll(client_raw, EPOLLIN | EPOLLRDHUP);
            active_connections_.push_back(UniqueFd(client_raw));
            std::cout << "[CPP-CLIENT] Під'єднано клієнта FD " << client_raw
                      << " (всього: " << active_connections_.size() << ")\n";
        }
    }

    void handle_client_io(int client_fd, std::span<char> buf) {
        ssize_t n = ::read(client_fd, buf.data(), buf.size() - 1);
        if (n > 0) {
            buf[n] = '\0';
            std::string_view header = (state_ == ServerState::Draining)
                ? "HTTP/1.1 200 OK\r\nConnection: close\r\n\r\n"
                : "ACK: ";
            ::write(client_fd, header.data(), header.size());
            ::write(client_fd, buf.data(), n);

            if (state_ == ServerState::Draining) {
                ::shutdown(client_fd, SHUT_WR);
            }
        } else {
            remove_from_epoll(client_fd);
            std::erase_if(active_connections_, [client_fd](const UniqueFd& conn) {
                return conn.get() == client_fd;
            });
            std::cout << "[CPP-CLIENT] Сесію FD " << client_fd
                      << " закрито. Залишилося: " << active_connections_.size() << '\n';

            if (state_ == ServerState::Draining && active_connections_.empty()) {
                std::cout << "[CPP-SERVER] Усі клієнти штатно завершили роботу.\n";
                state_ = ServerState::Done;
            }
        }
    }

    int perform_final_cleanup() {
        std::cout << "[CPP-SERVER] Очищення активних ресурсів перед виходом...\n";
        active_connections_.clear(); // RAII закриває всі клієнтські сокети
        listen_fd_.reset();
        signal_fd_.reset();
        timer_fd_.reset();
        epoll_fd_.reset();

        if (state_ == ServerState::Done) {
            std::cout << "[CPP-SERVER] Штатне вимикання завершено успішно (код 0).\n";
            return 0;
        }
        std::cerr << "[CPP-SERVER] Аварійне вимикання через таймаут (код 1).\n";
        return 1;
    }

    int port_;
    std::chrono::seconds timeout_duration_;
    std::atomic<ServerState> state_;
    UniqueFd epoll_fd_;
    UniqueFd signal_fd_;
    UniqueFd timer_fd_;
    UniqueFd listen_fd_;
    std::vector<UniqueFd> active_connections_;
};

} // namespace net

int main(int argc, char* argv[]) {
    int port = (argc > 1) ? std::stoi(argv[1]) : 8080;
    net::GracefulServer server(port);
    if (!server.initialize()) {
        return 1;
    }
    return server.run();
}
```
:::

## Поетапний системний аналіз коду

Розглянемо ключові підсистеми координатора, інваріанти ядра та механізми захисту від збоїв:

### 1. Ініціалізація та блокування сигналів
У функції `create_signalfd()` (та `setup_signalfd()` у C++) критичним є попередній виклик `pthread_sigmask(SIG_BLOCK, &mask, NULL)`. Якщо сигнали `SIGTERM` та `SIGINT` не заблокувати в масці процесу до створення `signalfd`, ядро застосує до них типову диспозицію — миттєве аварійне завершення процесу. Блокування гарантує, що сигнали залишаються у черзі очікування ядра і передаються виключно через файловий дескриптор.

Прапорець `SFD_CLOEXEC` гарантує, що у разі виклику `execve()` дочірнім процесом файловий дескриптор сигналів буде автоматично закрито ядром, що запобігає витоку системних ресурсів у сторонні бінарні файли.

Структура `struct signalfd_siginfo`, яку повертає виклик `read(sig_fd)`, містить багаті метадані ядра:
* `ssi_signo` — числовий ідентифікатор сигналу (15 для `SIGTERM`, 2 для `SIGINT`).
* `ssi_pid` — ідентифікатор процесу, який згенерував системний виклик `kill()`.
* `ssi_uid` — реальний числовий ідентифікатор користувача, від імені якого надіслано команду зупинки.

### 2. Захист від блокування вводу-виводу прапорцем O_NONBLOCK
Усі дескриптори (сокет прослуховування, клієнтські сокети, дескриптори `signalfd` та `timerfd`) обов'язково переводяться в неблокуючий режим за допомогою системного виклику `fcntl(fd, F_SETFL, flags | O_NONBLOCK)` або системного виклику `accept4()` із прапорцем `SOCK_NONBLOCK`.

Це унеможливлює зависання головного циклу: виклики `read()` та `write()` повертають код помилки `EAGAIN` або `EWOULDBLOCK`, якщо буфери сокета переповнені чи порожні, негайно повертаючи керування в `epoll_wait()`.

### 3. Дренування з'єднань та протокол FIN-обміну
Під час фази `STATE_DRAINING` сервер припиняє прийом нових з'єднань, вилучаючи `listen_fd` із дерева `epoll` через `EPOLL_CTL_DEL`. Для вже відкритих клієнтських сокетів після відправки відповіді викликається системний виклик `shutdown(cur_fd, SHUT_WR)`.

Цей системний виклик ініціює відправку службового TCP-сегмента `FIN` у бік клієнта, переводячи стан сокета в ядрі з `ESTABLISHED` у `FIN_WAIT_1`, а після підтвердження ACK від клієнта — у `FIN_WAIT_2`. При цьому сокет залишається відкритим для читання: сервер чекає, поки клієнт прочитає всі надіслані байти та закриє свій бік каналу (перевівши сокет на клієнті в стан `CLOSE_WAIT` -> `LAST_ACK`).

Коли клієнт закриває сесію, виклик `read()` на сервері повертає значення `0` (кінець файлу, EOF). Це слугує тригером для безпечного виклику `close(cur_fd)` та декременту лічильника активних підключень.

### 4. Сторожовий таймер timerfd та монотонний годинник
Для контролю дедлайну застосовується дескриптор `timerfd_create(CLOCK_MONOTONIC, ...)`. Використання годинника `CLOCK_MONOTONIC` є обов'язковою системною вимогою: на відміну від `CLOCK_REALTIME`, монотонний годинник ніколи не зазнає стрибків назад чи вперед при синхронізації системного часу протоколом NTP або зміні часових поясів адміністратором.

Таймер налаштовується одноразово (*one-shot*) на 5 секунд у момент переходу в режим зупинки. Якщо активні клієнти не встигли завершити роботу за цей час, ядро переводить дескриптор `timer_fd` у читабельний стан, що миттєво перериває цикл `epoll_wait()` і форсує перехід автомата в режим аварійного скиду `STATE_TIMEOUT`.

### 5. C++20 RAII та безпечне керування пам'яттю
У версії на C++20 клас `UniqueFd` забезпечує суворе дотримання ідіоми RAII (*Resource Acquisition Is Initialization*). Деструктор `~UniqueFd()` гарантовано закриває дескриптор через `::close()`, навіть якщо під час обробки виникне виняток. Конструктор копіювання заборонено (`= delete`), а конструктор переміщення реалізує семантику володіння, що запобігає повторному закриттю дескрипторів (*double close bug*).

Тип `std::expected<UniqueFd, int>` впроваджує монадичну обробку помилок: системні виклики повертають або валідний дескриптор, або числовий код помилки `errno`, усуваючи накладні витрати на генерацію винятків C++ у критичних шляхах ініціалізації.

Використання `std::span<char>` та `std::string_view` дозволяє передавати буфери та заголовки протоколів без жодного динамічного виділення пам'яті в купі (`heap allocation`), що гарантує максимальну швидкодію та нульову фрагментацію пам'яті.

### 6. Порівняння тригерів epoll: Level-Triggered проти Edge-Triggered під час зупинки
У нашому координаторі дескриптори реєструються у стандартному рівневому режимі (Level-Triggered, LT). Це критично для надійності вимикання:
* Якщо під час фази дренування в буфері сокета залишаються непрочитані байти або невідправлені відповіді, ядро продовжує генерувати подію готовності `EPOLLIN` або `EPOLLOUT` на кожній ітерації `epoll_wait()`.
* У крайовому режимі (Edge-Triggered, ET) подія генерується лише при зміні стану (перехід від порожнього буфера до непорожнього). Якщо координатор не вичитає всі байти до повернення `EAGAIN` за один прохід, у режимі ET він ніколи не отримає повторного сповіщення, що призведе до мертвого зависання дренування та аварійного спрацьовування таймера безпеки.

### 7. Безпека повторного використання портів (SO_REUSEADDR)
При створенні сокета прослуховування використовується опція `setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))`.

Коли сервер закриває з'єднання з клієнтом першим (активне закриття), сокет на стороні ядра переходить у стан `TIME_WAIT` тривалістю 60 секунд (два інтервали `2 * MSL`, Maximum Segment Lifetime) для гарантії того, що запізнілі дублікати пакетів не порушать нову сесію. Без опції `SO_REUSEADDR` спроба негайно перезапустити сервіс на тому самому порту призвела б до системної помилки `bind: Address already in use`.

## Практична верифікація та лабораторні тести

Перевірку працездатності координатора та стійкості до крайових станів проводять у терміналі за допомогою стандартних утиліт Linux:

### Тест 1: Перевірка штатного дренування (Graceful Success)

У першому терміналі збираємо та запускаємо C-сервер:
```bash
gcc -O2 -Wall -Wextra -std=gnu11 graceful_server.c -o graceful_server
./graceful_server 8080
```

У другому терміналі емулюємо підключення повільного клієнта за допомогою `nc` (netcat):
```bash
nc 127.0.0.1 8080
```

У третьому терміналі надсилаємо серверу системний сигнал зупинки:
```bash
kill -TERM $(pgrep graceful_server)
```

**Очікуваний результат у першому терміналі:**
Сервер повідомляє про перехоплення `SIGTERM`, закриває сокет прослуховування, запускає таймер дренування на 5 секунд та очікує від'єднання клієнта. Щойно у другому терміналі клієнт надсилає повідомлення або натискає `Ctrl-D`, сервер миттєво завершує роботу з кодом `0`.

### Тест 2: Перевірка аварійного таймауту Watchdog

1. Запускаємо сервер: `./graceful_server 8080`
2. Під'єднуємо клієнта: `nc 127.0.0.1 8080`
3. Надсилаємо сигнал: `kill -TERM $(pgrep graceful_server)`
4. Утримуємо клієнтське з'єднання відкритим, не надсилаючи жодних даних.

**Очікуваний результат:**
Рівно через 5.0 секунд спрацьовує дескриптор `timerfd`. Сервер виводить повідомлення про вичерпання ліміту часу, примусово розриває клієнтську сесію, скидає буфери та завершується з кодом помилки `1`, не чекаючи зовнішнього вбивства сигналом `SIGKILL`.

### Тест 3: Перевірка форсованого подвійного сигналу (Double-Signal Escalation)

1. Запускаємо сервер в інтерактивному режимі: `./graceful_server 8080`
2. Під'єднуємо клієнта: `nc 127.0.0.1 8080`
3. У терміналі сервера натискаємо `Ctrl-C` один раз — сервер переходить у режим дренування.
4. Не чекаючи 5 секунд, негайно тиснемо `Ctrl-C` вдруге.

**Очікуваний результат:**
Координатор фіксує повторний `SIGINT`, негайно скасовує фазу дренування, закриває сокети та миттєво повертає керування командній оболонці з кодом `1`.

### Тест 4: Навантажувальне тестування під час ротації (Zero-Downtime Bench)

За допомогою утиліти `wrk` або `ab` (Apache Bench) генеруємо безперервний потік із 1000 паралельних HTTP-запитів на секунду:
```bash
wrk -t4 -c100 -d30s http://127.0.0.1:8080/
```

Під час генерації навантаження надсилаємо серверу `kill -TERM`. Завдяки коректному протоколу дренування та відправці `Connection: close` утиліта фіксує рівно 0 помилок з'єднання (*Zero Socket Errors*): усі активні запити отримують код 200, після чого клієнти штатно закривають сесії.

## Пакетний аналіз TCP: FIN-рукостискання проти аварійного RST

Щоб наочно побачити різницю між коректним вимиканням та аварійним падінням процесу на мережевому рівні, простежимо системний дамп пакетів за допомогою утиліти `tcpdump -nn -vvv -i lo port 8080`:

### Штатний чотиристоронній обмін закриття TCP (FIN Handshake):

```
14:20:01.100 IP 127.0.0.1.8080 > 127.0.0.1.54321: Flags [P.], seq 1:45, ack 1 [HTTP 200 OK, Connection: close]
14:20:01.101 IP 127.0.0.1.54321 > 127.0.0.1.8080: Flags [.], ack 45, win 512
14:20:01.102 IP 127.0.0.1.8080 > 127.0.0.1.54321: Flags [F.], seq 45, ack 1  [Сервер: shutdown(SHUT_WR) -> FIN]
14:20:01.103 IP 127.0.0.1.54321 > 127.0.0.1.8080: Flags [.], ack 46, win 512 [Клієнт підтверджує FIN]
14:20:01.105 IP 127.0.0.1.54321 > 127.0.0.1.8080: Flags [F.], seq 1, ack 46  [Клієнт закриває свій бік -> FIN]
14:20:01.106 IP 127.0.0.1.8080 > 127.0.0.1.54321: Flags [.], ack 2, win 512  [Сервер підтверджує -> сесію закрито]
```

При такому обміні клієнтська бібліотека отримує всі надіслані байти, фіксує кінець потоку (EOF) і завершує обробку відповіді без жодної помилки.

### Аварійне закриття без дренування (Аварійний скид RST):

```
14:20:01.100 IP 127.0.0.1.54321 > 127.0.0.1.8080: Flags [P.], seq 1:120 [Клієнт відправляє тіло запиту]
14:20:01.101 IP 127.0.0.1.8080 > 127.0.0.1.54321: Flags [R], seq 1001    [Ядро надсилає TCP RST!]
```

Якщо процес убито сигналом `SIGKILL` або якщо `close(fd)` викликано за наявності непрочитаних вхідних байтів у черзі прийому сокета (`receive buffer`), стек TCP ядра Linux генерує прапорець `Flags [R]` (Reset). Клієнтська програма негайно отримує системну помилку `read: Connection reset by peer` (`ECONNRESET`), запит переривається, а дані втрачаються.

## Керування таблицею дескрипторів та успадкування у fork/exec

У складних сервісах, які під час роботи породжують дочірні процеси (наприклад, для виконання зовнішніх перетворювачів файлів, стиснення або генерації звітів), особливу небезпеку становить неконтрольований витік файлових дескрипторів.

Коли процес викликає `fork()`, новостворений дочірній процес отримує повну копію таблиці відкритих файлових дескрипторів батька:
1. Якщо дескриптор `listen_fd` або клієнтський сокет не мають прапорця `O_CLOEXEC` (`SOCK_CLOEXEC`), після виклику дочірнім процесом функції `execve()` ці дескриптори залишаться відкритими у новому бінарному образі.
2. Навіть якщо головний координатор виконає `close(listen_fd)`, лічильник посилань на файлову структуру `struct file` у ядрі не зменшиться до нуля, оскільки дескриптор продовжує утримуватися стороннім дочірнім процесом.
3. Як наслідок, порт прослуховування залишається зайнятим у ядрі, а віддалені клієнти продовжують установлювати TCP-з'єднання, які ніхто не вичитує, що повністю руйнує процедуру зупинки сервісу.

Використання викликів `epoll_create1(EPOLL_CLOEXEC)`, `accept4(..., SOCK_CLOEXEC)` та `signalfd(..., SFD_CLOEXEC)` у нашій реалізації є фундаментальною гарантією ізоляції дескрипторів.

## Виробниче розгортання під керуванням systemd

Для промислової експлуатації координатора створюється unit-файл `/etc/systemd/system/graceful-server.service`:

```ini
[Unit]
Description=Graceful Production TCP Coordinator
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/graceful_server 8080
TimeoutStopSec=10s
KillMode=control-group
KillSignal=SIGTERM
SendSIGKILL=yes
Restart=on-failure
RestartSec=2s

[Install]
WantedBy=multi-user.target
```

При виконанні команди `systemctl stop graceful-server` менеджер systemd передає процесу `SIGTERM` і надає регламентовані 10 секунд на повне дренування з'єднань. Координатор завершує всі активні сесії за 2-3 секунди і робить виклик `exit(0)`. systemd реєструє чисту деактивацію служби без жодного аварійного скидання.

## Розширення для багатопотокових пулів воркерів

У серверах із моделлю «один цикл подій — багато робочих потоків» (*Reactor-Worker Pool Pattern*) головний координатор розширюється за допомогою дескрипторів `eventfd`:

1. Головний потік приймає з'єднання в `epoll`, а важкі обчислення передає пулу потоків через потокобезпечну чергу.
2. При надходженні `SIGTERM` головний потік переводить глобальний атомарний прапорець `g_stopping = true` та надсилає сигнал пробудження всім потокам пулу через системний виклик `eventfd_write(worker_event_fd, 1)`.
3. Кожен потік пулу доопрацьовує поточну задачу, фіксує стан `stop_requested()` і завершує виконання.
4. Головний координатор виконує `pthread_join()` для всіх воркерів і лише після цього здійснює фінальне закриття сокетів.

Така багаторівнева модель повністю усуває стан гонитви, коли потік намагається відправити відповідь у сокет, який головний потік уже закрив через `close()`.

## Порівняння signalfd з pselect та ppoll

До появи `signalfd` у ядрі Linux (версія 2.6.22) єдиним стандартизованим способом уникнути стану гонитви між перевіркою прапорця сигналу та блокуючим викликом мультиплексування були системні виклики `pselect()` та `ppoll()`:

1. `pselect()` приймає маску сигналів `sigmask`, атомарно замінюючи поточну маску процесу на час очікування подій на дескрипторах.
2. Якщо сигнал надходить під час блокування, ядро тимчасово розблоковує сигнал, виконує користувацький обробник `sa_handler`, а системний виклик переривається з помилкою `EINTR`.
3. Після повернення ядро автоматично відновлює вихідну маску сигналів.

Проте механізм `pselect`/`ppoll` має два принципові недоліки:
* **Асинхронний контекст:** Обробка сигналу все одно змушена відбуватися всередині `sa_handler`, що накладає суворі обмеження асинхронно-сигнальної безпеки.
* **Масштабованість:** Виклики `pselect` та `ppoll` мають складність `O(N)` від кількості дескрипторів, що неприпустимо для серверів із десятками тисяч підключень.

Інтерфейс `signalfd` у поєднанні з `epoll` (`O(1)`) повністю усуває ці обмеження, надаючи сучасний, швидкий та абсолютно потокобезпечний стандарт обробки життєвого циклу. Оскільки маска заблокованих сигналів автоматично успадковується всіма потоками, створеними через `pthread_create()` або `std::jthread`, архітектура гарантує цілковиту відсутність випадкових переривань у будь-якій підсистемі процесу.

## Архітектурний висновок

Виробничий координатор коректного завершення на базі `signalfd`, неблокуючого `epoll` та `timerfd` демонструє канонічний підхід системного програмування Unix:
* Сигнали ядра повністю демілітаризовані та перетворені на звичайні дескрипторні потоки байтів.
* Усунуто будь-яку потребу в небезпечних асинхронних функціях-обробниках.
* Забезпечено повний контроль над дедлайнами за допомогою монотонних апаратних таймерів.
* Гарантовано відсутність витоків пам'яті, незакритих сокетів та аварійних помилок у клієнтів під час планових оновлень програмного забезпечення.

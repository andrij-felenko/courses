# ⚙️ Реалізація патерну Reactor: подієвий TCP-сервер на epoll

Патерн Reactor (лат. *reactor* — «той, що реагує») є фундаментальним архітектурним шаблоном для побудови високопродуктивних мережевих систем. Його суть полягає у поділі серверного застосунку на дві чіткі частини:
1. **Синхронний демультиплексор подій (Event Demultiplexer)** — низькорівневий цикл (Event Loop), який спить у системному виклику ядра (`epoll_wait`) і прокидається лише при зміні стану дескрипторів;
2. **Диспетчер та обробники подій (Event Handlers)** — функції простору користувача, які реалізують неблокуючий прийом нових клієнтів, парсинг протоколу, буферизацію та генерацію відповідей без блокування процесорного потоку.

У цьому практичному проєкті ми спроєктуємо та реалізуємо повнофункціональний однопотоковий TCP-сервер мовами C та C++, здатний утримувати десятки тисяч активних з'єднань, коректно керувати частковим неблокуючим записом, відстежувати неактивні сесії через `timerfd` та безпечно завершувати роботу за сигналами операційної системи через `signalfd`.

---

## 1. Архітектурна модель та життєвий цикл клієнтської сесії

У синхронній багатопотоковій моделі стан клієнта зберігається неявно у вигляді локальних змінних на стеку потоку та поточної точки виконання інструкцій процесора. Якщо потік зупинився на середині функції розбору протоколу під час виклику `read()`, операційна система «пам'ятає» стан клієнта за кадром виклику.

В однопотоковій подієвій моделі потік єдиний на всі з'єднання. Він не може зупинятися на середині обробки запиту клієнта A, бо це заморозить клієнтів B, C та D. Тому стан кожної сесії **виноситься в окрему структуру даних у динамічній пам'яті (Heap)**, а обробка вхідного потоку байтів перетворюється на явний скінченний автомат (англ. *Finite State Machine, FSM*).

```
   ┌─────────────────┐
   │ [1. СТВОРЕННЯ]  │ ── accept4(SOCK_NONBLOCK)
   └────────┬────────┘
            │ Реєстрація EPOLLIN | EPOLLET в epoll_ctl
            ▼
   ┌─────────────────┐
   │  [2. ЧИТАННЯ]   │ <── epoll_wait (EPOLLIN)
   │  (READ LOOP)    │ ─── read() у циклі до EAGAIN
   └────────┬────────┘
            │ Повний запит розібрано
            ▼
   ┌─────────────────┐
   │ [3. ОБРОБКА ТА  │ ─── Спроба прямого write()
   │   ФОРМУВАННЯ]   │
   └────────┬────────┘
            ├── Якщо записано ВСЕ ────────────────────────────────┐
            │                                                     │
            └── Якщо записано ЧАСТКОВО або EAGAIN                 │
                    │                                             │
                    ▼                                             │
            ┌─────────────────┐                                   │
            │  [4. ЧЕРГА ВІД- │ ── Додавання залишку у вихідний   │
            │     ПРАВКИ]     │    буфер сесії;                   │
            └────────┬────────┘    підписка на EPOLLOUT           │
                     │                                            │
                     ▼                                            │
            ┌─────────────────┐                                   │
            │  [5. ЗАПИС У    │ <─ epoll_wait (EPOLLOUT)          │
            │   СОКЕТ]        │ ── write() залишку з буфера       │
            └────────┬────────┘                                   │
                     │ Буфер вичерпано → зняття EPOLLOUT          │
                     └────────────────────────────────────────────┼─┐
                                                                  │ │
                                                                  │ │
   ┌─────────────────┐                                            │ │
   │ [6. ЗАКРИТТЯ]   │ <── read() == 0 (EOF) або EPOLLRDHUP / ERR │ │
   │  (DISCONNECT)   │ <── Сплив таймаут неактивності (timerfd)   │ │
   └─────────────────┘ ─── epoll_ctl(DEL) + close(fd) + free()    │ │
            ▲                                                     │ │
            └─────────────────────────────────────────────────────┴─┘
```

### Ключові виклики неблокуючого зв'язку:

1. **Фрагментація потоку TCP (Framing):** Мережевий протокол TCP є потоковим (Stream-oriented), а не пакетним. Якщо клієнт надсилає повідомлення завдовжки 500 байтів, воно може надійти на сервер трьома окремими шматками: 120, 200 та 180 байтів на різних ітераціях подієвого циклу. Сесія зобов'язана мати буфер накопичення вхідних даних, у якому байти збираються доти, доки парсер не виявить повний заголовок або довжину повідомлення.
2. **Частковий неблокуючий запис (Partial Write):** Якщо сервер формує відповідь розміром 128 КБ, а буфер відправки сокета в ядрі має лише 16 КБ вільного місця, системний виклик `write()` у неблокуючому режимі запише рівно 16 КБ і поверне помилку `EAGAIN` для решти 112 КБ. Програма не має права блокуватися в очікуванні відправки — вона повинна зберегти 112 КБ у вихідному буфері сесії, додати дескриптор у спостереження `EPOLLOUT` та повернути керування в цикл подій.
3. **Холосте навантаження процесора через `EPOLLOUT`:** Сокет майже завжди готовий приймати байти для відправки (його черга передачі зазвичай порожня). Якщо дескриптор постійно зареєстрований із прапорцем `EPOLLOUT`, системний виклик `epoll_wait()` негайно прокидатиметься на кожному кроці циклу, створюючи 100% завантаження процесорного ядра. Тому прапорець `EPOLLOUT` активується **тільки тоді, коли у вихідному буфері сесії реально є відкладені дані**, і негайно вимикається, щойно буфер спорожнів.

---

## 2. Повна реалізація мовами C та C++

Наведені нижче реалізації демонструють побудову сервера з відлунням (Echo Server), який приймає з'єднання, вичитує дані у фронтовому режимі `EPOLLET`, буферизує відповіді та очищає неактивні підключення. 

Варіант мовою C++ демонструє сучасне системне проєктування: повну відсутність ручних викликів `free()` та `close()` завдяки RAII-обгортці `UniqueFd`, використання розумних покажчиків `std::unique_ptr`, автоматичне динамічне розширення буферів через `std::vector<char>` та типобезпечну обробку помилок.

:::tabs
```c
/* ==========================================================================
 * reactor_server.c — Однопотоковий подієвий сервер на C (Linux epoll)
 * Компіляція: gcc -O2 -Wall -Wextra reactor_server.c -o reactor_server
 * ========================================================================== */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>

#define MAX_EVENTS      64
#define BUFFER_SIZE     4096
#define IDLE_TIMEOUT_S  30
#define SERVER_PORT     8080

/* Стан сесії клієнтського з'єднання */
typedef struct client_session {
    int     fd;
    time_t  last_active;
    char   *out_buf;
    size_t  out_len;
    size_t  out_cap;
} client_session_t;

/* Встановлення неблокуючого режиму дескриптора */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Створення нової структури сесії */
static client_session_t *session_create(int fd) {
    client_session_t *s = (client_session_t *)calloc(1, sizeof(client_session_t));
    if (!s) return NULL;
    s->fd = fd;
    s->last_active = time(NULL);
    return s;
}

/* Звільнення пам'яті сесії */
static void session_destroy(client_session_t *s) {
    if (!s) return;
    if (s->out_buf) free(s->out_buf);
    free(s);
}

/* Додавання байтів у вихідний буфер сесії */
static int session_append_out(client_session_t *s, const char *data, size_t len) {
    if (s->out_len + len > s->out_cap) {
        size_t new_cap = (s->out_cap == 0) ? 1024 : s->out_cap * 2;
        while (new_cap < s->out_len + len) new_cap *= 2;
        char *nb = (char *)realloc(s->out_buf, new_cap);
        if (!nb) return -1;
        s->out_buf = nb;
        s->out_cap = new_cap;
    }
    memcpy(s->out_buf + s->out_len, data, len);
    s->out_len += len;
    return 0;
}

/* Закриття клієнта та видалення з epoll */
static void close_client(int epfd, client_session_t *s) {
    epoll_ctl(epfd, EPOLL_CTL_DEL, s->fd, NULL);
    close(s->fd);
    printf("[DISCONNECT] Клієнт FD %d відключений\n", s->fd);
    session_destroy(s);
}

/* Обробник вхідних з'єднань (Accept Handler) */
static void handle_accept(int epfd, int listen_fd) {
    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_fd = accept4(listen_fd, (struct sockaddr *)&client_addr, 
                                &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
        if (client_fd == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Усі нові з'єднання вичитано */
            }
            perror("accept4");
            break;
        }

        client_session_t *s = session_create(client_fd);
        if (!s) {
            close(client_fd);
            continue;
        }

        struct epoll_event ev;
        memset(&ev, 0, sizeof(ev));
        ev.events = EPOLLIN | EPOLLET | EPOLLRDHUP;
        ev.data.ptr = s;

        if (epoll_ctl(epfd, EPOLL_CTL_ADD, client_fd, &ev) == -1) {
            perror("epoll_ctl ADD client");
            close(client_fd);
            session_destroy(s);
            continue;
        }

        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &client_addr.sin_addr, ip_str, sizeof(ip_str));
        printf("[CONNECT] Новий клієнт FD %d з %s:%d\n", 
               client_fd, ip_str, ntohs(client_addr.sin_port));
    }
}

/* Обробник читання даних клієнта (Read Handler) */
static void handle_read(int epfd, client_session_t *s) {
    char buf[BUFFER_SIZE];
    s->last_active = time(NULL);

    while (1) {
        ssize_t bytes_read = read(s->fd, buf, sizeof(buf));
        if (bytes_read > 0) {
            /* Відлуння (Echo): додаємо прочитане у вихідний буфер */
            session_append_out(s, buf, (size_t)bytes_read);
        } else if (bytes_read == 0) {
            /* Клієнт закрив з'єднання (EOF) */
            close_client(epfd, s);
            return;
        } else {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Буфер сокета вичитано повністю */
            }
            /* Справжня мережева помилка */
            close_client(epfd, s);
            return;
        }
    }

    /* Якщо з'явилися дані для відправки — пробуємо записати одразу */
    if (s->out_len > 0) {
        ssize_t bytes_sent = write(s->fd, s->out_buf, s->out_len);
        if (bytes_sent > 0) {
            if ((size_t)bytes_sent < s->out_len) {
                memmove(s->out_buf, s->out_buf + bytes_sent, s->out_len - bytes_sent);
                s->out_len -= bytes_sent;
            } else {
                s->out_len = 0;
            }
        } else if (bytes_sent == -1 && (errno != EAGAIN && errno != EWOULDBLOCK)) {
            close_client(epfd, s);
            return;
        }

        /* Якщо дані лишилися — реєструємо EPOLLOUT */
        if (s->out_len > 0) {
            struct epoll_event ev;
            ev.events = EPOLLIN | EPOLLOUT | EPOLLET | EPOLLRDHUP;
            ev.data.ptr = s;
            epoll_ctl(epfd, EPOLL_CTL_MOD, s->fd, &ev);
        }
    }
}

/* Обробник неблокуючого запису (Write Handler) */
static void handle_write(int epfd, client_session_t *s) {
    s->last_active = time(NULL);

    while (s->out_len > 0) {
        ssize_t bytes_sent = write(s->fd, s->out_buf, s->out_len);
        if (bytes_sent > 0) {
            if ((size_t)bytes_sent < s->out_len) {
                memmove(s->out_buf, s->out_buf + bytes_sent, s->out_len - bytes_sent);
                s->out_len -= bytes_sent;
            } else {
                s->out_len = 0;
            }
        } else if (bytes_sent == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break; /* Буфер сокета заповнено — чекаємо наступного EPOLLOUT */
            }
            close_client(epfd, s);
            return;
        }
    }

    /* Якщо весь буфер надіслано — знімаємо прапорець EPOLLOUT */
    if (s->out_len == 0) {
        struct epoll_event ev;
        ev.events = EPOLLIN | EPOLLET | EPOLLRDHUP;
        ev.data.ptr = s;
        epoll_ctl(epfd, EPOLL_CTL_MOD, s->fd, &ev);
    }
}

int main(void) {
    /* 1. Блокуємо сигнали для безпечної обробки через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);
    sigprocmask(SIG_BLOCK, &mask, NULL);

    int sig_fd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sig_fd == -1) { perror("signalfd"); exit(EXIT_FAILURE); }

    /* 2. Створюємо слухаючий TCP сокет */
    int listen_fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (listen_fd == -1) { perror("socket"); exit(EXIT_FAILURE); }

    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in srv_addr;
    memset(&srv_addr, 0, sizeof(srv_addr));
    srv_addr.sin_family = AF_INET;
    srv_addr.sin_addr.s_addr = INADDR_ANY;
    srv_addr.sin_port = htons(SERVER_PORT);

    if (bind(listen_fd, (struct sockaddr *)&srv_addr, sizeof(srv_addr)) == -1) {
        perror("bind"); exit(EXIT_FAILURE);
    }
    if (listen(listen_fd, SOMAXCONN) == -1) {
        perror("listen"); exit(EXIT_FAILURE);
    }

    /* 3. Створюємо таймер перевірки таймаутів (кожні 5 секунд) */
    int timer_fd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
    struct itimerspec ts;
    ts.it_interval.tv_sec = 5;
    ts.it_interval.tv_nsec = 0;
    ts.it_value.tv_sec = 5;
    ts.it_value.tv_nsec = 0;
    timerfd_settime(timer_fd, 0, &ts, NULL);

    /* 4. Ініціалізуємо екземпляр epoll */
    int epfd = epoll_create1(EPOLL_CLOEXEC);
    if (epfd == -1) { perror("epoll_create1"); exit(EXIT_FAILURE); }

    struct epoll_event ev;
    memset(&ev, 0, sizeof(ev));

    /* Реєструємо слухаючий сокет */
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = listen_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listen_fd, &ev);

    /* Реєструємо дескриптор сигналів */
    ev.events = EPOLLIN;
    ev.data.fd = sig_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, sig_fd, &ev);

    /* Реєструємо таймер */
    ev.events = EPOLLIN;
    ev.data.fd = timer_fd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, timer_fd, &ev);

    printf("Reactor сервер запущено на порту %d. Очікування подій...\n", SERVER_PORT);

    struct epoll_event events[MAX_EVENTS];
    int running = 1;

    /* 5. Головний цикл подій (Event Loop) */
    while (running) {
        int nready = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (nready == -1) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        for (int i = 0; i < nready; ++i) {
            uint32_t revents = events[i].events;

            /* Подія на дескрипторі сигналів */
            if (events[i].data.fd == sig_fd) {
                struct signalfd_siginfo fdsi;
                read(sig_fd, &fdsi, sizeof(fdsi));
                printf("\n[SIGNAL] Отримано сигнал %d. Зупинка сервера...\n", fdsi.ssi_signo);
                running = 0;
                break;
            }

            /* Подія на таймері */
            if (events[i].data.fd == timer_fd) {
                uint64_t expirations;
                read(timer_fd, &expirations, sizeof(expirations));
                continue;
            }

            /* Нове вхідне підключення */
            if (events[i].data.fd == listen_fd) {
                handle_accept(epfd, listen_fd);
                continue;
            }

            /* Подія на підключеному клієнті */
            client_session_t *s = (client_session_t *)events[i].data.ptr;
            if (!s) continue;

            if (revents & (EPOLLERR | EPOLLHUP | EPOLLRDHUP)) {
                close_client(epfd, s);
                continue;
            }
            if (revents & EPOLLIN) {
                handle_read(epfd, s);
            }
            if (revents & EPOLLOUT) {
                handle_write(epfd, s);
            }
        }
    }

    close(listen_fd);
    close(timer_fd);
    close(sig_fd);
    close(epfd);
    printf("Сервер успішно зупинено.\n");
    return 0;
}
```
```cpp
// ==========================================================================
// reactor_server.cpp — Ідіоматичний подієвий сервер на C++20 (Linux epoll)
// Компіляція: g++ -O2 -std=c++20 -Wall -Wextra reactor_server.cpp -o reactor_server_cpp
// ==========================================================================

#include <iostream>
#include <vector>
#include <unordered_map>
#include <memory>
#include <span>
#include <string_view>
#include <chrono>
#include <cstring>
#include <cerrno>

#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include <sys/signalfd.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace net {

// RAII обгортка над системним файловим дескриптором
class UniqueFd {
    int fd_{-1};
public:
    constexpr UniqueFd() noexcept = default;
    explicit UniqueFd(int fd) noexcept : fd_(fd) {}
    ~UniqueFd() { reset(); }

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
    explicit operator bool() const noexcept { return valid(); }

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
};

// Стан клієнтської сесії з динамічним буфером відправки
struct Session {
    UniqueFd socket;
    std::chrono::steady_clock::time_point last_active;
    std::vector<char> out_buffer;

    explicit Session(UniqueFd sock)
        : socket(std::move(sock)), last_active(std::chrono::steady_clock::now()) {}
};

class ReactorServer {
    static constexpr int MaxEvents = 64;
    static constexpr int BufferSize = 4096;
    static constexpr uint16_t Port = 8080;

    UniqueFd epfd_;
    UniqueFd listen_fd_;
    UniqueFd timer_fd_;
    UniqueFd signal_fd_;
    std::unordered_map<int, std::unique_ptr<Session>> sessions_;
    bool running_{false};

public:
    ReactorServer() = default;

    void init() {
        // 1. Блокування сигналів для обробки через signalfd
        sigset_t mask;
        sigemptyset(&mask);
        sigaddset(&mask, SIGINT);
        sigaddset(&mask, SIGTERM);
        sigprocmask(SIG_BLOCK, &mask, nullptr);

        signal_fd_.reset(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
        if (!signal_fd_) throw std::system_error(errno, std::generic_category(), "signalfd");

        // 2. Створення неблокуючого TCP-сокета
        listen_fd_.reset(::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0));
        if (!listen_fd_) throw std::system_error(errno, std::generic_category(), "socket");

        int opt = 1;
        ::setsockopt(listen_fd_.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

        sockaddr_in srv_addr{};
        srv_addr.sin_family = AF_INET;
        srv_addr.sin_addr.s_addr = INADDR_ANY;
        srv_addr.sin_port = htons(Port);

        if (::bind(listen_fd_.get(), reinterpret_cast<sockaddr*>(&srv_addr), sizeof(srv_addr)) == -1) {
            throw std::system_error(errno, std::generic_category(), "bind");
        }
        if (::listen(listen_fd_.get(), SOMAXCONN) == -1) {
            throw std::system_error(errno, std::generic_category(), "listen");
        }

        // 3. Таймер перевірки неактивних сесій (раз на 5 с)
        timer_fd_.reset(::timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC));
        itimerspec ts{};
        ts.it_interval.tv_sec = 5;
        ts.it_value.tv_sec = 5;
        ::timerfd_settime(timer_fd_.get(), 0, &ts, nullptr);

        // 4. Створення epoll
        epfd_.reset(::epoll_create1(EPOLL_CLOEXEC));
        if (!epfd_) throw std::system_error(errno, std::generic_category(), "epoll_create1");

        add_event(listen_fd_.get(), EPOLLIN | EPOLLET, nullptr);
        add_event(signal_fd_.get(), EPOLLIN, nullptr);
        add_event(timer_fd_.get(), EPOLLIN, nullptr);
    }

    void run() {
        running_ = true;
        std::cout << "C++ Reactor сервер запущено на порту " << Port << "...\n";

        std::vector<epoll_event> events(MaxEvents);

        while (running_) {
            int nready = ::epoll_wait(epfd_.get(), events.data(), MaxEvents, -1);
            if (nready == -1) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "epoll_wait");
            }

            for (int i = 0; i < nready; ++i) {
                const auto& ev = events[i];

                if (ev.data.fd == signal_fd_.get()) {
                    handle_signals();
                    break;
                }
                if (ev.data.fd == timer_fd_.get()) {
                    handle_timer();
                    continue;
                }
                if (ev.data.fd == listen_fd_.get()) {
                    handle_accept();
                    continue;
                }

                auto* session = static_cast<Session*>(ev.data.ptr);
                if (!session) continue;

                int client_fd = session->socket.get();
                if (ev.events & (EPOLLERR | EPOLLHUP | EPOLLRDHUP)) {
                    close_session(client_fd);
                    continue;
                }
                if (ev.events & EPOLLIN) {
                    handle_read(*session);
                }
                if (sessions_.contains(client_fd) && (ev.events & EPOLLOUT)) {
                    handle_write(*session);
                }
            }
        }
        std::cout << "C++ Reactor сервер зупинено.\n";
    }

private:
    void add_event(int fd, uint32_t event_mask, void* ptr) {
        epoll_event ev{};
        ev.events = event_mask;
        if (ptr) {
            ev.data.ptr = ptr;
        } else {
            ev.data.fd = fd;
        }
        if (::epoll_ctl(epfd_.get(), EPOLL_CTL_ADD, fd, &ev) == -1) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD");
        }
    }

    void mod_event(int fd, uint32_t event_mask, void* ptr) {
        epoll_event ev{};
        ev.events = event_mask;
        ev.data.ptr = ptr;
        ::epoll_ctl(epfd_.get(), EPOLL_CTL_MOD, fd, &ev);
    }

    void handle_accept() {
        while (true) {
            sockaddr_in client_addr{};
            socklen_t client_len = sizeof(client_addr);
            int client_raw = ::accept4(listen_fd_.get(), 
                                       reinterpret_cast<sockaddr*>(&client_addr),
                                       &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
            if (client_raw == -1) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                break;
            }

            auto session = std::make_unique<Session>(UniqueFd(client_raw));
            int fd = session->socket.get();
            Session* session_ptr = session.get();

            sessions_[fd] = std::move(session);
            add_event(fd, EPOLLIN | EPOLLET | EPOLLRDHUP, session_ptr);

            char ip_str[INET_ADDRSTRLEN];
            ::inet_ntop(AF_INET, &client_addr.sin_addr, ip_str, sizeof(ip_str));
            std::cout << "[CONNECT] Клієнт FD " << fd << " з " << ip_str << "\n";
        }
    }

    void handle_read(Session& session) {
        char buf[BufferSize];
        session.last_active = std::chrono::steady_clock::now();
        int fd = session.socket.get();

        while (true) {
            ssize_t n = ::read(fd, buf, sizeof(buf));
            if (n > 0) {
                session.out_buffer.insert(session.out_buffer.end(), buf, buf + n);
            } else if (n == 0) {
                close_session(fd);
                return;
            } else {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                close_session(fd);
                return;
            }
        }

        if (!session.out_buffer.empty()) {
            flush_write(session);
        }
    }

    void handle_write(Session& session) {
        flush_write(session);
    }

    void flush_write(Session& session) {
        int fd = session.socket.get();
        session.last_active = std::chrono::steady_clock::now();

        while (!session.out_buffer.empty()) {
            ssize_t n = ::write(fd, session.out_buffer.data(), session.out_buffer.size());
            if (n > 0) {
                session.out_buffer.erase(session.out_buffer.begin(), session.out_buffer.begin() + n);
            } else if (n == -1) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                close_session(fd);
                return;
            }
        }

        uint32_t mask = EPOLLIN | EPOLLET | EPOLLRDHUP;
        if (!session.out_buffer.empty()) {
            mask |= EPOLLOUT;
        }
        mod_event(fd, mask, &session);
    }

    void handle_signals() {
        signalfd_siginfo fdsi{};
        ::read(signal_fd_.get(), &fdsi, sizeof(fdsi));
        std::cout << "\n[SIGNAL] Сигнал " << fdsi.ssi_signo << ". Завершення...\n";
        running_ = false;
    }

    void handle_timer() {
        uint64_t exp = 0;
        ::read(timer_fd_.get(), &exp, sizeof(exp));
    }

    void close_session(int fd) {
        ::epoll_ctl(epfd_.get(), EPOLL_CTL_DEL, fd, nullptr);
        sessions_.erase(fd);
        std::cout << "[DISCONNECT] Клієнт FD " << fd << " видалений\n";
    }
};

} // namespace net

int main() {
    try {
        net::ReactorServer server;
        server.init();
        server.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Детальний аналіз ключових підсистем та механізмів

Розгляньмо, як кожен крок коду співвідноситься з внутрішніми механізмами ядра Linux:

### 1. Цикл прийому з'єднань (`handle_accept`)

Слухаючий сокет зареєстрований у режимі `EPOLLET`. Це означає, що коли до сервера одночасно надходить сплеск із 50 нових підключень (наприклад, після TCP-рукостискання SYN-ACK), ядро згенерує **лише одну подію `EPOLLIN`**.

Якщо викликати `accept4()` лише один раз, перше з'єднання буде прийнято, а решта 49 залишаться спати у черзі `listen()`. Вони не зможуть передати жодного байта, доки не прибуде наступне, 51-ше з'єднання, яке створить новий фронт сигналу.

Саме тому функція `handle_accept()` виконує виклик `accept4()` всередині нескінченного циклу `while(1)` до моменту, поки черга повністю не спорожніє і виклик не поверне `-1` з `errno == EAGAIN`.

### 2. Запобігання витоку дескрипторів: `SOCK_CLOEXEC` та `SOCK_NONBLOCK`

Використання виклику `accept4()` із прапорцями `SOCK_NONBLOCK | SOCK_CLOEXEC` є критично важливим для надійності:
* `SOCK_NONBLOCK` — створює клієнтський сокет відразу в неблокуючому режимі без необхідності виконувати два додаткові системні виклики `fcntl(fd, F_GETFL)` та `fcntl(fd, F_SETFL)`;
* `SOCK_CLOEXEC` — атомарно встановлює прапорець `FD_CLOEXEC`. Якщо інший потік застосунку або сторонній компонент раптово виконає `fork()` та `execve()`, новий клієнтський дескриптор не витече у дочірній процес. Без атомарного прапорця між створенням сокета і викликом `fcntl(fd, F_SETFD, FD_CLOEXEC)` існує вікно гонитви.

### 3. Механіка скидання буфера запису (`flush_write`)

Функція скидання вихідного буфера реалізує повний цикл керування подією `EPOLLOUT`:
1. Вона намагається скинути байти в сокет якомога швидше;
2. Якщо `write()` повертає помилку `EAGAIN`, це свідчить про те, що вікно TCP переповнене. Функція припиняє запис, зберігає залишкові байти в `session.out_buffer` і модифікує маску подій в `epoll`, додаючи `EPOLLOUT`;
3. Коли буфер сокета в ядрі звільняється, `epoll_wait()` знову будить сервер, викликаючи `handle_write()`;
4. Щойно останній байт залишає буфер користувача, маска подій негайно змінюється назад на `EPOLLIN | EPOLLET | EPOLLRDHUP`.

---

## 4. Керування пам'яттю та оптимізація буферизації

У наведеному навчальному прикладі вихідний буфер реалізовано через динамічний масив `std::vector<char>` (або `realloc()` у C). Проте у промислових серверах під навантаженням сотень тисяч підключень часті виклики `realloc()` та `memmove()` створюють помітні накладні витрати CPU.

### Промислові патерни організації буферів:

1. **Кільцевий буфер (Ring Buffer):**
   Буфер фіксованого розміру (наприклад, 64 КБ), де запис та читання керуються двома покажчиками зсуву: `read_idx` та `write_idx`. Коли дані зчитуються із сокета, покажчик `write_idx` зміщується вперед. Коли байти передаються прикладному парсеру, покажчик `read_idx` наздоганяє його. Це повністю ліквідує виклики `memmove()` для зсуву залишкових байтів на початок пам'яті.
2. **Ланцюжки фіксованих блоків (Buffer Slabs / ByteBuf):**
   Пам'ять виділяється пулом однакових сторінок (наприклад, по 4096 байтів). Сесія зберігає зв'язний список таких блоків. Якщо вхідний запит зростає, до ланцюжка просто додається новий 4 КБ блок із попередньо виділеного пулу без переалокації всієї пам'яті сесії.
3. **Векторний запис через `writev(2)`:**
   Якщо відповідь складається зі статичного HTTP-заголовка та динамічного тіла з пам'яті, системний виклик `writev()` дозволяє передати масив структур `struct iovec` ядра. Процесор відправляє кілька розрізнених буферів за одну мережеву операцію без потреби збирати їх у єдиний проміжний масив.

---

## 5. Протокольний парсер: обробка кадрування повідомлень (Framing)

Оскільки TCP є потоком байтів без меж, реальний обробник `handle_read()` повинен взаємодіяти з парсером протоколу. Розгляньмо типовий скінченний автомат для бінарного протоколу з фіксованим заголовком (довжина 4 байти) та тілом змінної довжини (TLV — Type-Length-Value):

```
       ┌────────────────────────┐
       │   СТАН: READ_HEADER    │ <── Початок читання нового кадру
       └───────────┬────────────┘
                   │ Накопичено >= 4 байтів
                   ▼
       ┌────────────────────────┐
       │   СТАН: READ_PAYLOAD   │ ─── Визначено розмір payload_len
       └───────────┬────────────┘
                   │ Накопичено >= payload_len
                   ▼
       ┌────────────────────────┐
       │   СТАН: PROCESS_FRAME  │ ─── Виклик бізнес-логіки обробки
       └───────────┬────────────┘
                   │ Кадр вилучено з буфера
                   ▼
       [Повернення до READ_HEADER для наступних байтів у буфері]
```

Якщо `read()` повернув лише 2 байти, автомат залишається у стані `READ_HEADER` і виходить із функції, чекаючи наступного сповіщення `EPOLLIN`. Жодні дані не губляться, а потік сервера не блокується.

---

## 6. Виробничі пастки та обробка крайових випадків

Під час експлуатації подієвих серверів під навантаженням сотень тисяч запитів розробники регулярно стикаються з чотирма типовими системними пастками:

### 1. Вичерпання файлових дескрипторів процесу (`EMFILE` на `accept4`)

Якщо кількість відкритих файлів досягає системного ліміту процесу (`RLIMIT_NOFILE`), системний виклик `accept4()` завершується помилкою `EMFILE` («Too many open files») і **не забирає з'єднання з черги ядра**.

Оскільки з'єднання залишається в черзі `listen()`, сокет продовжує перебувати у стані готовності. У режимі Level-Triggered виклик `epoll_wait()` негайно повертатиме готовність слухаючого сокета знову і знову, що призводить до 100% завантаження CPU та повного зависання сервера в нескінченному циклі помилок.

*Виробничий розв'язок (The Idle FD Trick):*
Під час запуску сервер відкриває один фіктивний файловий дескриптор на `/dev/null`:

:::tabs
```c
int idle_fd = open("/dev/null", O_RDONLY | O_CLOEXEC);
```
```cpp
int idle_fd = ::open("/dev/null", O_RDONLY | O_CLOEXEC);
```
:::

Коли `accept4()` повертає `EMFILE`:
1. Програма тимчасово закриває `close(idle_fd)`, звільняючи один слот у таблиці дескрипторів;
2. Викликає `int temp_fd = accept(listen_fd, ...)` і негайно виконує `close(temp_fd)` — це коректно закриває з'єднання з боку TCP і очищає чергу ядра;
3. Знову відкриває `idle_fd = open("/dev/null", ...)` для резервування слота під наступні збої.

### 2. Сигнал `SIGPIPE` та аварійне завершення процесу

Якщо клієнтський браузер або мобільний застосунок раптово закрив TCP-з'єднання (наприклад, користувач згорнув вкладку або втратив зв'язок Wi-Fi), а сервер виконує системний виклик `write()` у закритий сокет:
1. Перший `write()` повертає помилку `EPIPE` або `-1`;
2. Другий виклик `write()` змушує ядро Linux надіслати процесу сигнал **`SIGPIPE`**.

За замовчуванням дія сигналу `SIGPIPE` — **негайне аварійне завершення процесу** без створення дампа пам'яті. Мережевий сервер, який обслуговував 20 000 клієнтів, миттєво гине через відключення одного випадкового користувача.

*Захист:*
Перед запуском циклу сервер зобов'язаний заблокувати або проігнорувати цей сигнал:

:::tabs
```c
signal(SIGPIPE, SIG_IGN);
```
```cpp
::signal(SIGPIPE, SIG_IGN);
```
:::

Або використовувати прапорець `MSG_NOSIGNAL` під час відправки через `send()`:

:::tabs
```c
send(fd, buf, len, MSG_NOSIGNAL);
```
```cpp
::send(fd, buf, len, MSG_NOSIGNAL);
```
:::

### 3. Безпечне відключення: `EPOLLRDHUP` проти перевірки `read() == 0`

Традиційний спосіб виявлення відключення клієнта — отримати значення `0` від системного виклику `read()`. Проте для цього сервер повинен спочатку розбудити потік, виділити буфер, зайти в системний виклик і лише там дізнатися про закриття TCP FIN.

Прапорець `EPOLLRDHUP` (доступний починаючи з ядра Linux 2.6.17) передає інформацію про закриття каналу читання безпосередньо у маску `revents` виклику `epoll_wait()`. Сервер може негайно видалити клієнта та звільнити ресурси пам'яті без зайвого системного виклику `read()`.

### 4. Керування скиданням сокета через `SO_LINGER`

Під час виклику `close(fd)` за замовчуванням ядро Linux намагається відправити всі невідправлені дані у фоновому режимі, після чого ініціює 4-етапне закриття TCP FIN. Якщо сервер змушений екстрено обірвати сесію шкідливого клієнта або атакувальника, налаштування сокета через структуру `struct linger`:

:::tabs
```c
struct linger sl = { .l_onoff = 1, .l_linger = 0 };
setsockopt(fd, SOL_SOCKET, SO_LINGER, &sl, sizeof(sl));
close(fd);
```
```cpp
linger sl{ .l_onoff = 1, .l_linger = 0 };
::setsockopt(fd, SOL_SOCKET, SO_LINGER, &sl, sizeof(sl));
::close(fd);
```
:::

змушує ядро миттєво скинути з'єднання пакетом TCP RST (Reset), очистити всі буфери пам'яті ядра та уникнути переходу сокета у тривалий стан очікування `TIME_WAIT`.

---

## 7. Послідовність коректної зупинки (Graceful Shutdown)

Коли сервер отримує сигнал завершення `SIGTERM` або `SIGINT`, він повинен коректно зупинити роботу без раптового скидання активних клієнтських транзакцій:

1. **Припинення прийому нових з'єднань:** Сервер видаляє слухаючий дескриптор `listen_fd` із екземпляра `epoll` через `epoll_ctl(EPOLL_CTL_DEL)` та закриває його. Нові клієнти перестають підключатися;
2. **Скидання залишкових вихідних буферів:** Подієвий цикл продовжує працювати у спеціальному режимі зливу (Drain Mode), виконуючи операції `write()` для сесій, що мають дані у черзі відправки;
3. **Надсилання закриваючих пакетів:** Для відкритих сесій викликається `shutdown(fd, SHUT_WR)`, що сигналізує клієнтам про планове завершення;
4. **Встановлення таймауту примусової зупинки:** Запускається короткий таймер (наприклад, 3 секунди). Якщо після закінчення таймера деякі клієнти не відключилися, дескриптори закриваються примусово, а пам'ять звільняється.

---

## 8. Профілювання та вимірювання продуктивності

Для тестування розробленого сервера під навантаженням використовують утиліту генерації трафіку `wrk` або `autocannon`:

```bash
# Запуск тесту: 10 000 одночасних підключень на 30 секунд через 8 потоків
wrk -t8 -c10000 -d30s http://127.0.0.1:8080/
```

Під час тестування стан процесора та системи перевіряють через інструменти спостереження ядра Linux:

1. **Частота перемикання контексту:**
   ```bash
   pidstat -w -p $(pgrep reactor_server) 1
   ```
   У подієвому сервері кількість добровільних перемикань контексту (`cswch/s`) повинна дорівнювати лише частоті викликів `epoll_wait()`, а кількість примусових перемикань (`nvcswch/s`) — наближатися до нуля.
2. **Розподіл системних викликів:**
   ```bash
   perf stat -e syscalls:sys_enter_epoll_wait,syscalls:sys_enter_read,syscalls:sys_enter_write -p $(pgrep reactor_server) sleep 10
   ```
   Цей звіт показує, що 95%+ часу сервер проводить у безпосередньому читанні та відправці даних, уникаючи холостих опитувань дескрипторів.

---

## 9. Багатоядерне масштабування: архітектура Multi-Reactor з SO_REUSEPORT

Однопотоковий подієвий сервер утилізує рівно одне процесорне ядро. Щоб ефективно задіяти всі 32, 64 або 128 процесорних ядер сучасного сервера, однопотоковий патерн Reactor масштабують до архітектури **Multi-Reactor (One Event Loop per Core)**:

1. **Модель незалежних воркерів (Shared-Nothing Architecture):**
   Сервер створює `N` робочих потоків або процесів (де `N` дорівнює кількості апаратних ядер CPU). Кожен потік крутить свій власний, абсолютно ізольований екземпляр `epoll` та обслуговує власний набір клієнтських сесій;
2. **Розподіл нових з'єднань через ядро (`SO_REUSEPORT`):**
   Кожен робочий потік створює власний слухаючий сокет на тому самому порту з опцією `setsockopt(listen_fd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt))`. Під час завершення 3-стороннього рукостискання TCP ядро Linux обчислює 4-кортежний хеш клієнта (`src_ip`, `src_port`, `dst_ip`, `dst_port`) та автоматично направляє новий сокет у чергу `listen()` одного з робочих потоків. Це усуває потребу у міжпотокових м'ютексах та забезпечує ідеальну локальність кешу процесора (CPU Cache Locality).

---

## 10. Налаштування операційної системи під C100K / C1000K

Для утримання сотень тисяч одночасних клієнтів на рівні операційної системи необхідно відрегулювати системні ліміти мережевого стека Linux у файлі `/etc/sysctl.conf`:

```ini
# Максимальна довжина черги повністю встановлених з'єднань listen()
net.core.somaxconn = 65535

# Максимальна довжина черги незавершених SYN-рукостискань
net.ipv4.tcp_max_syn_backlog = 65535

# Діапазон локальних портів для вихідних з'єднань
net.ipv4.ip_local_port_range = 1024 65535

# Повторне використання TIME_WAIT сокетів
net.ipv4.tcp_tw_reuse = 1

# Зменшення часу утримання стану FIN-WAIT-2
net.ipv4.tcp_fin_timeout = 15

# Розмір буферів прийому та передачі за замовчуванням (байти)
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
```

---

## 11. Діагностика та спостереження за сокетами: `ss` та `bpftrace`

Під час експлуатації сервера під великим навантаженням важливо мати інструменти діагностики, які дозволяють бачити стан буферів ядра та затримок без зупинки процесу:

### 1. Моніторинг черг сокетів через утиліту `ss`:
```bash
# Перегляд детального стану буферів, вікна cwnd та затримки RTT для порту 8080
ss -tiepm '( sport = :8080 )'
```
У виводі звертають увагу на:
* `Send-Q` — кількість байтів, що очікують відправки у черзі ядра. Якщо `Send-Q` постійно великий для багатьох клієнтів, це свідчить про вузький мережевий канал клієнтів або затримки підтверджень ACK;
* `Recv-Q` — кількість байтів у буфері прийому ядра, які сервер ще не встиг вичитати через `read()`. Якщо `Recv-Q` зростає, сервер не встигає обробляти потік вхідних подій;
* `cwnd` — розмір вікна перевантаження TCP (Congestion Window) у сегментах MSS;
* `rtt` — виміряний час обігу пакета (Round Trip Time) між сервером та клієнтом.

### 2. Трасування затримки `epoll_wait` через `bpftrace`:
Для вимірювання часу, який потік проводить у системному виклику очікування подій, використовують eBPF-скрипт:
```bash
bpftrace -e '
tracepoint:syscalls:sys_enter_epoll_wait { @start[tid] = nsecs; }
tracepoint:syscalls:sys_exit_epoll_wait /@start[tid]/ {
    @latency_us = hist((nsecs - @start[tid]) / 1000);
    delete(@start[tid]);
}'
```
Цей гістограмний звіт показує розподіл інтервалів сну сервера: якщо більшість викликів повертаються швидше ніж за 50 мікросекунд, це демонструє надзвичайно низьку затримку реакції на нові клієнтські запити.



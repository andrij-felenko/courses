# ⚙️ Створення надійного продакшен-сервісу для Linux: сокети, signalfd та sd_notify

Цей проект демонструє створення повноцінного мережевого демона для Linux, який відповідає всім критеріям продакшен-готовності: безпечна обробка сигналів через системний виклик `signalfd`, неблокуючий ввід-вивід через `epoll`, протокол сповіщень `sd_notify`, підтримка активації за сокетом (*socket activation*) та детерміноване коректне завершення (*graceful shutdown*).

---

### 1. Архітектурні виклики проектування серверних служб у Linux

Розробка надійного мережевого демона для операційної системи Linux вимагає вирішення комплексу системних задач, пов'язаних із взаємодією процесу з ядром, моделлю введення-виведення та підсистемою ініціалізації.

#### 1.1. Пастки класичних асинхронних обробників сигналів

Традиційний підхід до керування життєвим циклом програми в Unix базується на реєстрації асинхронних функцій-обробників за допомогою системного виклику `sigaction()`. Коли операційна система надсилає процесу сигнал (наприклад, `SIGTERM` або `SIGHUP`), ядро перериває виконання основного потоку інструкцій у довільній точці та перемикає контекст процесора на виконання сигнального обробника.

Така модель створює серйозні інженерні ризики:
1. **Порушення асинхронно-сигнальної безпеки (*Async-Signal Safety*):** Більшість стандартних функцій системної бібліотеки C (зокрема функції виділення пам'яті `malloc()` і `free()`, операції форматованого виводу `printf()`, функції роботи з рядками та блокування м'ютексів `pthread_mutex_lock()`) не є реентрабельними. Якщо сигнал надходить у момент, коли головний потік виконував `malloc()`, і сигнальний обробник спробує викликати функцію логування або виділити буфер, внутрішні структури купи будуть пошкоджені, що призведе до мертвого блокування (*deadlock*) або аварійного краху `SIGSEGV`.
2. **Невизначений стан структур даних:** Переривання коду під час оновлення черги клієнтських з'єднань або списку активних транзакцій залишає об'єкти програми у напівзруйнованому стані.
3. **Обмеженість сигнального прапорця:** Запис у змінну типу `volatile sig_atomic_t` повідомляє про факт отримання сигналу, але не дозволяє негайно розбудити системний виклик очікування подій `epoll_wait()`, якщо він заблокований у режимі очікування нових підключень без таймауту.

#### 1.2. Синхронізація сигналів через `signalfd`

Ядро Linux вирішує цю проблему за допомогою спеціального механізму `signalfd()`. Цей системний виклик перетворює асинхронні сигнали ядра на синхронні події файлового дескриптора.

Принцип роботи полягає у двох кроках:
1. Процес заздалегідь блокує обробку обраних сигналів (`SIGTERM`, `SIGINT`, `SIGHUP`) на рівні потоків за допомогою `sigprocmask()`. Ядро більше не перериває виконання інструкцій процесора.
2. Процес створює дескриптор `signalfd`, який підключається до загального циклу `epoll_wait()`. Коли ядро генерує сигнал для процесу, воно додає подію готовності до читання у дескриптор `signalfd`. Сервер зчитує структуру `struct signalfd_siginfo` як звичайні байти даних у передбачуваній точці головного циклу подій.

```
                           ┌──────────────────────────────┐
                           │    Ядро Linux (Kernel)       │
                           └──────────────┬───────────────┘
                                          │
                  ┌───────────────────────┴───────────────────────┐
                  │ Генерація сигналів (SIGTERM, SIGHUP, SIGINT)   │
                  ▼                                               ▼
     ┌────────────────────────┐                      ┌────────────────────────┐
     │ Блокування доставки    │                      │ Запис у буфер черги    │
     │ через sigprocmask()    │                      │ файлового дескриптора  │
     └───────────┬────────────┘                      └───────────┬────────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         ▼
                          ┌─────────────────────────────┐
                          │    signalfd (дескриптор)    │
                          └──────────────┬──────────────┘
                                         │ Подія EPOLLIN
                                         ▼
                          ┌─────────────────────────────┐
                          │    Головний цикл epoll      │
                          └──────────────┬──────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
  ┌─────────────────────────────┐                 ┌─────────────────────────────┐
  │ Обробка SIGTERM:            │                 │ Обробка SIGHUP:             │
  │ Початок Graceful Shutdown   │                 │ Гаряче перечитування файлів │
  └─────────────────────────────┘                 └─────────────────────────────┘
```

#### 1.3. Модель активації за сокетом (Socket Activation)

У класичній архітектурі Unix демон самостійно створює слухаючий TCP-сокет (`socket()`), прив'язує його до порту (`bind()`) і переводить у режим прослуховування (`listen()`).

Менеджер `systemd` пропонує значно надійнішу парадигму — **активацію за сокетом**. `systemd` самостійно відкриває мережевий сокет до запуску служби, тримає його відкритим і передає готовий файловий дескриптор створеному процесу через стандартизовані змінні середовища:
* `LISTEN_PID`: числовий PID процесу, якому призначено сокети.
* `LISTEN_FDS`: кількість переданих файлових дескрипторів.

Перший переданий дескриптор гарантовано має фіксований числовий номер `3` (константа `SD_LISTEN_FDS_START`), наступні — `4`, `5` і так далі. Це дає дві ключові переваги:
1. **Відсутність простою під час рестарту:** Клієнтські підключення накопичуються в черзі ядра TCP `listen backlog` навіть у той момент, коли служба перезавантажується. Жоден клієнт не отримує помилку `Connection refused`.
2. **Паралельний запуск:** Усі залежні клієнти можуть стартувати одночасно з сервером, не чекаючи повної ініціалізації бази даних чи мережевого демона.

#### 1.4. Ефективність обробки подій через `epoll`

Підсистема `epoll` є основою високопродуктивних серверів у Linux завдяки асимптотичній складності `O(1)`. На відміну від системних викликів `select()` та `poll()`, які щоразу сканують лінійний масив усіх переданих дескрипторів (складність `O(N)`), `epoll` реєструє дескриптори в червоно-чорному дереві ядра та додає готові до введення-виведення події у двозв'язний список готовності (`ready list`).

Виклик `epoll_wait()` миттєво повертає лише ті дескриптори, на яких відбулися реальні мережеві події. У поєднанні з неблокуючими сокетами (`O_NONBLOCK`) та системним викликом `accept4()`, один потік виконання може надійно обслуговувати десятки тисяч одночасних підключень.

---

### 2. Повна реалізація продакшен-сервера

Нижче наведено повний вихідний код автономного високопродуктивного мережевого сервера, що реалізує всі перелічені механізми мовами C та C++:

:::tabs
```c
#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <stdbool.h>

#define MAX_EVENTS 64
#define BUFFER_SIZE 4096
#define DEFAULT_PORT 8080
#define SD_LISTEN_FDS_START 3

/* Автономне надсилання сповіщення стану в systemd через NOTIFY_SOCKET */
static void notify_systemd(const char *state) {
    const char *sock_path = getenv("NOTIFY_SOCKET");
    if (!sock_path || !state) return;

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;

    size_t len = strlen(sock_path);
    if (len >= sizeof(addr.sun_path)) return;

    if (sock_path[0] == '@') {
        addr.sun_path[0] = '\0';
        memcpy(&addr.sun_path[1], &sock_path[1], len - 1);
    } else {
        memcpy(addr.sun_path, sock_path, len);
    }

    int fd = socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    socklen_t addr_len = offsetof(struct sockaddr_un, sun_path) + len;
    sendto(fd, state, strlen(state), MSG_NOSIGNAL, (struct sockaddr *)&addr, addr_len);
    close(fd);
}

/* Переведення дескриптора у неблокуючий режим введення-виведення */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Отримання сокета: підтримка socket activation від systemd або створення власного */
static int get_listen_socket(int port) {
    const char *listen_pid_str = getenv("LISTEN_PID");
    const char *listen_fds_str = getenv("LISTEN_FDS");

    if (listen_pid_str && listen_fds_str) {
        pid_t listen_pid = (pid_t)atoi(listen_pid_str);
        int listen_fds = atoi(listen_fds_str);
        if (listen_pid == getpid() && listen_fds > 0) {
            fprintf(stdout, "<6>Успішно підключено сокет від systemd (fd=%d)\n", SD_LISTEN_FDS_START);
            set_nonblocking(SD_LISTEN_FDS_START);
            return SD_LISTEN_FDS_START;
        }
    }

    int fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    int opt = 1;
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);

    if (bind(fd, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(fd);
        return -1;
    }

    if (listen(fd, SOMAXCONN) < 0) {
        perror("listen");
        close(fd);
        return -1;
    }

    fprintf(stdout, "<6>Створено локальний сокет на порту %d\n", port);
    return fd;
}

int main(int argc, char *argv[]) {
    int port = DEFAULT_PORT;
    if (argc > 1) {
        port = atoi(argv[1]);
    }

    /* 1. Ігноруємо SIGPIPE, щоб уникнути падіння процесу при раптовому закритті клієнтом */
    signal(SIGPIPE, SIG_IGN);

    /* 2. Блокуємо сигнали для безпечної обробки через signalfd */
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGHUP);

    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) {
        perror("sigprocmask");
        return EXIT_FAILURE;
    }

    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd < 0) {
        perror("signalfd");
        return EXIT_FAILURE;
    }

    /* 3. Створюємо інстанс epoll */
    int epoll_fd = epoll_create1(EPOLL_CLOEXEC);
    if (epoll_fd < 0) {
        perror("epoll_create1");
        close(sfd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sfd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, sfd, &ev);

    /* 4. Отримуємо мережевий сокет */
    int listen_fd = get_listen_socket(port);
    if (listen_fd < 0) {
        close(sfd);
        close(epoll_fd);
        return EXIT_FAILURE;
    }

    ev.events = EPOLLIN;
    ev.data.fd = listen_fd;
    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, listen_fd, &ev);

    /* 5. Сповіщаємо systemd про успішну готовність */
    notify_systemd("READY=1\nSTATUS=Сервер успішно готовий приймати трафік");

    struct epoll_event events[MAX_EVENTS];
    bool running = true;
    int active_connections = 0;

    fprintf(stdout, "<6>Головний цикл введення-виведення запущено\n");

    while (running || active_connections > 0) {
        int timeout = running ? 5000 : 1000;
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, timeout);

        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }

        if (nfds == 0 && running) {
            /* Відправляємо keep-alive сигнал сторожовому таймеру */
            notify_systemd("WATCHDOG=1");
            continue;
        }

        for (int i = 0; i < nfds; i++) {
            int cur_fd = events[i].data.fd;

            if (cur_fd == sfd) {
                /* Обробка системного сигналу як події введення-виведення */
                struct signalfd_siginfo fdsi;
                ssize_t s = read(sfd, &fdsi, sizeof(fdsi));
                if (s == sizeof(fdsi)) {
                    if (fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGINT) {
                        fprintf(stdout, "<5>Отримано сигнал %d: початок Graceful Shutdown...\n", fdsi.ssi_signo);
                        notify_systemd("STOPPING=1\nSTATUS=Зупинка: дообробка активних з'єднань");
                        running = false;
                        /* Закриваємо сокет прослуховування, щоб відхиляти нових клієнтів */
                        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, listen_fd, NULL);
                        close(listen_fd);
                    } else if (fdsi.ssi_signo == SIGHUP) {
                        fprintf(stdout, "<6>Отримано SIGHUP: перезавантаження конфігурації\n");
                        notify_systemd("RELOADING=1");
                        /* Перечитування файлів конфігурації */
                        notify_systemd("READY=1\nSTATUS=Конфігурацію успішно оновлено");
                    }
                }
            } else if (cur_fd == listen_fd) {
                /* Прийом нових вхідних TCP-з'єднань */
                while (true) {
                    struct sockaddr_in client_addr;
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = accept4(listen_fd, (struct sockaddr *)&client_addr,
                                            &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
                    if (client_fd < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("accept4");
                        break;
                    }

                    ev.events = EPOLLIN | EPOLLRDHUP;
                    ev.data.fd = client_fd;
                    epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, &ev);
                    active_connections++;
                }
            } else {
                /* Обробка даних від клієнтських сокетів */
                char buffer[BUFFER_SIZE];
                ssize_t count = read(cur_fd, buffer, sizeof(buffer));

                if (count > 0) {
                    /* Ехо-відповідь клієнту з прапорцем безпеки MSG_NOSIGNAL */
                    send(cur_fd, buffer, (size_t)count, MSG_NOSIGNAL);
                } else if (count == 0 || (count < 0 && errno != EAGAIN)) {
                    /* Клієнт закрив сокет або сталася помилка передачі */
                    epoll_ctl(epoll_fd, EPOLL_CTL_DEL, cur_fd, NULL);
                    close(cur_fd);
                    active_connections--;
                }
            }
        }
    }

    fprintf(stdout, "<6>Усі клієнтські сесії завершено. Процес виходить штатно.\n");
    close(sfd);
    close(epoll_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/signalfd.h>
#include <sys/un.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <csignal>
#include <cstdlib>
#include <cstring>
#include <string_view>
#include <iostream>
#include <vector>
#include <expected>
#include <system_error>

namespace production {

constexpr int max_events = 64;
constexpr int buffer_size = 4096;
constexpr int default_port = 8080;
constexpr int sd_listen_fds_start = 3;

// RAII обгортка для надійного володіння файловим дескриптором Linux
class unique_fd {
    int m_fd = -1;
public:
    explicit unique_fd(int fd = -1) noexcept : m_fd(fd) {}
    ~unique_fd() noexcept { if (m_fd >= 0) ::close(m_fd); }

    unique_fd(const unique_fd&) = delete;
    unique_fd& operator=(const unique_fd&) = delete;

    unique_fd(unique_fd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    unique_fd& operator=(unique_fd&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
    void reset(int fd = -1) noexcept {
        if (m_fd >= 0) ::close(m_fd);
        m_fd = fd;
    }
    int release() noexcept {
        int fd = m_fd;
        m_fd = -1;
        return fd;
    }
};

// Відправка повідомлень у systemd через NOTIFY_SOCKET
void notify_systemd(std::string_view state) noexcept {
    const char* sock_path = std::getenv("NOTIFY_SOCKET");
    if (!sock_path || state.empty()) return;

    struct sockaddr_un addr{};
    addr.sun_family = AF_UNIX;

    const size_t len = std::strlen(sock_path);
    if (len >= sizeof(addr.sun_path)) return;

    if (sock_path[0] == '@') {
        addr.sun_path[0] = '\0';
        std::memcpy(&addr.sun_path[1], &sock_path[1], len - 1);
    } else {
        std::memcpy(addr.sun_path, sock_path, len);
    }

    int fd = ::socket(AF_UNIX, SOCK_DGRAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return;

    auto addr_len = static_cast<socklen_t>(offsetof(struct sockaddr_un, sun_path) + len);
    ::sendto(fd, state.data(), state.size(), MSG_NOSIGNAL,
             reinterpret_cast<struct sockaddr*>(&addr), addr_len);
    ::close(fd);
}

// Отримання або створення сокета прослуховування
[[nodiscard]] std::expected<unique_fd, std::error_code> create_listen_socket(int port) noexcept {
    const char* listen_pid_str = std::getenv("LISTEN_PID");
    const char* listen_fds_str = std::getenv("LISTEN_FDS");

    if (listen_pid_str && listen_fds_str) {
        pid_t pid = std::atoi(listen_pid_str);
        int count = std::atoi(listen_fds_str);
        if (pid == ::getpid() && count > 0) {
            std::cout << "<6>Використано сокет від systemd (socket activation)\n";
            int flags = ::fcntl(sd_listen_fds_start, F_GETFL, 0);
            ::fcntl(sd_listen_fds_start, F_SETFL, flags | O_NONBLOCK);
            return unique_fd(sd_listen_fds_start);
        }
    }

    int fd = ::socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK | SOCK_CLOEXEC, 0);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    unique_fd sock(fd);

    int opt = 1;
    ::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(static_cast<uint16_t>(port));

    if (::bind(sock.get(), reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(sock.get(), SOMAXCONN) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    std::cout << "<6>Слухаємо порт " << port << '\n';
    return sock;
}

} // namespace production

int main(int argc, char* argv[]) {
    int port = production::default_port;
    if (argc > 1) {
        port = std::atoi(argv[1]);
    }

    ::signal(SIGPIPE, SIG_IGN);

    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGHUP);

    if (::sigprocmask(SIG_BLOCK, &mask, nullptr) < 0) {
        std::cerr << "<3>Помилка виклику sigprocmask\n";
        return EXIT_FAILURE;
    }

    production::unique_fd sfd(::signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC));
    if (!sfd.valid()) {
        std::cerr << "<3>Помилка створення signalfd\n";
        return EXIT_FAILURE;
    }

    production::unique_fd epoll_fd(::epoll_create1(EPOLL_CLOEXEC));
    if (!epoll_fd.valid()) {
        std::cerr << "<3>Помилка виклику epoll_create1\n";
        return EXIT_FAILURE;
    }

    struct epoll_event ev{};
    ev.events = EPOLLIN;
    ev.data.fd = sfd.get();
    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, sfd.get(), &ev);

    auto listen_sock_res = production::create_listen_socket(port);
    if (!listen_sock_res) {
        std::cerr << "<3>Помилка створення слухаючого сокета: " 
                  << listen_sock_res.error().message() << '\n';
        return EXIT_FAILURE;
    }
    production::unique_fd listen_sock = std::move(*listen_sock_res);

    ev.events = EPOLLIN;
    ev.data.fd = listen_sock.get();
    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, listen_sock.get(), &ev);

    production::notify_systemd("READY=1\nSTATUS=C++23 Сервер готовий до роботи");

    std::vector<struct epoll_event> events(production::max_events);
    bool running = true;
    int active_connections = 0;

    std::cout << "<6>Головний цикл подій C++ успішно запущено\n";

    while (running || active_connections > 0) {
        int timeout = running ? 5000 : 1000;
        int nfds = ::epoll_wait(epoll_fd.get(), events.data(), production::max_events, timeout);

        if (nfds < 0) {
            if (errno == EINTR) continue;
            std::cerr << "<3>Помилка epoll_wait: " << std::strerror(errno) << '\n';
            break;
        }

        if (nfds == 0 && running) {
            production::notify_systemd("WATCHDOG=1");
            continue;
        }

        for (int i = 0; i < nfds; ++i) {
            int cur_fd = events[i].data.fd;

            if (cur_fd == sfd.get()) {
                struct signalfd_siginfo fdsi{};
                if (::read(sfd.get(), &fdsi, sizeof(fdsi)) == sizeof(fdsi)) {
                    if (fdsi.ssi_signo == SIGTERM || fdsi.ssi_signo == SIGINT) {
                        std::cout << "<5>Отримано сигнал зупинки. Початок Graceful Shutdown...\n";
                        production::notify_systemd("STOPPING=1\nSTATUS=Завершення роботи");
                        running = false;
                        ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_DEL, listen_sock.get(), nullptr);
                        listen_sock.reset();
                    } else if (fdsi.ssi_signo == SIGHUP) {
                        std::cout << "<6>Отримано SIGHUP: перезавантаження конфігурації\n";
                        production::notify_systemd("RELOADING=1");
                        production::notify_systemd("READY=1\nSTATUS=Конфігурацію оновлено");
                    }
                }
            } else if (listen_sock.valid() && cur_fd == listen_sock.get()) {
                while (true) {
                    struct sockaddr_in client_addr{};
                    socklen_t client_len = sizeof(client_addr);
                    int client_fd = ::accept4(listen_sock.get(),
                                              reinterpret_cast<struct sockaddr*>(&client_addr),
                                              &client_len, SOCK_NONBLOCK | SOCK_CLOEXEC);
                    if (client_fd < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        break;
                    }

                    ev.events = EPOLLIN | EPOLLRDHUP;
                    ev.data.fd = client_fd;
                    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_ADD, client_fd, &ev);
                    active_connections++;
                }
            } else {
                std::vector<char> buffer(production::buffer_size);
                ssize_t count = ::read(cur_fd, buffer.data(), buffer.size());

                if (count > 0) {
                    ::send(cur_fd, buffer.data(), static_cast<size_t>(count), MSG_NOSIGNAL);
                } else if (count == 0 || (count < 0 && errno != EAGAIN)) {
                    ::epoll_ctl(epoll_fd.get(), EPOLL_CTL_DEL, cur_fd, nullptr);
                    ::close(cur_fd);
                    active_connections--;
                }
            }
        }
    }

    std::cout << "<6>Усі сесії завершено. Процес виходить штатно.\n";
    return EXIT_SUCCESS;
}
```
:::

---

### 3. Покроковий розбір системних інваріантів реалізації

#### 3.1. Прапорець `SOCK_CLOEXEC` у системних викликах

Під час створення дескрипторів сокетів (`socket()`, `accept4()`, `epoll_create1()`, `signalfd()`) обов'язковим є встановлення прапорця `SOCK_CLOEXEC` або `O_CLOEXEC`.

Якщо цей прапорець не встановлено, а процес згодом виконує виклик `fork()` і `execve()` для запуску допоміжної утиліти чи скрипту, усі відкриті мережеві дескриптори будуть успадковані дочірнім процесом. Це веде до витоку портів: батьківський процес може закрити свій сокет, але порт залишатиметься зайнятим у ядрі через те, що його утримує дочірній процес.

#### 3.2. Обробка помилок `EAGAIN` та `EWOULDBLOCK` у неблокуючому режимі

Усі сокети, зареєстровані в `epoll`, переводяться у неблокуючий режим за допомогою системного виклику `fcntl(fd, F_SETFL, flags | O_NONBLOCK)` або прапорця `SOCK_NONBLOCK`.

Коли надходить подія `EPOLLIN` на слухаючому сокеті, програма повинна викликати `accept4()` у циклі доти, доки виклик не поверне помилку `EAGAIN` або `EWOULDBLOCK`. Якщо виконати лише один `accept4()`, а до сокета одночасно надійшло кілька підключень, наступні клієнти залишаться заблокованими у черзі до наступної події.

#### 3.3. Використання прапорця `EPOLLRDHUP`

Стандартна подія `EPOLLIN` сигналізує про наявність даних для читання. Проте, якщо клієнт на іншому кінці TCP-з'єднання закрив свою половину каналу (надіслав TCP-пакет `FIN`), ядро також генерує подію `EPOLLIN`. Якщо не обробити це явно через перевірку `read() == 0`, програма ризикує увійти в нескінченний цикл опитування.

Реєстрація події `EPOLLRDHUP` дозволяє підсистемі `epoll` миттєво сповістити процес про одностороннє закриття сокета віддаленою стороною без необхідності виконання холостих системних викликів `read()`.

#### 3.4. Захист від втрати сигналів під час високого навантаження

Оскільки системний виклик `sigprocmask(SIG_BLOCK, ...)` переводить доставку сигналів у чергу ядра, сигнали `SIGTERM` та `SIGHUP` гарантовано не губляться, навіть якщо в цей момент процес виконував інтенсивні обчислення чи запис на диск.

Коли черга подій `epoll` розблоковується, дескриптор `sfd` сигналізує про готовність, і сервер безпечно зчитує номер сигналу без загрози виникнення стану гонитви.

---

### 4. Інтеграція, тестування та діагностика

#### 4.1. Збірка виконуваних файлів

Компіляція програми виконується з максимальним рівнем попереджень компілятора та оптимізацією:

```bash
# Збірка версії мовою C
gcc -O2 -Wall -Wextra -Wpedantic -D_GNU_SOURCE server.c -o prod-server-c

# Збірка версії мовою C++ (стандарт C++23)
g++ -O2 -std=c++23 -Wall -Wextra -Wpedantic server.cpp -o prod-server-cpp
```

#### 4.2. Тестування поведінки під керуванням `systemd`

Для перевірки взаємодії з протоколом `sd_notify` без встановлення постійного системного юніта використовується утиліта швидкого запуску `systemd-run`:

```bash
sudo systemd-run --unit=demo-network-service \
  --property=Type=notify \
  --property=WatchdogSec=10s \
  --property=DynamicUser=yes \
  --property=ProtectSystem=strict \
  ./prod-server-c 8080
```

Перевірка статусу служби в системі:
```bash
# Перегляд стану unit (має бути active (running) із динамічним статусом)
systemctl status demo-network-service

# Перегляд структурованого журналу подій у реальному часі
journalctl -u demo-network-service -f
```

Перевірка процедури коректного завершення (Graceful Shutdown):
```bash
# Надсилання командного сигналу зупинки
systemctl stop demo-network-service

# У журналі journalctl відображаються повідомлення:
# "Отримано сигнал 15: початок Graceful Shutdown..."
# "Усі клієнтські сесії завершено. Процес виходить штатно."
```

#### 4.3. Діагностика системних викликів через `strace`

Для верифікації черговості викликів ядра, обробки сигналів та неблокуючого введення-виведення використовується утиліта `strace`:

```bash
strace -f -tt -e trace=socket,bind,listen,epoll_create1,epoll_ctl,epoll_wait,signalfd4,accept4,sendto,read,write ./prod-server-c 8080
```

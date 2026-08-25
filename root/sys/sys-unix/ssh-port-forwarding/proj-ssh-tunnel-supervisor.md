# ⚙️ Проектування надійного супервізора SSH-тунелів із моніторингом сокетів

Фонові SSH-тунелі, запущені через стандартний клієнт `ssh -f -N`, мають характерну системну слабкість: при тимчасовому розриві інтернет-з'єднання, перезавантаженні маршрутизатора або мовчазному скиданні сесії NAT-брандмауером дочірній процес `ssh` може зависнути або аварійно завершитися. У такому стані локальні процеси втрачають зв'язок із віддаленими базами даних чи мікросервісами, а операційна система не має вбудованого механізму автоматичної перевірки доступності прокинутого порту.

Створення автономного системного супервізора розв'язує цю проблему: демон запускає SSH-тунель у дочірньому процесі, періодично перевіряє доступність локального сокета за допомогою неблокуючих системних викликів `connect()` та `poll()`, а в разі відмови перезапускає тунель із контрольованою експоненційною затримкою (exponential backoff).

## Архітектурні виклики та обмеження наївного підходу

При створенні надійного системного сервісу утримання тунелю розробник стикається з кількома підступними крайовими випадками ядра Linux:

1. **Мовчазне зависання сокета при обриві NAT:** Якщо проміжний брандмауер вилучає запис про з'єднання зі своєї таблиці трансляції, ядро локальної машини не отримує жодних пакетів `FIN` чи `RST`. Сокет клієнта продовжує перебувати у стані `TCP_ESTABLISHED`. Якщо процес просто перевіряє факт існування PID дочірнього процесу `ssh`, він вважатиме тунель справним, хоча реальний трафік через нього не проходить.
2. **Пастка перевірки виклику `poll()`:** Системний виклик `poll()` (або `epoll`) сигналізує про готовність сокета до запису (`POLLOUT`) як у разі успішного завершення тристороннього рукостискання TCP, так і в разі відхилення з'єднання (отримання пакета `RST` з помилкою `ECONNREFUSED`). Перевірка лише прапорця `POLLOUT` без виклику `getsockopt()` є класичною помилкою, через яку супервізор вважає мертвий порт відкритим.
3. **Накопичення зомбі-процесів (Zombie Proliferation):** Якщо дочірній процес `ssh` завершує роботу (наприклад, через розрив сесії або помилку автентифікації), запис про нього залишається у таблиці процесів ядра Linux у стані `Z` (Zombie) доти, доки батьківський процес не виконає системний виклик `waitpid()`. У разі постійних перезапусків це призводить до вичерпання системного пулу PID.
4. **Аварійне завершення від сигналу `SIGPIPE`:** Якщо супервізор або прикладний код намагається виконати запис у сокет або канал, який уже був закритий протилежною стороною, ядро Linux надсилає процесу сигнал `SIGPIPE`. За замовчуванням дія цього сигналу полягає у негайному примусовому завершенні програми без створення дампу пам'яті.

## Механізм неблокуючого зондування сокета

Для перевірки реальної працездатності прокинутого порту супервізор виконує спеціальний неблокуючий алгоритм зондування:

```
[socket(AF_INET, SOCK_STREAM)]
             │
             ▼
[fcntl(O_NONBLOCK)] ──► переведення сокета в неблокуючий режим
             │
             ▼
[connect(127.0.0.1:port)]
       ├── res == 0 ────────────────────────► Успіх (порт миттєво відкритий)
       └── errno == EINPROGRESS
             │
             ▼
[poll(&pfd, 1, timeout_ms)]
       ├── timeout (0) ─────────────────────► Помилка (порт не відповів за таймаут)
       └── POLLOUT
             │
             ▼
[getsockopt(SOL_SOCKET, SO_ERROR)]
       ├── err == 0 ────────────────────────► Успіх (рукостискання завершено)
       └── err != 0 (ECONNREFUSED) ────────► Помилка (порт закритий)
```

1. Створюється новий сокет `AF_INET`, `SOCK_STREAM`.
2. За допомогою `fcntl()` на дескриптор встановлюється прапорець `O_NONBLOCK`.
3. Викликається `connect()` до `127.0.0.1:local_port`. Оскільки сокет неблокуючий, ядро негайно повертає керування:
   - Якщо `connect()` повернув `0`, з'єднання встановлено миттєво (типово для локальної петлі loopback).
   - Якщо повернуто `-1`, а змінна `errno` дорівнює `EINPROGRESS`, це означає, що TCP-рукостискання розпочато, але ще не завершено. Будь-який інший код `errno` свідчить про негайну відмову.
4. Викликається системний виклик `poll()` з обмеженим таймаутом (наприклад, 1000 мс) та подією `POLLOUT`.
5. Якщо `poll()` повертає подію `POLLOUT`, супервізор обов'язково викликає `getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len)`. Тільки якщо значення `err == 0`, порт вважається повністю справним і готовим приймати трафік.
6. Дескриптор сокета закривається викликом `close()`.

## Реалізація супервізора: C та сучасний C++

Нижче наведено повнофункціональні реалізації супервізора мовами C та C++.

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
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

static volatile sig_atomic_t g_running = 1;
static volatile sig_atomic_t g_child_dead = 0;

static void handle_sigterm(int sig) {
    (void)sig;
    g_running = 0;
}

static void handle_sigchld(int sig) {
    (void)sig;
    g_child_dead = 1;
}

/* Неблокуюча перевірка доступності локального TCP-порту */
static int probe_local_port(int port, int timeout_ms) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        return -1;
    }

    int flags = fcntl(fd, F_GETFL, 0);
    if (flags < 0 || fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        close(fd);
        return -1;
    }

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((uint16_t)port);
    inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

    int res = connect(fd, (struct sockaddr*)&addr, sizeof(addr));
    if (res == 0) {
        close(fd);
        return 0; /* Порт негайно відповів */
    }

    if (errno != EINPROGRESS) {
        close(fd);
        return -1; /* Порт закритий або збій */
    }

    struct pollfd pfd;
    pfd.fd = fd;
    pfd.events = POLLOUT;
    pfd.revents = 0;

    int poll_res = poll(&pfd, 1, timeout_ms);
    if (poll_res > 0 && (pfd.revents & POLLOUT)) {
        int err = 0;
        socklen_t len = sizeof(err);
        if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) == 0 && err == 0) {
            close(fd);
            return 0; /* Успішне підключення */
        }
    }

    close(fd);
    return -1;
}

/* Запуск процесу SSH у фоновому режимі */
static pid_t launch_ssh_tunnel(const char *host, int local_port, const char *remote_dest) {
    char forward_arg[256];
    snprintf(forward_arg, sizeof(forward_arg), "%d:%s", local_port, remote_dest);

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return -1;
    }

    if (pid == 0) {
        /* Дочірній процес: запуск клієнта OpenSSH */
        char *args[] = {
            "ssh",
            "-N",
            "-L", forward_arg,
            "-o", "ExitOnForwardFailure=yes",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=3",
            "-o", "BatchMode=yes",
            (char *)host,
            NULL
        };
        execvp("ssh", args);
        perror("execvp ssh");
        _exit(127);
    }

    return pid;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <ssh_host> <local_port> <remote_host:port>\n", argv[0]);
        fprintf(stderr, "Приклад: %s user@gateway.domain 5432 10.0.1.5:5432\n", argv[0]);
        return 1;
    }

    const char *ssh_host = argv[1];
    int local_port = atoi(argv[2]);
    const char *remote_dest = argv[3];

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_sigterm;
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGINT, &sa, NULL);

    struct sigaction sc;
    memset(&sc, 0, sizeof(sc));
    sc.sa_handler = handle_sigchld;
    sc.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    sigaction(SIGCHLD, &sc, NULL);

    signal(SIGPIPE, SIG_IGN);

    printf("[supervisor] Запуск супервізора тунелю для 127.0.0.1:%d -> %s через %s\n",
           local_port, remote_dest, ssh_host);

    pid_t child_pid = -1;
    int backoff_sec = 2;

    while (g_running) {
        if (child_pid <= 0) {
            printf("[supervisor] Запуск процесу ssh...\n");
            child_pid = launch_ssh_tunnel(ssh_host, local_port, remote_dest);
            if (child_pid <= 0) {
                sleep((unsigned int)backoff_sec);
                backoff_sec = (backoff_sec < 30) ? backoff_sec * 2 : 30;
                continue;
            }
            g_child_dead = 0;
            sleep(2); /* Пауза на ініціалізацію сокета */
        }

        if (g_child_dead) {
            int status;
            pid_t p = waitpid(child_pid, &status, WNOHANG);
            if (p > 0) {
                printf("[supervisor] Процес ssh (PID %d) завершився зі статусом %d\n", child_pid, status);
                child_pid = -1;
                sleep((unsigned int)backoff_sec);
                continue;
            }
        }

        /* Зондуємо локальний порт */
        if (probe_local_port(local_port, 1000) == 0) {
            backoff_sec = 2; /* Тунель здоровий, скидаємо затримку */
            sleep(5);
        } else {
            printf("[supervisor] Зонд не вдався! Локальний порт %d не відповідає.\n", local_port);
            if (child_pid > 0) {
                kill(child_pid, SIGTERM);
                sleep(1);
                kill(child_pid, SIGKILL);
                waitpid(child_pid, NULL, 0);
                child_pid = -1;
            }
            sleep((unsigned int)backoff_sec);
            backoff_sec = (backoff_sec < 30) ? backoff_sec * 2 : 30;
        }
    }

    if (child_pid > 0) {
        printf("[supervisor] Зупинка дочірнього процесу ssh (PID %d)...\n", child_pid);
        kill(child_pid, SIGTERM);
        waitpid(child_pid, NULL, 0);
    }

    printf("[supervisor] Роботу завершено.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <chrono>
#include <thread>
#include <atomic>
#include <expected>
#include <system_error>
#include <cstring>
#include <csignal>
#include <unistd.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/wait.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace {
    std::atomic<bool> g_running{true};
    std::atomic<bool> g_child_dead{false};

    void signal_handler(int sig) noexcept {
        if (sig == SIGTERM || sig == SIGINT) {
            g_running.store(false);
        } else if (sig == SIGCHLD) {
            g_child_dead.store(true);
        }
    }

    // RAII-обгортка над сокетним файловим дескриптором
    class UniqueFd {
    public:
        constexpr UniqueFd() noexcept : fd_(-1) {}
        explicit constexpr UniqueFd(int fd) noexcept : fd_(fd) {}
        
        ~UniqueFd() {
            reset();
        }

        UniqueFd(const UniqueFd&) = delete;
        UniqueFd& operator=(const UniqueFd&) = delete;

        UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) {
            other.fd_ = -1;
        }

        UniqueFd& operator=(UniqueFd&& other) noexcept {
            if (this != &other) {
                reset();
                fd_ = other.fd_;
                other.fd_ = -1;
            }
            return *this;
        }

        [[nodiscard]] constexpr int get() const noexcept { return fd_; }
        [[nodiscard]] constexpr bool valid() const noexcept { return fd_ >= 0; }

        void reset(int new_fd = -1) noexcept {
            if (fd_ >= 0) {
                ::close(fd_);
            }
            fd_ = new_fd;
        }

    private:
        int fd_{-1};
    };

    // RAII-керування процесом
    class ProcessGuard {
    public:
        constexpr ProcessGuard() noexcept : pid_(-1) {}
        explicit constexpr ProcessGuard(pid_t pid) noexcept : pid_(pid) {}

        ~ProcessGuard() {
            terminate();
        }

        ProcessGuard(const ProcessGuard&) = delete;
        ProcessGuard& operator=(const ProcessGuard&) = delete;

        ProcessGuard(ProcessGuard&& other) noexcept : pid_(other.pid_) {
            other.pid_ = -1;
        }

        ProcessGuard& operator=(ProcessGuard&& other) noexcept {
            if (this != &other) {
                terminate();
                pid_ = other.pid_;
                other.pid_ = -1;
            }
            return *this;
        }

        [[nodiscard]] constexpr pid_t get() const noexcept { return pid_; }
        [[nodiscard]] constexpr bool active() const noexcept { return pid_ > 0; }

        void release() noexcept {
            pid_ = -1;
        }

        void terminate() noexcept {
            if (pid_ > 0) {
                ::kill(pid_, SIGTERM);
                int status = 0;
                for (int i = 0; i < 10; ++i) {
                    if (::waitpid(pid_, &status, WNOHANG) > 0) {
                        pid_ = -1;
                        return;
                    }
                    std::this_thread::sleep_for(std::chrono::milliseconds(100));
                }
                ::kill(pid_, SIGKILL);
                ::waitpid(pid_, &status, 0);
                pid_ = -1;
            }
        }

    private:
        pid_t pid_{-1};
    };
}

class TunnelSupervisor {
public:
    TunnelSupervisor(std::string host, int local_port, std::string remote_dest)
        : host_(std::move(host)), local_port_(local_port), remote_dest_(std::move(remote_dest)) {}

    void run() {
        std::cout << "[supervisor++] Запуск для 127.0.0.1:" << local_port_
                  << " -> " << remote_dest_ << " через " << host_ << '\n';

        auto backoff = std::chrono::seconds(2);

        while (g_running.load()) {
            if (!process_.active()) {
                auto start_res = spawn_ssh();
                if (!start_res) {
                    std::cerr << "[supervisor++] Помилка fork: " << start_res.error().message() << '\n';
                    std::this_thread::sleep_for(backoff);
                    backoff = std::min(backoff * 2, std::chrono::seconds(30));
                    continue;
                }
                process_ = ProcessGuard(*start_res);
                g_child_dead.store(false);
                std::this_thread::sleep_for(std::chrono::seconds(2));
            }

            if (g_child_dead.load()) {
                int status = 0;
                pid_t p = ::waitpid(process_.get(), &status, WNOHANG);
                if (p > 0) {
                    std::cout << "[supervisor++] SSH завершився зі статусом " << status << '\n';
                    process_.release();
                    std::this_thread::sleep_for(backoff);
                    continue;
                }
            }

            if (probe_port(std::chrono::milliseconds(1000))) {
                backoff = std::chrono::seconds(2);
                std::this_thread::sleep_for(std::chrono::seconds(5));
            } else {
                std::cout << "[supervisor++] Зонд не вдався! Перезапуск тунелю...\n";
                process_.terminate();
                std::this_thread::sleep_for(backoff);
                backoff = std::min(backoff * 2, std::chrono::seconds(30));
            }
        }

        std::cout << "[supervisor++] Завершення роботи.\n";
    }

private:
    [[nodiscard]] std::expected<pid_t, std::error_code> spawn_ssh() {
        const std::string forward_spec = std::to_string(local_port_) + ":" + remote_dest_;

        pid_t pid = ::fork();
        if (pid < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        if (pid == 0) {
            std::vector<const char*> args = {
                "ssh",
                "-N",
                "-L", forward_spec.c_str(),
                "-o", "ExitOnForwardFailure=yes",
                "-o", "ServerAliveInterval=15",
                "-o", "ServerAliveCountMax=3",
                "-o", "BatchMode=yes",
                host_.c_str(),
                nullptr
            };
            ::execvp("ssh", const_cast<char* const*>(args.data()));
            ::_exit(127);
        }

        return pid;
    }

    [[nodiscard]] bool probe_port(std::chrono::milliseconds timeout) const {
        UniqueFd sock(::socket(AF_INET, SOCK_STREAM, 0));
        if (!sock.valid()) {
            return false;
        }

        int flags = ::fcntl(sock.get(), F_GETFL, 0);
        if (flags < 0 || ::fcntl(sock.get(), F_SETFL, flags | O_NONBLOCK) < 0) {
            return false;
        }

        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(static_cast<uint16_t>(local_port_));
        ::inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);

        int res = ::connect(sock.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
        if (res == 0) {
            return true;
        }

        if (errno != EINPROGRESS) {
            return false;
        }

        pollfd pfd{};
        pfd.fd = sock.get();
        pfd.events = POLLOUT;

        int poll_res = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
        if (poll_res > 0 && (pfd.revents & POLLOUT)) {
            int err = 0;
            socklen_t len = sizeof(err);
            if (::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &err, &len) == 0 && err == 0) {
                return true;
            }
        }

        return false;
    }

    std::string host_;
    int local_port_;
    std::string remote_dest_;
    ProcessGuard process_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <ssh_host> <local_port> <remote_host:port>\n";
        return 1;
    }

    struct sigaction sa{};
    sa.sa_handler = signal_handler;
    ::sigaction(SIGTERM, &sa, nullptr);
    ::sigaction(SIGINT, &sa, nullptr);

    struct sigaction sc{};
    sc.sa_handler = signal_handler;
    sc.sa_flags = SA_RESTART | SA_NOCLDSTOP;
    ::sigaction(SIGCHLD, &sc, nullptr);

    ::signal(SIGPIPE, SIG_IGN);

    TunnelSupervisor supervisor(argv[1], std::stoi(argv[2]), argv[3]);
    supervisor.run();

    return 0;
}
```
:::

## Відмінності архітектури реалізацій у C та C++

Порівняння двох реалізацій наочно демонструє переваги та парадигми кожної мови:

1. **Керування ресурсами (Resource Management):**
   - У версії C кожен дескриптор сокета вимагає ручного виклику `close(fd)` на кожній гілці завершення функції (наприклад, при помилках `fcntl`, `connect` або `getsockopt`). Будь-який пропущений шлях повернення створює витік файлових дескрипторів (`EMFILE`).
   - У версії C++ застосовано ідіому RAII (Resource Acquisition Is Initialization) через клас `UniqueFd`. Деструктор автоматично закриває сокет при виході з області видимості за будь-яких умов, включно з генерацією винятків або поверненням через `return`.
2. **Керування життєвим циклом процесу:**
   - У C завершення дочірнього процесу вимагає послідовного надсилання сигналів `SIGTERM`, короткої паузи та примусового `SIGKILL` з обов'язковим викликом `waitpid()` у тілі головної функції.
   - У C++ цю логіку інкапсульовано в обгортці `ProcessGuard`, яка автоматично ліквідує завислий дочірній процес у своєму деструкторі.
3. **Обробка помилок:**
   - C спирається на глобальну змінну `errno` та повернення цілочисельних кодів `-1 / 0`.
   - C++ використовує шаблон `std::expected<pid_t, std::error_code>` (C++23) для строго типізованої передачі статусу виконання без використання винятків на критичних шляхах.

## Стратегія експоненційного відступу та системні переваги

Реалізація затримки перезапуску (Backoff Strategy) є обов'язковою вимогою для стабільності операційної системи. Якщо віддалений сервер тимчасово недоступний (наприклад, виконується планове перезавантаження або відсутній інтернет-зв'язок), нескінченний миттєвий перезапуск у щільному циклі створює шторм викликів `fork()` та `execvp()`, завантажуючи центральний процесор на 100% і швидко заповнюючи системні журнали помилками.

Супервізор починає з мінімальної затримки 2 секунди, подвоює її після кожної невдалої спроби (`2с → 4с → 8с → 16с → 30с`) і утримує на максимальній стелі 30 секунд. Як тільки зондування сокета підтверджує успішну передачу даних, лічильник затримки миттєво скидається до базових 2 секунд.

На відміну від утиліти `autossh`, яка вимагає виділення двох додаткових TCP-портів для передачі ехо-пакетів і додаткової конфігурації брандмауера на обох вузлах, розроблений супервізор використовує пряме прикладне зондування вже відкритого локального сокета. Це робить його повністю прозорим для мережевої інфраструктури та придатним для розгортання в обмежених контейнеризованих середовищах.

## Простеження виконання через strace

Для діагностики поведінки зондувального коду в системі Linux можна використати утиліту системного трасування `strace`:

```bash
strace -e trace=socket,connect,fcntl,poll,getsockopt,close ./supervisor user@bastion 5432 10.0.1.5:5432
```

Типовий лог успішного зондування:

```
socket(AF_INET, SOCK_STREAM, IPPROTO_IP) = 3
fcntl(3, F_GETFL)                       = 0x2 (flags O_RDWR)
fcntl(3, F_SETFL, O_RDWR|O_NONBLOCK)    = 0
connect(3, {sa_family=AF_INET, sin_port=htons(5432), sin_addr=inet_addr("127.0.0.1")}, 16) = -1 EINPROGRESS
poll([{fd=3, events=POLLOUT}], 1, 1000) = 1 ([{fd=3, revents=POLLOUT}])
getsockopt(3, SOL_SOCKET, SO_ERROR, [0], [4]) = 0
close(3)                                = 0
```

Цей вивід наочно підтверджує, що зонд пройшов повний неблокуючий цикл без жодної зупинки або затримки основного циклу обробки.

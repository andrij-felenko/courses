# ⚙️ Автоматизований зонд мережевої досяжності: від імені до банера SSH

Коли віддалений хост або служба перестає відповідати, інженеру необхідно за лічені секунди отримати об'єктивний діагноз: на якому саме рівні (DNS, маршрутизація, TCP-порт чи прикладний демон) обривається зв'язок. Ручний запуск кількох утиліт забирає дорогоцінний час і часто дає суперечливі результати через різні механізми тайм-аутів. Тут розібрано архітектуру та реалізовано автономний низькорівневий діагностичний зонд, який послідовно виконує всі 4 ланки перевірки — від системного виклику `getaddrinfo` до неблокуючого тристороннього рукостискання TCP та зчитування стартового банера протоколу SSH.

---

## 1. Архітектура та послідовність роботи зонда

Програма реалізує конвеєр швидкої детермінованої перевірки, розрахований на роботу в умовах нестабільної мережі:

```
[Вхід: hostname / IP та port]
            │
            ▼
[Крок 1: getaddrinfo()] ─── помилка EAI ───> [ЗВІТ: Збій розв'язання імені (DNS/NSS)]
            │ успіх (отримано sockaddr)
            ▼
[Крок 2: Оцінка маршруту] ─── помилка ENETUNREACH ───> [ЗВІТ: Немає маршруту в ядрі (FIB)]
            │ успіх
            ▼
[Крок 3: Неблокуючий connect()]
  - fcntl(O_NONBLOCK)
  - connect() -> очікуємо EINPROGRESS
  - poll() з таймаутом 3000 мс
  - getsockopt(SO_ERROR)
            │
            ├─ помилка ECONNREFUSED ───> [ЗВІТ: Порт закритий / RST (Connection refused)]
            ├─ помилка ETIMEDOUT    ───> [ЗВІТ: Мовчазний DROP / Firewall (Timed out)]
            ├─ помилка EHOSTUNREACH ───> [ЗВІТ: Хост недосяжний / ARP failure]
            │ успіх (сокети з'єднано)
            ▼
[Крок 4: L7 Зондування банера]
  - Очікування перших байтів від сервера (2000 мс)
  - Для порту 22: зчитування ідентифікатора SSH (наприклад, "SSH-2.0-OpenSSH_9.6p1")
            │
            ▼
[ЗВІТ: Вузол повністю досяжний на рівнях L3, L4 та L7]
```

Головна інженерна перевага утиліти полягає в переведенні сокета в неблокуючий режим `O_NONBLOCK`. Стандартний блокуючий виклик `connect()` при скиданні пакетів фаєрволом (DROP) зависає в ядрі на 60–120 секунд через системні ретрансміти `tcp_syn_retries`. Неблокуючий виклик негайно повертає керування з кодом `-1` та `errno = EINPROGRESS`, після чого функція `poll()` очікує подій `POLLOUT` або `POLLERR` рівно задану кількість мілісекунд.

---

## 2. Реалізація діагностичного зонда

Програму спроєктовано для компіляції як на чистому C (стандарт C99/POSIX.1-2008), так і на сучасному ідіоматичному C++20 з використанням концепцій RAII, `std::expected` та безпечної роботи з пам'яттю.

:::tabs
== C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define CONNECT_TIMEOUT_MS 3000
#define BANNER_TIMEOUT_MS  2000
#define BUFFER_SIZE        512

typedef struct {
    char ip_str[INET6_ADDRSTRLEN];
    int family;
    int error_stage; // 1: DNS, 2: Connect, 3: Banner, 0: OK
    int sys_errno;
    char banner[BUFFER_SIZE];
} ProbeResult;

static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int probe_target(const char *host, const char *port_str, ProbeResult *res) {
    memset(res, 0, sizeof(*res));
    
    // Крок 1: Розв'язання імені через NSS / DNS
    struct addrinfo hints;
    struct addrinfo *addr_list = NULL;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;     // IPv4 або IPv6
    hints.ai_socktype = SOCK_STREAM; // TCP
    hints.ai_protocol = IPPROTO_TCP;

    int gai_rc = getaddrinfo(host, port_str, &hints, &addr_list);
    if (gai_rc != 0) {
        res->error_stage = 1;
        res->sys_errno = gai_rc;
        return -1;
    }

    int sockfd = -1;
    int connect_success = 0;
    struct addrinfo *rp = NULL;

    // Перебір знайдених IP-адрес
    for (rp = addr_list; rp != NULL; rp = rp->ai_next) {
        void *raw_addr = NULL;
        if (rp->ai_family == AF_INET) {
            raw_addr = &((struct sockaddr_in *)rp->ai_addr)->sin_addr;
        } else if (rp->ai_family == AF_INET6) {
            raw_addr = &((struct sockaddr_in6 *)rp->ai_addr)->sin6_addr;
        }
        inet_ntop(rp->ai_family, raw_addr, res->ip_str, sizeof(res->ip_str));
        res->family = rp->ai_family;

        sockfd = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (sockfd < 0) {
            continue;
        }

        if (set_nonblocking(sockfd) < 0) {
            close(sockfd);
            sockfd = -1;
            continue;
        }

        // Крок 2 та 3: Неблокуюче підключення TCP
        int rc = connect(sockfd, rp->ai_addr, rp->ai_addrlen);
        if (rc == 0) {
            // Миттєве підключення (типово для loopback)
            connect_success = 1;
            break;
        }

        if (errno == EINPROGRESS) {
            struct pollfd pfd;
            pfd.fd = sockfd;
            pfd.events = POLLOUT | POLLERR | POLLHUP;
            pfd.revents = 0;

            int poll_rc;
            do {
                poll_rc = poll(&pfd, 1, CONNECT_TIMEOUT_MS);
            } while (poll_rc < 0 && errno == EINTR);

            if (poll_rc > 0) {
                int sock_err = 0;
                socklen_t opt_len = sizeof(sock_err);
                if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
                    res->sys_errno = errno;
                } else if (sock_err != 0) {
                    res->sys_errno = sock_err; // ECONNREFUSED, ETIMEDOUT, EHOSTUNREACH
                } else {
                    connect_success = 1;
                    break;
                }
            } else if (poll_rc == 0) {
                res->sys_errno = ETIMEDOUT; // Таймаут очікування SYN-ACK
            } else {
                res->sys_errno = errno;
            }
        } else {
            res->sys_errno = errno; // ENETUNREACH або EHOSTUNREACH
        }

        close(sockfd);
        sockfd = -1;
    }

    freeaddrinfo(addr_list);

    if (!connect_success) {
        res->error_stage = 2;
        return -1;
    }

    // Крок 4: Перевірка прикладного рівня L7 (зчитування банера)
    struct pollfd pfd_read;
    pfd_read.fd = sockfd;
    pfd_read.events = POLLIN;
    pfd_read.revents = 0;

    int poll_read_rc;
    do {
        poll_read_rc = poll(&pfd_read, 1, BANNER_TIMEOUT_MS);
    } while (poll_read_rc < 0 && errno == EINTR);

    if (poll_read_rc > 0 && (pfd_read.revents & POLLIN)) {
        ssize_t n = read(sockfd, res->banner, sizeof(res->banner) - 1);
        if (n > 0) {
            res->banner[n] = '\0';
            // Видаляємо кінцеві перенесення рядків
            char *newline = strpbrk(res->banner, "\r\n");
            if (newline) *newline = '\0';
        }
    } else {
        snprintf(res->banner, sizeof(res->banner), "(сервер мовчить, немає початкового банера)");
    }

    close(sockfd);
    res->error_stage = 0;
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <host> <port>\n", argv[0]);
        return 1;
    }

    const char *target_host = argv[1];
    const char *target_port = argv[2];
    ProbeResult res;

    printf("=== ДІАГНОСТИКА ЗВ'ЯЗКУ: %s:%s ===\n", target_host, target_port);

    int rc = probe_target(target_host, target_port, &res);
    if (rc == 0) {
        printf("[+] Рівень 1 (DNS):   Успіх -> IP-адреса %s (%s)\n",
               res.ip_str, res.family == AF_INET ? "IPv4" : "IPv6");
        printf("[+] Рівень 2-3 (TCP): З'єднання встановлено (порт %s відкритий)\n", target_port);
        printf("[+] Рівень 4 (L7):    Банер служби: \"%s\"\n", res.banner);
        printf("\nРЕЗУЛЬТАТ: Вузол повністю доступний.\n");
        return 0;
    }

    printf("[-] Помилка на стадії %d:\n", res.error_stage);
    if (res.error_stage == 1) {
        printf("    Стадія 1 (Розпізнавання імені DNS/NSS):\n");
        printf("    Код помилки: %s\n", gai_strerror(res.sys_errno));
        printf("    Рекомендація: Перевірте /etc/resolv.conf, systemd-resolved та правильність імені.\n");
    } else if (res.error_stage == 2) {
        printf("    Стадія 2-3 (Маршрутизація / TCP Транспорт):\n");
        printf("    Цільова IP-адреса: %s\n", res.ip_str[0] ? res.ip_str : "(невідома)");
        printf("    Системна помилка errno %d: %s\n", res.sys_errno, strerror(res.sys_errno));
        if (res.sys_errno == ECONNREFUSED) {
            printf("    Аналіз: Отримано TCP RST. Сервіс не запущено або порт слухається лише на 127.0.0.1.\n");
        } else if (res.sys_errno == ETIMEDOUT) {
            printf("    Аналіз: Мовчазний DROP пакета. Перевірте nftables, Security Group або маршрутизатор.\n");
        } else if (res.sys_errno == ENETUNREACH || res.sys_errno == EHOSTUNREACH) {
            printf("    Аналіз: Відсутній маршрут у ядрі або L2-сусід не відповідає на ARP-запити.\n");
        }
    }

    return 2;
}
```
== C++
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <chrono>
#include <cstring>
#include <unistd.h>
#include <fcntl.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace net_probe {

using namespace std::chrono_literals;

enum class StageError {
    DnsResolution,
    RoutingOrTransport,
    BannerRead
};

struct DiagnosticReport {
    std::string resolved_ip;
    std::string ip_family;
    bool port_open{false};
    std::string banner;
};

struct DiagnosticFailure {
    StageError stage;
    int error_code{0};
    std::string message;
    std::string target_ip;
};

class SocketHandle {
public:
    explicit SocketHandle(int fd = -1) noexcept : m_fd(fd) {}
    ~SocketHandle() noexcept {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }

    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;

    SocketHandle(SocketHandle&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (m_fd >= 0) ::close(m_fd);
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    bool set_nonblocking() noexcept {
        const int flags = ::fcntl(m_fd, F_GETFL, 0);
        if (flags == -1) return false;
        return ::fcntl(m_fd, F_SETFL, flags | O_NONBLOCK) != -1;
    }

private:
    int m_fd{-1};
};

class NetworkProber {
public:
    static std::expected<DiagnosticReport, DiagnosticFailure> probe(
        std::string_view host,
        std::string_view port,
        std::chrono::milliseconds timeout = 3000ms) 
    {
        DiagnosticReport report;

        // Крок 1: Розв'язання імені в IP-адреси
        addrinfo hints{};
        hints.ai_family = AF_UNSPEC;
        hints.ai_socktype = SOCK_STREAM;
        hints.ai_protocol = IPPROTO_TCP;

        addrinfo* raw_list = nullptr;
        const int gai_rc = ::getaddrinfo(host.data(), port.data(), &hints, &raw_list);
        if (gai_rc != 0) {
            return std::unexpected(DiagnosticFailure{
                .stage = StageError::DnsResolution,
                .error_code = gai_rc,
                .message = ::gai_strerror(gai_rc)
            });
        }

        // Автоматичне звільнення списку addrinfo
        struct AddrInfoGuard {
            addrinfo* ptr;
            ~AddrInfoGuard() { if (ptr) ::freeaddrinfo(ptr); }
        } guard{raw_list};

        int last_connect_error = 0;
        std::string candidate_ip;

        for (auto* rp = raw_list; rp != nullptr; rp = rp->ai_next) {
            char ip_buffer[INET6_ADDRSTRLEN]{};
            const void* addr_src = (rp->ai_family == AF_INET)
                ? static_cast<const void*>(&reinterpret_cast<const sockaddr_in*>(rp->ai_addr)->sin_addr)
                : static_cast<const void*>(&reinterpret_cast<const sockaddr_in6*>(rp->ai_addr)->sin6_addr);

            ::inet_ntop(rp->ai_family, addr_src, ip_buffer, sizeof(ip_buffer));
            candidate_ip = ip_buffer;
            report.resolved_ip = candidate_ip;
            report.ip_family = (rp->ai_family == AF_INET) ? "IPv4" : "IPv6";

            SocketHandle sock(::socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol));
            if (!sock.valid()) {
                last_connect_error = errno;
                continue;
            }

            if (!sock.set_nonblocking()) {
                last_connect_error = errno;
                continue;
            }

            // Крок 2 та 3: Неблокуюче підключення TCP
            const int rc = ::connect(sock.get(), rp->ai_addr, rp->ai_addrlen);
            if (rc == 0) {
                report.port_open = true;
                return inspect_application_layer(std::move(sock), std::move(report));
            }

            if (errno == EINPROGRESS) {
                pollfd pfd{};
                pfd.fd = sock.get();
                pfd.events = POLLOUT | POLLERR | POLLHUP;

                int poll_rc;
                do {
                    poll_rc = ::poll(&pfd, 1, static_cast<int>(timeout.count()));
                } while (poll_rc < 0 && errno == EINTR);

                if (poll_rc > 0) {
                    int sock_err = 0;
                    socklen_t opt_len = sizeof(sock_err);
                    if (::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
                        last_connect_error = errno;
                    } else if (sock_err != 0) {
                        last_connect_error = sock_err; // ECONNREFUSED / ETIMEDOUT / EHOSTUNREACH
                    } else {
                        report.port_open = true;
                        return inspect_application_layer(std::move(sock), std::move(report));
                    }
                } else if (poll_rc == 0) {
                    last_connect_error = ETIMEDOUT;
                } else {
                    last_connect_error = errno;
                }
            } else {
                last_connect_error = errno;
            }
        }

        return std::unexpected(DiagnosticFailure{
            .stage = StageError::RoutingOrTransport,
            .error_code = last_connect_error,
            .message = std::strerror(last_connect_error),
            .target_ip = candidate_ip
        });
    }

private:
    static std::expected<DiagnosticReport, DiagnosticFailure> inspect_application_layer(
        SocketHandle sock, DiagnosticReport report) 
    {
        pollfd pfd_read{};
        pfd_read.fd = sock.get();
        pfd_read.events = POLLIN;

        // Очікування банера до 2000 мс
        int poll_rc;
        do {
            poll_rc = ::poll(&pfd_read, 1, 2000);
        } while (poll_rc < 0 && errno == EINTR);

        if (poll_rc > 0 && (pfd_read.revents & POLLIN)) {
            char buffer[512]{};
            const ssize_t bytes = ::read(sock.get(), buffer, sizeof(buffer) - 1);
            if (bytes > 0) {
                std::string banner_str(buffer, static_cast<size_t>(bytes));
                const auto pos = banner_str.find_first_of("\r\n");
                if (pos != std::string::npos) {
                    banner_str.resize(pos);
                }
                report.banner = std::move(banner_str);
            }
        } else {
            report.banner = "(сервер мовчить, немає стартового банера)";
        }

        return report;
    }
};

} // namespace net_probe

int main(int argc, char* argv[]) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <host> <port>\n";
        return 1;
    }

    const std::string_view target_host = argv[1];
    const std::string_view target_port = argv[2];

    std::cout << "=== ДІАГНОСТИКА ЗВ'ЯЗКУ: " << target_host << ":" << target_port << " ===\n";

    auto result = net_probe::NetworkProber::probe(target_host, target_port);
    if (result.has_value()) {
        const auto& rep = result.value();
        std::cout << "[+] Рівень 1 (DNS):   Успіх -> IP-адреса " << rep.resolved_ip << " (" << rep.ip_family << ")\n";
        std::cout << "[+] Рівень 2-3 (TCP): З'єднання встановлено (порт " << target_port << " відкритий)\n";
        std::cout << "[+] Рівень 4 (L7):    Банер служби: \"" << rep.banner << "\"\n";
        std::cout << "\nРЕЗУЛЬТАТ: Вузол повністю доступний.\n";
        return 0;
    }

    const auto& fail = result.error();
    std::cout << "[-] Відмова на стадії ";
    switch (fail.stage) {
        case net_probe::StageError::DnsResolution:
            std::cout << "1 (Розпізнавання імені DNS/NSS):\n"
                      << "    Код помилки: " << fail.message << "\n"
                      << "    Рекомендація: Перевірте DNS-сервер та файл /etc/hosts.\n";
            break;
        case net_probe::StageError::RoutingOrTransport:
            std::cout << "2-3 (Маршрутизація / TCP Транспорт):\n"
                      << "    Цільова IP-адреса: " << fail.target_ip << "\n"
                      << "    Системна помилка errno " << fail.error_code << ": " << fail.message << "\n";
            if (fail.error_code == ECONNREFUSED) {
                std::cout << "    Аналіз: Отримано TCP RST. Процес не слухає порт або фаєрвол REJECT.\n";
            } else if (fail.error_code == ETIMEDOUT) {
                std::cout << "    Аналіз: Мовчазний DROP пакета SYN. Перевірте nftables або хмарні фаєрволи.\n";
            } else if (fail.error_code == ENETUNREACH || fail.error_code == EHOSTUNREACH) {
                std::cout << "    Аналіз: Немає маршруту в таблиці FIB або збій виявлення L2-сусідів (ARP).\n";
            }
            break;
        default:
            std::cout << "невідомій стадії.\n";
            break;
    }

    return 2;
}
```
:::

---

## 3. Глибокий розбір системних механізмів

### 3.1. Переходи станів сокета в ядрі при неблокуючому `connect()`
У стандартному блокуючому режимі системний виклик `connect()` переводить викликаючий процес у стан сну (`TASK_INTERRUPTIBLE`) доти, доки віддалений хост не відповість пакетом `SYN-ACK` або `TCP RST`. Якщо ж пакети поглинаються фаєрволом, процес блокується на 60–130 секунд через системні ретрансміти ядра.

У неблокуючому режимі (`O_NONBLOCK`), який налаштовується функцією `fcntl(fd, F_SETFL, flags | O_NONBLOCK)`, функція ядра `tcp_v4_connect` переводить внутрішню структуру сокета `struct sock` у стан `TCP_SYN_SENT`, відправляє перший пакет `SYN` і негайно повертає керування в простір користувача зі значенням `-1` та `errno = EINPROGRESS`.

Коли тристороннє рукостискання завершується (успіхом чи скиданням), ядро викликає функцію `sock_def_write_space()`, яка будить усі потоки, що очікують на черзі сокета `sk_sleep`. Утиліта `poll()` або системний виклик `epoll_wait()` фіксують подію готовності до запису `POLLOUT`.

### 3.2. Чому необхідний виклик `getsockopt(..., SO_ERROR)`
Стандарт POSIX визначає важливий крайовий випадок асинхронних сокетів: **подія `POLLOUT` генерується як у разі успішного підключення, так і у разі фатального збою (наприклад, отримання `TCP RST` чи повідомлення ICMP Host Unreachable)**. Більше того, на різних операційних системах UNIX при скиданні з'єднання можуть генеруватися одночасно прапорці `POLLOUT | POLLERR | POLLHUP`.

Тому сам факт повернення з функції `poll()` не означає успішного з'єднання. Для вилучення реального результату операції викликають:

:::tabs
== C
```c
int sock_err = 0;
socklen_t opt_len = sizeof(sock_err);
if (getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
    perror("getsockopt");
}
```
== C++
```cpp
int sock_err = 0;
socklen_t opt_len = sizeof(sock_err);
if (::getsockopt(sock.get(), SOL_SOCKET, SO_ERROR, &sock_err, &opt_len) < 0) {
    std::cerr << "getsockopt failed: " << std::strerror(errno) << "\n";
}
```
:::

Цей виклик атомарно зчитує накопичений код помилки з поля `sk->sk_err` у пам'яті ядра та скидає її в нуль. Аналіз можливих значень:
* `sock_err == 0` — тристороннє рукостискання завершено успішно, сокет перейшов у стан `TCP_ESTABLISHED`.
* `sock_err == ECONNREFUSED` — отримано активний пакет `TCP RST` (порт не слухається або відхилений правилом фаєрволу `reject`).
* `sock_err == ETIMEDOUT` — таймаут очікування `SYN-ACK` вичерпано на рівні нашого таймера `poll()`.
* `sock_err == EHOSTUNREACH` — шлюз не зміг знайти MAC-адресу вузла (збій протоколу ARP або отримано `ICMP Host Unreachable`).

### 3.3. Захист від переривання сигналами (`EINTR`)
Під час виконання системного виклику `poll()` процес може отримати асинхронний сигнал ОС (наприклад, `SIGCHLD`, `SIGALRM` чи `SIGWINCH`). За замовчуванням виклик `poll()` переривається, повертаючи `-1` зі встановленою змінною `errno = EINTR`. Без обгортки `do ... while (poll_rc < 0 && errno == EINTR)` зонд міг би хибно повідомляти про таймаут або системний збій під час зміни розміру вікна термінала.

### 3.4. Обробка подвійного стека IPv4/IPv6 (Dual-Stack)
Утиліта використовує структуру `struct addrinfo` із прапорцем `hints.ai_family = AF_UNSPEC`. Функція `getaddrinfo()` повертає зв'язний список усіх знайдених адрес: спочатку AAAA (IPv6), потім A (IPv4).

Зонд послідовно ітерує список адрес: якщо спроба підключення до IPv6 завершується збоєм `ENETUNREACH` (наприклад, локальний інтернет-провайдер або маршрутизатор не підтримує IPv6), сокет негайно закривається, і програма переходить до наступного IPv4-вузла без зупинки роботи, реалізуючи алгоритм швидкого перемикання Happy Eyeballs (RFC 8305).

### 3.5. Зчитування стартового банера протоколу L7
Після успішного встановлення TCP-з'єднання зонд очікує надходження вхідних даних протягом 2000 мілісекунд через виклик `poll(POLLIN)`. Більшість мережевих служб (SSH, FTP, SMTP) згідно зі специфікаціями протоколів першими надсилають вітальний рядок ідентифікації.

Для протоколу SSH згідно з RFC 4253 сервер зобов'язаний негайно відправити текстовий рядок формату:

```
SSH-protoversion-softwareversion SP comments CR LF
```

Наприклад: `SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13`. Отримання цього рядка є беззаперечним доказом того, що демон `sshd` не просто відкрив порт, але й успішно ініціалізував внутрішній стан сесії, виділив пам'ять під буфери шифрування та готовий до криптографічного обміну ключами.

---

## 4. Інструкція зі збирання та приклади виводу

### Компіляція
Для збирання C-версії:
```sh
gcc -O2 -Wall -Wextra -std=c99 -o net_probe_c net_probe.c
```

Для збирання C++20 версії:
```sh
g++ -O2 -Wall -Wextra -std=c++20 -o net_probe_cpp net_probe.cpp
```

### Сценарій 1: Успішне підключення до SSH-сервера
```sh
$ ./net_probe_cpp node-01.internal 22
=== ДІАГНОСТИКА ЗВ'ЯЗКУ: node-01.internal:22 ===
[+] Рівень 1 (DNS):   Успіх -> IP-адреса 10.0.4.15 (IPv4)
[+] Рівень 2-3 (TCP): З'єднання встановлено (порт 22 відкритий)
[+] Рівень 4 (L7):    Банер служби: "SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13"

РЕЗУЛЬТАТ: Вузол повністю доступний.
```

### Сценарій 2: Закритий порт або демон впав (Connection refused)
```sh
$ ./net_probe_cpp node-01.internal 2222
=== ДІАГНОСТИКА ЗВ'ЯЗКУ: node-01.internal:2222 ===
[-] Відмова на стадії 2-3 (Маршрутизація / TCP Транспорт):
    Цільова IP-адреса: 10.0.4.15
    Системна помилка errno 111: Connection refused
    Аналіз: Отримано TCP RST. Процес не слухає порт або фаєрвол REJECT.
```

### Сценарій 3: Мовчазне скидання фаєрволом (Connection timed out)
```sh
$ ./net_probe_cpp node-01.internal 8080
=== ДІАГНОСТИКА ЗВ'ЯЗКУ: node-01.internal:8080 ===
[-] Відмова на стадії 2-3 (Маршрутизація / TCP Транспорт):
    Цільова IP-адреса: 10.0.4.15
    Системна помилка errno 110: Connection timed out
    Аналіз: Мовчазний DROP пакета SYN. Перевірте nftables або хмарні фаєрволи.
```

### Сценарій 4: Неіснуюче доменне ім'я (NXDOMAIN)
```sh
$ ./net_probe_cpp ghost-node.internal 22
=== ДІАГНОСТИКА ЗВ'ЯЗКУ: ghost-node.internal:22 ===
[-] Відмова на стадії 1 (Розпізнавання імені DNS/NSS):
    Код помилки: Name or service not known
    Рекомендація: Перевірте DNS-сервер та файл /etc/hosts.
```

Такий детальний і швидкий звіт дає змогу черговому інженеру однозначно локалізувати несправність за 3 секунди замість ручного збору логів та послідовного запуску розрізнених утиліт.

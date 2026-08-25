# ⚙️ Розробка стійкого клієнт-серверного додатку на SCTP з мультистрімінгом

Цей практичний проект демонструє створення надійної розподіленої системи керування та передачі телеметрії на базі протоколу SCTP (*Stream Control Transmission Protocol*, RFC 4960, RFC 6458, заголовок `netinet/sctp.h`, системна бібліотека `libsctp`). У межах єдиної асоціації реалізується паралельне функціонування двох ізольованих логічних каналів: каналу впорядкованих команд керування критичної важливості та високочастотного каналу телеметричних даних із миттєвою невпорядкованою доставкою без блокування початку черги (*Head-of-Line Blocking*).

---

## 1. Архітектура та постановка інженерної задачі

У сучасних телекомунікаційних мережах (площина керування 4G/5G), системах дистанційного пілотування безпілотних апаратів та комплексах промислової телемеханіки виникає гостра необхідність одночасної передачі двох принципово різних класів трафіку:

1. **Критичний потік команд керування (Control Plane):**  
   Потребує абсолютної надійності доставки та суворого збереження послідовності дій. Наприклад, команда конфігурації `INIT_SUBSYSTEM` обов'язково має бути оброблена сервером раніше за команду `ARM_ACTUATORS`. Втрата або зміна порядку проходження цих інструкцій призводить до аварійних збоїв апаратури.

2. **Високочастотний потік сенсорної телеметрії (Data Plane):**  
   Генерує десятки оновлень координат, напруги та кутових швидкостей на секунду. Для телеметрії ключовим параметром є мінімальна затримка (*low latency*). Якщо один пакет із координатами затримався або загубився на перевантаженому проміжному маршрутизаторі, приймальний вузол не повинен зупиняти обробку наступних свіжих вимірювань заради очікування застарілого кадру.

### Чому традиційні підходи зазнають невдачі

- **Спроба використати одне TCP-з'єднання:** TCP сприймає всі байти як єдину нерозривну послідовність. Якщо один пакет телеметрії втрачається, приймальний буфер ядра TCP блокує видачу всіх наступних байтів (включаючи критичні команди керування) до моменту прибуття повторно надісланого сегмента. Це класичне блокування початку черги (*Head-of-Line Blocking*), яке в умовах нестабільного радіоканалу спричиняє неприпустимі затримки реакції системи на команди оператора.
- **Спроба відкрити два незалежні TCP-з'єднання:** Подвоює кількість рукостискань, вимагає подвійного набору портів, споживає вдвічі більше пам'яті ядра під буфери та TCB, а головне — не забезпечує спільного керування перевантаженням і взаємного моніторингу працездатності фізичних лінків.
- **Спроба використати UDP:** Усуває блокування черги, проте змушує інженера вручну створювати в прикладному коді механізми ковзного вікна, таймери RTO, захист від дублювання та алгоритми Congestion Control для каналу керування.

### Архітектурне рішення на базі SCTP

SCTP надає вичерпну платформу для розв'язання цього протиріччя в межах **однієї асоціації**:
- **Потік 0 (`STREAM_CONTROL`):** надійна впорядкована доставка (`flags = 0`, `PPID = 0x0100`). Ядро виділяє потоку власний лічильник `SSN` (*Stream Sequence Number*), гарантуючи послідовне виконання команд.
- **Потік 1 (`STREAM_TELEMETRY`):** надійна невпорядкована доставка (`flags = SCTP_UNORDERED`, `PPID = 0x0200`). Чанки позначаються бітом `U=1` і передаються застосунку негайно після перевірки цілісності CRC32c, не блокуючи чергу та не очікуючи попередніх пакетів.
- **Підсистема сповіщень ядра (`SCTP_EVENTS`):** сервер і клієнт підписуються на події асоціації, отримуючи асинхронні повідомлення про відкриття/закриття зв'язку та зміну працездатності резервних IP-адрес при мультихоумінгу.

---

## 2. Реалізація сервера телеметрії та команд

Серверний процес створює сокет у режимі «Один-до-одного» (`SOCK_STREAM`), налаштовує параметри черг через опцію `SCTP_INITMSG`, підписується на події ядра `SCTP_EVENTS`, прив'язується до порту `9899` та запускає цикл демультиплексування вхідних потоків за допомогою функції `sctp_recvmsg()`.

:::tabs
```c
/* sctp_server.c — Сервер телеметрії та команд на SCTP (C99 / POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

#define SERVER_PORT 9899
#define BUFFER_SIZE 2048
#define STREAM_CONTROL   0
#define STREAM_TELEMETRY 1
#define PPID_CONTROL   0x0100
#define PPID_TELEMETRY 0x0200

void handle_notification(const union sctp_notification *notif) {
    switch (notif->sn_header.sn_type) {
        case SCTP_ASSOC_CHANGE: {
            const struct sctp_assoc_change *sac = &notif->sn_assoc_change;
            if (sac->sac_state == SCTP_COMM_UP) {
                printf("[ПОДІЯ] Асоціацію встановлено (ID: %u, InStr: %u, OutStr: %u)\n",
                       sac->sac_assoc_id, sac->sac_inbound_streams, sac->sac_outbound_streams);
            } else if (sac->sac_state == SCTP_COMM_LOST) {
                printf("[ПОДІЯ] Асоціацію втрачено (ID: %u)\n", sac->sac_assoc_id);
            }
            break;
        }
        case SCTP_PEER_ADDR_CHANGE: {
            const struct sctp_paddr_change *spc = &notif->sn_paddr_change;
            char ip_str[INET_ADDRSTRLEN];
            const struct sockaddr_in *sin = (const struct sockaddr_in *)&spc->spc_aaddr;
            inet_ntop(AF_INET, &sin->sin_addr, ip_str, sizeof(ip_str));
            printf("[ПОДІЯ] Зміна стану адреси піра %s: стан = %u\n", ip_str, spc->spc_state);
            break;
        }
        case SCTP_SHUTDOWN_EVENT:
            printf("[ПОДІЯ] Пір ініціював плавне закриття (Shutdown)\n");
            break;
        default:
            break;
    }
}

int main(void) {
    int listen_fd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (listen_fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* 1. Налаштовуємо кількість потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    if (setsockopt(listen_fd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        perror("setsockopt SCTP_INITMSG");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    /* 2. Підписуємося на події ядра */
    struct sctp_event_subscribe events;
    memset(&events, 0, sizeof(events));
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (setsockopt(listen_fd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        perror("setsockopt SCTP_EVENTS");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    /* 3. Прив'язка до порту */
    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(SERVER_PORT);

    if (bind(listen_fd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("bind");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    if (listen(listen_fd, 5) < 0) {
        perror("listen");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    printf("SCTP Сервер запущено на порту %d. Очікування клієнтів...\n", SERVER_PORT);

    struct sockaddr_in cliaddr;
    socklen_t clilen = sizeof(cliaddr);
    int conn_fd = accept(listen_fd, (struct sockaddr *)&cliaddr, &clilen);
    if (conn_fd < 0) {
        perror("accept");
        close(listen_fd);
        return EXIT_FAILURE;
    }

    char client_ip[INET_ADDRSTRLEN];
    inet_ntop(AF_INET, &cliaddr.sin_addr, client_ip, sizeof(client_ip));
    printf("Клієнт підключився: %s:%d\n", client_ip, ntohs(cliaddr.sin_port));

    /* 4. Цикл прийому повідомлень та обробки потоків */
    char buffer[BUFFER_SIZE];
    struct sctp_sndrcvinfo sinfo;
    int flags = 0;

    while (1) {
        memset(buffer, 0, sizeof(buffer));
        memset(&sinfo, 0, sizeof(sinfo));
        flags = 0;

        ssize_t bytes = sctp_recvmsg(conn_fd, buffer, sizeof(buffer) - 1,
                                     NULL, 0, &sinfo, &flags);
        if (bytes <= 0) {
            printf("З'єднання закрито або виникла помилка.\n");
            break;
        }

        if (flags & MSG_NOTIFICATION) {
            handle_notification((const union sctp_notification *)buffer);
            continue;
        }

        buffer[bytes] = '\0';
        uint32_t ppid = ntohl(sinfo.sinfo_ppid);

        if (sinfo.sinfo_stream == STREAM_CONTROL) {
            printf("[КОМАНДА] Потік: %u, SSN: %u, TSN: %u, PPID: 0x%04X | Вміст: %s\n",
                   sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, ppid, buffer);
            /* Відправляємо підтвердження виконання команди */
            char ack_msg[64];
            snprintf(ack_msg, sizeof(ack_msg), "ACK-CMD:%s", buffer);
            sctp_sendmsg(conn_fd, ack_msg, strlen(ack_msg), NULL, 0,
                         htonl(PPID_CONTROL), 0, STREAM_CONTROL, 0, 0);
        } else if (sinfo.sinfo_stream == STREAM_TELEMETRY) {
            printf("[ТЕЛЕМЕТРІЯ] Потік: %u, SSN: %u (Unordered), TSN: %u | Дані: %s\n",
                   sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, buffer);
        } else {
            printf("[НЕВІДОМИЙ ПОТІК] Потік: %u | Дані: %s\n", sinfo.sinfo_stream, buffer);
        }
    }

    close(conn_fd);
    close(listen_fd);
    return EXIT_SUCCESS;
}
```
```cpp
// sctp_server.cpp — Ідіоматичний еквівалент сервера на C++20 (RAII, string_view, std::expected)
#include <iostream>
#include <string_view>
#include <format>
#include <array>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

namespace sctp {

constexpr uint16_t ServerPort = 9899;
constexpr size_t BufferSize = 2048;
constexpr uint16_t StreamControl = 0;
constexpr uint16_t StreamTelemetry = 1;
constexpr uint32_t PpidControl = 0x0100;
constexpr uint32_t PpidTelemetry = 0x0200;

class Socket {
public:
    explicit Socket(int fd = -1) noexcept : fd_(fd) {}
    ~Socket() {
        if (fd_ >= 0) ::close(fd_);
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_{-1};
};

void log_notification(const union sctp_notification* notif) {
    if (!notif) return;
    switch (notif->sn_header.sn_type) {
        case SCTP_ASSOC_CHANGE: {
            const auto& sac = notif->sn_assoc_change;
            if (sac.sac_state == SCTP_COMM_UP) {
                std::cout << std::format("[ПОДІЯ] Асоціацію встановлено (ID: {}, In: {}, Out: {})\n",
                                         sac.sac_assoc_id, sac.sac_inbound_streams, sac.sac_outbound_streams);
            } else if (sac.sac_state == SCTP_COMM_LOST) {
                std::cout << std::format("[ПОДІЯ] Асоціацію втрачено (ID: {})\n", sac.sac_assoc_id);
            }
            break;
        }
        case SCTP_PEER_ADDR_CHANGE: {
            const auto& spc = notif->sn_paddr_change;
            std::array<char, INET_ADDRSTRLEN> ip_buf{};
            const auto* sin = reinterpret_cast<const sockaddr_in*>(&spc->spc_aaddr);
            ::inet_ntop(AF_INET, &sin->sin_addr, ip_buf.data(), ip_buf.size());
            std::cout << std::format("[ПОДІЯ] Зміна стану адреси піра {}: стан = {}\n", ip_buf.data(), spc->spc_state);
            break;
        }
        case SCTP_SHUTDOWN_EVENT:
            std::cout << "[ПОДІЯ] Пір ініціював плавне закриття (Shutdown)\n";
            break;
        default:
            break;
    }
}

std::expected<Socket, std::error_code> create_server(uint16_t port) {
    int fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    Socket server_sock(fd);

    // 1. Конфігурація кількості потоків
    sctp_initmsg initmsg{};
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    if (::setsockopt(fd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Підписка на події ядра
    sctp_event_subscribe events{};
    events.sctp_data_io_event = 1;
    events.sctp_association_event = 1;
    events.sctp_address_event = 1;
    events.sctp_shutdown_event = 1;
    if (::setsockopt(fd, IPPROTO_SCTP, SCTP_EVENTS, &events, sizeof(events)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 3. Прив'язка та прослуховування
    sockaddr_in servaddr{};
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(port);

    if (::bind(fd, reinterpret_cast<sockaddr*>(&servaddr), sizeof(servaddr)) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::listen(fd, 5) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return server_sock;
}

} // namespace sctp

int main() {
    auto server = sctp::create_server(sctp::ServerPort);
    if (!server) {
        std::cerr << "Помилка запуску сервера: " << server.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << std::format("SCTP Сервер запущено на порту {}. Очікування клієнтів...\n", sctp::ServerPort);

    sockaddr_in cliaddr{};
    socklen_t clilen = sizeof(cliaddr);
    int client_raw = ::accept(server->get(), reinterpret_cast<sockaddr*>(&cliaddr), &clilen);
    if (client_raw < 0) {
        std::cerr << "Помилка accept: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }
    sctp::Socket client_sock(client_raw);

    std::array<char, INET_ADDRSTRLEN> client_ip{};
    ::inet_ntop(AF_INET, &cliaddr.sin_addr, client_ip.data(), client_ip.size());
    std::cout << std::format("Клієнт підключився: {}:{}\n", client_ip.data(), ntohs(cliaddr.sin_port));

    std::array<char, sctp::BufferSize> buffer{};
    sctp_sndrcvinfo sinfo{};
    int flags = 0;

    while (true) {
        buffer.fill(0);
        std::memset(&sinfo, 0, sizeof(sinfo));
        flags = 0;

        ssize_t bytes = ::sctp_recvmsg(client_sock.get(), buffer.data(), buffer.size() - 1,
                                       nullptr, 0, &sinfo, &flags);
        if (bytes <= 0) {
            std::cout << "З'єднання закрито або виникла помилка.\n";
            break;
        }

        if (flags & MSG_NOTIFICATION) {
            sctp::log_notification(reinterpret_cast<const union sctp_notification*>(buffer.data()));
            continue;
        }

        std::string_view msg(buffer.data(), static_cast<size_t>(bytes));
        uint32_t ppid = ntohl(sinfo.sinfo_ppid);

        if (sinfo.sinfo_stream == sctp::StreamControl) {
            std::cout << std::format("[КОМАНДА] Потік: {}, SSN: {}, TSN: {}, PPID: 0x{:04X} | Вміст: {}\n",
                                     sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, ppid, msg);
            std::string ack = std::format("ACK-CMD:{}", msg);
            ::sctp_sendmsg(client_sock.get(), ack.data(), ack.size(), nullptr, 0,
                           htonl(sctp::PpidControl), 0, sctp::StreamControl, 0, 0);
        } else if (sinfo.sinfo_stream == sctp::StreamTelemetry) {
            std::cout << std::format("[ТЕЛЕМЕТРІЯ] Потік: {}, SSN: {} (Unordered), TSN: {} | Дані: {}\n",
                                     sinfo.sinfo_stream, sinfo.sinfo_ssn, sinfo.sinfo_tsn, msg);
        }
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Реалізація клієнта та генерація змішаного трафіку

Клієнтський процес відкриває сокет SCTP, встановлює асоціацію з сервером через чотириетапне рукостискання та демонструє чергування двох режимів відправки даних:
1. **Передача команд керування на Потоці 0:** застосовує прапорець `0` (впорядкована доставка). Стек автоматично присвоює кожному пакету зростаючий порядковий номер `SSN` (`0, 1, 2...`).
2. **Передача пакетів телеметрії на Потоці 1:** застосовує прапорець `SCTP_UNORDERED`. Поле `SSN` у заголовку чанка `DATA` залишається рівним `0`, а повідомлення доставляється приймальному процесу негайно без чергування.

:::tabs
```c
/* sctp_client.c — Клієнт телеметрії та команд на SCTP (C99 / POSIX) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 9899
#define STREAM_CONTROL   0
#define STREAM_TELEMETRY 1
#define PPID_CONTROL   0x0100
#define PPID_TELEMETRY 0x0200

int main(void) {
    int sd = socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* Налаштовуємо кількість потоків */
    struct sctp_initmsg initmsg;
    memset(&initmsg, 0, sizeof(initmsg));
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg));

    struct sockaddr_in servaddr;
    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &servaddr.sin_addr);

    printf("Підключення до SCTP сервера %s:%d...\n", SERVER_IP, SERVER_PORT);
    if (connect(sd, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0) {
        perror("connect");
        close(sd);
        return EXIT_FAILURE;
    }
    printf("Асоціацію успішно встановлено!\n");

    /* 1. Відправляємо впорядковані команди на Потоці 0 */
    const char *commands[] = {
        "CMD:INIT_SYSTEM",
        "CMD:CALIBRATE_SENSORS",
        "CMD:ARM_MOTORS",
        "CMD:TAKEOFF_ALT_20M"
    };
    for (int i = 0; i < 4; ++i) {
        sctp_sendmsg(sd, commands[i], strlen(commands[i]), NULL, 0,
                     htonl(PPID_CONTROL), 0, STREAM_CONTROL, 0, 0);
        printf("[КЛІЄНТ] Надіслано на Потік %d (Ordered): %s\n", STREAM_CONTROL, commands[i]);
        usleep(50000); // 50 мс
    }

    /* 2. Відправляємо високочастотну телеметрію на Потоці 1 (Unordered) */
    char telemetry[64];
    for (int i = 1; i <= 5; ++i) {
        snprintf(telemetry, sizeof(telemetry), "TELEM:pkt=%d;lat=50.4501;lon=30.5234;alt=%d.5", i, 20 + i);
        sctp_sendmsg(sd, telemetry, strlen(telemetry), NULL, 0,
                     htonl(PPID_TELEMETRY), SCTP_UNORDERED, STREAM_TELEMETRY, 0, 0);
        printf("[КЛІЄНТ] Надіслано на Потік %d (Unordered): %s\n", STREAM_TELEMETRY, telemetry);
        usleep(20000); // 20 мс
    }

    /* 3. Очікуємо підтвердження команд */
    char recv_buf[256];
    struct sctp_sndrcvinfo sinfo;
    int flags = 0;
    for (int i = 0; i < 4; ++i) {
        ssize_t n = sctp_recvmsg(sd, recv_buf, sizeof(recv_buf) - 1, NULL, 0, &sinfo, &flags);
        if (n > 0) {
            recv_buf[n] = '\0';
            printf("[КЛІЄНТ ВІДПОВІДЬ] Потік %d: %s\n", sinfo.sinfo_stream, recv_buf);
        }
    }

    printf("Завершення роботи клієнта.\n");
    close(sd);
    return EXIT_SUCCESS;
}
```
```cpp
// sctp_client.cpp — Ідіоматичний еквівалент клієнта на C++20
#include <iostream>
#include <string_view>
#include <format>
#include <array>
#include <chrono>
#include <thread>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/sctp.h>
#include <arpa/inet.h>

namespace sctp {
constexpr std::string_view ServerIp = "127.0.0.1";
constexpr uint16_t ServerPort = 9899;
constexpr uint16_t StreamControl = 0;
constexpr uint16_t StreamTelemetry = 1;
constexpr uint32_t PpidControl = 0x0100;
constexpr uint32_t PpidTelemetry = 0x0200;
}

int main() {
    int sd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_SCTP);
    if (sd < 0) {
        std::cerr << "Помилка створення сокета: " << std::generic_category().message(errno) << '\n';
        return EXIT_FAILURE;
    }

    sctp_initmsg initmsg{};
    initmsg.sinit_num_ostreams = 5;
    initmsg.sinit_max_instreams = 5;
    initmsg.sinit_max_attempts = 4;
    ::setsockopt(sd, IPPROTO_SCTP, SCTP_INITMSG, &initmsg, sizeof(initmsg));

    sockaddr_in servaddr{};
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(sctp::ServerPort);
    ::inet_pton(AF_INET, sctp::ServerIp.data(), &servaddr.sin_addr);

    std::cout << std::format("Підключення до SCTP сервера {}:{}...\n", sctp::ServerIp, sctp::ServerPort);
    if (::connect(sd, reinterpret_cast<sockaddr*>(&servaddr), sizeof(servaddr)) < 0) {
        std::cerr << "Помилка connect: " << std::generic_category().message(errno) << '\n';
        ::close(sd);
        return EXIT_FAILURE;
    }
    std::cout << "Асоціацію успішно встановлено!\n";

    // 1. Відправка впорядкованих команд на Потоці 0
    std::array<std::string_view, 4> commands = {
        "CMD:INIT_SYSTEM",
        "CMD:CALIBRATE_SENSORS",
        "CMD:ARM_MOTORS",
        "CMD:TAKEOFF_ALT_20M"
    };

    for (const auto& cmd : commands) {
        ::sctp_sendmsg(sd, cmd.data(), cmd.size(), nullptr, 0,
                       htonl(sctp::PpidControl), 0, sctp::StreamControl, 0, 0);
        std::cout << std::format("[КЛІЄНТ] Надіслано на Потік {} (Ordered): {}\n", sctp::StreamControl, cmd);
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    // 2. Відправка телеметрії на Потоці 1 (Unordered)
    for (int i = 1; i <= 5; ++i) {
        std::string telem = std::format("TELEM:pkt={};lat=50.4501;lon=30.5234;alt={}.5", i, 20 + i);
        ::sctp_sendmsg(sd, telem.data(), telem.size(), nullptr, 0,
                       htonl(sctp::PpidTelemetry), SCTP_UNORDERED, sctp::StreamTelemetry, 0, 0);
        std::cout << std::format("[КЛІЄНТ] Надіслано на Потік {} (Unordered): {}\n", sctp::StreamTelemetry, telem);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));
    }

    // 3. Очікування відповідей
    std::array<char, 256> recv_buf{};
    sctp_sndrcvinfo sinfo{};
    int flags = 0;
    for (int i = 0; i < 4; ++i) {
        ssize_t n = ::sctp_recvmsg(sd, recv_buf.data(), recv_buf.size() - 1, nullptr, 0, &sinfo, &flags);
        if (n > 0) {
            std::string_view resp(recv_buf.data(), static_cast<size_t>(n));
            std::cout << std::format("[КЛІЄНТ ВІДПОВІДЬ] Потік {}: {}\n", sinfo.sinfo_stream, resp);
        }
    }

    std::cout << "Завершення роботи клієнта.\n";
    ::close(sd);
    return EXIT_SUCCESS;
}
```
:::

---

## 4. Збірка, запуск та аналіз поведінки черг у ядрі

Для компіляції та запуску програми в операційній системі Linux необхідно переконатися в наявності системної бібліотеки `libsctp` та завантаженого драйвера ядра:

```bash
# 1. Завантаження модуля ядра SCTP
sudo modprobe sctp

# 2. Встановлення пакетів розробки (для Ubuntu/Debian)
sudo apt-get install -y libsctp-dev lksctp-tools

# 3. Компіляція серверної та клієнтської частини на C
gcc -O2 -Wall sctp_server.c -o sctp_server -lsctp
gcc -O2 -Wall sctp_client.c -o sctp_client -lsctp

# 4. Або компіляція на C++20
g++ -std=c++20 -O2 -Wall sctp_server.cpp -o sctp_server_cpp -lsctp
g++ -std=c++20 -O2 -Wall sctp_client.cpp -o sctp_client_cpp -lsctp
```

### Запуск серверної частини

У першому терміналі запускаємо серверний процес:

```text
$ ./sctp_server
SCTP Сервер запущено на порту 9899. Очікування клієнтів...
```

### Запуск клієнтської частини та журнал подій

У другому терміналі запускаємо клієнт:

```text
$ ./sctp_client
Підключення до SCTP сервера 127.0.0.1:9899...
Асоціацію успішно встановлено!
[КЛІЄНТ] Надіслано на Потік 0 (Ordered): CMD:INIT_SYSTEM
[КЛІЄНТ] Надіслано на Потік 0 (Ordered): CMD:CALIBRATE_SENSORS
[КЛІЄНТ] Надіслано на Потік 0 (Ordered): CMD:ARM_MOTORS
[КЛІЄНТ] Надіслано на Потік 0 (Ordered): CMD:TAKEOFF_ALT_20M
[КЛІЄНТ] Надіслано на Потік 1 (Unordered): TELEM:pkt=1;lat=50.4501;lon=30.5234;alt=21.5
[КЛІЄНТ] Надіслано на Потік 1 (Unordered): TELEM:pkt=2;lat=50.4501;lon=30.5234;alt=22.5
[КЛІЄНТ] Надіслано на Потік 1 (Unordered): TELEM:pkt=3;lat=50.4501;lon=30.5234;alt=23.5
[КЛІЄНТ] Надіслано на Потік 1 (Unordered): TELEM:pkt=4;lat=50.4501;lon=30.5234;alt=24.5
[КЛІЄНТ] Надіслано на Потік 1 (Unordered): TELEM:pkt=5;lat=50.4501;lon=30.5234;alt=25.5
[КЛІЄНТ ВІДПОВІДЬ] Потік 0: ACK-CMD:CMD:INIT_SYSTEM
[КЛІЄНТ ВІДПОВІДЬ] Потік 0: ACK-CMD:CMD:CALIBRATE_SENSORS
[КЛІЄНТ ВІДПОВІДЬ] Потік 0: ACK-CMD:CMD:ARM_MOTORS
[КЛІЄНТ ВІДПОВІДЬ] Потік 0: ACK-CMD:CMD:TAKEOFF_ALT_20M
Завершення роботи клієнта.
```

На стороні сервера ми бачимо чітке розділення атрибутів чанків:

```text
Клієнт підключився: 127.0.0.1:41208
[ПОДІЯ] Асоціацію встановлено (ID: 1, InStr: 5, OutStr: 5)
[КОМАНДА] Потік: 0, SSN: 0, TSN: 1001, PPID: 0x0100 | Вміст: CMD:INIT_SYSTEM
[КОМАНДА] Потік: 0, SSN: 1, TSN: 1002, PPID: 0x0100 | Вміст: CMD:CALIBRATE_SENSORS
[КОМАНДА] Потік: 0, SSN: 2, TSN: 1003, PPID: 0x0100 | Вміст: CMD:ARM_MOTORS
[КОМАНДА] Потік: 0, SSN: 3, TSN: 1004, PPID: 0x0100 | Вміст: CMD:TAKEOFF_ALT_20M
[ТЕЛЕМЕТРІЯ] Потік: 1, SSN: 0 (Unordered), TSN: 1005 | Дані: TELEM:pkt=1;lat=50.4501;lon=30.5234;alt=21.5
[ТЕЛЕМЕТРІЯ] Потік: 1, SSN: 0 (Unordered), TSN: 1006 | Дані: TELEM:pkt=2;lat=50.4501;lon=30.5234;alt=22.5
[ТЕЛЕМЕТРІЯ] Потік: 1, SSN: 0 (Unordered), TSN: 1007 | Дані: TELEM:pkt=3;lat=50.4501;lon=30.5234;alt=23.5
[ТЕЛЕМЕТРІЯ] Потік: 1, SSN: 0 (Unordered), TSN: 1008 | Дані: TELEM:pkt=4;lat=50.4501;lon=30.5234;alt=24.5
[ТЕЛЕМЕТРІЯ] Потік: 1, SSN: 0 (Unordered), TSN: 1009 | Дані: TELEM:pkt=5;lat=50.4501;lon=30.5234;alt=25.5
```

### Аналіз механізму нумерації TSN та SSN

Зверніть увагу на відмінність у поведінці полів заголовка `DATA`:
1. **Поле `TSN` (Transmission Sequence Number):** монотонно зростає від `1001` до `1009` для кожного чанка незалежно від номера потоку. Це число використовується ковзним вікном надійності та чанками `SACK` для підтвердження отримання байтів і виявлення втрат на рівні всієї асоціації.
2. **Поле `SSN` (Stream Sequence Number):** для Потоку 0 послідовно інкрементується (`0, 1, 2, 3`), оскільки стек гарантує суворий порядок доставки команд. Для Потоку 1 (де виставлено прапорець `SCTP_UNORDERED`) поле `SSN` завжди залишається рівним `0`, оскільки ядро не виділяє ресурси під відстеження порядкових номерів для невпорядкованих даних.

---

## 5. Простеження стану асоціації через `procfs` та Wireshark

Під час функціонування системи стан асоціацій SCTP у ядрі Linux можна проінспектувати через віртуальну файлову систему `/proc`:

```bash
# Перегляд активних кінцевих точок сокетів
cat /proc/net/sctp/eps

# Перегляд дійсних асоціацій, ідентифікаторів TCB та адрес пірів
cat /proc/net/sctp/assocs

# Загальна статистика переданих чанків, повторних передач та помилок контрольної суми
cat /proc/net/sctp/snmp
```

Файл `/proc/net/sctp/assocs` містить детальну інформацію про кожне з'єднання:
- `ASSOC`: адреса структури `struct sctp_association` у пам'яті ядра.
- `SOCK`: покажчик на `struct sock`.
- `STY`: стиль сокета (`1` для `SOCK_STREAM`, `2` для `SOCK_SEQPACKET`).
- `SST`: поточний стан FSM (`3` для `ESTABLISHED`).
- `TXQUEUE` / `RXQUEUE`: розмір черг відправки та прийому в байтах.
- `UID`: ідентифікатор користувача, який запустив процес.
- `INODE`: номер іноди сокета.
- `LPORT` / `RPORT`: локальний та віддалений порти.
- `LADDRS` / `RADDRS`: переліки всіх локальних та віддалених IP-адрес асоціації.
- `HBINT`: інтервал надсилання чанків `HEARTBEAT` (у мілісекундах).
- `INS` / `OUTS`: узгоджена кількість вхідних та вихідних потоків.

### Аналіз трафіку за допомогою `tcpdump`

Для діагностики обміну пакетами на рівні інтерфейсу `lo` виконайте:

```bash
sudo tcpdump -i lo -nn -vvv -X "sctp"
```

У виводі дампа чітко видно чотириетапне рукостискання:
1. `INIT [init tag: 0x... rwnd: 65535 OS: 5 MIS: 5 initial tsn: 1000]`
2. `INIT_ACK [init tag: 0x... rwnd: 65535 OS: 5 MIS: 5 initial tsn: 5000 (COOKIE)]`
3. `COOKIE_ECHO [cookie: ...]`
4. `COOKIE_ACK`
5. Наступні пакети з чанками `DATA (TSN: ..., SID: 0, SSN: 0, PPID: 0x0100)` та зворотними `SACK (Cumulative TSN: ...)`.

---

## 6. Експеримент: симуляція обриву лінку та перевірка Failover

Для практичної перевірки стійкості мультихоумінгу можна налаштувати дві віртуальні IP-адреси на інтерфейсі петлі:

```bash
# Додавання додаткової IP-адреси до інтерфейсу loopback
sudo ip addr add 127.0.0.2/8 dev lo

# Запуск сервера, прив'язаного до 127.0.0.1 та 127.0.0.2 через sctp_bindx
# Запуск клієнта з підключенням до обох адрес через sctp_connectx
```

Під час активної передачі телеметрії заблокуємо трафік на основну адресу `127.0.0.1` за допомогою `iptables`:

```bash
sudo iptables -A INPUT -p sctp -d 127.0.0.1 -j DROP
```

### Що відбувається в системі

1. Стек SCTP на клієнті фіксує таймаут `RTO` на основній адресі `127.0.0.1`.
2. Лічильник помилок `Path.Error.Count` збільшується з кожною повторною спробою відправки.
3. Коли кількість помилок перевищує поріг `Path.Max.Retrans` (типово 5), ядро переводить адресу `127.0.0.1` у стан `INACTIVE` і генерує для застосунку сповіщення `SCTP_PEER_ADDR_CHANGE` зі значенням `spc_state = SCTP_ADDR_UNREACHABLE`.
4. Стек автоматично і прозоро перенаправляє всі непідтверджені чанки `DATA` на резервну адресу `127.0.0.2`.
5. Клієнтська програма не отримує помилки сокета `ECONNRESET` чи `EPIPE` — з'єднання залишається відкритим, а прикладний код продовжує безперервно передавати телеметрію та команди!

Після зняття блокування (`sudo iptables -D INPUT -p sctp -d 127.0.0.1 -j DROP`) чанки `HEARTBEAT` відновлюють зв'язок, і адреса повертається в статус `SCTP_ADDR_AVAILABLE`.

---

## 7. Експеримент: симуляція втрат пакетів за допомогою Linux Traffic Control (`tc netem`)

Щоб наочно переконатися у відсутності блокування черги між потоками, створимо штучну втрату 20% пакетів на тестовому інтерфейсі за допомогою модуля ядра `netem` (*Network Emulator*):

```bash
# Встановлення затримки 30 мс та 20% втрати пакетів на інтерфейсі loopback
sudo tc qdisc add dev lo root netem delay 30ms loss 20%
```

Під час запуску клієнта спостерігається така поведінка:
- **Потік 0 (Команди, Ordered):** при втраті пакета з номером `SSN=1` сервер затримує видачу команди `SSN=2` до моменту надходження повторно надісланого пакета `SSN=1`. Це гарантує суворий порядок виконання.
- **Потік 1 (Телеметрія, Unordered):** пакети з прапорцем `SCTP_UNORDERED` надходять у застосунок негайно в міру прибуття. Втрата пакета з `TSN=1005` жодним чином не затримує доставку пакетів `TSN=1006` або `TSN=1007`. Застосунок отримує свіжі координати без найменшої штучної паузи!

Після завершення експерименту тестове правило видаляється командою:

```bash
sudo tc qdisc del dev lo root
```

---

## 8. Асинхронне мультиплексування з epoll: архітектура One-to-Many

При побудові високонавантажених шлюзів сигналізації (наприклад, концентраторів M3UA або вузлів AMF 5G Core), що обслуговують десятки тисяч одночасних асоціацій, модель «один потік на сокет» стає неефективною через обмеження пам'яті та накладні витрати на перемикання контексту ядра. У таких сценаріях використовується сокет стилю «Один-до-багатьох» (`SOCK_SEQPACKET`) у поєднанні з системним мультиплексором `epoll` у режимі тригера за фронтом (`EPOLLET`).

### Архітектура диспетчера сесій

1. **Єдиний файловий дескриптор:**  
   Серверний процес створює лише один сокет `SOCK_SEQPACKET` і реєструє його в `epoll_create1()` з прапорцями `EPOLLIN | EPOLLET`.
2. **Таблиця асоціацій у просторі користувача:**  
   Застосунок веде хеш-таблицю сесій (`std::unordered_map<sctp_assoc_t, ClientSession>`). При отриманні сповіщення `SCTP_COMM_UP` запис додається в таблицю; при отриманні `SCTP_COMM_LOST` або `SCTP_SHUTDOWN_COMP` ресурси сесії звільняються.
3. **Неблокуюча вичитка черги:**  
   При спрацюванні події `EPOLLIN` застосунок у циклі викликає `sctp_recvmsg()` до повернення помилки `-1` із `errno = EAGAIN` або `EWOULDBLOCK`, передаючи кожне прочитане повідомлення відповідному екземпляру `ClientSession` за його `sinfo_assoc_id`.

Така архітектура дозволяє єдиному робочому потоку процесора обслуговувати понад 50 000 сигнальних асоціацій із затримкою обробки менше 1 мілісекунди.

---

## 9. Архітектурні шаблони C++20 та безпека ресурсів

Реалізація клієнта та сервера на сучасному стандарті C++20 демонструє ключові переваги перед класичним спадковим кодом мови C:

1. **Ідіома RAII та безпека дескрипторів:**  
   Клас `sctp::Socket` бере на себе монопольне володіння файловим дескриптором. Конструктори копіювання заблоковані (`= delete`), а операції переміщення (`move semantics`) гарантують передачу дескриптора між контекстами виконання без ризику подвійного закриття чи витоку дескриптора при генерації винятків у користувацькому коді.

2. **Явне моделювання помилок через `std::expected`:**  
   Замість повернення «магічних чисел» `-1` та небезпечного читання глобальної змінної `errno` (яка може бути перезаписана іншим потоком або вкладеним викликом), функція `create_server()` повертає типізований об'єкт `std::expected<Socket, std::error_code>`. Це змушує розробника явно обробити сценарій збою на етапі компіляції.

3. **Нульові накладні витрати на копіювання з `std::string_view` та `std::span`:**  
   При передачі корисного навантаження викликами `sctp_sendmsg()` та читанні метаданих обробники оперують легковагими представленнями безперервної пам'яті (`std::string_view`), уникаючи непотрібного динамічного виділення буферів у купі (*heap allocation*) для кожного пакета телеметрії.

---

## 10. Промислове налаштування параметрів ядра Linux (sysctl)

При розгортанні високонавантажених телекомунікаційних вузлів на базі SCTP стандартні параметри ядра потребують оптимізації через підсистему `sysctl`:

- `net.sctp.rto_initial = 1000`: Початковий таймаут RTO встановлюється в 1 секунду (замість стандартних 3 секунд за RFC 4960) для прискореного виявлення втрати первинних пакетів у низьколатентних ЦОД.
- `net.sctp.rto_min = 100`: Нижня межа RTO в 100 мілісекунд запобігає тривалим паузам при виявленні втрат на високошвидкісних оптоволоконних лінках.
- `net.sctp.rto_max = 5000`: Верхня межа RTO обмежується 5 секундами, щоб уникнути експоненційного росту затримок при тривалих перевантаженнях.
- `net.sctp.path_max_retrans = 3`: Зменшення порогу відмови з 5 до 3 спроб прискорює автоматичне перемикання трафіку на резервний маршрут (*Failover*) при фізичному обриві кабелю.
- `net.sctp.association_max_retrans = 6`: Поріг сумарних помилок асоціації до її остаточного аварійного розриву.
- `net.sctp.hb_interval = 2000`: Інтервал періодичного зондування `HEARTBEAT` встановлюється в 2 секунди, що забезпечує актуальну інформацію про стан резервних IP-адрес.
- `net.sctp.rcvbuf_policy = 1`: Вмикає індивідуальне виділення буфера пам'яті розміром `SO_RCVBUF` для кожної асоціації окремо (актуально для серверів зі стилем сокета `SOCK_SEQPACKET`).
- `net.sctp.cookie_preserve_time = 30000`: Час дійсності `State Cookie` у 30 секунд запобігає застаріванню маркерів при затримках у глобальних трансконтинентальних маршрутах.

---

## 11. Мережева безпека, фільтрація та міжмережеві екрани

При розгортанні систем на базі SCTP у відкритих мережах інженери стикаються з питаннями мережевої безпеки та проходження брандмауерів:

1. **Ідентифікація протоколу в IP-заголовку:**  
   SCTP має власний офіційний номер протоколу в заголовку IPv4/IPv6 — **`132`** (`IPPROTO_SCTP`). Для пропуску трафіку через міжмережевий екран Linux Netfilter (`iptables` / `nftables`) необхідно явно дозволити цей протокол і завантажити модуль відстеження станів `nf_conntrack_sctp`:
   ```bash
   # Дозвіл проходження SCTP трафіку на порт 9899
   sudo iptables -A INPUT -p sctp --dport 9899 -j ACCEPT
   sudo iptables -A OUTPUT -p sctp --sport 9899 -j ACCEPT
   ```

2. **Захист від підміни пакетів (Verification Tag):**  
   Кожен пакет SCTP містить 32-бітний `Verification Tag`, сформований випадковим чином під час 4-way handshake. Ядро відкидає будь-який пакет, якщо його тег верифікації не збігається з очікуваним значенням для цієї асоціації. Це робить сліпу ін'єкцію даних (*Blind Packet Injection*) практично нездійсненною, оскільки зловмиснику потрібно вгадати одне з 4.29 мільярда значень.

3. **Стійкість до сканування портів:**  
   Якщо на адресу сервера надходить неочікуваний чанк `DATA` або `COOKIE ECHO` з некоректним тегом верифікації для неіснуючої асоціації, SCTP відповідає чанком `ABORT` із віддзеркаленим тегом або мовчки ігнорує пакет (залежно від прапорців безпеки), запобігаючи витоку інформації про топологію внутрішньої мережі.

4. **Проходження трансляції адрес (NAT Traversal) та інкапсуляція:**  
   Більшість побутових маршрутизаторів підтримують трансляцію NAT лише для портів TCP та UDP, блокуючи «чистий» IP-протокол 132. Для подолання цієї перешкоди у відкритому Інтернеті та WebRTC застосовується стандарт RFC 6951 (інкапсуляція SCTP поверх UDP на порту 9899) або RFC 8261 (SCTP поверх DTLS поверх UDP). Це гарантує безперешкодне проходження будь-яких типів симетричного NAT без зміни коду застосунку.

---

## 12. Підводні камені та типові інженерні помилки

1. **Неузгодженість порядку байтів у PPID:**  
   Поле `ppid` у `sctp_sendmsg()` та `sctp_recvmsg()` інтерпретується стеком ядра як 32-бітне беззнакове число в мережевому порядку байтів (*Big-Endian*). Якщо відправник забуде викликати `htonl(PPID)` або отримувач не викличе `ntohl(sinfo.sinfo_ppid)`, на архітектурах Little-Endian (x86_64, ARM64) байти числа перевернуться, що призведе до некоректної фільтрації трафіку.

2. **Забута підписка на подію `sctp_data_io_event`:**  
   Якщо у структурі `sctp_event_subscribe` пропустити ініціалізацію `events.sctp_data_io_event = 1`, системний виклик `sctp_recvmsg()` не буде заповнювати поля структури `sctp_sndrcvinfo`. У результаті програма отримає корисні дані повідомлення, але поля `sinfo_stream` та `sinfo_ppid` міститимуть невизначені значення.

3. **Фрагментація повідомлень та прапорець `MSG_EOR`:**  
   Якщо розмір надісланого повідомлення перевищує Path MTU (наприклад, масив розміром 4096 байтів при MTU 1500), ядро автоматично фрагментує запис на кілька чанків `DATA`. Якщо приймальний буфер програми в `sctp_recvmsg()` менший за повний розмір повідомлення, виклик зчитає першу порцію байтів без прапорця `MSG_EOR`. Застосунок повинен перевіряти біт `flags & MSG_EOR` і продовжувати зчитування частин до повного збирання кадру.

4. **Витік оперативної пам'яті при роботі з `sctp_getpaddrs()`:**  
   Функція `sctp_getpaddrs()` виділяє блок пам'яті у просторі користувача за допомогою системного алокатора. Кожен виклик цієї функції обов'язково має завершуватися викликом `sctp_freepaddrs()`, інакше постійний моніторинг адрес піра спричинить прогресуючий витік оперативної пам'яті процесу.

# ⚙️ Створення MPTCP-сокета та інспекція підпотоків у C та C++

У даній практичній вставці детально розглядається розробка мережевого клієнтського додатка, який ініціалізує нативний сокет MPTCP у ядрі Linux, виконує підключення до віддаленого сервера, здійснює інспекцію стану підпотоків та прозоро обробляє можливий фолбек (fallback) до одношляхового TCP.

---

## 1. Архітектура сокетного виклику IPPROTO_MPTCP та перевірка фолбеку

Починаючи з версії ядра Linux 5.6, використання Багатошляхового TCP у програмному забезпеченні не потребує лінкування сторонніх бібліотек чи виклику складних макросів. Підсистема MPTCP інтегрована безпосередньо в мережевий стек ядра й доступна через стандартне сімейство сокетів `AF_INET` або `AF_INET6`.

Для ініціалізації MPTCP-сокета в системному виклику `socket()` замість стандартного протоколу `IPPROTO_TCP` (або `0`) вказується спеціалізована константа `IPPROTO_MPTCP` (числове значення `262` у системних заголовках `<netinet/in.h>` та `<linux/in.h>`):

:::tabs
```c
int fd = socket(AF_INET, SOCK_STREAM, IPPROTO_MPTCP);
```
```cpp
int fd = ::socket(AF_INET, SOCK_STREAM, IPPROTO_MPTCP);
```
:::

### 1.1 Механізм автоматичного прозорого фолбеку

Ключовою перевагою MPTCP є повна зворотна сумісність із мережевою інфраструктурою. Якщо локальне ядро Linux не підтримує MPTCP, віддалений сервер виявився застарілим, або проміжний фаєрвол (middlebox) вирізає опцію `MP_CAPABLE` з пакета `SYN`, ядро не перериває виконання програми й не повертає помилку. 

Натомість ядро здійснює **прозорий фолбек (transparent fallback)**: сокет продовжує функціонувати як звичайний одношляховий TCP-сокет.

Для того щоб прикладний додаток міг програмно перевірити, чи з'єднання дійсно працює в багатошляховому режимі, використовується системний виклик `getsockopt()` із рівнем `SOL_MPTCP` (значення `284`) та опцією `MPTCP_INFO` (значення `1`):

:::tabs
```c
struct mptcp_info info;
socklen_t len = sizeof(info);
getsockopt(fd, SOL_MPTCP, MPTCP_INFO, &info, &len);
```
```cpp
struct mptcp_info info{};
socklen_t len = sizeof(info);
::getsockopt(fd, SOL_MPTCP, MPTCP_INFO, &info, &len);
```
:::

### 1.2 Аналіз структури struct mptcp_info

Ядро Linux повертає у структуру `struct mptcp_info` поточний метричний зріз стану MPTCP-мета-сокета. Найважливішими полями цієї структури є:

1. `mptcpi_subflows`: Кількість додаткових активних підпотоків (subflows), приєднаних до даного мета-сокета (не враховуючи первинний підпотік).
2. `mptcpi_add_addr_accepted`: Кількість успішно прийнятих від віддаленого вузла сигналів `ADD_ADDR`.
3. `mptcpi_flags`: Бітова маска внутрішнього стану. Якщо в цій масці встановлено біт `MPTCP_INFO_FLAG_FALLBACK` (`0x01`), це означає, що з'єднання втратило MPTCP-опції й працює як звичайний одношляховий TCP.
4. `mptcpi_token`: Унікальний 32-бітний токен з'єднання, обчислений під час рукостискання `MP_CAPABLE`.

---

## 2. Повноцінна реалізація клієнта мовами C та C++

Нижче наведено готові до компіляції та запуску вихідні файли клієнтського додатка.

У вкладці **C** продемонстровано класичний процедурний підхід POSIX C99 із обробкою помилок через `errno`, явним створенням структур sockaddr_in та ручним закриттям файлових дескрипторів.

У вкладці **C++** застосовано ідіоматичний стандарт C++20:
- RAII-клас `mptcp::Socket`, який автоматично гарантує закриття файлового дескриптора у деструкторі при виході з області видимості чи при виникненні винятків.
- Тип `std::expected` (із C++23 / C++20 backport) для безпечного повернення результатів або об'єктів `std::error_code` без використання винятків.
- Незмінні строкові представлення `std::string_view` для запобігання зайвим алокаціям пам'яті у купі.

:::tabs
```c
/* MPTCP Client implementation in C (POSIX C99) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

/* Резервні макроси для застарілих версій системних заголовків glibc */
#ifndef IPPROTO_MPTCP
#define IPPROTO_MPTCP 262
#endif

#ifndef SOL_MPTCP
#define SOL_MPTCP 284
#endif

#ifndef MPTCP_INFO
#define MPTCP_INFO 1
#endif

#define MPTCP_INFO_FLAG_FALLBACK 0x01

/* Сумісний буфер для зчитування ядерної структури mptcp_info */
struct mptcp_info_buffer {
    uint8_t  mptcpi_subflows;
    uint8_t  mptcpi_add_addr_accepted;
    uint8_t  mptcpi_subflows_max;
    uint8_t  mptcpi_add_addr_accepted_max;
    uint32_t mptcpi_flags;
    uint32_t mptcpi_token;
    uint32_t mptcpi_write_seq;
    uint32_t mptcpi_snd_una;
    uint32_t mptcpi_rcv_nxt;
};

static void print_mptcp_status(int sock_fd) {
    struct mptcp_info_buffer info;
    socklen_t len = sizeof(info);
    memset(&info, 0, sizeof(info));

    if (getsockopt(sock_fd, SOL_MPTCP, MPTCP_INFO, &info, &len) < 0) {
        perror("[!] getsockopt(SOL_MPTCP, MPTCP_INFO) failed");
        return;
    }

    printf("=========================================\n");
    printf("     ПОТОЧНИЙ СТАН MPTCP-МЕТА-СОКЕТА     \n");
    printf("=========================================\n");
    printf(" Токен з'єднання (Token)        : 0x%08x\n", info.mptcpi_token);
    printf(" Додаткових підпотоків (Subflows): %u\n", info.mptcpi_subflows);
    printf(" Прийнятих адрес (ADD_ADDR)     : %u\n", info.mptcpi_add_addr_accepted);
    
    if (info.mptcpi_flags & MPTCP_INFO_FLAG_FALLBACK) {
        printf(" Стан протоколу                : FALLBACK (Одношляховий TCP)\n");
    } else {
        printf(" Стан протоколу                : MULTIPATH TCP ACTIVE (Багатошляховий режим)\n");
    }
    printf("=========================================\n\n");
}

int main(int argc, char *argv[]) {
    const char *server_ip = (argc > 1) ? argv[1] : "127.0.0.1";
    uint16_t port = (argc > 2) ? (uint16_t)atoi(argv[2]) : 8080;
    int sockfd = -1;
    struct sockaddr_in serv_addr;
    const char *msg = "GET / HTTP/1.1\r\nHost: mptcp.test\r\nConnection: close\r\n\r\n";
    char response[512];
    ssize_t bytes;

    printf("[+] Створення мережевого сокета IPPROTO_MPTCP...\n");
    sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_MPTCP);
    if (sockfd < 0) {
        if (errno == EPROTONOSUPPORT || errno == ENOPROTOOPT) {
            fprintf(stderr, "[-] Ядро Linux не підтримує IPPROTO_MPTCP. Спроба створити звичайний TCP сокет...\n");
            sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_IP);
        }
        if (sockfd < 0) {
            perror("[-] Помилка створення сокета");
            return EXIT_FAILURE;
        }
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    if (inet_pton(AF_INET, server_ip, &serv_addr.sin_addr) <= 0) {
        fprintf(stderr, "[-] Некоректний формат IP-адреси: %s\n", server_ip);
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[+] Підключення до сервера %s:%u...\n", server_ip, port);
    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("[-] Помилка підключення connect()");
        close(sockfd);
        return EXIT_FAILURE;
    }

    printf("[+] З'єднання успішно встановлено!\n");
    print_mptcp_status(sockfd);

    printf("[+] Надсилання HTTP-запиту...\n");
    if (send(sockfd, msg, strlen(msg), 0) < 0) {
        perror("[-] Помилка відправки send()");
    } else {
        bytes = recv(sockfd, response, sizeof(response) - 1, 0);
        if (bytes > 0) {
            response[bytes] = '\0';
            printf("[+] Отримано відповідь сервера (%zd байт):\n%s\n", bytes, response);
        }
    }

    print_mptcp_status(sockfd);

    close(sockfd);
    printf("[+] Сокет закрито. Завершення програми.\n");
    return EXIT_SUCCESS;
}
```
```cpp
// MPTCP Client implementation in C++ (C++20 Idiomatic RAII)
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <system_error>
#include <expected>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

namespace mptcp {

constexpr int kProtocolMptcp = 262;
constexpr int kSolMptcp = 284;
constexpr int kMptcpInfo = 1;
constexpr uint32_t kFlagFallback = 0x01;

struct MptcpState {
    uint32_t token{0};
    uint8_t subflows{0};
    uint8_t add_addr_accepted{0};
    bool is_fallback{false};
};

// Безпечна RAII обгортка для сокетного дескриптора
class Socket {
public:
    explicit Socket(int fd) noexcept : fd_(fd) {}
    
    ~Socket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    Socket(const Socket&) = delete;
    Socket& operator=(const Socket&) = delete;

    Socket(Socket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    Socket& operator=(Socket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }

    static std::expected<Socket, std::error_code> create_mptcp() noexcept {
        int fd = ::socket(AF_INET, SOCK_STREAM, kProtocolMptcp);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return Socket(fd);
    }

    std::expected<void, std::error_code> connect(std::string_view ip, uint16_t port) noexcept {
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_port = htons(port);
        
        std::string ip_null_term(ip);
        if (::inet_pton(AF_INET, ip_null_term.c_str(), &addr.sin_addr) <= 0) {
            return std::unexpected(std::make_error_code(std::errc::invalid_argument));
        }

        if (::connect(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    [[nodiscard]] std::expected<MptcpState, std::error_code> get_mptcp_state() const noexcept {
        struct RawMptcpInfo {
            uint8_t  subflows;
            uint8_t  add_addr_accepted;
            uint8_t  subflows_max;
            uint8_t  add_addr_accepted_max;
            uint32_t flags;
            uint32_t token;
            uint32_t write_seq;
            uint32_t snd_una;
            uint32_t rcv_nxt;
        } raw_info{};

        socklen_t len = sizeof(raw_info);
        if (::getsockopt(fd_, kSolMptcp, kMptcpInfo, &raw_info, &len) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        MptcpState state;
        state.token = raw_info.token;
        state.subflows = raw_info.subflows;
        state.add_addr_accepted = raw_info.add_addr_accepted;
        state.is_fallback = (raw_info.flags & kFlagFallback) != 0;
        return state;
    }

    std::expected<size_t, std::error_code> send_data(std::string_view data) noexcept {
        ssize_t res = ::send(fd_, data.data(), data.size(), 0);
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return static_cast<size_t>(res);
    }

private:
    int fd_{-1};
};

} // namespace mptcp

int main(int argc, char* argv[]) {
    const std::string_view server_ip = (argc > 1) ? argv[1] : "127.0.0.1";
    const uint16_t port = (argc > 2) ? static_cast<uint16_t>(std::stoi(argv[2])) : 8080;

    std::cout << "[+] [C++20] Ініціалізація MPTCP сокета...\n";
    auto socket_res = mptcp::Socket::create_mptcp();
    if (!socket_res) {
        std::cerr << "[-] Помилка створення MPTCP сокета: " << socket_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    mptcp::Socket client_sock = std::move(*socket_res);
    std::cout << "[+] Підключення до сервера " << server_ip << ':' << port << "...\n";

    if (auto conn_res = client_sock.connect(server_ip, port); !conn_res) {
        std::cerr << "[-] Помилка підключення: " << conn_res.error().message() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "[+] З'єднання успішно встановлено!\n";

    if (auto state = client_sock.get_mptcp_state(); state) {
        std::cout << "=========================================\n"
                  << "        СТАН MPTCP З'ЄДНАННЯ (C++)      \n"
                  << "=========================================\n"
                  << " Токен          : 0x" << std::hex << state->token << std::dec << '\n'
                  << " Підпотоки       : " << static_cast<int>(state->subflows) << '\n'
                  << " Прийняті адреси : " << static_cast<int>(state->add_addr_accepted) << '\n'
                  << " Режим           : " << (state->is_fallback ? "FALLBACK (Single TCP)" : "MULTIPATH TCP ACTIVE") << '\n'
                  << "=========================================\n";
    }

    constexpr std::string_view kHttpRequest = "GET / HTTP/1.1\r\nHost: mptcp.test\r\nConnection: close\r\n\r\n";
    if (auto sent = client_sock.send_data(kHttpRequest); sent) {
        std::cout << "[+] Надіслано " << *sent << " байт запиту.\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Збірка, запуск та інспекція в системі

Для компіляції та перевірки розробленого клієнтського додатка у Linux виконуються наступні команди:

```bash
# Компіляція версії на мові C
gcc -O2 -Wall -std=c99 mptcp_client.c -o mptcp_client_c

# Компіляція версії на мові C++20
g++ -O2 -Wall -std=c++20 mptcp_client.cpp -o mptcp_client_cpp

# Перевірка наявності ендпоінтів у ядрі перед запуском
ip mptcp endpoint show

# Запуск монітора подій MPTCP у сусідній термінальній сесії
ip mptcp monitor

# Запуск C++ клієнта
./mptcp_client_cpp 127.0.0.1 8080
```

---

## 4. Простеження підпотоків та діагностика через procfs та bpftrace

Під час виконання клієнтської програми стан MPTCP-сокета та його підпотоків можна інспектувати на рівні ядра Linux за допомогою стандартної утиліти `ss` (з пакета `iproute2`):

```bash
# Перегляд мета-сокетів MPTCP
ss -M

# Перегляд детальних параметрів підпотоків та токенів
ss -t -i -M
```

Приклад виводу утиліти `ss -M`:
```text
State       Recv-Q Send-Q   Local Address:Port       Peer Address:Port
ESTAB       0      0        192.168.1.50:42100       93.184.216.34:443
    token:0x3a8f1b12 subflows:1 add_addr_accepted:0
```

### 4.1 Трасування за допомогою bpftrace

Для глибшого аналізу роботи ядерного планувальника пакетів та викликів створення підпотоків використовується інструмент eBPF / `bpftrace`. Ядро Linux надає наступні трасувальні точки (tracepoints):
- `tracepoint:mptcp:mptcp_subflow_get_send`: Викликається під час вибору підпотоку для відправки чергового пакета.
- `tracepoint:mptcp:mptcp_subflow_connect`: Викликається в момент ініціації вихідного підпотоку `MP_JOIN`.

Однорядковий скрипт `bpftrace` для відстеження викликів створення підпотоків:
```bash
sudo bpftrace -e 'tracepoint:mptcp:mptcp_subflow_connect { printf("MPTCP Subflow connect: token=%u\n", args->token); }'
```

---

## 5. Практичні поради, сокетні опції та специфічні пастки реалізації

1. **Захист від відсутності констант у glibc:** У застарілих системних дистрибутивах (наприклад, Ubuntu 20.04 або CentOS 8) стандартний заголовок `<netinet/in.h>` може не містити розширень MPTCP. Завжди слід використовувати розсудливу перевірку `#ifndef IPPROTO_MPTCP` з явним визначенням константи `262` та `SOL_MPTCP = 284`.
2. **Вплив виклику `bind()` перед `connect()`:** Якщо клієнтський додаток явно викликає `bind()` до конкретного локального мережевого інтерфейсу перед викликом `connect()`, це примусово прив'язує первинний підпотік до цієї IP-адреси. Проте ядерний Path Manager все одно зможе відкривати додаткові підпотоки `MP_JOIN` з інших інтерфейсів системи відповідно до конфігурації `ip mptcp endpoint`.
3. **Обробка таймаутів та `SO_KEEPALIVE`:** Вмикання опції `SO_KEEPALIVE` на мета-сокеті MPTCP автоматично поширюється на всі активні підпотоки. Якщо один із фізичних каналів (наприклад, Wi-Fi) вимикається, проби keepalive для відповідного підпотоку завершаться помилкою, і ядро закриє цей конкретний підпотік, залишаючи загальне MPTCP-з'єднання живим через стільниковий канал.
4. **Неблокуючий режим I/O (Non-blocking I/O) та `epoll`:** Сокет `IPPROTO_MPTCP` повністю підтримує виклики `fcntl(fd, F_SETFL, O_NONBLOCK)` та системне опитування через `epoll_wait()`. Події `EPOLLIN` та `EPOLLOUT` спрацьовують на рівні загального мета-сокета, тому прикладному коду не потрібно самостійно відстежувати події на рівні окремих підпотоків.

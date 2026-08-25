# ⚙️ Реалізація ICMP-трасування на сирих сокетах

Коли системному інженеру або розробнику мережевих сервісів необхідно вбудувати діагностику маршрутизації безпосередньо у власний процес (наприклад, у систему моніторингу затримок SLA, агент SD-WAN, сервісну сітку Service Mesh чи високонавантажений балансувальник трафіку), запуск зовнішньої утиліти `traceroute` через `fork()` та `execve()` створює неприйнятні накладні витрати. Створення нових процесів операційної системи на кожен діагностичний зонд блокує диспетчер потоків, споживає файлові дескриптори, створює зайве навантаження на підсистему пам'яті та обмежує частоту вимірювання затримок.

Пряма реалізація алгоритму трасування на рівні системних викликів ядра Linux спирається на використання сирих сокетів (`SOCK_RAW`), динамічне керування полем `IP_TTL` через сокетні параметри та самостійне формування й розбір двійкових кадрів протоколу ICMP.

---

## Принцип функціонування та взаємодія з ядром

Для реалізації зондування мережевого маршруту програма виконує чітку послідовність низькорівневих дій на стику з мережевим стеком ядра:

1. **Створення сирого сокета**: процес відкриває сокет у домені `AF_INET` з типом `SOCK_RAW` та протоколом `IPPROTO_ICMP`. Оскільки доступ до сирих сокетів дозволяє перехоплювати та підробляти будь-який трафік на хості, ядро Linux вимагає наявності привілею `CAP_NET_RAW` або прав суперкористувача `root`.
2. **Налаштування таймауту отримання**: за допомогою системного виклику `setsockopt()` з рівнем `SOL_SOCKET` та опцією `SO_RCVTIMEO` встановлюється максимальний час очікування відповіді (наприклад, 1000 мс). Це гарантує, що виклик `recvfrom()` не заблокує потік виконання назавжди, якщо транзитний маршрутизатор мовчки відкине пакет без генерації ICMP-відповіді.
3. **Ітеративне керування полем TTL**: у циклі від 1 до максимальної кількості хопів (зазвичай 30) перед відправкою кожного зонда викликається `setsockopt(sockfd, IPPROTO_IP, IP_TTL, &ttl, sizeof(ttl))`. Це змушує мережевий стек ядра записувати поточне значення `ttl` у відповідне 8-бітне поле заголовка IPv4.
4. **Формування структури ICMP Echo Request**: заповнюється стандартна структура `struct icmphdr`. Поле `type` встановлюється в `ICMP_ECHO` (тип 8, код 0). У поле `un.echo.id` записується унікальний ідентифікатор процесу (наприклад, молодші 16 бітів PID), а в `un.echo.sequence` — порядковий номер зонда (значення TTL). Обчислюється 16-бітна контрольна сума за алгоритмом Internet Checksum (RFC 1071). Перед викликом `sendto()` фіксується точна мітка монотонного годинника ядра (`CLOCK_MONOTONIC`).
5. **Прийом та демультиплексування пакетів**: виклик `recvfrom()` повертає сирий двійковий буфер. Оскільки сокет відкритий у режимі `SOCK_RAW`, ядро повертає пакет, починаючи безпосередньо з заголовка IPv4 (`struct iphdr`). Програма динамічно обчислює зміщення до заголовка ICMP (`iphdr->ihl * 4`) та аналізує тип відповіді.

### Анатомія корисного навантаження ICMP Time Exceeded

Згідно зі стандартом RFC 792, коли проміжний маршрутизатор знищує дейтаграму через $TTL = 0$, він формує повідомлення `ICMP_TIME_EXCEEDED` (тип 11, код 0). Тіло цього повідомлення містить:
- Заголовок ICMP (8 байтів);
- Копію початкового IPv4-заголовка нашого зондувального пакета (20 або більше байтів);
- Перші 64 біти (8 байтів) корисного навантаження нашого початкового пакета.

Саме в цих перших 8 байтах вкладеного навантаження містяться поля `id` та `sequence` нашого початкового `ICMP_ECHO`. Програма зчитує ці значення та зіставляє відповідь з конкретним відправленим зондом, що дозволяє коректно обчислювати RTT навіть в умовах багатопотокового або асинхронного зондування.

---

## Програмна реалізація

Нижче наведено повноцінну та безпечну реалізацію трасування адреси IPv4 на мовах C та ідіоматичному C++20 з використанням RAII, `std::chrono` та сучасної безпечної типізації.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

#define MAX_HOPS 30
#define TIMEOUT_MS 1000

/* Обчислення 16-бітної контрольної суми Internet Checksum (RFC 1071) */
static unsigned short compute_checksum(const void *data, size_t len) {
    const unsigned short *ptr = (const unsigned short *)data;
    unsigned int sum = 0;
    while (len > 1) {
        sum += *ptr++;
        len -= 2;
    }
    if (len == 1) {
        sum += *(const unsigned char *)ptr;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    return (unsigned short)(~sum);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Використання: %s <IPv4-адреса>\n", argv[0]);
        return EXIT_FAILURE;
    }

    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    if (inet_pton(AF_INET, argv[1], &target_addr.sin_addr) <= 0) {
        perror("Некоректна IPv4-адреса");
        return EXIT_FAILURE;
    }

    /* Відкриття сирого сокета для протоколу ICMP */
    int sockfd = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sockfd < 0) {
        perror("Помилка створення SOCK_RAW (потрібен привілей CAP_NET_RAW)");
        return EXIT_FAILURE;
    }

    /* Встановлення таймауту очікування на сокеті */
    struct timeval tv;
    tv.tv_sec = TIMEOUT_MS / 1000;
    tv.tv_usec = (TIMEOUT_MS % 1000) * 1000;
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        close(sockfd);
        return EXIT_FAILURE;
    }

    uint16_t pid_ident = (uint16_t)(getpid() & 0xFFFF);
    printf("Трасування маршруту до %s (максимум %d хопів):\n", argv[1], MAX_HOPS);

    for (int ttl = 1; ttl <= MAX_HOPS; ++ttl) {
        /* Налаштування поля TTL у заголовку вихідного IP-пакета */
        if (setsockopt(sockfd, IPPROTO_IP, IP_TTL, &ttl, sizeof(ttl)) < 0) {
            perror("setsockopt(IP_TTL)");
            break;
        }

        /* Підготовка пакета ICMP Echo Request */
        struct icmphdr icmp_req;
        memset(&icmp_req, 0, sizeof(icmp_req));
        icmp_req.type = ICMP_ECHO;
        icmp_req.code = 0;
        icmp_req.un.echo.id = htons(pid_ident);
        icmp_req.un.echo.sequence = htons((uint16_t)ttl);
        icmp_req.checksum = compute_checksum(&icmp_req, sizeof(icmp_req));

        struct timespec start_ts, end_ts;
        clock_gettime(CLOCK_MONOTONIC, &start_ts);

        ssize_t sent = sendto(sockfd, &icmp_req, sizeof(icmp_req), 0,
                              (struct sockaddr *)&target_addr, sizeof(target_addr));
        if (sent < 0) {
            perror("sendto");
            break;
        }

        /* Очікування та обробка відповіді від мережі */
        unsigned char recv_buf[512];
        struct sockaddr_in reply_addr;
        socklen_t addr_len = sizeof(reply_addr);

        ssize_t received = recvfrom(sockfd, recv_buf, sizeof(recv_buf), 0,
                                    (struct sockaddr *)&reply_addr, &addr_len);
        clock_gettime(CLOCK_MONOTONIC, &end_ts);

        if (received < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                printf("%2d  * * * (таймаут вузла)\n", ttl);
                continue;
            }
            perror("recvfrom");
            break;
        }

        double rtt_ms = (double)(end_ts.tv_sec - start_ts.tv_sec) * 1000.0 +
                        (double)(end_ts.tv_nsec - start_ts.tv_nsec) / 1000000.0;

        if (received < (ssize_t)sizeof(struct iphdr)) {
            continue;
        }

        struct iphdr *ip_hdr = (struct iphdr *)recv_buf;
        size_t ip_hdr_len = (size_t)(ip_hdr->ihl * 4);
        if (received < (ssize_t)(ip_hdr_len + sizeof(struct icmphdr))) {
            continue;
        }

        struct icmphdr *icmp_reply = (struct icmphdr *)(recv_buf + ip_hdr_len);
        char ip_str[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &reply_addr.sin_addr, ip_str, sizeof(ip_str));

        if (icmp_reply->type == ICMP_TIME_EXCEEDED && icmp_reply->code == 0) {
            /* Проміжний маршрутизатор */
            printf("%2d  %-15s  %.3f ms\n", ttl, ip_str, rtt_ms);
        } else if (icmp_reply->type == ICMP_ECHOREPLY) {
            /* Кінцевий цільовий вузол */
            printf("%2d  %-15s  %.3f ms (досягнуто призначення)\n", ttl, ip_str, rtt_ms);
            break;
        } else {
            printf("%2d  %-15s  ICMP type=%d code=%d  %.3f ms\n",
                   ttl, ip_str, icmp_reply->type, icmp_reply->code, rtt_ms);
        }
    }

    close(sockfd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <chrono>
#include <span>
#include <format>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

namespace net {

// RAII-обгортка для керування життєвим циклом сокетного дескриптора
class UniqueSocket {
public:
    explicit UniqueSocket(int fd = -1) noexcept : fd_{fd} {}
    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_{other.fd_} {
        other.fd_ = -1;
    }
    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
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
    int fd_;
};

// Обчислення контрольної суми RFC 1071 над константним діапазоном пам'яті
[[nodiscard]] constexpr uint16_t compute_checksum(std::span<const uint8_t> bytes) noexcept {
    uint32_t sum = 0;
    size_t i = 0;
    while (i + 1 < bytes.size()) {
        const uint16_t word = static_cast<uint16_t>(bytes[i]) | 
                              (static_cast<uint16_t>(bytes[i + 1]) << 8);
        sum += word;
        i += 2;
    }
    if (i < bytes.size()) {
        sum += static_cast<uint16_t>(bytes[i]);
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<uint16_t>(~sum);
}

class TracerouteEngine {
public:
    static constexpr int MaxHops = 30;
    static constexpr int TimeoutMs = 1000;

    explicit TracerouteEngine(std::string target_ip) 
        : target_ip_{std::move(target_ip)} {}

    void execute() {
        sockaddr_in target{};
        target.sin_family = AF_INET;
        if (::inet_pton(AF_INET, target_ip_.c_str(), &target.sin_addr) <= 0) {
            std::cerr << "Некоректна IP-адреса: " << target_ip_ << "\n";
            return;
        }

        UniqueSocket sock{::socket(AF_INET, SOCK_RAW, IPPROTO_ICMP)};
        if (!sock.valid()) {
            std::cerr << "Помилка відкриття SOCK_RAW (потрібен CAP_NET_RAW): " 
                      << std::strerror(errno) << "\n";
            return;
        }

        timeval tv{
            .tv_sec = TimeoutMs / 1000,
            .tv_usec = (TimeoutMs % 1000) * 1000
        };
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            std::cerr << "Помилка встановлення таймауту сокета\n";
            return;
        }

        const auto pid = static_cast<uint16_t>(::getpid() & 0xFFFF);
        std::cout << "Трасування маршруту до " << target_ip_ 
                  << " (максимум " << MaxHops << " хопів):\n";

        for (int ttl = 1; ttl <= MaxHops; ++ttl) {
            if (::setsockopt(sock.get(), IPPROTO_IP, IP_TTL, &ttl, sizeof(ttl)) < 0) {
                std::cerr << "Помилка setsockopt(IP_TTL)\n";
                break;
            }

            icmphdr req{};
            req.type = ICMP_ECHO;
            req.code = 0;
            req.un.echo.id = htons(pid);
            req.un.echo.sequence = htons(static_cast<uint16_t>(ttl));
            
            auto req_span = std::span<const uint8_t>(
                reinterpret_cast<const uint8_t*>(&req), sizeof(req)
            );
            req.checksum = compute_checksum(req_span);

            const auto start_time = std::chrono::steady_clock::now();

            const auto sent = ::sendto(sock.get(), &req, sizeof(req), 0,
                                       reinterpret_cast<const sockaddr*>(&target), 
                                       sizeof(target));
            if (sent < 0) {
                std::cerr << "Помилка sendto: " << std::strerror(errno) << "\n";
                break;
            }

            std::vector<uint8_t> buffer(512);
            sockaddr_in reply_addr{};
            socklen_t addr_len = sizeof(reply_addr);

            const auto received = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0,
                                             reinterpret_cast<sockaddr*>(&reply_addr), 
                                             &addr_len);
            const auto end_time = std::chrono::steady_clock::now();

            if (received < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    std::cout << std::format("{:2d}  * * * (таймаут вузла)\n", ttl);
                    continue;
                }
                std::cerr << "Помилка recvfrom: " << std::strerror(errno) << "\n";
                break;
            }

            const std::chrono::duration<double, std::milli> rtt = end_time - start_time;

            if (static_cast<size_t>(received) < sizeof(iphdr)) {
                continue;
            }

            const auto* ip_hdr = reinterpret_cast<const iphdr*>(buffer.data());
            const size_t ip_hdr_bytes = ip_hdr->ihl * 4;
            if (static_cast<size_t>(received) < ip_hdr_bytes + sizeof(icmphdr)) {
                continue;
            }

            const auto* icmp_reply = reinterpret_cast<const icmphdr*>(buffer.data() + ip_hdr_bytes);
            char ip_str[INET_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET, &reply_addr.sin_addr, ip_str, sizeof(ip_str));

            if (icmp_reply->type == ICMP_TIME_EXCEEDED && icmp_reply->code == 0) {
                std::cout << std::format("{:2d}  {:15s}  {:.3f} ms\n", ttl, ip_str, rtt.count());
            } else if (icmp_reply->type == ICMP_ECHOREPLY) {
                std::cout << std::format("{:2d}  {:15s}  {:.3f} ms (досягнуто призначення)\n", ttl, ip_str, rtt.count());
                break;
            } else {
                std::cout << std::format("{:2d}  {:15s}  ICMP type={} code={}  {:.3f} ms\n",
                                         ttl, ip_str, icmp_reply->type, icmp_reply->code, rtt.count());
            }
        }
    }

private:
    std::string target_ip_;
};

} // namespace net

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Використання: " << argv[0] << " <IPv4-адреса>\n";
        return EXIT_FAILURE;
    }

    net::TracerouteEngine engine{argv[1]};
    engine.execute();
    return EXIT_SUCCESS;
}
```
:::

---

## Інженерні пастки та оптимізації

1. **Мінімальні привілеї та POSIX Capabilities**: для уникнення запуску бінарного файлу від користувача `root` використовують привілей ядра `CAP_NET_RAW`. Його можна призначити бінарному файлу утиліти за допомогою утиліти `setcap`:
   ```bash
   sudo setcap cap_net_raw+ep ./custom_traceroute
   ```
2. **Змінний розмір заголовка IPv4**: заголовок IPv4 не завжди дорівнює 20 байтам. Поле `iphdr->ihl` містить довжину заголовка в 32-бітних словах (наприклад, `ihl = 5` відповідає 20 байтам, `ihl = 6` — 24 байтам при наявності опцій безпеки або часових міток IP Options). Нехтування множенням `ihl * 4` призводить до неправильного обчислення зміщення заголовка ICMP і прочитання пошкоджених даних.
3. **Особливості подвійного стеку (IPv6)**: для трасування IPv6-маршрутів створюється сокет з протоколом `IPPROTO_ICMPV6`. Замість сокетної опції `IP_TTL` використовується `IPV6_UNICAST_HOPS`, а замість `ICMP_TIME_EXCEEDED` очікується константа `ICMP6_TIME_EXCEEDED`. Крім того, ядро Linux автоматично обчислює контрольну суму для ICMPv6-пакетів (псевдозаголовок IPv6), тому ручне заповнення поля `checksum` для IPv6 не потрібне.
4. **Асинхронний режим через epoll**: у промислових системах моніторингу, які опитують тисячі цілей одночасно, послідовні блокуючі виклики `recvfrom()` замінюють на неблокуючий сирий сокет (`O_NONBLOCK`) у поєднанні з системним викликом `epoll_wait()`. Це дозволяє відправляти всі 30 зондів паралельно з різними значеннями `sequence` та збирати відповіді в єдиному циклі обробки подій без затримок на таймаутах.
5. **Фільтрація стороннього ICMP-трафіку через BPF**: оскільки сирий сокет `SOCK_RAW` для `IPPROTO_ICMP` отримує копії **всіх** вхідних ICMP-пакетів системи (включаючи `ping`, запущений іншими користувачами хоста), процес змушений перевіряти кожен отриманий пакет. Для оптимізації процесу в ядрі можна підключити BPF-фільтр через `SO_ATTACH_FILTER`, який перевірятиме поле `un.echo.id` і пропускатиме у виклик `recvfrom()` виключно зонди власного процесу.
6. **Розрахунок контрольної суми Internet Checksum**: обчислення поля `checksum` спирається на порозрядне додавання 16-бітних слів у зворотному коді (one's complement sum). Якщо довжина структури непарна, останній байт доповнюється нульовим байтом. Перед обчисленням поле `checksum` у структурі `icmphdr` обов'язково обнуляється, інакше результат перевірки буде хибним.

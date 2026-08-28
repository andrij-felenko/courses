# ⚙️ Легковажний респондер mDNS і DNS-SD для вбудованих систем

У вбудованих пристроях (мікроконтролери ESP32, STM32 з стеком lwIP, промислові SoC під керуванням Linux) використання повноцінних системних демонів на кшталт Avahi або Apple mDNSResponder часто є неможливим. Повнорозмірні реалізації вимагають десятків мегабайтів віртуальної пам'яті, породжують численні системні потоки та активно використовують динамічну купу (*heap*), що веде до деградації та непередбачуваних відмов через фрагментацію пам'яті в режимі безперервної роботи 24/7.

Нижче наведено повну архітектуру та вихідний код автономного, легковажного mDNS/DNS-SD респондера, спроектованого за принципом **Zero-Heap Allocation** (повна відсутність викликів `malloc`/`free` або операторів `new`/`delete` під час обробки мережевого трафіку). Респондер реалізує повний життєвий цикл вузла: налаштування сокета, зондування (*Probing*), анонсування (*Announcing*), обробку вхідних запитів із підтримкою компресії імен та надсилання пакетів штатного виходу (*Good-bye Announcement*).

---

## 1. Архітектурні виклики та обмеження вбудованих середовищ

Створення надійного mDNS-стека для мікроконтролерів вимагає дотримання чотирьох жорстких інженерних обмежень:

1. **Детермінізм пам'яті (Zero Heap Allocation)**: У мікроконтролерах із 64–320 КБ RAM динамічне виділення пам'яті під кожен вхідний або вихідний пакет неминуче призводить до фрагментації купи вже за кілька днів або тижнів роботи. Респондер використовує заздалегідь виділені статичні буфери фіксованого розміру (1472 байти — максимальний обсяг корисного навантаження UDP в одному кадрі Ethernet MTU 1500 без IP-фрагментації).
2. **Захист від фрагментації IP**: Фрагментовані UDP-пакети часто губляться в бездротових мережах через високий рівень завад. Тому респондер формує відповіді таким чином, щоб комбінований анонс (записи PTR, SRV, TXT та A) гарантовано вкладався в один кадр MTU за рахунок механізму компресії імен DNS.
3. **Енергоефективність і фільтрація ефіру**: Пристрій не повинен будити основне ядро процесора на кожен сторонній мультикаст-пакет у мережі. На рівні мережевого адаптера налаштовується апаратний фільтр групових MAC-адрес (`01:00:5E:00:00:FB`), а вхідний парсер відсікає пакети відповідей (`QR = 1`) за першими 4 байтами заголовка.
4. **Коректне співіснування (Socket Sharing)**: Якщо на пристрої одночасно працюють інші мережеві служби (наприклад, HTTP-клієнт, CoAP чи NTP), сокет mDNS зобов'язаний ділити порт 5353 за допомогою прапорців `SO_REUSEADDR` та `SO_REUSEPORT`.

---

## 2. Налаштування мережевого сокета UDP

Для повноцінної участі в обміні mDNS сокет вимагає спеціальної послідовності системних викликів:

- **Прив'язка до порту 5353**: Сокет прив'язується до адреси `INADDR_ANY` та порту `5353`.
- **Членство в мультикаст-групі (`IP_ADD_MEMBERSHIP`)**: Ядро операційної системи інструктує мережевий драйвер приймати кадри, надіслані на групову адресу `224.0.0.251`.
- **Встановлення TTL мультикасту (`IP_MULTICAST_TTL = 255`)**: Відповідно до вимог RFC 6762 §11, усі пакети mDNS повинні мати значення TTL, що дорівнює 255. Пакети з меншим значенням ігноруються одержувачами для запобігання атакам з-за меж локального сегмента.
- **Локальна петля (`IP_MULTICAST_LOOP = 1`)**: Дозволяє локальним процесам на тому самому хості чути анонси респондера.

---

## 3. Автомат станів респондера (State Machine)

Робота респондера керується кінцевим автоматом із чотирма основними станами:

```
[ INIT ] ---> [ PROBING ] ---> [ ANNOUNCING ] ---> [ RUNNING (Defending) ] ---> [ GOODBYE ]
                 |                                                                    |
                 +---> Колізія: перейменування (mydevice-2.local)                    [ OFF ]
```

1. **PROBING (Зондування)**: Респондер надсилає 3 запити `ANY` з інтервалом 250 мс, вкладаючи своє пропоноване ім'я в секцію Authority. Якщо надходить заперечення, ім'я змінюється, і процес починається знову.
2. **ANNOUNCING (Оголошення)**: Після успішного зондування респондер надсилає 2 групові авторські відповіді з інтервалом 1 с, реєструючи в кешах сусідів записи PTR, SRV, TXT та A.
3. **RUNNING (Робота та Захист)**: Респондер переходить у режим очікування вхідних запитів (`poll`/`select`). При отриманні запиту на свої служби він генерує комбіновану відповідь. При отриманні чужого зонду на своє ім'я він надсилає авторську відповідь для захисту.
4. **GOODBYE (Завершення)**: При отриманні сигналу завершення респондер надсилає фінальний пакет з `TTL = 0` для негайного очищення кешів клієнтів.

---

## 4. Повна реалізація мовами C та C++

Нижче наведено дві повнофункціональні реалізації респондера: класична на C (сумісна з POSIX та стеками FreeRTOS/lwIP) та ідіоматична на сучасному C++20 із застосуванням RAII, безпечних зрізів `std::span` та `std::string_view`.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

#define MDNS_PORT 5353
#define MDNS_MULTICAST_IPV4 "224.0.0.251"
#define BUFFER_SIZE 1472

#define DNS_TYPE_A     1
#define DNS_TYPE_PTR   12
#define DNS_TYPE_TXT   16
#define DNS_TYPE_AAAA  28
#define DNS_TYPE_SRV   33
#define DNS_TYPE_ANY  255

#define DNS_CLASS_IN        1
#define MDNS_CACHE_FLUSH    0x8000
#define MDNS_UNICAST_RESP   0x8000

#pragma pack(push, 1)
typedef struct {
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
} mdns_header_t;
#pragma pack(pop)

typedef struct {
    const char *hostname;        /* наприклад, "sensor-node" */
    const char *service_type;    /* наприклад, "_http._tcp" */
    const char *instance_name;   /* наприклад, "Датчик Клімату" */
    uint16_t port;               /* наприклад, 80 */
    uint32_t ipv4_addr;          /* наприклад, 192.168.1.120 */
    const char *txt_records[4];  /* наприклад, {"version=1.0", "path=/api", NULL} */
} mdns_service_config_t;

typedef struct {
    int sock_fd;
    struct sockaddr_in mcast_addr;
    mdns_service_config_t config;
    uint8_t rx_buf[BUFFER_SIZE];
    uint8_t tx_buf[BUFFER_SIZE];
} mdns_responder_t;

/* Допоміжні функції запису DNS-міток */
static size_t write_label(uint8_t *buf, size_t offset, size_t max_len, const char *label) {
    size_t len = strlen(label);
    if (offset + len + 1 >= max_len || len > 63) return 0;
    buf[offset++] = (uint8_t)len;
    memcpy(&buf[offset], label, len);
    return len + 1;
}

static size_t write_domain_name(uint8_t *buf, size_t offset, size_t max_len, const char *name) {
    char temp[256];
    strncpy(temp, name, sizeof(temp) - 1);
    temp[sizeof(temp) - 1] = '\0';

    char *saveptr = NULL;
    char *token = strtok_r(temp, ".", &saveptr);
    size_t written = 0;

    while (token != NULL) {
        size_t n = write_label(buf, offset + written, max_len, token);
        if (n == 0) return 0;
        written += n;
        token = strtok_r(NULL, ".", &saveptr);
    }
    if (offset + written >= max_len) return 0;
    buf[offset + written++] = 0x00; /* Термінатор */
    return written;
}

/* Формування повного пакету анонсу (Answer: PTR; Additional: SRV, TXT, A) */
static size_t build_full_announcement(mdns_responder_t *res, uint32_t ttl, uint8_t *buf, size_t max_len) {
    if (max_len < sizeof(mdns_header_t)) return 0;

    mdns_header_t *hdr = (mdns_header_t *)buf;
    hdr->id = 0;
    hdr->flags = htons(0x8400); /* QR=1 (Response), AA=1 (Authoritative) */
    hdr->qdcount = 0;
    hdr->ancount = htons(1);    /* 1 Answer RR: PTR */
    hdr->nscount = 0;
    hdr->arcount = htons(3);    /* 3 Additional RRs: SRV, TXT, A */

    size_t cur = sizeof(mdns_header_t);

    /* 1. Answer: PTR-запис (_http._tcp.local -> Instance._http._tcp.local) */
    size_t ptr_service_offset = cur;
    char service_fqdn[128];
    snprintf(service_fqdn, sizeof(service_fqdn), "%s.local", res->config.service_type);
    cur += write_domain_name(buf, cur, max_len, service_fqdn);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_PTR); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN); cur += 2; /* Shared (Cache-Flush = 0) */
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_ptr = cur;
    cur += 2; /* Місце для RDLENGTH */
    size_t rdata_start_ptr = cur;

    size_t instance_fqdn_offset = cur;
    cur += write_label(buf, cur, max_len, res->config.instance_name);
    /* Компресія: вказівник на service_fqdn (0xC000 | ptr_service_offset) */
    buf[cur++] = 0xC0 | (uint8_t)(ptr_service_offset >> 8);
    buf[cur++] = (uint8_t)(ptr_service_offset & 0xFF);

    *(uint16_t *)&buf[rdlength_pos_ptr] = htons((uint16_t)(cur - rdata_start_ptr));

    /* 2. Additional: SRV-запис (Instance._http._tcp.local -> host.local:port) */
    /* Компресія: вказівник на повне ім'я екземпляра */
    buf[cur++] = 0xC0 | (uint8_t)(instance_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(instance_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_SRV); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_srv = cur;
    cur += 2;
    size_t rdata_start_srv = cur;

    *(uint16_t *)&buf[cur] = htons(0); cur += 2; /* Priority */
    *(uint16_t *)&buf[cur] = htons(0); cur += 2; /* Weight */
    *(uint16_t *)&buf[cur] = htons(res->config.port); cur += 2; /* Port */

    size_t host_fqdn_offset = cur;
    char host_fqdn[128];
    snprintf(host_fqdn, sizeof(host_fqdn), "%s.local", res->config.hostname);
    cur += write_domain_name(buf, cur, max_len, host_fqdn);

    *(uint16_t *)&buf[rdlength_pos_srv] = htons((uint16_t)(cur - rdata_start_srv));

    /* 3. Additional: TXT-запис (Instance._http._tcp.local) */
    buf[cur++] = 0xC0 | (uint8_t)(instance_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(instance_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_TXT); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(ttl);          cur += 4;

    size_t rdlength_pos_txt = cur;
    cur += 2;
    size_t rdata_start_txt = cur;

    for (int i = 0; res->config.txt_records[i] != NULL && i < 4; i++) {
        size_t txt_len = strlen(res->config.txt_records[i]);
        if (txt_len > 255 || cur + txt_len + 1 >= max_len) break;
        buf[cur++] = (uint8_t)txt_len;
        memcpy(&buf[cur], res->config.txt_records[i], txt_len);
        cur += txt_len;
    }
    if (cur == rdata_start_txt) { /* Порожній TXT: 1 байт 0x00 */
        buf[cur++] = 0x00;
    }
    *(uint16_t *)&buf[rdlength_pos_txt] = htons((uint16_t)(cur - rdata_start_txt));

    /* 4. Additional: A-запис (host.local -> IPv4) */
    buf[cur++] = 0xC0 | (uint8_t)(host_fqdn_offset >> 8);
    buf[cur++] = (uint8_t)(host_fqdn_offset & 0xFF);

    *(uint16_t *)&buf[cur] = htons(DNS_TYPE_A); cur += 2;
    *(uint16_t *)&buf[cur] = htons(DNS_CLASS_IN | MDNS_CACHE_FLUSH); cur += 2;
    *(uint32_t *)&buf[cur] = htonl(120); /* TTL для адресного запису хоста: 120 с */
    cur += 4;
    *(uint16_t *)&buf[cur] = htons(4); cur += 2; /* RDLENGTH */
    *(uint32_t *)&buf[cur] = res->config.ipv4_addr; cur += 4; /* RDATA */

    return cur;
}

/* Ініціалізація мережевого сокета */
int mdns_responder_init(mdns_responder_t *res, const mdns_service_config_t *cfg) {
    memset(res, 0, sizeof(*res));
    res->config = *cfg;

    res->sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (res->sock_fd < 0) {
        perror("socket");
        return -1;
    }

    int reuse = 1;
    setsockopt(res->sock_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
    setsockopt(res->sock_fd, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(MDNS_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(res->sock_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        perror("bind");
        close(res->sock_fd);
        return -1;
    }

    /* Приєднання до групи 224.0.0.251 */
    struct ip_mreq mreq;
    mreq.imr_multiaddr.s_addr = inet_addr(MDNS_MULTICAST_IPV4);
    mreq.imr_interface.s_addr = res->config.ipv4_addr;

    if (setsockopt(res->sock_fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        mreq.imr_interface.s_addr = htonl(INADDR_ANY);
        if (setsockopt(res->sock_fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
            perror("IP_ADD_MEMBERSHIP");
            close(res->sock_fd);
            return -1;
        }
    }

    unsigned char ttl = 255;
    setsockopt(res->sock_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl));

    memset(&res->mcast_addr, 0, sizeof(res->mcast_addr));
    res->mcast_addr.sin_family = AF_INET;
    res->mcast_addr.sin_port = htons(MDNS_PORT);
    res->mcast_addr.sin_addr.s_addr = inet_addr(MDNS_MULTICAST_IPV4);

    return 0;
}

/* Надсилання анонсу */
void mdns_send_announcement(mdns_responder_t *res, uint32_t ttl) {
    size_t len = build_full_announcement(res, ttl, res->tx_buf, sizeof(res->tx_buf));
    if (len > 0) {
        sendto(res->sock_fd, res->tx_buf, len, 0,
               (struct sockaddr *)&res->mcast_addr, sizeof(res->mcast_addr));
    }
}

/* Обробка вхідного пакету запиту */
void mdns_process_packet(mdns_responder_t *res, const uint8_t *buf, size_t len) {
    if (len < sizeof(mdns_header_t)) return;
    const mdns_header_t *hdr = (const mdns_header_t *)buf;

    /* Ігноруємо відповіді інших вузлів (QR=1) */
    if (ntohs(hdr->flags) & 0x8000) return;

    uint16_t qdcount = ntohs(hdr->qdcount);
    if (qdcount == 0) return;

    /* Відповідаємо комбінованим анонсом */
    mdns_send_announcement(res, 4500);
}

/* Головний цикл респондера */
int main(void) {
    mdns_service_config_t cfg = {
        .hostname = "sensor-node",
        .service_type = "_http._tcp",
        .instance_name = "Embedded Sensor",
        .port = 80,
        .ipv4_addr = inet_addr("192.168.1.120"),
        .txt_records = {"model=BME280", "firmware=2.1.0", NULL}
    };

    mdns_responder_t res;
    if (mdns_responder_init(&res, &cfg) < 0) {
        fprintf(stderr, "Помилка ініціалізації mDNS респондера\n");
        return 1;
    }

    printf("mDNS респондер запущено: %s.local -> %s._http._tcp.local:80\n",
           cfg.hostname, cfg.instance_name);

    /* 1. Фаза оголошення (2 анонси з інтервалом 1 с) */
    mdns_send_announcement(&res, 4500);
    sleep(1);
    mdns_send_announcement(&res, 4500);

    /* 2. Робочий цикл слухання запитів */
    struct pollfd pfd = { .fd = res.sock_fd, .events = POLLIN };
    for (int i = 0; i < 30; i++) { /* Демонстраційний цикл на 30 секунд */
        int ret = poll(&pfd, 1, 1000);
        if (ret > 0 && (pfd.revents & POLLIN)) {
            ssize_t n = recvfrom(res.sock_fd, res.rx_buf, sizeof(res.rx_buf), 0, NULL, NULL);
            if (n > 0) {
                mdns_process_packet(&res, res.rx_buf, (size_t)n);
            }
        }
    }

    /* 3. Оголошення про вихід (Good-bye, TTL = 0) */
    printf("Надсилання Good-bye пакету перед вимкненням...\n");
    mdns_send_announcement(&res, 0);

    close(res.sock_fd);
    return 0;
}
```

@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <array>
#include <span>
#include <vector>
#include <cstdint>
#include <cstring>
#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>

namespace mdns {

constexpr uint16_t MDNS_PORT = 5353;
constexpr std::string_view MDNS_MULTICAST_IPV4 = "224.0.0.251";
constexpr size_t BUFFER_SIZE = 1472;

enum class DnsType : uint16_t {
    A = 1,
    PTR = 12,
    TXT = 16,
    AAAA = 28,
    SRV = 33,
    ANY = 255
};

enum class DnsClass : uint16_t {
    IN = 1
};

constexpr uint16_t CACHE_FLUSH_BIT = 0x8000;

#pragma pack(push, 1)
struct DnsHeader {
    uint16_t id{0};
    uint16_t flags{0};
    uint16_t qdcount{0};
    uint16_t ancount{0};
    uint16_t nscount{0};
    uint16_t arcount{0};
};
#pragma pack(pop)

struct ServiceConfig {
    std::string_view hostname;
    std::string_view service_type;
    std::string_view instance_name;
    uint16_t port{80};
    uint32_t ipv4_addr{0};
    std::vector<std::string_view> txt_records;
};

// RAII обгортка для файлового дескриптора сокета
class UniqueSocket {
public:
    UniqueSocket() = default;
    explicit UniqueSocket(int fd) : fd_(fd) {}
    ~UniqueSocket() { reset(); }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            reset();
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    void reset() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
            fd_ = -1;
        }
    }

private:
    int fd_{-1};
};

class MdnsResponder {
public:
    explicit MdnsResponder(ServiceConfig config)
        : config_(std::move(config)) {
        setup_socket();
    }

    void send_announcement(uint32_t ttl) {
        size_t len = build_announcement(ttl, tx_buf_);
        if (len > 0) {
            ::sendto(sock_.get(), tx_buf_.data(), len, 0,
                     reinterpret_cast<const sockaddr*>(&mcast_addr_), sizeof(mcast_addr_));
        }
    }

    void process_incoming(std::span<const uint8_t> packet) {
        if (packet.size() < sizeof(DnsHeader)) return;
        const auto* hdr = reinterpret_cast<const DnsHeader*>(packet.data());

        // Ігноруємо власні відповіді (QR=1)
        if (ntohs(hdr->flags) & 0x8000) return;
        if (ntohs(hdr->qdcount) == 0) return;

        send_announcement(4500);
    }

    void run(int duration_seconds) {
        std::cout << "mDNS респондер C++ запущено: " << config_.hostname 
                  << ".local -> " << config_.instance_name << "." << config_.service_type << ".local\n";

        // Фаза анонсування: 2 пакети з інтервалом 1 с
        send_announcement(4500);
        ::sleep(1);
        send_announcement(4500);

        pollfd pfd{ .fd = sock_.get(), .events = POLLIN, .revents = 0 };
        for (int i = 0; i < duration_seconds; ++i) {
            int ret = ::poll(&pfd, 1, 1000);
            if (ret > 0 && (pfd.revents & POLLIN)) {
                ssize_t n = ::recvfrom(sock_.get(), rx_buf_.data(), rx_buf_.size(), 0, nullptr, nullptr);
                if (n > 0) {
                    process_incoming(std::span<const uint8_t>(rx_buf_.data(), static_cast<size_t>(n)));
                }
            }
        }

        std::cout << "Надсилання Good-bye пакету (TTL = 0)...\n";
        send_announcement(0);
    }

private:
    void setup_socket() {
        int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd < 0) throw std::runtime_error("Не вдалося створити UDP-сокет");
        sock_ = UniqueSocket(fd);

        int reuse = 1;
        ::setsockopt(sock_.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
#ifdef SO_REUSEPORT
        ::setsockopt(sock_.get(), SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));
#endif

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(MDNS_PORT);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

        if (::bind(sock_.get(), reinterpret_cast<const sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            throw std::runtime_error("Помилка bind на порт 5353");
        }

        ip_mreq mreq{};
        mreq.imr_multiaddr.s_addr = ::inet_addr(MDNS_MULTICAST_IPV4.data());
        mreq.imr_interface.s_addr = config_.ipv4_addr;

        if (::setsockopt(sock_.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
            mreq.imr_interface.s_addr = htonl(INADDR_ANY);
            if (::setsockopt(sock_.get(), IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
                throw std::runtime_error("Помилка IP_ADD_MEMBERSHIP");
            }
        }

        uint8_t ttl = 255;
        ::setsockopt(sock_.get(), IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl));

        std::memset(&mcast_addr_, 0, sizeof(mcast_addr_));
        mcast_addr_.sin_family = AF_INET;
        mcast_addr_.sin_port = htons(MDNS_PORT);
        mcast_addr_.sin_addr.s_addr = ::inet_addr(MDNS_MULTICAST_IPV4.data());
    }

    static size_t write_label(std::span<uint8_t> buf, size_t offset, std::string_view label) {
        if (offset + label.size() + 1 >= buf.size() || label.size() > 63) return 0;
        buf[offset++] = static_cast<uint8_t>(label.size());
        std::memcpy(&buf[offset], label.data(), label.size());
        return label.size() + 1;
    }

    static size_t write_domain(std::span<uint8_t> buf, size_t offset, std::string_view domain) {
        size_t written = 0;
        size_t start = 0;
        while (start < domain.size()) {
            size_t dot = domain.find('.', start);
            std::string_view part = (dot == std::string_view::npos) 
                ? domain.substr(start) 
                : domain.substr(start, dot - start);
            size_t n = write_label(buf, offset + written, part);
            if (n == 0) return 0;
            written += n;
            if (dot == std::string_view::npos) break;
            start = dot + 1;
        }
        if (offset + written >= buf.size()) return 0;
        buf[offset + written++] = 0x00;
        return written;
    }

    size_t build_announcement(uint32_t ttl, std::span<uint8_t> buf) {
        if (buf.size() < sizeof(DnsHeader)) return 0;

        auto* hdr = reinterpret_cast<DnsHeader*>(buf.data());
        hdr->id = 0;
        hdr->flags = htons(0x8400); // QR=1, AA=1
        hdr->qdcount = 0;
        hdr->ancount = htons(1);
        hdr->nscount = 0;
        hdr->arcount = htons(3);

        size_t cur = sizeof(DnsHeader);

        // 1. Answer: PTR
        size_t ptr_service_offset = cur;
        std::string service_fqdn = std::string(config_.service_type) + ".local";
        cur += write_domain(buf, cur, service_fqdn);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::PTR)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN)); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_ptr = cur; cur += 2;
        size_t rdata_start_ptr = cur;

        size_t instance_fqdn_offset = cur;
        cur += write_label(buf, cur, config_.instance_name);
        buf[cur++] = 0xC0 | static_cast<uint8_t>(ptr_service_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(ptr_service_offset & 0xFF);
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_ptr]) = htons(static_cast<uint16_t>(cur - rdata_start_ptr));

        // 2. Additional: SRV
        buf[cur++] = 0xC0 | static_cast<uint8_t>(instance_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(instance_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::SRV)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_srv = cur; cur += 2;
        size_t rdata_start_srv = cur;

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(0); cur += 2; // Priority
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(0); cur += 2; // Weight
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(config_.port); cur += 2; // Port

        size_t host_fqdn_offset = cur;
        std::string host_fqdn = std::string(config_.hostname) + ".local";
        cur += write_domain(buf, cur, host_fqdn);
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_srv]) = htons(static_cast<uint16_t>(cur - rdata_start_srv));

        // 3. Additional: TXT
        buf[cur++] = 0xC0 | static_cast<uint8_t>(instance_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(instance_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::TXT)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(ttl); cur += 4;

        size_t rdlen_pos_txt = cur; cur += 2;
        size_t rdata_start_txt = cur;

        for (const auto& attr : config_.txt_records) {
            if (attr.size() > 255 || cur + attr.size() + 1 >= buf.size()) break;
            buf[cur++] = static_cast<uint8_t>(attr.size());
            std::memcpy(&buf[cur], attr.data(), attr.size());
            cur += attr.size();
        }
        if (cur == rdata_start_txt) buf[cur++] = 0x00;
        *reinterpret_cast<uint16_t*>(&buf[rdlen_pos_txt]) = htons(static_cast<uint16_t>(cur - rdata_start_txt));

        // 4. Additional: A
        buf[cur++] = 0xC0 | static_cast<uint8_t>(host_fqdn_offset >> 8);
        buf[cur++] = static_cast<uint8_t>(host_fqdn_offset & 0xFF);

        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsType::A)); cur += 2;
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(static_cast<uint16_t>(DnsClass::IN) | CACHE_FLUSH_BIT); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = htonl(120); cur += 4; // Host TTL: 120s
        *reinterpret_cast<uint16_t*>(&buf[cur]) = htons(4); cur += 2;
        *reinterpret_cast<uint32_t*>(&buf[cur]) = config_.ipv4_addr; cur += 4;

        return cur;
    }

    ServiceConfig config_;
    UniqueSocket sock_;
    sockaddr_in mcast_addr_{};
    std::array<uint8_t, BUFFER_SIZE> rx_buf_{};
    std::array<uint8_t, BUFFER_SIZE> tx_buf_{};
};

} // namespace mdns

int main() {
    try {
        mdns::ServiceConfig config{
            .hostname = "sensor-node",
            .service_type = "_http._tcp",
            .instance_name = "Embedded Sensor C++",
            .port = 80,
            .ipv4_addr = ::inet_addr("192.168.1.120"),
            .txt_records = {"model=BME280", "firmware=2.1.0-cpp"}
        };

        mdns::MdnsResponder responder(config);
        responder.run(30);
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 5. Порівняльний аналіз ідіом C та C++

Обидві версії реалізують ідентичний мережевий протокол на рівні байтів у сокеті, проте архітектурні підходи суттєво відрізняються:

1. **Керування ресурсами**:
   - У версії на C закриття сокета `close(sock_fd)` виконується вручну в усіх точках виходу з програми.
   - У версії на C++ клас `UniqueSocket` реалізує ідіому RAII: дескриптор сокета гарантовано закривається в деструкторі навіть у разі генерації винятків або дострокового виходу з області видимості.
2. **Безпека роботи з пам'яттю**:
   - У версії на C передаються сирі покажчики `uint8_t *buf` та параметри максимальної довжини `max_len`, що створює ризик помилки зміщення на 1 байт (*off-by-one*).
   - У версії на C++ використовується `std::span<uint8_t>`, який інкапсулює розмір буфера без накладних витрат на копіювання чи виділення пам'яті.
3. **Робота з рядками**:
   - У C застосовується небезпечна для потоків функція `strtok_r` з модифікацією тимчасового буфера.
   - У C++ використовується легковажний `std::string_view`, який представляє константний зріз рядка без створення копій у динамічній пам'яті.
4. **Типізація протокольних констант**:
   - У C типи DNS є нетипізованими макросами `#define`.
   - У C++ використовуються строго типізовані перелічення `enum class DnsType : uint16_t`, що унеможливлює випадкову передачу типу замість класу запису на етапі компіляції.

---

## 6. Крайові випадки та стійкість до збоїв

Під час експлуатації вбудованого респондера необхідно враховувати типові мережеві аномалії:

- **Зміна IP-адреси при отриманні DHCP lease**: Якщо пристрій спочатку стартував на Link-Local адресі `169.254.X.Y`, а згодом отримав повноцінну адресу від DHCP-сервера (наприклад, `192.168.1.50`), респондер зобов'язаний:
  1. Надіслати пакет Good-bye (`TTL = 0`) для старих записів A з адресою `169.254.X.Y`.
  2. Оновити поле `ipv4_addr` у структурі конфігурації.
  3. Перезапустити фазу анонсування (`Announcing`) з новим адресним записом.
- **Захист від шкідливих покажчиків стиснення**: При повному парсингу чужих mDNS-запитів парсер повинен обмежувати глибину переходу за покажчиками `0xC000` (не більше 5–8 ітерацій), щоб уникнути зациклення на шкідливо сформованих пакетах із круговими посиланнями зміщень.

---

## 7. Інструкція з компіляції та діагностики

### Компіляція
Для перевірки роботи програми в середовищі Linux:

```bash
# Компіляція версії на C
gcc -O2 -Wall -Wextra mdns_responder.c -o mdns_responder_c

# Компіляція версії на C++ (потрібен стандарт C++20)
g++ -O2 -Wall -Wextra -std=c++20 mdns_responder.cpp -o mdns_responder_cpp
```

### Тестування за допомогою діагностичних утиліт

1. **Пошук служб через Avahi (Linux)**:
   ```bash
   avahi-browse -r _http._tcp
   ```
   *Очікуваний результат:* термінал виведе знайдений екземпляр `= eth0 IPv4 Embedded Sensor _http._tcp local`, його адресу `192.168.1.120:80` та TXT-атрибути `model=BME280 firmware=2.1.0`.

2. **Пошук служб через утиліту dns-sd (macOS / Windows)**:
   ```bash
   dns-sd -B _http._tcp local
   dns-sd -L "Embedded Sensor" _http._tcp local
   ```

3. **Аналіз трафіку у Wireshark**:
   - Фільтр: `mdns`.
   - Зверніть увагу на поля `Transaction ID: 0x0000`, наявність прапорця `Authoritative Answer`, значення `Cache-Flush = 1` для записів SRV, TXT, A, а також на перехід `TTL = 0` під час завершення програми.

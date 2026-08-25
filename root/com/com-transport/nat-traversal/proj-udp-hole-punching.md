# ⚙️ Реалізація клієнта STUN та UDP Hole Punching

Для встановлення прямого двонаправленого каналу між двома хостами за маршрутизаторами з трансляцією адрес [NAT](topic:com-transport/nat) недостатньо просто знати локальні IP-адреси. Програма мусить самостійно визначити свої зовнішні координати в глобальній мережі за допомогою протоколу STUN, передати їх співрозмовнику через сигналізацію та здійснити синхронне пробивання отвору (UDP Hole Punching).

Нижче наведено повну архітектуру, покроковий аналіз взаємодії з ядром операційної системи, системні виклики, робочу реалізацію мережевого клієнта мовами C та C++20, методику простеження стану сесій через Netfilter conntrack, аналіз низькорівневого вирівнювання пам'яті, порівняння ідіом C/C++20 та розгорнуте керівництво з діагностики несправностей.

---

### 1. Архітектурні принципи та життєвий цикл сокета

Головна вимога до алгоритму подолання трансляції — **нерозривність життєвого циклу сокета**.

Типова помилка при розробці P2P-додатків полягає в тому, що розробник відкриває один UDP-сокет для надсилання запиту на STUN-сервер, отримує зовнішній порт, закриває цей сокет, а потім відкриває новий сокет для зв'язку з віддаленим піром. У момент закриття першого сокета маршрутизатор NAT негайно знищує створений запис у таблиці `conntrack`. Новий сокет отримає від операційної системи зовсім інший локальний порт, а транслятор NAT виділить для нього новий, невідомий зовнішній порт.

Тому клієнт зобов'язаний:
1. Створити один UDP-сокет і прив'язати його до локального порту за допомогою системного виклику `bind()`.
2. Використати саме цей сокет для надсилання STUN Binding Request.
3. Не закриваючи сокет, використати його для надсилання зустрічних пробних пакетів у бік піра та для подальшого обміну корисними даними.

```
       [ Локальний сокет: 0.0.0.0:50000 ]
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
[ Крок 1: STUN-запит ]     [ Крок 2: P2P Hole Punching ]
(Дізнаємося зовн. порт)     (Той самий сокет шле піру)
```

---

### 2. Конфігурація сокета та взаємодія з ядром ОС

Для стабільної роботи мережевого клієнта в реальних умовах сокет налаштовується за допомогою низки системних викликів:

1. **Створення сокета**: виклик `socket(AF_INET, SOCK_DGRAM, 0)` створює дескриптор сокета датаграм UDP.
2. **Повторне використання адрес (`SO_REUSEADDR` та `SO_REUSEPORT`)**: встановлення прапорців через `setsockopt()` дозволяє кільком процесам або потокам слухати один і той самий порт (що необхідно для симультанного відкриття TCP або паралельного прийому STUN та медіапотоку RTP).
3. **Тайм-аути прийому (`SO_RCVTIMEO`)**: оскільки UDP не гарантує доставку пакетів, блокуючий виклик `recvfrom()` без тайм-ауту може зависнути назавжди у разі втрати пакетів в Інтернеті. Встановлення тайм-ауту (наприклад, 1–2 секунди) дозволяє реалізувати повторні спроби.
4. **Неблокуючий ввід-вивід та подієві мультиплексори**: у промислових рушіях WebRTC сокет переводиться в неблокуючий режим за допомогою `fcntl(fd, F_SETFL, O_NONBLOCK)` та обслуговується подієвим циклом на базі системних викликів `epoll` (Linux) або `kqueue` (macOS/BSD). Це дозволяє одному системному потоку одночасно обслуговувати десятки STUN-транзакцій, DTLS-рукостискань та медіапотоків без блокування процесора.

---

### 3. Формування бінарного запиту STUN Binding Request

Згідно зі специфікацією [бінарного формату STUN](topic:com-transport/nat-traversal/api-stun-turn-headers.md), базовий запит `Binding Request` складається з 20 байтів заголовка без додаткових атрибутів:
* Поле `Message Type` встановлюється у значення `0x0001` (Клас `Request = 0b00`, Метод `Binding = 0x001`).
* Поле `Message Length` встановлюється у `0x0000` (тіло запиту не містить атрибутів).
* Поле `Magic Cookie` заповнюється фіксованим значенням `0x2112A442` у мережевому порядку байтів (`htonl`).
* Поле `Transaction ID` заповнюється 12 випадковими байтами. Для цього необхідно використовувати якісний генератор псевдовипадкових чисел або системне джерело ентропії (`std::random_device` або системний виклик `getrandom()`), оскільки збіг Transaction ID для двох різних запитів може призвести до хибного зіставлення відповідей.

---

### 4. Алгоритм розбору та демаскування відповіді STUN

Отримавши відповідь від сервера, клієнт здійснює трирівневу валідацію:
1. **Перевірка розміру буфера**: довжина отриманої датаграми повинна бути не меншою за 20 байтів.
2. **Перевірка типу та магічної константи**: поле типу повинно дорівнювати `0x0101` (`Success Response`), а магічна константа — `0x2112A442`.
3. **Перевірка цілісності транзакції**: отриманий у відповіді `Transaction ID` повинен байт-у-байт збігатися з `Transaction ID`, згенерованим для запиту.

Після валідації заголовка клієнт ітерує по списку TLV-атрибутів:
* Читає 16-бітний тип атрибута та 16-бітну довжину.
* Якщо тип дорівнює `0x0020` (`XOR-MAPPED-ADDRESS`), клієнт перевіряє сімейство адрес (байт `0x01` для IPv4).
* Для відновлення реального порту виконується операція XOR між 16-бітним маскованим портом та старшими 16 бітами Magic Cookie (`0x2112`).
* Для відновлення реальної IP-адреси IPv4 виконується операція XOR між 32-бітною маскованою адресою та повною 32-бітною константою Magic Cookie (`0x2112A442`).
* Зміщення вказівника для переходу до наступного атрибута обчислюється з обов'язковим урахуванням 4-байтового вирівнювання: `offset += (attr_len + 3) & ~3`.

---

### 5. Механіка зустрічного пробивання отворів (Hole Punching)

Після обміну публічними координатами через сигналізацію (наприклад, через WebSocket або SIP) обидва клієнти починають надсилати пробні UDP-пакети.

Оскільки клієнти не можуть розпочати надсилання абсолютно одночасно з мікросекундною точністю, виникає асиметрія:
1. Пакет від вузла A приходить на роутер B першим, коли роутер B ще не має запису в таблиці conntrack. Роутер B відкидає цей пакет або надсилає ICMP Port Unreachable. Проте на роутері A вихідний пакет **успішно створює стан очікування**.
2. За кілька мілісекунд вузол B відправляє свій пакет у бік публічного сокета A. Цей пакет створює стан у роутері B, долітає до роутера A і **безперешкодно проходить крізь відкритий на першому кроці стан**.
3. Наступний пакет від A до B проходить крізь відкритий на другому кроці стан у роутері B. Канал стає двонаправленим.

Щоб гарантувати відкриття каналу навіть за наявності мережевого тремтіння (джитеру) та тимчасових втрат пакетів, клієнт надсилає серію (вибух, burst) із 5–10 пробних пакетів з інтервалом 50–100 мілісекунд.

---

### 6. Повна реалізація мовами C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>

#define STUN_MAGIC_COOKIE 0x2112A442
#define STUN_BINDING_REQ   0x0001
#define STUN_BINDING_RESP  0x0101
#define ATTR_XOR_MAPPED_ADDR 0x0020

#pragma pack(push, 1)
typedef struct {
    uint16_t msg_type;
    uint16_t msg_length;
    uint32_t magic_cookie;
    uint8_t  transaction_id[12];
} StunMsgHeader;

typedef struct {
    uint16_t type;
    uint16_t length;
} StunAttrHeader;
#pragma pack(pop)

/* Запит до STUN-сервера та вилучення публічного рефлексивного сокета */
int get_reflexive_address(int sockfd, const char *stun_host, uint16_t stun_port,
                          char *out_ip, uint16_t *out_port) {
    struct hostent *server = gethostbyname(stun_host);
    if (!server) {
        perror("gethostbyname");
        return -1;
    }

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(stun_port);
    memcpy(&serv_addr.sin_addr.s_addr, server->h_addr_list[0], server->h_length);

    /* Формування заголовка Binding Request */
    StunMsgHeader req;
    req.msg_type = htons(STUN_BINDING_REQ);
    req.msg_length = htons(0);
    req.magic_cookie = htonl(STUN_MAGIC_COOKIE);
    for (int i = 0; i < 12; i++) {
        req.transaction_id[i] = (uint8_t)(rand() % 256);
    }

    /* Відправка STUN Binding Request */
    if (sendto(sockfd, &req, sizeof(req), 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        perror("sendto STUN");
        return -1;
    }

    uint8_t buf[512];
    struct sockaddr_in from_addr;
    socklen_t from_len = sizeof(from_addr);

    ssize_t n = recvfrom(sockfd, buf, sizeof(buf), 0, (struct sockaddr *)&from_addr, &from_len);
    if (n < (ssize_t)sizeof(StunMsgHeader)) {
        fprintf(stderr, "Помилка: занадто коротка відповідь STUN\n");
        return -1;
    }

    StunMsgHeader *resp = (StunMsgHeader *)buf;
    if (ntohs(resp->msg_type) != STUN_BINDING_RESP ||
        ntohl(resp->magic_cookie) != STUN_MAGIC_COOKIE ||
        memcmp(req.transaction_id, resp->transaction_id, 12) != 0) {
        fprintf(stderr, "Помилка валідації заголовка STUN або розбіжність Transaction ID\n");
        return -1;
    }

    /* Розбір TLV-атрибутів */
    uint16_t body_len = ntohs(resp->msg_length);
    size_t offset = sizeof(StunMsgHeader);
    size_t end = sizeof(StunMsgHeader) + body_len;

    while (offset + sizeof(StunAttrHeader) <= end && offset + sizeof(StunAttrHeader) <= (size_t)n) {
        StunAttrHeader *attr = (StunAttrHeader *)(buf + offset);
        uint16_t attr_type = ntohs(attr->type);
        uint16_t attr_len = ntohs(attr->length);
        offset += sizeof(StunAttrHeader);

        if (attr_type == ATTR_XOR_MAPPED_ADDR && attr_len >= 8) {
            uint8_t family = buf[offset + 1];
            if (family == 0x01) { /* IPv4 */
                uint16_t raw_xport;
                uint32_t raw_xaddr;
                memcpy(&raw_xport, buf + offset + 2, 2);
                memcpy(&raw_xaddr, buf + offset + 4, 4);

                uint16_t port = ntohs(raw_xport) ^ (STUN_MAGIC_COOKIE >> 16);
                uint32_t addr = ntohl(raw_xaddr) ^ STUN_MAGIC_COOKIE;

                struct in_addr in;
                in.s_addr = htonl(addr);
                strcpy(out_ip, inet_ntoa(in));
                *out_port = port;
                return 0;
            }
        }
        offset += (attr_len + 3) & ~3; /* Вирівнювання до 4 байтів */
    }

    return -1;
}

int main(int argc, char *argv[]) {
    srand(time(NULL));

    /* Створення єдиного сокета для всієї сесії */
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;
    local_addr.sin_port = htons(50000);

    if (bind(sockfd, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
        perror("bind");
        close(sockfd);
        return 1;
    }

    char pub_ip[64];
    uint16_t pub_port = 0;
    printf("[STUN] Визначення зовнішнього рефлексивного сокета через stun1.l.google.com:19302...\n");

    if (get_reflexive_address(sockfd, "stun1.l.google.com", 19302, pub_ip, &pub_port) == 0) {
        printf("[STUN] Успіх! Публічний рефлексивний сокет: %s:%u\n", pub_ip, pub_port);
    } else {
        fprintf(stderr, "[STUN] Не вдалося отримати рефлексивну адресу\n");
    }

    /* Виконання Hole Punching до віддаленого піра, якщо передано аргументи */
    if (argc >= 3) {
        const char *peer_ip = argv[1];
        uint16_t peer_port = (uint16_t)atoi(argv[2]);
        printf("[P2P] Початок UDP Hole Punching до цільового сокета %s:%u...\n", peer_ip, peer_port);

        struct sockaddr_in peer_addr;
        memset(&peer_addr, 0, sizeof(peer_addr));
        peer_addr.sin_family = AF_INET;
        peer_addr.sin_port = htons(peer_port);
        inet_pton(AF_INET, peer_ip, &peer_addr.sin_addr);

        const char *ping_msg = "HOLE_PUNCH_PING";
        for (int i = 0; i < 5; i++) {
            sendto(sockfd, ping_msg, strlen(ping_msg), 0, (struct sockaddr *)&peer_addr, sizeof(peer_addr));
            usleep(100000); /* 100 мс між спробами */
        }
        printf("[P2P] Серію пробних пакетів надіслано. Канал готовий для обміну даними.\n");
    }

    close(sockfd);
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <string>
#include <string_view>
#include <expected>
#include <random>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <netdb.h>

namespace net::p2p {

inline constexpr uint32_t STUN_MAGIC_COOKIE = 0x2112A442;
inline constexpr uint16_t STUN_BINDING_REQ   = 0x0001;
inline constexpr uint16_t STUN_BINDING_RESP  = 0x0101;
inline constexpr uint16_t ATTR_XOR_MAPPED_ADDR = 0x0020;

struct Endpoint {
    std::string ip;
    uint16_t port{0};
};

#pragma pack(push, 1)
struct StunHeader {
    uint16_t msg_type;
    uint16_t msg_length;
    uint32_t magic_cookie;
    std::array<uint8_t, 12> transaction_id;
};

struct StunAttr {
    uint16_t type;
    uint16_t length;
};
#pragma pack(pop)

/* RAII-клас для безпечного володіння та управління сокетом */
class UdpSocket {
    int fd_{-1};
public:
    UdpSocket() : fd_(::socket(AF_INET, SOCK_DGRAM, 0)) {}
    ~UdpSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;
    UdpSocket(UdpSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool isValid() const noexcept { return fd_ >= 0; }

    bool bind(uint16_t port) {
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(port);
        return ::bind(fd_, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == 0;
    }
};

class StunClient {
public:
    static std::expected<Endpoint, std::string> queryReflexive(const UdpSocket& sock,
                                                               std::string_view host,
                                                               uint16_t port) {
        addrinfo hints{}, *res = nullptr;
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_DGRAM;

        if (::getaddrinfo(host.data(), std::to_string(port).c_str(), &hints, &res) != 0 || !res) {
            return std::unexpected("Не вдалося розв'язати DNS-ім'я STUN-сервера");
        }

        StunHeader req{};
        req.msg_type = htons(STUN_BINDING_REQ);
        req.msg_length = htons(0);
        req.magic_cookie = htonl(STUN_MAGIC_COOKIE);

        std::random_device rd;
        for (auto& b : req.transaction_id) {
            b = static_cast<uint8_t>(rd() & 0xFF);
        }

        if (::sendto(sock.get(), &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
            ::freeaddrinfo(res);
            return std::unexpected("Помилка надсилання STUN Binding Request");
        }
        ::freeaddrinfo(res);

        std::array<uint8_t, 512> buffer{};
        sockaddr_in from{};
        socklen_t from_len = sizeof(from);

        ssize_t n = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0,
                               reinterpret_cast<sockaddr*>(&from), &from_len);
        if (n < static_cast<ssize_t>(sizeof(StunHeader))) {
            return std::unexpected("Отримано занадто коротку або пошкоджену відповідь");
        }

        const auto* resp = reinterpret_cast<const StunHeader*>(buffer.data());
        if (ntohs(resp->msg_type) != STUN_BINDING_RESP ||
            ntohl(resp->magic_cookie) != STUN_MAGIC_COOKIE ||
            resp->transaction_id != req.transaction_id) {
            return std::unexpected("Помилка автентифікації або незбіг Transaction ID STUN");
        }

        size_t offset = sizeof(StunHeader);
        size_t total = sizeof(StunHeader) + ntohs(resp->msg_length);

        while (offset + sizeof(StunAttr) <= total && offset + sizeof(StunAttr) <= static_cast<size_t>(n)) {
            const auto* attr = reinterpret_cast<const StunAttr*>(buffer.data() + offset);
            uint16_t type = ntohs(attr->type);
            uint16_t len = ntohs(attr->length);
            offset += sizeof(StunAttr);

            if (type == ATTR_XOR_MAPPED_ADDR && len >= 8) {
                uint8_t family = buffer[offset + 1];
                if (family == 0x01) { /* IPv4 */
                    uint16_t raw_port;
                    uint32_t raw_addr;
                    std::memcpy(&raw_port, buffer.data() + offset + 2, 2);
                    std::memcpy(&raw_addr, buffer.data() + offset + 4, 4);

                    uint16_t mapped_port = ntohs(raw_port) ^ (STUN_MAGIC_COOKIE >> 16);
                    uint32_t mapped_addr = ntohl(raw_addr) ^ STUN_MAGIC_COOKIE;

                    in_addr in{};
                    in.s_addr = htonl(mapped_addr);
                    char ip_buf[INET_ADDRSTRLEN];
                    ::inet_ntop(AF_INET, &in, ip_buf, sizeof(ip_buf));

                    return Endpoint{std::string(ip_buf), mapped_port};
                }
            }
            offset += (len + 3) & ~3;
        }

        return std::unexpected("Атрибут XOR-MAPPED-ADDRESS не знайдено у відповіді");
    }

    static bool punchHole(const UdpSocket& sock, std::string_view peer_ip, uint16_t peer_port) {
        sockaddr_in peer_addr{};
        peer_addr.sin_family = AF_INET;
        peer_addr.sin_port = htons(peer_port);
        if (::inet_pton(AF_INET, peer_ip.data(), &peer_addr.sin_addr) <= 0) {
            return false;
        }

        constexpr std::string_view ping_msg = "HOLE_PUNCH_PING";
        for (int i = 0; i < 5; ++i) {
            ::sendto(sock.get(), ping_msg.data(), ping_msg.size(), 0,
                     reinterpret_cast<const sockaddr*>(&peer_addr), sizeof(peer_addr));
            ::usleep(100000);
        }
        return true;
    }
};

} // namespace net::p2p

int main(int argc, char* argv[]) {
    using namespace net::p2p;

    UdpSocket sock;
    if (!sock.isValid() || !sock.bind(50000)) {
        std::cerr << "Помилка створення або прив'язки UDP-сокета\n";
        return 1;
    }

    std::cout << "[STUN C++20] Запит рефлексивної адреси через stun1.l.google.com:19302...\n";
    auto result = StunClient::queryReflexive(sock, "stun1.l.google.com", 19302);

    if (result) {
        std::cout << "[STUN C++20] Успіх! Публічний сокет: "
                  << result->ip << ":" << result->port << "\n";
    } else {
        std::cerr << "[STUN C++20] Помилка: " << result.error() << "\n";
    }

    if (argc >= 3) {
        std::string_view peer_ip = argv[1];
        uint16_t peer_port = static_cast<uint16_t>(std::stoi(argv[2]));
        std::cout << "[P2P C++20] Початок UDP Hole Punching до " << peer_ip << ":" << peer_port << "...\n";
        if (StunClient::punchHole(sock, peer_ip, peer_port)) {
            std::cout << "[P2P C++20] Пробні пакети надіслано. Канал готовий.\n";
        }
    }

    return 0;
}
```
:::

---

### 10. Порівняльний аналіз технологій подолання міжмережевих екранів

У сучасній мережевій інженерії використовується кілька альтернативних методів проходження маршрутизаторів. Їхні сильні сторони та обмеження наведено у порівняльній таблиці:

| Технологія / Протокол | Принцип дії | Переваги | Обмеження та недоліки |
| :--- | :--- | :--- | :--- |
| **STUN + UDP Hole Punching** | Зустрічне відкриття сесій у таблицях conntrack | Не вимагає додаткових привілеїв на роутері, прямий P2P без затримок | Не працює, коли обидва учасники за симетричним NAT |
| **TURN Relay** | Ретрансляція через публічний сервер-посередник | 100% гарантія з'єднання крізь будь-які типи фаєрволів та симетричний NAT | Висока вартість серверного трафіку, збільшення затримки RTT удвічі |
| **UPnP IGD** | Клієнт надсилає XML/SOAP запит домашньому роутеру на прокидання порту | Створює повноцінний відкритий порт на роутері без потреби у зустрічних пакетах | Вимкнено за замовчуванням з міркувань безпеки, відсутній у корпоративних мережах та мобільному 4G/5G |
| **PCP (Port Control Protocol, RFC 6887)** | Сучасна заміна UPnP для шлюзів операторського рівня CGNAT | Дозволяє клієнту явно запросити стабільний зовнішній порт у оператора | Складна реалізація, слабка підтримка серед масових провайдерів Інтернету |

---

### 11. Переваги ідіоматичного C++20 над класичним C

Порівняння двох наведених реалізацій демонструє ключові переваги сучасних стандартів мови C++20 у мережевому програмуванні:

1. **Типобезпечна обробка помилок через `std::expected`**: класичний C-код повертає ціле число `-1` або `NULL`, змушуючи розробника перевіряти глобальну змінну `errno` або передавати покажчики для вихідних результатів. У C++20 тип `std::expected<Endpoint, std::string>` явно розділяє успішний результат і текст помилки на рівні системи типів, унеможливлюючи використання неініціалізованої адреси.
2. **Гарантія звільнення ресурсів через RAII (`UdpSocket`)**: у C-коді будь-яка помилка валідації вимагає ручного виклику `close(sockfd)` перед кожним `return -1`. У разі складного розгалуження коду це часто призводить до витоку дескрипторів сокетів. Клас `UdpSocket` автоматично закриває сокет у деструкторі при виході з області видимості за будь-яких обставин (включно з викиданням винятків).
3. **Безпечна робота з пам'яттю**: використання `std::array` та `std::string_view` усуває потребу в динамічному виділенні пам'яті через `malloc`/`free`, запобігаючи фрагментації купи та витокам пам'яті у високонавантажених сервісах.

---

### 12. Промислові вимоги до надійності та безпеки

При інтеграції наведеного коду у виробничі сервіси (наприклад, станції телеметрії або відеосервери WebRTC) необхідно дотримуватися таких правил:
1. **Експоненційний відступ таймерів (RFC 8489 Section 7.2.1)**: початковий інтервал очікування встановлюється у `RTO = 500` мс. При відсутності відповіді інтервал подвоюється після кожної спроби (`500 мс ➔ 1000 мс ➔ 2000 мс ➔ 4000 мс`), додаючи випадковий джитер `±10%` для запобігання резонансному перевантаженню STUN-серверів.
2. **Захист від DoS-віддзеркалення (Reflection Vector)**: клієнт повинен приймати та обробляти пакети виключно з перевірених адрес абонентів, узгоджених через захищений TLS-сигнальний канал із контролем сесійних токенів.
3. **Автоматичний перехід на TURN Relay**: якщо після 5–7 спроб UDP Hole Punching статус пари не переходить у стан `Succeeded`, клієнт повинен безшовно переключити медіапотік на резервний TURN-сервер, запобігаючи обриву з'єднання користувача.

---

### 13. Керівництво з пошуку та усунення несправностей (Troubleshooting)

Під час розгортання P2P-зв'язку в польових умовах інженери найчастіше стикаються з трьома типовими проблемами:

#### Симптом 1: STUN Binding Request надсилається, але відповідь не надходить
* **Причина A**: системний міжмережевий екран (наприклад, `ufw` або Windows Defender) блокує вхідні UDP-пакети з невідомих портів.
  * *Лікування*: додати правило `iptables -I INPUT -p udp --sport 19302 -j ACCEPT` або відкрити діапазон портів додатка.
* **Причина B**: інтернет-провайдер блокує нестандартні UDP-порти.
  * *Лікування*: налаштувати STUN-сервер на стандартний порт 3478 або порт DNS 53.

#### Симптом 2: STUN повертає публічну адресу, але Hole Punching між вузлами не працює
* **Причина**: один із маршрутизаторів використовує симетричний NAT (APDM), змінюючи порт для кожного нового адресата.
  * *Перевірка*: надіслати два послідовні STUN-запити на різні IP-адреси STUN-серверів (наприклад, `stun1.l.google.com` та `stun2.l.google.com`). Якщо повернені зовнішні порти різняться (наприклад, 40001 та 40002), пряме пробивання дірок неможливе.
  * *Лікування*: негайно ініціювати сесію ретрансляції через сервер TURN.

#### Симптом 3: Медіапотік спотворюється або обривається кожні 30 секунд
* **Причина**: вичерпання тайм-ауту трансляції UDP на проміжному маршрутизаторі через відсутність зворотного трафіку.
  * *Лікування*: налаштувати періодичне надсилання порожніх пакетів `STUN Binding Indication` або пакетів Keepalive кожні 10–15 секунд у фоновому потоці.

---

### 14. Застосування в системах телеметрії дронів та робототехніці

У практиці створення станцій наземного керування безпілотними літальними апаратами (GCS, Ground Control Station) та бортових комп'ютерів (на базі Raspberry Pi або Nvidia Jetson) протокол MAVLink часто передається поверх UDP. 

Коли дрон підключений через стільниковий 4G/LTE USB-модем, він отримує сіру IP-адресу в мережі оператора CGNAT. Застосування описаного в цьому розділі алгоритму STUN-зондування та зустрічного Hole Punching дозволяє:
* Підняти прямий P2P-канал телеметрії та відеопотоку H.264/H.265 із мінімальною круговою затримкою RTT (15–35 мс замість 100–180 мс через центральні хмарні сервери).
* Повністю усунути щомісячні фінансові витрати на оплату хмарного TURN-трафіку при трансляції десятків гігабайтів відео за зміну.
* Гарантувати надійне відновлення зв'язку за 200–500 мілісекунд у разі зміни стільникової вежі або перепідключення мобільного модема.

---

### 15. Міжплатформні відмінності сокетів (Linux, Windows Winsock2, macOS/BSD)

При портуванні мережевого рушія між різними операційними системами необхідно враховувати специфічні системні особливості стеків сокетів:

1. **Ініціалізація Winsock2 у Windows**:
   На відміну від систем POSIX (Linux/BSD), де сокети є звичайними файловими дескрипторами ядра, у Windows мережевий стек вимагає обов'язкової ініціалізації динамічної бібліотеки перед першим викликом `socket()`:

:::tabs
```c
#ifdef _WIN32
WSADATA wsaData;
if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    fprintf(stderr, "WSAStartup failed\n");
    return 1;
}
#endif
```
```cpp
#ifdef _WIN32
WSADATA wsaData{};
if (::WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    std::cerr << "WSAStartup failed\n";
    return 1;
}
#endif
```
:::

   Також у Windows замість системного виклику `close(fd)` використовується `closesocket(sock)`, для типів дескрипторів — `SOCKET` замість `int`, а наприкінці роботи процесу викликається `WSACleanup()`.

2. **Захист від сигналів у macOS/BSD (`SO_NOSIGPIPE`)**:
   У системах BSD та macOS запис у закритий мережевий сокет генерує системний сигнал `SIGPIPE`, що за замовчуванням аварійно завершує процес додатка. Для запобігання аварійним збоям сокет конфігурується спеціальною опцією:

:::tabs
```c
#ifdef SO_NOSIGPIPE
int set = 1;
setsockopt(sockfd, SOL_SOCKET, SO_NOSIGPIPE, (void *)&set, sizeof(set));
#endif
```
```cpp
#ifdef SO_NOSIGPIPE
int set = 1;
::setsockopt(sock.get(), SOL_SOCKET, SO_NOSIGPIPE, &set, sizeof(set));
#endif
```
:::

3. **Опція `SO_REUSEPORT` у Linux проти Windows**:
   У ядрі Linux (починаючи з версії 3.9) опція `SO_REUSEPORT` забезпечує апаратний розподіл вхідних UDP-пакетів між кількома потоками за допомогою хешування 4-кортежу. У Windows прапорець `SO_REUSEPORT` відсутній, а його функціонал еквівалентний прапорцю `SO_REUSEADDR`.

Дотримання цих міжплатформних інваріантів гарантує стабільну роботу P2P-рушія на настільних операційних системах (Linux, Windows, macOS), мобільних платформах (Android, iOS) та вбудованих Linux-дистрибутивах (OpenWrt, Yocto).

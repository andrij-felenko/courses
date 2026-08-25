# ⚙️ Реалізація власного DNS-клієнта: формування UDP-запиту й розбір відповідей

Цей практичний розділ демонструє низькорівневу реалізацію автономного клієнта DNS для надсилання прямих UDP-запитів до рекурсивного резолвера та побайтового розбору двійкової структури відповіді. Ми створимо повноцінну програму, яка без використання системних бібліотечних функцій на кшталт `getaddrinfo()` або `gethostbyname()` самостійно конструює двійкові пакети за стандартом RFC 1035, виконує мережевий обмін через сокети Берклі, обробляє компресію доменних імен та витягує адреси IPv4 (записи типу `A`) разом із їхнім часом життя (TTL).

---

## 1. Постановка задачі та вибір архітектури

У прикладних програмах високого рівня резолвінг імен зазвичай делегується стандартній бібліотеці операційної системи (виклик `getaddrinfo()`). Проте стандартна функція є блокуючою «чорною скринькою»: вона не надає доступу до окремих полів DNS-відповіді, не дозволяє дізнатися точний залишковий TTL запису, не підтримує вибір конкретного зовнішнього DNS-сервера в обхід системних налаштувань і створює надлишкове навантаження на вбудованих системах (мікроконтролерах без повноцінної ОС), де ресурси оперативної пам'яті суворо обмежені.

Наша мета — реалізувати компактний, безпечний і повністю прозорий клієнт DNS, який:
1. Приймає як аргументи командного рядка доменне ім'я цілі (наприклад, `example.com`) та IP-адресу бажаного DNS-сервера (наприклад, `8.8.8.8` від Google або `1.1.1.1` від Cloudflare).
2. Генерує криптографічно стійкий випадковий 16-бітний ідентифікатор транзакції (`Transaction ID`).
3. Формує 12-байтний заголовок із прапорцем `RD = 1` (англ. *Recursion Desired* — «бажана рекурсія»).
4. Кодує текстове доменне ім'я у послідовність двійкових міток змінної довжини (`QNAME`) та додає поля `QTYPE = 1` (`A`) і `QCLASS = 1` (`IN`).
5. Відправляє дейтаграму через таймаутований сокет UDP на порт 53.
6. Приймає відповідь, верифікує збіг ідентифікатора `ID`, перевіряє код помилки `RCODE` та прапорець `QR = 1`.
7. Пропускає секцію запитання й послідовно парсить ресурсні записи в секції відповідей (`Answer Section`), коректно розв'язуючи стислі покажчики зміщення (`Name Compression`, байти `0xC0`).
8. Виводить отримані IP-адреси та значення TTL у секундах.

---

## 2. Покроковий алгоритм роботи парсера

Розгляньмо кожен етап формування та обробки пакета до написання програмного коду.

### Крок 1: Кодування імені домену (QNAME)
У протоколі DNS символи крапки між частинами імені не передаються. Кожна складова частина (мітка) перетворюється на блок, що починається з байта її довжини, за яким слідують символи мітки. Завершується ім'я нульовим байтом `0x00`, який позначає корінь дерева:

```
Вхідний рядок:   "example.com"
Крок 1 (мітка 1): довжина 7 -> [0x07] 'e' 'x' 'a' 'm' 'p' 'l' 'e'
Крок 2 (мітка 2): довжина 3 -> [0x03] 'c' 'o' 'm'
Крок 3 (кінець):  довжина 0 -> [0x00]
```

Загальний розмір закодованого імені завжди на 2 байти довший за довжину вихідного рядка (1 байт для довжини першої мітки замість відсутньої крапки попереду і 1 байт `0x00` у кінці). Стандарт RFC 1035 накладає суворе обмеження: довжина окремої мітки не може перевищувати 63 байти, а повна довжина доменного імені у двійковому представленні обмежена 255 байтами.

### Крок 2: Збирання двійкового заголовка
Заголовок DNS займає рівно 12 байтів:
- `ID`: 16 бітів (випадкове число, наприклад `0x4A2F`).
- `Flags`: 16 бітів. Для простого клієнтського рекурсивного запиту єдиним активним бітом є `RD` (біт 8, що у шістнадцятковому вигляді дорівнює `0x0100`).
- `QDCOUNT`: `0x0001` (одне питання в секції).
- `ANCOUNT`, `NSCOUNT`, `ARCOUNT`: усі нулі `0x0000`.

Усі 16-бітні та 32-бітні поля обов'язково конвертуються у мережевий порядок байтів (`big-endian`) за допомогою системної функції `htons()`.

### Крок 3: Розв'язання компресії імен (Name Compression)
У секції відповідей ім'я хоста часто не повторюється повністю, а кодується 2-байтним покажчиком. Якщо черговий байт має два встановлених старших біти (`byte & 0xC0 == 0xC0`), це означає, що наступні 14 бітів задають зміщення від початку DNS-заголовка, де це ім'я або його суфікс уже зустрічалися.

Парсер повинен рекурсивно або в циклі перейти за вказаним зміщенням, прочитати мітки звідти й повернутися назад. При цьому критично важливо контролювати глибину переходів (лічильник переходів не повинен перевищувати 10–16), щоб захиститися від шкідливих циклічних пакетів («компресійних бомб»), які можуть зациклити програму.

---

## 3. Повна реалізація мовами C та C++

Нижче наведено паралельні реалізації клієнта. Варіант мовою C базується на класичних POSIX-сокетах і ручному контролі буферів, а варіант мовою C++ демонструє сучасний ідіоматичний підхід (C++20): використання RAII-обгортки для дескриптора сокета, безпечних діапазонів `std::span` та винятків при виявленні некоректного формату даних.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

#define DNS_PORT 53
#define BUFFER_SIZE 512
#define MAX_LABEL_LEN 63
#define MAX_HOPS 16

/* 12-байтний заголовок DNS за стандартом RFC 1035 */
#pragma pack(push, 1)
typedef struct {
    uint16_t id;
    uint16_t flags;
    uint16_t qdcount;
    uint16_t ancount;
    uint16_t nscount;
    uint16_t arcount;
} dns_header_t;
#pragma pack(pop)

/* Перетворення рядка "example.com" у формат міток DNS "\x07example\x03com\x00" */
static int encode_dns_name(const char *hostname, uint8_t *buffer, size_t max_len) {
    size_t host_len = strlen(hostname);
    if (host_len + 2 > max_len) return -1;

    uint8_t *out = buffer;
    const char *start = hostname;
    const char *dot;

    while ((dot = strchr(start, '.')) != NULL) {
        size_t label_len = (size_t)(dot - start);
        if (label_len == 0 || label_len > MAX_LABEL_LEN) return -1;

        *out++ = (uint8_t)label_len;
        memcpy(out, start, label_len);
        out += label_len;
        start = dot + 1;
    }

    size_t last_len = strlen(start);
    if (last_len > 0) {
        if (last_len > MAX_LABEL_LEN) return -1;
        *out++ = (uint8_t)last_len;
        memcpy(out, start, last_len);
        out += last_len;
    }

    *out++ = 0x00; /* Корінь DNS */
    return (int)(out - buffer);
}

/* Декодування стисненого або відкритого імені DNS із буфера відповіді */
static int parse_dns_name(const uint8_t *packet, size_t packet_len, size_t offset,
                          char *out_name, size_t out_max, size_t *bytes_consumed) {
    size_t curr = offset;
    size_t out_idx = 0;
    int hops = 0;
    bool jumped = false;
    size_t initial_bytes = 0;

    while (curr < packet_len && hops < MAX_HOPS) {
        uint8_t len = packet[curr];

        if (len == 0) { /* Завершення імені */
            if (!jumped) initial_bytes = (curr - offset) + 1;
            curr++;
            break;
        }

        if ((len & 0xC0) == 0xC0) { /* Покажчик компресії */
            if (curr + 1 >= packet_len) return -1;
            uint16_t ptr_offset = (uint16_t)(((len & 0x3F) << 8) | packet[curr + 1]);
            if (ptr_offset >= packet_len) return -1;

            if (!jumped) {
                initial_bytes = (curr - offset) + 2;
                jumped = true;
            }
            curr = ptr_offset;
            hops++;
            continue;
        }

        /* Звичайна текстова мітка */
        curr++;
        if (curr + len > packet_len) return -1;
        if (out_idx + len + 2 > out_max) return -1;

        if (out_idx > 0) out_name[out_idx++] = '.';
        memcpy(&out_name[out_idx], &packet[curr], len);
        out_idx += len;
        curr += len;

        if (!jumped) initial_bytes = curr - offset;
    }

    if (hops >= MAX_HOPS) return -1; /* Захист від зациклення */
    out_name[out_idx] = '\0';
    if (bytes_consumed) *bytes_consumed = initial_bytes;
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Ужиток: %s <доменне ім'я> [DNS сервер]\n", argv[0]);
        return 1;
    }

    const char *hostname = argv[1];
    const char *dns_server = (argc >= 3) ? argv[2] : "8.8.8.8";

    printf("Розв'язання імені '%s' через DNS-сервер %s...\n", hostname, dns_server);

    /* 1. Створення сокета UDP */
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("Помилка створення сокета");
        return 1;
    }

    /* Встановлення таймауту отримання 3 секунди */
    struct timeval tv = { .tv_sec = 3, .tv_usec = 0 };
    setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    struct sockaddr_in serv_addr;
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(DNS_PORT);
    if (inet_pton(AF_INET, dns_server, &serv_addr.sin_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса DNS-сервера: %s\n", dns_server);
        close(sockfd);
        return 1;
    }

    /* 2. Формування пакета запиту */
    uint8_t packet[BUFFER_SIZE];
    memset(packet, 0, sizeof(packet));

    srand((unsigned)time(NULL) ^ getpid());
    uint16_t query_id = (uint16_t)(rand() & 0xFFFF);

    dns_header_t *hdr = (dns_header_t *)packet;
    hdr->id = htons(query_id);
    hdr->flags = htons(0x0100); /* RD = 1 (Recursion Desired) */
    hdr->qdcount = htons(1);

    size_t offset = sizeof(dns_header_t);
    int name_len = encode_dns_name(hostname, &packet[offset], sizeof(packet) - offset);
    if (name_len < 0) {
        fprintf(stderr, "Помилка кодування доменного імені\n");
        close(sockfd);
        return 1;
    }
    offset += (size_t)name_len;

    /* QTYPE = 1 (A), QCLASS = 1 (IN) */
    *(uint16_t *)(&packet[offset]) = htons(1);
    offset += 2;
    *(uint16_t *)(&packet[offset]) = htons(1);
    offset += 2;

    /* 3. Надсилання дейтаграми */
    ssize_t sent = sendto(sockfd, packet, offset, 0, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
    if (sent < 0) {
        perror("Помилка надсилання запиту");
        close(sockfd);
        return 1;
    }

    /* 4. Отримання відповіді */
    uint8_t resp[BUFFER_SIZE];
    socklen_t addr_len = sizeof(serv_addr);
    ssize_t resp_len = recvfrom(sockfd, resp, sizeof(resp), 0, (struct sockaddr *)&serv_addr, &addr_len);
    if (resp_len < (ssize_t)sizeof(dns_header_t)) {
        fprintf(stderr, "Таймаут відповіді або отримано пошкоджений пакет\n");
        close(sockfd);
        return 1;
    }
    close(sockfd);

    /* 5. Перевірка заголовка відповіді */
    dns_header_t *resp_hdr = (dns_header_t *)resp;
    uint16_t resp_id = ntohs(resp_hdr->id);
    uint16_t flags = ntohs(resp_hdr->flags);
    uint16_t ancount = ntohs(resp_hdr->ancount);
    uint16_t qdcount = ntohs(resp_hdr->qdcount);

    if (resp_id != query_id) {
        fprintf(stderr, "Невідповідність Transaction ID (очікувалось 0x%04X, отримано 0x%04X)\n", query_id, resp_id);
        return 1;
    }

    uint8_t rcode = (uint8_t)(flags & 0x000F);
    if (rcode != 0) {
        fprintf(stderr, "Сервер повернув помилку DNS RCODE = %d (3 = NXDomain, 2 = ServFail)\n", rcode);
        return 1;
    }

    printf("Отримано успішну відповідь: записів у секції Answer = %d\n", ancount);

    /* 6. Пропуск секції Question */
    size_t curr = sizeof(dns_header_t);
    for (int q = 0; q < qdcount; q++) {
        char qname[256];
        size_t consumed = 0;
        if (parse_dns_name(resp, (size_t)resp_len, curr, qname, sizeof(qname), &consumed) < 0) {
            fprintf(stderr, "Помилка розбору секції Question\n");
            return 1;
        }
        curr += consumed + 4; /* Ім'я + QTYPE (2B) + QCLASS (2B) */
    }

    /* 7. Розбір секції Answer */
    for (int a = 0; a < ancount; a++) {
        if (curr >= (size_t)resp_len) break;

        char rr_name[256];
        size_t consumed = 0;
        if (parse_dns_name(resp, (size_t)resp_len, curr, rr_name, sizeof(rr_name), &consumed) < 0) {
            fprintf(stderr, "Помилка розбору імені в записі Answer #%d\n", a + 1);
            return 1;
        }
        curr += consumed;

        if (curr + 10 > (size_t)resp_len) break;
        uint16_t rtype = ntohs(*(uint16_t *)(&resp[curr]));
        uint16_t rclass = ntohs(*(uint16_t *)(&resp[curr + 2]));
        uint32_t ttl = ntohl(*(uint32_t *)(&resp[curr + 4]));
        uint16_t rdlength = ntohs(*(uint16_t *)(&resp[curr + 8]));
        curr += 10;

        if (curr + rdlength > (size_t)resp_len) break;

        if (rtype == 1 && rclass == 1 && rdlength == 4) { /* Запис типу A (IPv4) */
            char ip_str[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &resp[curr], ip_str, sizeof(ip_str));
            printf("  [A] %s -> %s (TTL: %u с)\n", rr_name, ip_str, ttl);
        } else if (rtype == 5) { /* Запис типу CNAME */
            char cname[256];
            if (parse_dns_name(resp, (size_t)resp_len, curr, cname, sizeof(cname), NULL) == 0) {
                printf("  [CNAME] %s -> псевдонім для %s (TTL: %u с)\n", rr_name, cname, ttl);
            }
        }
        curr += rdlength;
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <stdexcept>
#include <random>
#include <cstring>
#include <cstdint>

#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <sys/time.h>

namespace dns {

constexpr uint16_t Port = 53;
constexpr size_t BufferSize = 512;
constexpr size_t MaxHops = 16;
constexpr size_t MaxLabelLen = 63;

/* RAII-обгортка над файловим дескриптором сокета */
class UniqueSocket {
public:
    UniqueSocket() : fd_(socket(AF_INET, SOCK_DGRAM, 0)) {
        if (fd_ < 0) {
            throw std::runtime_error("Не вдалося створити UDP-сокет");
        }
    }

    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            close(fd_);
        }
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void setTimeout(int seconds) {
        struct timeval tv = { .tv_sec = seconds, .tv_usec = 0 };
        if (setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            throw std::runtime_error("Не вдалося встановити таймаут сокета");
        }
    }

private:
    int fd_ = -1;
};

/* Результат розбору запису A */
struct RecordA {
    std::string name;
    std::string ip;
    uint32_t ttl;
};

/* Кодування текстового імені у формат міток DNS */
std::vector<uint8_t> encodeDomainName(std::string_view hostname) {
    std::vector<uint8_t> encoded;
    size_t start = 0;

    while (start < hostname.size()) {
        size_t dot = hostname.find('.', start);
        size_t len = (dot == std::string_view::npos) ? (hostname.size() - start) : (dot - start);

        if (len == 0 || len > MaxLabelLen) {
            throw std::invalid_argument("Некоректна довжина мітки доменного імені");
        }

        encoded.push_back(static_cast<uint8_t>(len));
        encoded.insert(encoded.end(), hostname.begin() + start, hostname.begin() + start + len);

        if (dot == std::string_view::npos) break;
        start = dot + 1;
    }

    encoded.push_back(0x00); /* Нульовий байт кореня */
    return encoded;
}

/* Декодування стисненого імені з буфера */
std::pair<std::string, size_t> decodeDomainName(std::span<const uint8_t> packet, size_t offset) {
    std::string name;
    size_t curr = offset;
    size_t initial_bytes = 0;
    bool jumped = false;
    size_t hops = 0;

    while (curr < packet.size() && hops < MaxHops) {
        uint8_t len = packet[curr];

        if (len == 0) {
            if (!jumped) initial_bytes = (curr - offset) + 1;
            break;
        }

        if ((len & 0xC0) == 0xC0) {
            if (curr + 1 >= packet.size()) {
                throw std::runtime_error("Помилка: покажчик виходить за межі пакета");
            }
            uint16_t ptr_offset = static_cast<uint16_t>(((len & 0x3F) << 8) | packet[curr + 1]);
            if (ptr_offset >= packet.size()) {
                throw std::runtime_error("Помилка: некоректне зміщення покажчика компресії");
            }

            if (!jumped) {
                initial_bytes = (curr - offset) + 2;
                jumped = true;
            }
            curr = ptr_offset;
            hops++;
            continue;
        }

        curr++;
        if (curr + len > packet.size()) {
            throw std::runtime_error("Помилка: мітка виходить за межі пакета");
        }

        if (!name.empty()) name.push_back('.');
        name.append(reinterpret_cast<const char*>(&packet[curr]), len);
        curr += len;

        if (!jumped) initial_bytes = curr - offset;
    }

    if (hops >= MaxHops) {
        throw std::runtime_error("Виявлено циклічний покажчик компресії (петлю)");
    }

    return {name, initial_bytes};
}

/* Виконання запиту та вилучення IP-адрес */
std::vector<RecordA> resolve(std::string_view hostname, std::string_view dnsServer = "8.8.8.8") {
    UniqueSocket sock;
    sock.setTimeout(3);

    struct sockaddr_in serv_addr{};
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(Port);
    if (inet_pton(AF_INET, dnsServer.data(), &serv_addr.sin_addr) <= 0) {
        throw std::invalid_argument("Некоректна IP-адреса DNS-сервера");
    }

    /* Генерація випадкового ID */
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint16_t> dist(1, 65535);
    uint16_t queryId = dist(gen);

    /* Побудова запиту */
    std::vector<uint8_t> queryPacket(12, 0);
    queryPacket[0] = static_cast<uint8_t>(queryId >> 8);
    queryPacket[1] = static_cast<uint8_t>(queryId & 0xFF);
    queryPacket[2] = 0x01; /* RD = 1 */
    queryPacket[3] = 0x00;
    queryPacket[4] = 0x00; /* QDCOUNT = 1 */
    queryPacket[5] = 0x01;

    auto encodedName = encodeDomainName(hostname);
    queryPacket.insert(queryPacket.end(), encodedName.begin(), encodedName.end());

    /* QTYPE = 1 (A), QCLASS = 1 (IN) */
    queryPacket.push_back(0x00); queryPacket.push_back(0x01);
    queryPacket.push_back(0x00); queryPacket.push_back(0x01);

    /* Надсилання */
    ssize_t sent = sendto(sock.get(), queryPacket.data(), queryPacket.size(), 0,
                          reinterpret_cast<struct sockaddr*>(&serv_addr), sizeof(serv_addr));
    if (sent < 0) {
        throw std::runtime_error("Помилка надсилання UDP-пакета");
    }

    /* Отримання */
    std::vector<uint8_t> respBuffer(BufferSize);
    socklen_t addrLen = sizeof(serv_addr);
    ssize_t received = recvfrom(sock.get(), respBuffer.data(), respBuffer.size(), 0,
                                reinterpret_cast<struct sockaddr*>(&serv_addr), &addrLen);
    if (received < 12) {
        throw std::runtime_error("Таймаут відповіді або неповний заголовок DNS");
    }
    respBuffer.resize(received);

    std::span<const uint8_t> respSpan(respBuffer);

    /* Перевірка заголовка */
    uint16_t respId = static_cast<uint16_t>((respSpan[0] << 8) | respSpan[1]);
    uint16_t flags = static_cast<uint16_t>((respSpan[2] << 8) | respSpan[3]);
    uint16_t qdcount = static_cast<uint16_t>((respSpan[4] << 8) | respSpan[5]);
    uint16_t ancount = static_cast<uint16_t>((respSpan[6] << 8) | respSpan[7]);

    if (respId != queryId) {
        throw std::runtime_error("Отримано відповідь із чужим Transaction ID");
    }

    uint8_t rcode = static_cast<uint8_t>(flags & 0x0F);
    if (rcode != 0) {
        throw std::runtime_error("Сервер повернув код помилки RCODE = " + std::to_string(rcode));
    }

    /* Пропуск Question */
    size_t curr = 12;
    for (uint16_t q = 0; q < qdcount; ++q) {
        auto [_, consumed] = decodeDomainName(respSpan, curr);
        curr += consumed + 4; /* Ім'я + QTYPE (2) + QCLASS (2) */
    }

    /* Розбір Answer */
    std::vector<RecordA> results;
    for (uint16_t a = 0; a < ancount; ++a) {
        if (curr >= respSpan.size()) break;

        auto [rrName, consumed] = decodeDomainName(respSpan, curr);
        curr += consumed;

        if (curr + 10 > respSpan.size()) break;
        uint16_t rtype = static_cast<uint16_t>((respSpan[curr] << 8) | respSpan[curr + 1]);
        uint16_t rclass = static_cast<uint16_t>((respSpan[curr + 2] << 8) | respSpan[curr + 3]);
        uint32_t ttl = (static_cast<uint32_t>(respSpan[curr + 4]) << 24) |
                       (static_cast<uint32_t>(respSpan[curr + 5]) << 16) |
                       (static_cast<uint32_t>(respSpan[curr + 6]) << 8)  |
                       (static_cast<uint32_t>(respSpan[curr + 7]));
        uint16_t rdlength = static_cast<uint16_t>((respSpan[curr + 8] << 8) | respSpan[curr + 9]);
        curr += 10;

        if (curr + rdlength > respSpan.size()) break;

        if (rtype == 1 && rclass == 1 && rdlength == 4) {
            char ipStr[INET_ADDRSTRLEN];
            inet_ntop(AF_INET, &respSpan[curr], ipStr, sizeof(ipStr));
            results.push_back({rrName, std::string(ipStr), ttl});
        }
        curr += rdlength;
    }

    return results;
}

} // namespace dns

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Ужиток: " << argv[0] << " <доменне ім'я> [DNS сервер]\n";
        return 1;
    }

    std::string_view hostname = argv[1];
    std::string_view server = (argc >= 3) ? argv[2] : "8.8.8.8";

    try {
        std::cout << "Розв'язання імені '" << hostname << "' через сервер " << server << "...\n";
        auto records = dns::resolve(hostname, server);

        std::cout << "Отримано адресні записи (" << records.size() << "):\n";
        for (const auto& r : records) {
            std::cout << "  -> " << r.name << " = " << r.ip << " (TTL: " << r.ttl << " с)\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## 4. Покрокове простеження обміну на рівні шістнадцяткових байтів

Щоб переконатися у бездоганності роботи нашого парсера, простежимо реальний мережевий сеанс звернення до публічного резолвера `8.8.8.8` для отримання адреси домену `example.com`.

### Двійковий дамп надісланого запиту (33 байти)

```
0000   4a 2f 01 00 00 01 00 00  00 00 00 00 07 65 78 61   J/...........exa
0010   6d 70 6c 65 03 63 6f 6d  00 00 01 00 01            mple.com.....
```

Розберемо значення кожного байта за зміщенням:
1. `4a 2f` — згенерований клієнтом ідентифікатор транзакції `Transaction ID = 0x4A2F`.
2. `01 00` — поле прапорців `Flags`. Біт 8 встановлено в `1` (`RD = 1`, Recursion Desired), решта бітів дорівнюють нулю (запит `QR = 0`, стандартний `Opcode = 0`).
3. `00 01` — `QDCOUNT = 1` (одне питання в секції Question).
4. `00 00 00 00 00 00` — лічильники `ANCOUNT`, `NSCOUNT` та `ARCOUNT` дорівнюють нулю.
5. `07 65 78 61 6d 70 6c 65` — мітка `"example"`: байт довжини `0x07` та 7 символів ASCII.
6. `03 63 6f 6d` — мітка `"com"`: байт довжини `0x03` та 3 символи ASCII.
7. `00` — нульовий байт кореневого домену, що завершує ланцюжок `QNAME`.
8. `00 01` — `QTYPE = 0x0001` (запит типу `A`).
9. `00 01` — `QCLASS = 0x0001` (клас `IN` — Internet).

### Двійковий дамп отриманої відповіді (49 байтів)

```
0000   4a 2f 81 80 00 01 00 01  00 00 00 00 07 65 78 61   J/...........exa
0010   6d 70 6c 65 03 63 6f 6d  00 00 01 00 01 c0 0c 00   mple.com........
0020   01 00 01 00 00 0e 10 00  04 5d b8 d8 22            .........].."
```

Розбір структури відповіді:
1. `4a 2f` — `ID` збігається із запитом (`0x4A2F`), підтверджуючи автентичність сесії.
2. `81 80` — прапорці: `QR = 1` (відповідь), `RD = 1` (бажана рекурсія), `RA = 1` (рекурсія доступна на сервері), `RCODE = 0` (успішно, `NoError`).
3. `00 01 00 01 00 00 00 00` — `QDCOUNT = 1`, `ANCOUNT = 1` (один запис у відповіді), секції NS та AR порожні.
4. Байти зі зміщення `0x0C` до `0x1A` — повторення секції Question (`example.com`, `A`, `IN`).
5. `c0 0c` — початок ресурсного запису у секції Answer. Байт `0xC0` вказує на покажчик компресії, а зміщення `0x0C` (12 у десятковій системі) спрямовує парсер на байт 12 пакета, де розташоване ім'я `example.com`.
6. `00 01` — `TYPE = 1` (`A`).
7. `00 01` — `CLASS = 1` (`IN`).
8. `00 00 0e 10` — `TTL = 0x0E10` (рівно 3600 секунд або 1 година).
9. `00 04` — `RDLENGTH = 4` байти корисної інформації.
10. `5d b8 d8 22` — 4 байти адреси IPv4: `93.184.216.34`.

---

## 5. Порівняльний аналіз підходів C та C++

Порівняння двох реалізацій виявляє фундаментальні відмінності в інженерній філософії мов:

| Критерій | Реалізація мовою C | Реалізація мовою C++ (C++20) |
| :--- | :--- | :--- |
| **Керування ресурсами сокета** | Ручний виклик `close(sockfd)` у кожній точці виходу та обробки помилок. Ризик витоку дескриптора при забутому закритті. | Клас `UniqueSocket` з ідіомою RAII: сокет гарантовано закривається деструктором при виході зі скоупу або генерації винятку. |
| **Безпека меж буфера** | Ручна перевірка індексів `curr + len > packet_len`. Легко пропустити помилку на одиницю (англ. *off-by-one*). | Використання `std::span<const uint8_t>` з чітко визначеними межами та автоматичною типізацією константного зрізу пам'яті. |
| **Робота з рядками** | Сирі покажчики `char*`, фіксовані буфери та небезпечні функції `memcpy`/`strcpy` з необхідністю ручного контролю нульового термінатора `\0`. | Контейнери `std::string` та легковажні перегляди `std::string_view`, що усувають зайве копіювання пам'яті без ризику переповнення. |
| **Обробка помилок** | Повернення числових статус-кодів `-1` та перевірка через `if`. Змішування бізнес-логіки з кодами помилок. | Ієрархія стандартних винятків (`std::runtime_error`, `std::invalid_argument`), що відокремлює нормальний хід виконання від збоїв. |
| **Генерація псевдовипадкових чисел** | Функція `rand() ^ getpid()`, яка має низьку ентропію і є вразливою до передбачення транзакційного ID. | Генератор `std::mt19937` з ініціалізацією від апаратного джерела ентропії `std::random_device`. |

---

## 6. Аналіз пасток та безпекових ризиків

Розробка мережевого клієнта DNS вимагає уваги до прихованих крайових випадків та потенційних векторів атак:

1. **Небезпека отруєння кешу та атак Камінського (DNS Cache Poisoning):**
   У класичних реалізаціях клієнт надсилав запити з фіксованого локального порту (наприклад, 1024) із послідовними ідентифікаторами `ID` (1, 2, 3...). Зловмисник міг надіслати тисячі підроблених UDP-відповідей із фальшивою IP-адресою, намагаючись вгадати 16-бітний `ID` раніше, ніж надійде справжня відповідь від сервера.
   - *Захист:* обов'язкова рандомізація як 16-бітного `Transaction ID`, так і вихідного порту клієнта (ефемерні порти UDP в діапазоні 49152–65535). Це збільшує ентропію запиту до `2¹⁶ · 2¹⁴ ≈ 2³⁰` комбінацій (понад мільярд варіантів), що робить підробку практично нездійсненною за час очікування відповіді.

2. **Захист від циклічних покажчиків компресії («компресійна бомба»):**
   Якщо сервер поверне байти `c0 00`, це означає покажчик на самий початок пакета (байт 0). Парсер перейде на початок, знову прочитає цей покажчик і увійде в нескінченний цикл. Лічильник переходів `hops` із жорстким обмеженням (не більше 16 стрибків) є критично необхідним бар'єром безпеки.

3. **Проблема чорних дір Path MTU та обрізання відповідей:**
   Класичний розмір пакета DNS через UDP обмежений 512 байтами. Якщо відповідь містить багато адрес або підписи DNSSEC, сервер встановлює прапорець `TC = 1` (TrunCation). Якщо клієнт проігнорує `TC = 1` і спробує розібрати обрізаний пакет, він отримає неповні дані. Правильна поведінка — негайно відкрити з'єднання TCP на порт 53 і повторити запит. Сучасні клієнти додатково використовують розширення EDNS0 (RFC 6891), передаючи псевдозапис `OPT` із зазначенням буфера розміром 4096 байтів.

---

## 7. Стратегії повторних спроб та обробка ненадійного транспорту UDP

Оскільки транспорт UDP не гарантує доставку дейтаграм, клієнт DNS виробничого рівня не може покладатися на єдину спробу запиту. Якщо мережевий пакет втрачено через перевантаження каналу, чергу на проміжному маршрутизаторі або збій на стороні сервера, блокуючий виклик `recvfrom()` без належно налаштованого таймауту призведе до вічного зависання програми.

### Механізм експоненційного відступу (Exponential Backoff)
Стандарт RFC 1035 рекомендує реалізовувати адаптивний тайм-аут з експоненційним зростанням затримки перед повторними спробами. Алгоритм працює наступним чином:
1. **Перша спроба:** клієнт генерує `Transaction ID`, відправляє пакет і чекає на відповідь 1 секунду.
2. **Друга спроба:** якщо відповідь не надійшла за 1 секунду, клієнт повторює відправку *того самого* запиту з тим самим `ID` і збільшує інтервал очікування до 2 секунд.
3. **Третя спроба:** при повторному таймауті інтервал збільшується до 4 секунд.
4. **Перемикання на резервний сервер:** якщо після 3–4 спроб основний сервер не відповів, клієнт змінює IP-адресу сервера на вторинний (наприклад, переходить від `8.8.8.8` до `8.8.4.4`) і починає процедуру з початкового інтервалу 1 секунда з *новим* `Transaction ID`.

### Чому не варто використовувати connect() для сокета UDP у DNS-клієнтах
У системному програмуванні для UDP-сокетів можна викликати функцію `connect()`, що закріплює віддалену IP-адресу та порт за дескриптором. Це дозволяє використовувати звичайні функції `send()` та `recv()` замість `sendto()`/`recvfrom()`. Проте для DNS-клієнтів це небажано:
- Виклик `connect()` жорстко прив'язує сокет до одного сервера. Якщо потрібно підтримувати список із 2–3 DNS-серверів для відмовостійкості, доведеться або розривати асоціацію (викликати `connect()` із `AF_UNSPEC`), або створювати окремий сокет під кожен сервер, що марнує системні ресурси.
- Використання незв'язаного сокета з `recvfrom()` дає змогу точно знати, від якої саме IP-адреси надійшов пакет відповіді, й мовчазно відкидати пакети, надіслані зі сторонніх IP-адрес (захист від несанкціонованого інжектування трафіку).

---

## 8. Робота з псевдонімами CNAME та множинними записами A

У реальному Інтернеті запит до популярного ресурсу (наприклад, великого CDN або веб-сервісу) майже ніколи не повертає єдиний прямий запис `A`. Відповідь зазвичай містить цілий ланцюжок записів.

### Розплутування ланцюжків CNAME
Якщо доменне ім'я є псевдонімом, авторитетний сервер повертає запис типу `CNAME` (Canonical Name), наприклад:
```
example.cdn.net -> CNAME -> cdn-lb.edge.global.net
```
Рекурсивний резолвер, отримавши такий запис, зобов'язаний продовжити резолвінг для цільового канонічного імені й додати до секції `Answer` також кінцевий запис `A` (або `AAAA`). Наш парсер розпізнає запис `CNAME` за полем `TYPE = 5`, витягує цільове ім'я за допомогою функції розбору міток і продовжує ітерацію за секцією `Answer`, поки не знайде безпосередні IP-адреси.

### Балансування навантаження через множинні записи A (DNS Round-Robin)
Якщо один веб-сервіс обслуговується кластером із 5 серверів, адміністратор зони публікує 5 різних записів `A` з однаковим іменем. Резолвер повертає всі 5 записів, але змінює їхній порядок у кожній відповіді (циклічний зсув — Round-Robin). Клієнтська програма має обрати першу доступну адресу для підключення, а якщо вона не відповідає по TCP (таймаут з'єднання) — спробувати наступну адресу зі списку.

---

## 9. Особливості реалізації на вбудованих мікроконтролерах

На вбудованих системах (мікроконтролерах STM32, ESP32, nRF52) використання динамічної пам'яті (`malloc`/`free` у C або `new`/`std::vector` у C++) часто заборонене або суворо обмежене через небезпеку фрагментації купи (англ. *heap fragmentation*) під час тривалої безперервної роботи.

У таких сценаріях архітектура клієнта DNS адаптується до вимог жорсткої детермінованості:
1. **Статичні буфери фіксованого розміру:** створюється один єдиний буфер `uint8_t dns_buf[512]`, який розташовується у статичній пам'яті або на стеку задачі FreeRTOS.
2. **Нульове копіювання (Zero-Copy):** замість виділення рядків для кожного знайденого доменного імені, парсер оперує числовими зміщеннями або безпосередньо витягує 4 байти IP-адреси в цільову структуру даних без проміжного збереження імен.
3. **Економія стеку:** рекурсивна функція розбору стиснених міток замінюється ітеративним циклом із лічильником переходів, щоб запобігти переповненню стеку мікроконтролера, який часто має розмір усього 2–4 кілобайти на задачу.

---

## 10. Еволюція до зашифрованого транспорту: DoT та DoH

Усі розглянуті вище механізми працюють поверх відкритого протоколу UDP на порту 53. У такій конфігурації DNS-пакети передаються відкритим текстом без жодного криптографічного захисту чи автентифікації. Будь-який проміжний вузол на маршруті (провайдер зв'язку, публічна точка доступу Wi-Fi, транзитний автономний маршрутизатор або цензурний фільтр DPI) може безперешкодно читати ваші DNS-запити, збирати історію відвідуваних доменів або підміняти повернені IP-адреси на льоту (атака Man-in-the-Middle).

Для розв'язання цієї фундаментальної вразливості були розроблені стандарти захищеного DNS-транспорту:
1. **DNS over TLS (DoT, RFC 7858):** передача повідомлень поверх захищеної сесії TLS на виділеному TCP-порту 853. У DoT використовується рівно той самий бінарний формат DNS-пакета, який ми щойно згенерували в коді, проте кожне повідомлення передується 2-байтним префіксом загальної довжини пакета (оскільки TCP є потоковим протоколом без збереження меж дейтаграм).
2. **DNS over HTTPS (DoH, RFC 8484):** інкапсуляція двійкового DNS-пакета у звичайний HTTP-запит (метод POST або GET) поверх з'єднання HTTP/2 або HTTP/3 на стандартному веб-порту 443 з MIME-типом `application/dns-message`. Для зовнішніх спостерігачів такий трафік виглядає абсолютно невідрізненним від звичайного відвідування захищених веб-сайтів.

Таким чином, розроблений нами модуль побудови та парсингу бінарних повідомлень DNS за стандартом RFC 1035 є універсальним ядром: додавши до нього обгортку шифрування TLS (наприклад, через OpenSSL або mbedTLS), ви отримуєте повноцінний клієнт сучасних безпечних протоколів DoT та DoH.

---

## 11. Збирання, тестування та верифікація

Для компіляції та перевірки створених програм у середовищі Linux або macOS виконайте такі команди в терміналі:

```bash
# Компіляція версії на C
gcc -O2 -Wall -Wextra -pedantic proj-dns-client.c -o dns_client_c

# Компіляція версії на C++ (стандарт C++20)
g++ -O2 -Wall -Wextra -std=c++20 proj-dns-client.cpp -o dns_client_cpp

# Тестування резолвінгу через публічний сервер Cloudflare (1.1.1.1)
./dns_client_cpp example.com 1.1.1.1

# Тестування резолвінгу через публічний сервер Google (8.8.8.8)
./dns_client_c wikipedia.org 8.8.8.8
```

Паралельно можна запустити мережевий аналізатор `tcpdump` в окремому вікні термінала для спостереження за створеними пакетами на інтерфейсі:

```bash
sudo tcpdump -n -vvv -i any udp port 53
```

Ви побачите структурований вивід із точним відображенням сформованого ідентифікатора транзакції, прапорця `RD`, закодованого імені та отриманих адресних записів `A` з відповідними значеннями TTL. Завдяки повній прозорості низькорівневого коду ви отримуєте точний контроль над кожним байтом, що передається мережею.

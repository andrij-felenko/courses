# ⚙️ Парсер та генератор повідомлень DHCP

Низькорівнева робота з протоколом DHCP вимагає прямого формування, серіалізації та безпечного розбору двійкових дейтаграм UDP без використання важких сторонніх бібліотек. Така задача постає перед інженерами під час розробки вбудованого програмного забезпечення для мікроконтролерів (де кожен кілобайт оперативної пам'яті на рахунку), написання власних завантажувачів операційних систем у середовищах PXE, створення легкодосяжних мережевих агентів для контейнерних середовищ або побудови діагностичних утиліт для тестування мережевої безпеки.

---

### Архітектура взаємодії з мережевим сокетом

Під час реалізації власного клієнта DHCP розробник стикається з фундаментальною особливістю операційних систем сімейства POSIX: на етапі запуску програми мережевий інтерфейс ще не має призначеної IP-адреси. Стандартний системний виклик `sendto()` через звичайний сокет `AF_INET` / `SOCK_DGRAM` не може відправити пакет, якщо таблиця маршрутизації ядра порожня і немає визначеного маршруту для адреси `255.255.255.255`.

Для забезпечення коректної відправки та прийому повідомлень DHCP на системному рівні необхідно виконати послідовне налаштування сокета:

1. **Отримання апаратної адреси інтерфейсу (`SIOCGIFHWADDR`):** Перш ніж формувати пакет, клієнт викликає функцію `ioctl(fd, SIOCGIFHWADDR, &ifr)` для запиту MAC-адреси фізичної мережевої карти безпосередньо у драйвера ядра Linux.
2. **Прапорець `SO_BROADCAST`:** За замовчуванням стек протоколів ядра Linux блокує відправку дейтаграм на широкомовну адресу `255.255.255.255`. Встановлення опції сокета через виклик `setsockopt(fd, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt))` знімає це обмеження і дозволяє вихідному трафіку залишати мережевий адаптер.
3. **Прив'язка до фізичного інтерфейсу (`SO_BINDTODEVICE`):** Якщо в комп'ютері або маршрутизаторі присутні кілька мережевих карт (наприклад, провідний інтерфейс `eth0` та бездротовий модуль `wlan0`), стек ядра без налаштованої таблиці маршрутизації не знає, через який саме фізичний порт виштовхувати дейтаграму на невизначену адресу `255.255.255.255`. Опція `SO_BINDTODEVICE` жорстко зв'язує сокет із конкретною назвою мережевого пристрою.
4. **Повторне використання порту (`SO_REUSEADDR` та `SO_REUSEPORT`):** Оскільки порт `68` може бути відкритий системним демоном управління мережею (наприклад, `systemd-networkd` або `NetworkManager`), увімкнення прапорців повторного використання портів дозволяє діагностичній утиліті слухати транзитні пакети одночасно з системними службами.
5. **Прив'язка до порту (`bind`):** Клієнтський процес зобов'язаний прив'язати сокет до локальної адреси `INADDR_ANY` (`0.0.0.0`) та порту `68` (`DHCP_CLIENT_PORT`). Це гарантує, що ядро передасть усі вхідні дейтаграми, надіслані сервером на порт 68, безпосередньо у буфер нашої програми.

---

### Структури даних та бітові інваріанти

Формат пакета DHCP суворо регламентований стандартом RFC 2131. Він складається з фіксованого 236-байтного заголовка, 4 байтів магічного числа (Magic Cookie `0x63825363`) та послідовності кортежів опцій змінної довжини TLV (Type-Length-Value).

```text
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     op (1B)   |   htype (1B)  |   hlen (1B)   |   hops (1B)   |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                            xid (4B)                           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           secs (2B)           |           flags (2B)          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          ciaddr  (4B)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          yiaddr  (4B)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          siaddr  (4B)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          giaddr  (4B)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          chaddr  (16B)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          sname   (64B)                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                          file    (128B)                       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                     magic cookie (4B: 0x63825363)             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                   опції TLV ... Опція 255 (End)               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Перед серіалізацією або читанням двійкових даних критично важливо враховувати порядок байтів. У комп'ютерних мережах стандартом є прямий порядок байтів (**Big-Endian** або **Network Byte Order**), де найстарший байт записується першим. На більшості сучасних процесорів архітектури x86/x86-64 та ARM за замовчуванням використовується зворотний порядок (**Little-Endian**).

Тому всі 16-бітні та 32-бітні поля заголовка і значень опцій вимагають обов'язкового перетворення функціями:
- `htonl()` (Host to Network Long) / `ntohl()` (Network to Host Long) для 32-бітних чисел (`xid`, IP-адреси, час оренди).
- `htons()` (Host to Network Short) / `ntohs()` (Network to Host Short) для 16-бітних чисел (`secs`, `flags`).

---

### Захист пам'яті та безпека TLV-парсера

Обробка сирих мережевих пакетів — одна з найбільш вразливих ділянок системного коду. Некоректно написаний парсер може стати вектором для атак типу відмови в обслуговуванні (DoS) або віддаленого виконання коду (RCE) через переповнення буфера на купі чи стеку.

Під час проектування алгоритму обходу опцій TLV необхідно суворо дотримуватися чотирьох захисних інваріантів:

1. **Контроль меж буфера (Bounds Checking):** Кожен крок ітератора повинен перевіряти, чи залишається в буфері хоча б один байт для коду опції, один байт для поля довжини і `Length` байтів для значення. Якщо `offset + 2 + opt_len > packet_size`, обробка пакета повинна негайно перериватися з кодом помилки.
2. **Захист від нескінченного циклу:** Пакет від зловмисника може не містити завершального байта Опції 255 (`End`). Умова виходу з циклу повинна контролюватися виключно фактичною довжиною отриманого буфера UDP, а не наявністю прапорця завершення.
3. **Обробка 1-байтних опцій:** Опція 0 (`Pad`) та Опція 255 (`End`) не мають полів довжини і значення. Спроба прочитати наступний байт як довжину для коду 0 призводить до зсуву всієї таблиці опцій і фатального спотворення даних.
4. **Запобігання невирівняному доступу до пам'яті (Unaligned Memory Access):** На багатьох мікроконтролерах (наприклад, ARM Cortex-M0/M3) пряме приведення вказівника на непарну адресу `uint32_t val = *(uint32_t*)(buffer + offset)` викликає апаратне переривання процесора `HardFault`. Безпечним та переносним способом читання багатобайтних чисел є використання `memcpy()` або побайтових бітових зсувів.

---

### Робоча реалізація мовами C та C++

Нижче наведено повну реалізацію модуля генерації запиту `DHCPDISCOVER` та захищеного парсера відповідей `DHCPOFFER` / `DHCPACK`.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <arpa/inet.h>

#define DHCP_CHADDR_LEN     16
#define DHCP_SNAME_LEN      64
#define DHCP_FILE_LEN       128
#define DHCP_MAGIC_COOKIE   0x63825363
#define DHCP_MIN_OPTIONS    312
#define DHCP_MAX_PACKET_LEN 576

#define OPT_PAD             0
#define OPT_SUBNET_MASK     1
#define OPT_ROUTER          3
#define OPT_DNS_SERVER      6
#define OPT_HOST_NAME       12
#define OPT_DOMAIN_NAME     15
#define OPT_REQUESTED_IP    50
#define OPT_LEASE_TIME      51
#define OPT_MSG_TYPE        53
#define OPT_SERVER_ID       54
#define OPT_PARAM_REQ_LIST  55
#define OPT_CLIENT_ID       61
#define OPT_END             255

#define DHCP_DISCOVER       1
#define DHCP_OFFER          2
#define DHCP_REQUEST        3
#define DHCP_ACK            5

#pragma pack(push, 1)
struct dhcp_packet {
    uint8_t  op;
    uint8_t  htype;
    uint8_t  hlen;
    uint8_t  hops;
    uint32_t xid;
    uint16_t secs;
    uint16_t flags;
    uint32_t ciaddr;
    uint32_t yiaddr;
    uint32_t siaddr;
    uint32_t giaddr;
    uint8_t  chaddr[DHCP_CHADDR_LEN];
    char     sname[DHCP_SNAME_LEN];
    char     file[DHCP_FILE_LEN];
    uint32_t magic_cookie;
    uint8_t  options[DHCP_MIN_OPTIONS];
};
#pragma pack(pop)

/* Структура вилучених параметрів конфігурації */
struct dhcp_parsed_info {
    uint32_t xid;
    uint32_t offered_ip;
    uint32_t server_ip;
    uint32_t subnet_mask;
    uint32_t router_ip;
    uint32_t dns_ip;
    uint32_t lease_time;
    uint8_t  msg_type;
    bool     valid;
};

/* Створення пакета DHCPDISCOVER */
size_t build_dhcp_discover(uint8_t *buffer, size_t max_len, const uint8_t mac[6], uint32_t xid) {
    if (!buffer || max_len < sizeof(struct dhcp_packet)) return 0;

    struct dhcp_packet *pkt = (struct dhcp_packet *)buffer;
    memset(pkt, 0, sizeof(struct dhcp_packet));

    pkt->op = 1;        /* BOOTREQUEST */
    pkt->htype = 1;     /* 10Mb Ethernet */
    pkt->hlen = 6;      /* MAC length */
    pkt->hops = 0;
    pkt->xid = htonl(xid);
    pkt->secs = htons(0);
    pkt->flags = htons(0x8000); /* Broadcast Flag: просимо широкомовну відповідь */
    pkt->ciaddr = 0;
    pkt->yiaddr = 0;
    pkt->siaddr = 0;
    pkt->giaddr = 0;
    memcpy(pkt->chaddr, mac, 6);
    pkt->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

    size_t opt_idx = 0;

    /* Option 53: DHCP Message Type = DHCPDISCOVER */
    pkt->options[opt_idx++] = OPT_MSG_TYPE;
    pkt->options[opt_idx++] = 1;
    pkt->options[opt_idx++] = DHCP_DISCOVER;

    /* Option 61: Client Identifier (Hardware Type 1 = Ethernet + MAC) */
    pkt->options[opt_idx++] = OPT_CLIENT_ID;
    pkt->options[opt_idx++] = 7;
    pkt->options[opt_idx++] = 1;
    memcpy(&pkt->options[opt_idx], mac, 6);
    opt_idx += 6;

    /* Option 55: Parameter Request List */
    pkt->options[opt_idx++] = OPT_PARAM_REQ_LIST;
    pkt->options[opt_idx++] = 4;
    pkt->options[opt_idx++] = OPT_SUBNET_MASK;
    pkt->options[opt_idx++] = OPT_ROUTER;
    pkt->options[opt_idx++] = OPT_DNS_SERVER;
    pkt->options[opt_idx++] = OPT_DOMAIN_NAME;

    /* Option 255: End */
    pkt->options[opt_idx++] = OPT_END;

    return 240 + opt_idx;
}

/* Безпечний розбір отриманої відповіді */
bool parse_dhcp_response(const uint8_t *buffer, size_t len, const uint8_t mac[6],
                         uint32_t expected_xid, struct dhcp_parsed_info *out_info) {
    if (!buffer || !out_info || len < 240) return false;

    const struct dhcp_packet *pkt = (const struct dhcp_packet *)buffer;

    /* Верифікація інваріантів заголовка */
    if (pkt->op != 2) return false; /* Очікуємо BOOTREPLY */
    if (ntohl(pkt->xid) != expected_xid) return false;
    if (memcmp(pkt->chaddr, mac, 6) != 0) return false;
    if (ntohl(pkt->magic_cookie) != DHCP_MAGIC_COOKIE) return false;

    memset(out_info, 0, sizeof(*out_info));
    out_info->xid = ntohl(pkt->xid);
    out_info->offered_ip = ntohl(pkt->yiaddr);

    /* Ітеративний захищений обхід опцій TLV */
    size_t offset = 240;
    while (offset < len) {
        uint8_t opt_code = buffer[offset++];

        if (opt_code == OPT_PAD) continue;
        if (opt_code == OPT_END) break;

        if (offset >= len) return false;
        uint8_t opt_len = buffer[offset++];

        if (offset + opt_len > len) return false; /* Захист від виходу за межі */

        const uint8_t *val = &buffer[offset];

        switch (opt_code) {
            case OPT_MSG_TYPE:
                if (opt_len >= 1) out_info->msg_type = val[0];
                break;
            case OPT_SERVER_ID:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->server_ip = ntohl(raw);
                }
                break;
            case OPT_SUBNET_MASK:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->subnet_mask = ntohl(raw);
                }
                break;
            case OPT_ROUTER:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->router_ip = ntohl(raw);
                }
                break;
            case OPT_DNS_SERVER:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->dns_ip = ntohl(raw);
                }
                break;
            case OPT_LEASE_TIME:
                if (opt_len >= 4) {
                    uint32_t raw;
                    memcpy(&raw, val, 4);
                    out_info->lease_time = ntohl(raw);
                }
                break;
            default:
                break;
        }

        offset += opt_len;
    }

    out_info->valid = (out_info->msg_type == DHCP_OFFER || out_info->msg_type == DHCP_ACK);
    return out_info->valid;
}

int main(void) {
    uint8_t client_mac[6] = {0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E};
    uint32_t xid = 0x39A4F2B1;
    uint8_t tx_buf[DHCP_MAX_PACKET_LEN];

    size_t tx_len = build_dhcp_discover(tx_buf, sizeof(tx_buf), client_mac, xid);
    printf("Сформовано DHCPDISCOVER довжиною %zu байтів.\n", tx_len);

    uint8_t rx_buf[DHCP_MAX_PACKET_LEN];
    memset(rx_buf, 0, sizeof(rx_buf));
    struct dhcp_packet *resp = (struct dhcp_packet *)rx_buf;
    resp->op = 2;
    resp->htype = 1;
    resp->hlen = 6;
    resp->xid = htonl(xid);
    resp->yiaddr = htonl(0xC0A80169); /* 192.168.1.105 */
    memcpy(resp->chaddr, client_mac, 6);
    resp->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

    size_t o = 240;
    rx_buf[o++] = OPT_MSG_TYPE; rx_buf[o++] = 1; rx_buf[o++] = DHCP_OFFER;
    rx_buf[o++] = OPT_SERVER_ID; rx_buf[o++] = 4;
    uint32_t s_ip = htonl(0xC0A80101); memcpy(&rx_buf[o], &s_ip, 4); o += 4;
    rx_buf[o++] = OPT_SUBNET_MASK; rx_buf[o++] = 4;
    uint32_t mask = htonl(0xFFFFFF00); memcpy(&rx_buf[o], &mask, 4); o += 4;
    rx_buf[o++] = OPT_LEASE_TIME; rx_buf[o++] = 4;
    uint32_t lease = htonl(86400); memcpy(&rx_buf[o], &lease, 4); o += 4;
    rx_buf[o++] = OPT_END;

    struct dhcp_parsed_info info;
    if (parse_dhcp_response(rx_buf, o, client_mac, xid, &info)) {
        struct in_addr ip_addr;
        ip_addr.s_addr = htonl(info.offered_ip);
        printf("Успішно розібрано DHCPOFFER:\n");
        printf("  Запропонована адреса: %s\n", inet_ntoa(ip_addr));
        printf("  Час оренди: %u секунд\n", info.lease_time);
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <cstdint>
#include <cstring>
#include <arpa/inet.h>

inline constexpr size_t DHCP_CHADDR_LEN     = 16;
inline constexpr size_t DHCP_SNAME_LEN      = 64;
inline constexpr size_t DHCP_FILE_LEN       = 128;
inline constexpr uint32_t DHCP_MAGIC_COOKIE = 0x63825363;

enum class DhcpOptionCode : uint8_t {
    Pad              = 0,
    SubnetMask       = 1,
    Router           = 3,
    DnsServer        = 6,
    HostName         = 12,
    DomainName       = 15,
    RequestedIp      = 50,
    LeaseTime        = 51,
    MessageType      = 53,
    ServerIdentifier = 54,
    ParamRequestList = 55,
    ClientIdentifier = 61,
    End              = 255
};

enum class DhcpMessageType : uint8_t {
    Discover = 1,
    Offer    = 2,
    Request  = 3,
    Decline  = 4,
    Ack      = 5,
    Nak      = 6,
    Release  = 7,
    Inform   = 8
};

#pragma pack(push, 1)
struct DhcpPacketHeader {
    uint8_t  op;
    uint8_t  htype;
    uint8_t  hlen;
    uint8_t  hops;
    uint32_t xid;
    uint16_t secs;
    uint16_t flags;
    uint32_t ciaddr;
    uint32_t yiaddr;
    uint32_t siaddr;
    uint32_t giaddr;
    std::array<uint8_t, DHCP_CHADDR_LEN> chaddr;
    std::array<char, DHCP_SNAME_LEN>     sname;
    std::array<char, DHCP_FILE_LEN>      file;
    uint32_t magic_cookie;
};
#pragma pack(pop)

struct DhcpOfferInfo {
    uint32_t xid{0};
    uint32_t offered_ip{0};
    uint32_t server_ip{0};
    uint32_t subnet_mask{0};
    uint32_t router_ip{0};
    uint32_t dns_ip{0};
    uint32_t lease_time{0};
    DhcpMessageType msg_type{DhcpMessageType::Discover};
};

class DhcpMessageBuilder {
public:
    static std::vector<uint8_t> create_discover(std::span<const uint8_t, 6> mac, uint32_t xid) {
        std::vector<uint8_t> buffer(sizeof(DhcpPacketHeader), 0);
        auto* hdr = reinterpret_cast<DhcpPacketHeader*>(buffer.data());

        hdr->op = 1; // BOOTREQUEST
        hdr->htype = 1; // Ethernet
        hdr->hlen = 6;
        hdr->hops = 0;
        hdr->xid = htonl(xid);
        hdr->secs = htons(0);
        hdr->flags = htons(0x8000); // Broadcast Flag
        std::memcpy(hdr->chaddr.data(), mac.data(), 6);
        hdr->magic_cookie = htonl(DHCP_MAGIC_COOKIE);

        add_option(buffer, DhcpOptionCode::MessageType, std::array<uint8_t, 1>{static_cast<uint8_t>(DhcpMessageType::Discover)});

        std::array<uint8_t, 7> client_id{1}; // Type 1: Ethernet
        std::memcpy(client_id.data() + 1, mac.data(), 6);
        add_option(buffer, DhcpOptionCode::ClientIdentifier, client_id);

        std::array<uint8_t, 4> req_params{
            static_cast<uint8_t>(DhcpOptionCode::SubnetMask),
            static_cast<uint8_t>(DhcpOptionCode::Router),
            static_cast<uint8_t>(DhcpOptionCode::DnsServer),
            static_cast<uint8_t>(DhcpOptionCode::DomainName)
        };
        add_option(buffer, DhcpOptionCode::ParamRequestList, req_params);

        buffer.push_back(static_cast<uint8_t>(DhcpOptionCode::End));
        return buffer;
    }

private:
    static void add_option(std::vector<uint8_t>& buf, DhcpOptionCode code, std::span<const uint8_t> data) {
        buf.push_back(static_cast<uint8_t>(code));
        buf.push_back(static_cast<uint8_t>(data.size()));
        buf.insert(buf.end(), data.begin(), data.end());
    }
};

class DhcpMessageParser {
public:
    static std::optional<DhcpOfferInfo> parse(std::span<const uint8_t> packet,
                                              std::span<const uint8_t, 6> expected_mac,
                                              uint32_t expected_xid) {
        if (packet.size() < sizeof(DhcpPacketHeader)) {
            return std::nullopt;
        }

        const auto* hdr = reinterpret_cast<const DhcpPacketHeader*>(packet.data());
        if (hdr->op != 2) return std::nullopt;
        if (ntohl(hdr->xid) != expected_xid) return std::nullopt;
        if (std::memcmp(hdr->chaddr.data(), expected_mac.data(), 6) != 0) return std::nullopt;
        if (ntohl(hdr->magic_cookie) != DHCP_MAGIC_COOKIE) return std::nullopt;

        DhcpOfferInfo info;
        info.xid = ntohl(hdr->xid);
        info.offered_ip = ntohl(hdr->yiaddr);

        size_t offset = sizeof(DhcpPacketHeader);
        while (offset < packet.size()) {
            uint8_t code = packet[offset++];
            if (code == static_cast<uint8_t>(DhcpOptionCode::Pad)) continue;
            if (code == static_cast<uint8_t>(DhcpOptionCode::End)) break;

            if (offset >= packet.size()) return std::nullopt;
            uint8_t len = packet[offset++];

            if (offset + len > packet.size()) return std::nullopt;

            auto val = packet.subspan(offset, len);
            auto opt = static_cast<DhcpOptionCode>(code);

            switch (opt) {
                case DhcpOptionCode::MessageType:
                    if (val.size() >= 1) info.msg_type = static_cast<DhcpMessageType>(val[0]);
                    break;
                case DhcpOptionCode::ServerIdentifier:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.server_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::SubnetMask:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.subnet_mask = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::Router:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.router_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::DnsServer:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.dns_ip = ntohl(raw);
                    }
                    break;
                case DhcpOptionCode::LeaseTime:
                    if (val.size() >= 4) {
                        uint32_t raw;
                        std::memcpy(&raw, val.data(), 4);
                        info.lease_time = ntohl(raw);
                    }
                    break;
                default:
                    break;
            }

            offset += len;
        }

        return info;
    }
};

int main() {
    std::array<uint8_t, 6> mac = {0x00, 0x1A, 0x2B, 0x3C, 0x4D, 0x5E};
    uint32_t xid = 0x39A4F2B1;

    auto discover_pkt = DhcpMessageBuilder::create_discover(mac, xid);
    std::cout << "Сформовано DHCPDISCOVER (C++20), розмір: " << discover_pkt.size() << " байтів.\n";

    return 0;
}
```
:::

---

### Розширений розбір складних опцій: Опція 121 та Опція 82

У виробничих середовищах парсер повинен підтримувати розпакування складних вкладених структур:

#### 1. Розбір безкласових статичних маршрутів (Опція 121 / RFC 3442)
Формат Опції 121 вимагає динамічного розрахунку кількості байтів, виділених під префікс мережі. Довжина маски задається одним байтом `M ∈ [0, 32]`, а кількість значущих байтів адреси обчислюється як:

```text
октетів = ⌈M / 8⌉ = ⌊(M + 7) / 8⌋
```

Після байтів префікса завжди слідують 4 байти IP-адреси шлюзу. Алгоритм розбору в циклі:
```text
Поки в полі значення Опції 121 залишаються байти:
  1. mask_bits = *ptr++
  2. if (mask_bits > 32) return error
  3. octets = (mask_bits + 7) / 8
  4. if (remaining_len < octets + 4) return error
  5. prefix_ip = 0
  6. memcpy(&prefix_ip, ptr, octets); ptr += octets
  7. gateway_ip = *(uint32_t*)ptr; ptr += 4
  8. Додати маршрут (prefix_ip / mask_bits -> gateway_ip) до таблиці маршрутизації
```

#### 2. Декодування субопцій Relay Agent Information (Опція 82)
Коли пакет проходить через ретранслятор, поле значення Опції 82 містить внутрішні суб-TLV контейнери:
- **Sub-Option 1 (`Circuit ID`):** Витягує фізичний номер порту комутатора та VLAN абонента.
- **Sub-Option 2 (`Remote ID`):** Витягує MAC-адресу комутатора або логічний ID абонентського договору.

Парсер інспектує внутрішній буфер Опції 82 за тими самими правилами безпеки TLV, запобігаючи переповненню внутрішніх масивів.

---

### Асинхронний цикл опитування сокета та керування подіями

Справжній клієнт DHCP працює в асинхронному режимі з використанням системного виклику `poll()` або `epoll()`, оскільки блокуючий виклик `recv()` може заморозити системний потік у разі втрати широкомовних дейтаграм у бездротовому чи комутованому середовищі.

Типова структура циклу опитування:

1. **Ініціалізація структури опитування:** Створюється дескриптор сокета, який реєструється у масиві `struct pollfd pfd = { .fd = sock_fd, .events = POLLIN }`.
2. **Розрахунок інтервалу очікування:** Для запобігання стану гонитви та одночасного навантаження серверів клієнт розраховує таймаут з експоненційним відступом та випадковим тремтінням (Jitter). Наприклад, для першої спроби таймаут встановлюється у діапазоні від 3000 до 5000 мілісекунд (`timeout_ms = 4000 + (rand() % 2000 - 1000)`).
3. **Очікування події через `poll(&pfd, 1, timeout_ms)`:**
   - Якщо `poll()` повертає `0`, час очікування вичерпано. Клієнт збільшує лічильник спроб, подвоює інтервал відступу і повторно транслює пакет `DHCPDISCOVER`.
   - Якщо `poll()` повертає `-1`, перевіряється код помилки `errno` (наприклад, переривання системним сигналом `EINTR`).
   - Якщо `poll()` повертає `> 0` і прапорець `pfd.revents & POLLIN` активний, викликається системний виклик `recvfrom()`, який зчитує сирі байти з черги сокета у виділений буфер.
4. **Фільтрація та перехід автомата:** Отриманий буфер негайно передається функції `parse_dhcp_response()`. Якщо `xid` або MAC-адреса не збігаються (запізнілий пакет від іншого пристрою в сегменті), дейтаграма мовчки відкидається, а цикл опитування продовжує очікування легітимної відповіді.

---

### Зондування конфліктів через сирий сокет ARP (RFC 5227)

Перед передачею конфігурації в ядро клієнт зобов'язаний виконати перевірку унікальності адреси за стандартом RFC 5227. Для цього програма відкриває низькорівневий сокет `socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ARP))` та формує зондувальні кадри:

1. **Формування заголовка Ethernet:** Тип кадру `0x0806` (ARP), MAC-адреса джерела — локальний MAC, адреса призначення — широкомовна `FF:FF:FF:FF:FF:FF`.
2. **Формування заголовка ARP:**
   - Тип апаратної адреси `htype = 1` (Ethernet).
   - Протокольний тип `ptype = 0x0800` (IPv4).
   - Довжини адрес: `hlen = 6`, `plen = 4`.
   - Код операції: `op = 1` (ARP Request).
   - **Sender IP Address (`spa`):** встановлюється в `0.0.0.0` (критично для зондування, щоб не забруднити ARP-кеші сусідів).
   - **Target IP Address (`tpa`):** запропонована адреса `yiaddr`.
3. **Моніторинг колізій:** Клієнт слухає сокет протягом 2 секунд. Якщо надходить хоча б одна відповідь із MAC-адресою іншого вузла, програма надсилає серверу `DHCPDECLINE` і перезапускає процес.

---

### Взаємодія з ядром через Linux Netlink (rtnetlink)

Після успішного отримання підтвердження `DHCPACK` та перевірки адреси через ARP перед програмою постає задача застосування конфігурації до операційної системи. Запуск зовнішніх утиліт (наприклад, через `system("ip addr add ...")`) є повільним, ресурсомістким і небезпечним підходом.

Професійні системні демони (такі як `dhcpcd` або `systemd-networkd`) взаємодіють безпосередньо з мережевою підсистемою ядра Linux через сокети **Netlink** (`AF_NETLINK`, протокол `NETLINK_ROUTE`):

1. **Призначення IP-адреси (`RTM_NEWADDR`):** Програма формує бінарне повідомлення з заголовком `struct nlmsghdr` та тілом `struct ifaddrmsg`, де вказує індекс мережевого інтерфейсу (`ifa_index`), довжину маски підмережі (`ifa_prefixlen`) та атрибути `IFA_LOCAL` / `IFA_ADDRESS` із виділеною IP-адресою.
2. **Встановлення маршруту за замовчуванням (`RTM_NEWROUTE`):** Формується повідомлення з тілом `struct rtmsg`, де сімейство адрес встановлюється в `AF_INET`, тип таблиці — `RT_TABLE_MAIN`, протокол — `RTPROT_BOOT`, а в атрибутах передаються `RTA_GATEWAY` (IP-адреса шлюзу з Опції 3 або 121) та `RTA_OIF` (індекс вихідного інтерфейсу).
3. **Оновлення конфігурації DNS:** Отримані адреси серверів імен з Опції 6 записуються у файл `/etc/resolv.conf` або передаються через D-Bus до системного резолвера `systemd-resolved`.

---

### Методологія модульного тестування (Unit Testing) та захисні фікстури

Для гарантування відмовостійкості парсера в критичних виробничих умовах модуль піддається комплексному автоматизованому тестуванню набором синтетичних пакетних фікстур (Test Fixtures):

1. **Тест обрізаного заголовка:** Буфер довжиною менше 240 байтів (наприклад, 120 або 239 байтів). Функція `parse_dhcp_response()` зобов'язана миттєво повернути `false` або `std::nullopt`, не здійснюючи спроб розіменування вказівників на опції.
2. **Тест пошкодженого Magic Cookie:** Пакет правильного розміру, де байти `[236..239]` містять довільні значення замість `0x63825363`. Парсер відкидає дейтаграму як несумісну з DHCP.
3. **Тест зловмисної довжини TLV (Buffer Overflow Attack):** Опція вказує довжину `opt_len = 200`, коли до кінця буфера залишається лише 10 байтів. Парсер успішно детектує вихід за межі та коректно завершує роботу.
4. **Тест відсутності Опції 255 (Missing End Option):** Пакет із валідними опціями, але без фінального байта `0xFF`. Парсер повинен безпечно зупинитися по досягненні кінця буфера, не зациклюючись.

---

### Покроковий розбір та крайові випадки

Розглянемо ключові інженерні нюанси, які необхідно враховувати під час практичної інтеграції модуля у виробничі системи:

1. **Асинхронний таймаут очікування відповідей:** Оскільки UDP не гарантує доставку дейтаграм, клієнт повинен реалізувати алгоритм експоненційного відступу (Exponential Backoff, RFC 2131). Початковий таймаут становить 4 секунди з рандомізованим тремтінням (jitter ±1 с: інтервал від 3 до 5 секунд). Якщо відповіді немає, таймаут подвоюється (8 с, 16 с, 32 с, до максимуму 64 с). Рандомізація захищає комутатори від шторму одночасних повторних запитів при раптовому відновленні живлення в офісі.
2. **Фрагментація UDP та розмір MTU:** Згідно зі стандартом RFC 2131, клієнт зобов'язаний бути готовим приймати повідомлення DHCP довжиною щонайменше 576 байтів (мінімальний розмір дейтаграми IPv4). Якщо сервер повертає велику кількість опцій (довгі списки статичних маршрутів Опції 121, доменні суфікси, PXE-меню), розмір пакета може досягати 1400 байтів. Буфер прийому завжди повинен виділятися з запасом під повний кадр Ethernet MTU (1500 байтів).
3. **Опція Overload (Опція 52):** У складних мережах область опцій може переповнитися. Сервер має право використати невикористані поля заголовка `sname` (64 байти) та `file` (128 байтів) для розміщення додаткових опцій TLV. Наявність Опції 52 зі значенням `1` вказує, що поле `file` містить опції; значення `2` сигналізує про опції в полі `sname`; значення `3` — в обох полях. Повнофункціональний парсер повинен підтримувати послідовний перехід між цими областями пам'яті.
4. **Контроль цілісності транзакції (`xid`):** Якщо клієнт перезапустив процес опитування або в мережі одночасно стартують кілька віртуальних машин з одного хоста, на сокет можуть приходити запізнілі пакети `DHCPOFFER` від попередніх спроб. Сувора фільтрація за `pkt->xid != expected_xid` є обов'язковим бар'єром від стану гонитви (race condition).
5. **Фаззинг-тестування та стійкість до сміттєвих даних:** Надійні мережеві демони регулярно тестуються інструментами автоматичного фаззингу (AFL++, libFuzzer). Парсер повинен гарантовано повертати `false` або `std::nullopt` на будь-яких псевдовипадкових комбінаціях байтів, нульових довжинах опцій, циклічних вкладеннях та обрізаних пакетах, не допускаючи зависання процесора або аварійного завершення програми (Segmentation Fault).
6. **Робота в середовищах з кількома шлюзами (Multi-Homed Hosts):** Якщо пристрій підключено до двох фізичних мереж одночасно, на кожному інтерфейсі створюється окремий екземпляр клієнта DHCP з незалежним пулом сокетів та власним ідентифікатором транзакції `xid`. Отримані маршрути за замовчуванням повинні встановлюватися в ядрі з різними метриками пріоритету (metric), запобігаючи непередбачуваній поведінці таблиці маршрутизації.
7. **Управління таймерами через `timerfd`:** Для відстеження дедлайнів поновлення оренди T1 (50%) та T2 (87.5%) у Linux найефективніше використовувати дескриптор таймера `timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK)`. Монотонний системний годинник гарантує, що ручне переведення системного часу користувачем або корекція через NTP не призведуть до раптового передчасного скидання активної оренди.
8. **Діагностичне дамп-логування (Hex Dump):** Під час налагодження протоколу сирі байти буфера виводяться у шістнадцятковому форматі. Це дозволяє миттєво локалізувати помилки зміщення змісту опцій TLV та перевірити правильність вирівнювання байтів Magic Cookie безпосередньо у виводі термінала.
9. **Захист від витоку пам'яті та багатопоточність:** Парсер спроєктовано як чисту функцію без внутрішнього стану (stateless and reentrant). Він не виконує динамічного виділення пам'яті на купі (`malloc`/`new`) під час розбору, що унеможливлює витоки пам'яті навіть при безперервній обробці мільйонів пакетів за добу в режимі 24/7.
10. **Розрахунок контрольної суми UDP:** За стандартом RFC 768 для протоколу IPv4 контрольна сума дейтаграми UDP є необов'язковою і може встановлюватися в `0x0000` при відправці через низькорівневі сокети. Проте у разі розрахунку псевдозаголовка IPv4 значення суми, що дорівнює у зворотному коді `0x0000`, обов'язково кодується як `0xFFFF`, оскільки нульове значення зарезервовано для позначення відсутності контрольної суми.

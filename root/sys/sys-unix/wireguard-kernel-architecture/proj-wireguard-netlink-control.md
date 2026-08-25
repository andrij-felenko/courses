# ⚙️ Керування WireGuard через Generic Netlink у C та C++

Утиліти керування мережею (`wg`, `iproute2`, `systemd-networkd`, `NetworkManager`) налаштовують віртуальні інтерфейси WireGuard у ядрі Linux безпосередньо через системний інтерфейс Generic Netlink (`NETLINK_GENERIC`). Нижче наведено детальний розбір та повний робочий приклад коду на мовах C та C++, який показує, як відкрити Netlink-сокет, динамічно запитати ідентифікатор сімейства WireGuard у ядрі, сформувати бінарне повідомлення `WG_CMD_SET_DEVICE` та атомарно додати нового піра з дозволеними підмережами (`allowed-ips`).

---

## 1. Постановка завдання та архітектурна ідея

Для програмного керування пристроєм WireGuard без залучення зовнішніх бінарних утиліт необхідно виконати наступну послідовність кроків на рівні системного програмування:

1. **Створення сокету Netlink:** Відкрити сирий сокет протоколу `NETLINK_GENERIC` за допомогою системного виклику `socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC)` та прив'язати його до локального порту викликом `bind()`.
2. **Динамічний пошук ID сімейства (`GENL_ID_CTRL`):** Запитати у системного контролера Generic Netlink підсистеми ядра числове значення ідентифікатора сімейства за ім'ям `"wireguard"`.
3. **Формування атрибутів `WG_CMD_SET_DEVICE`:** Побудувати буфер з заголовками `struct nlmsghdr` та `struct genlmsghdr`, додати атрибут ім'я пристрою `WGDEVICE_A_IFNAME` ("wg0"), відкрити вкладені атрибути пірів `WGDEVICE_A_PEERS` та записати:
   - 32-байтний публічний ключ піра (`WGPEER_A_PUBLIC_KEY`).
   - Зовнішню IP-адресу та UDP-порт кінцевої точки (`WGPEER_A_ENDPOINT`).
   - Список дозволених внутрішніх підмереж `WGPEER_A_ALLOWEDIPS` (наприклад, `10.0.0.2/32`).
4. **Відправка та перевірка ACK:** Надіслати сформований буфер у ядро викликом `sendto()` та прочитати статус виконання у відповідному повідомленні `NLMSG_ERROR`.

---

## 2. Детальний аналіз реалізації на C та C++

При виконанні мережевого керування через Netlink системний програміст стикається з вибором між двома підходами: низькорівнева обробка бінарних буферів у стилі C або безпечна об'єктно-орієнтована реалізація у стилі C++.

### 2.1. Особливості низькорівневої реалізації на C

Реалізація мовою C спирається безпосередньо на макроси ядра Linux, визначені у заголовкових файлах `<linux/netlink.h>` та `<linux/genetlink.h>`:

- Макрос `NLMSG_LENGTH(len)` обчислює повну довжину повідомлення Netlink із урахуванням заголовка `struct nlmsghdr`.
- Макрос `NLMSG_ALIGN(len)` та `RTA_ALIGN(len)` вирівнює довжину заголовків та атрибутів за межею 4 байт (32 біти), заповнюючи проміжні байти нулями.
- Для створення вкладених атрибутів (`NLA_F_NESTED`) застосовується двохкрокова схема: спочатку у буфер пишеться заголовок `struct rtattr` з нульовою довжиною через функцію `nest_start()`, після чого додаються дочірні атрибути, і наприкінці функція `nest_end()` підраховує фактичну сумарну довжину вкладеного блоку та коригує поле `rta_len`.

Для очищення ресурсів при виникненні помилок у C-коді застосовується явне закриття файлового дескриптора сокету `close(fd)` перед поверненням з функції.

### 2.2. Ідіоматичний підхід C++ (RAII та Type Safety)

Укладка того самого коду мовою C++ демонструє переваги сучасної стандартизованої мови без залучення застарілих концепцій C:

- **Управління ресурсами (RAII):** Клас `NetlinkSocket` інкапсулює відкриття сокета в конструкорі та автоматично викликає `::close(fd_)` у деструкторі. Це унеможливлює витік файлових дескрипторів навіть при виникненні винятків (`std::system_error`).
- **Динамічний буфер замість сирого масиву:** Замість статичного масиву `char buffer[4096]` використовується безпечний контейнер `std::vector<uint8_t>`, який автоматично виділяє необхідний обсяг пам'яті під час додавання нових атрибутів Netlink.
- **Типізація та String View:** Ім'я тунельного інтерфейсу передається через `std::string_view`, що усуває зайве копіювання рядків у пам'яті. Команди та атрибути загорнуті у строгі `enum class`, запобігаючи неявним приведенням типів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <net/if.h>
#include <arpa/inet.h>

#define WG_GENL_NAME "wireguard"
#define WG_GENL_VERSION 1

enum wg_cmd {
    WG_CMD_GET_DEVICE,
    WG_CMD_SET_DEVICE,
};

enum wgdevice_attribute {
    WGDEVICE_A_UNSPEC,
    WGDEVICE_A_IFINDEX,
    WGDEVICE_A_IFNAME,
    WGDEVICE_A_PRIVATE_KEY,
    WGDEVICE_A_PUBLIC_KEY,
    WGDEVICE_A_LISTEN_PORT,
    WGDEVICE_A_FWMARK,
    WGDEVICE_A_FLAGS,
    WGDEVICE_A_PEERS,
    __WGDEVICE_A_MAX
};

enum wgpeer_attribute {
    WGPEER_A_UNSPEC,
    WGPEER_A_PUBLIC_KEY,
    WGPEER_A_PRESHARED_KEY,
    WGPEER_A_ENDPOINT,
    WGPEER_A_PERSISTENT_KEEPALIVE_INTERVAL,
    WGPEER_A_FLAGS,
    WGPEER_A_ALLOWEDIPS,
    __WGPEER_A_MAX
};

enum wgallowedip_attribute {
    WGALLOWEDIP_A_UNSPEC,
    WGALLOWEDIP_A_FAMILY,
    WGALLOWEDIP_A_IPADDR,
    WGALLOWEDIP_A_CIDR_MASK,
    __WGALLOWEDIP_A_MAX
};

/* Допоміжна функція додавання звичайного атрибута Netlink */
static void add_attr(struct nlmsghdr *nlh, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: буфер Netlink переповнено\n");
        exit(EXIT_FAILURE);
    }
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (data && alen > 0) {
        memcpy(RTA_DATA(rta), data, alen);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
}

/* Відкриття вкладеного контейнера атрибутів (NLA_F_NESTED) */
static struct rtattr *nest_start(struct nlmsghdr *nlh, int maxlen, int type) {
    struct rtattr *nest = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, maxlen, type, NULL, 0);
    return nest;
}

/* Завершення та фіксація довжини вкладеного атрибута */
static void nest_end(struct nlmsghdr *nlh, struct rtattr *nest) {
    nest->rta_len = (char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len) - (char *)nest;
}

int main(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_nl local = { .nl_family = AF_NETLINK };
    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("bind");
        close(fd);
        return 1;
    }

    char buffer[4096];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct genlmsghdr));
    nlh->nlmsg_type = 0x10; /* Символічний ID сімейства wireguard у ядрі */
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    nlh->nlmsg_seq = 1;

    struct genlmsghdr *genl = (struct genlmsghdr *)NLMSG_DATA(nlh);
    genl->cmd = WG_CMD_SET_DEVICE;
    genl->version = WG_GENL_VERSION;

    /* Вказуємо ім'я пристрою wg0 */
    const char *ifname = "wg0";
    add_attr(nlh, sizeof(buffer), WGDEVICE_A_IFNAME, ifname, strlen(ifname) + 1);

    /* Вкладений блок пірів WGDEVICE_A_PEERS */
    struct rtattr *peers_nest = nest_start(nlh, sizeof(buffer), WGDEVICE_A_PEERS | NLA_F_NESTED);
    struct rtattr *peer_nest = nest_start(nlh, sizeof(buffer), 0 | NLA_F_NESTED);

    /* Фіктивний публічний ключ піра (32 байти) */
    unsigned char pubkey[32] = {
        0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
        0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
        0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
        0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
    };
    add_attr(nlh, sizeof(buffer), WGPEER_A_PUBLIC_KEY, pubkey, 32);

    /* Зовнішня кінцева точка: 192.168.1.100:51820 */
    struct sockaddr_in ep = {
        .sin_family = AF_INET,
        .sin_port = htons(51820)
    };
    inet_pton(AF_INET, "192.168.1.100", &ep.sin_addr);
    add_attr(nlh, sizeof(buffer), WGPEER_A_ENDPOINT, &ep, sizeof(ep));

    /* Додаємо дозволені IP-адреси AllowedIPs (10.0.0.2/32) */
    struct rtattr *aips_nest = nest_start(nlh, sizeof(buffer), WGPEER_A_ALLOWEDIPS | NLA_F_NESTED);
    struct rtattr *aip_nest = nest_start(nlh, sizeof(buffer), 0 | NLA_F_NESTED);

    uint16_t family = AF_INET;
    struct in_addr ip_addr;
    inet_pton(AF_INET, "10.0.0.2", &ip_addr);
    uint8_t cidr = 32;

    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_FAMILY, &family, sizeof(family));
    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_IPADDR, &ip_addr, sizeof(ip_addr));
    add_attr(nlh, sizeof(buffer), WGALLOWEDIP_A_CIDR_MASK, &cidr, sizeof(cidr));

    nest_end(nlh, aip_nest);
    nest_end(nlh, aips_nest);

    nest_end(nlh, peer_nest);
    nest_end(nlh, peers_nest);

    struct sockaddr_nl nl_kernel = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nl_kernel, sizeof(nl_kernel)) < 0) {
        perror("sendto");
        close(fd);
        return 1;
    }

    printf("Повідомлення WG_CMD_SET_DEVICE надіслано до ядра Linux\n");
    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <array>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <arpa/inet.h>

namespace wireguard {

constexpr std::string_view WG_GENL_NAME = "wireguard";
constexpr uint8_t WG_GENL_VERSION = 1;

enum class WgCmd : uint8_t {
    GetDevice = 0,
    SetDevice = 1
};

enum WgDeviceAttr {
    WgDeviceAttrIfName = 2,
    WgDeviceAttrPeers = 8
};

enum WgPeerAttr {
    WgPeerAttrPublicKey = 1,
    WgPeerAttrEndpoint = 3,
    WgPeerAttrAllowedIps = 6
};

enum WgAllowedIpAttr {
    WgAllowedIpAttrFamily = 1,
    WgAllowedIpAttrIpAddr = 2,
    WgAllowedIpAttrCidrMask = 3
};

// RAII-обгортка для управління ресурсом Netlink сокету
class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити NETLINK_GENERIC сокет");
        }
        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        if (::bind(fd_, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати Netlink сокет");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Динамічний буфер для формування повідомлення Netlink
class NetlinkBuffer {
    std::vector<uint8_t> buffer_;

public:
    explicit NetlinkBuffer(size_t initial_capacity = 4096) {
        buffer_.reserve(initial_capacity);
        buffer_.resize(NLMSG_LENGTH(sizeof(genlmsghdr)), 0);
        
        auto* nlh = reinterpret_cast<nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(genlmsghdr));
        nlh->nlmsg_type = 0x10; // Символічний WireGuard Generic Netlink ID
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
        nlh->nlmsg_seq = 1;

        auto* genl = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        genl->cmd = static_cast<uint8_t>(WgCmd::SetDevice);
        genl->version = WG_GENL_VERSION;
    }

    void add_attribute(uint16_t type, const void* data, uint16_t len) {
        auto* nlh = reinterpret_cast<nlmsghdr*>(buffer_.data());
        uint16_t rta_len = RTA_LENGTH(len);
        size_t old_size = buffer_.size();
        size_t aligned_len = RTA_ALIGN(rta_len);

        buffer_.resize(old_size + aligned_len, 0);
        auto* rta = reinterpret_cast<rtattr*>(buffer_.data() + old_size);
        rta->rta_type = type;
        rta->rta_len = rta_len;
        if (data && len > 0) {
            std::memcpy(RTA_DATA(rta), data, len);
        }

        nlh->nlmsg_len = static_cast<uint32_t>(buffer_.size());
    }

    [[nodiscard]] size_t start_nested(uint16_t type) {
        size_t offset = buffer_.size();
        add_attribute(type | NLA_F_NESTED, nullptr, 0);
        return offset;
    }

    void end_nested(size_t offset) {
        auto* rta = reinterpret_cast<rtattr*>(buffer_.data() + offset);
        rta->rta_len = static_cast<uint16_t>(buffer_.size() - offset);
    }

    [[nodiscard]] const uint8_t* data() const noexcept { return buffer_.data(); }
    [[nodiscard]] size_t size() const noexcept { return buffer_.size(); }
};

} // namespace wireguard

int main() {
    try {
        wireguard::NetlinkSocket sock;
        wireguard::NetlinkBuffer msg;

        // Вказуємо ім'я тунельного пристрою wg0
        std::string_view ifname = "wg0";
        msg.add_attribute(wireguard::WgDeviceAttrIfName, ifname.data(), static_cast<uint16_t>(ifname.size() + 1));

        // Створюємо вкладений блок пірів
        size_t peers_nest = msg.start_nested(wireguard::WgDeviceAttrPeers);
        size_t peer_nest = msg.start_nested(0);

        // Передаємо 32-байтний публічний ключ піра
        std::array<uint8_t, 32> pubkey = {
            0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08,
            0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f, 0x10,
            0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18,
            0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f, 0x20
        };
        msg.add_attribute(wireguard::WgPeerAttrPublicKey, pubkey.data(), pubkey.size());

        // Зовнішній endpoint 192.168.1.100:51820
        sockaddr_in ep{};
        ep.sin_family = AF_INET;
        ep.sin_port = htons(51820);
        inet_pton(AF_INET, "192.168.1.100", &ep.sin_addr);
        msg.add_attribute(wireguard::WgPeerAttrEndpoint, &ep, sizeof(ep));

        // Allowed IPs (10.0.0.2/32)
        size_t aips_nest = msg.start_nested(wireguard::WgPeerAttrAllowedIps);
        size_t aip_nest = msg.start_nested(0);

        uint16_t family = AF_INET;
        in_addr ip_addr{};
        inet_pton(AF_INET, "10.0.0.2", &ip_addr);
        uint8_t cidr = 32;

        msg.add_attribute(wireguard::WgAllowedIpAttrFamily, &family, sizeof(family));
        msg.add_attribute(wireguard::WgAllowedIpAttrIpAddr, &ip_addr, sizeof(ip_addr));
        msg.add_attribute(wireguard::WgAllowedIpAttrCidrMask, &cidr, sizeof(cidr));

        msg.end_nested(aip_nest);
        msg.end_nested(aips_nest);

        msg.end_nested(peer_nest);
        msg.end_nested(peers_nest);

        sockaddr_nl nl_kernel{};
        nl_kernel.nl_family = AF_NETLINK;

        if (::sendto(sock.get(), msg.data(), msg.size(), 0, reinterpret_cast<sockaddr*>(&nl_kernel), sizeof(nl_kernel)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка sendto до ядра");
        }

        std::cout << "Приклад C++ успішно сформував та надіслав конфігурацію WireGuard через Netlink\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка виконання: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

## 3. Перевірка статусу виконання та зчитування ACK-повідомлень

Оскільки при побудові заголовка Netlink було передано прапорець `NLM_F_ACK`, ядро обов'язково надсилає у відповідь повідомлення підтвердження виконання або код помилки (`NLMSG_ERROR`).

Для перевірки успішності виконання застосунок повинен виконати системний виклик `recv()` і прочитати заголовок `struct nlmsghdr`:

1. Якщо тип повідомлення `nlh->nlmsg_type == NLMSG_ERROR`, дані пакета приводяться до структури `struct nlmsgerr`.
2. Поле `err->error` містить 0 у випадку успішної конфігурації пристрою, або від'ємне значення `errno` (наприклад, `-EINVAL` або `-ENODEV`) у випадку виникнення помилки валідації атрибутів.
3. Якщо застосунок здійснює зчитування конфігурації за допомогою прапорця `NLM_F_DUMP`, ядро повертає послідовність пакетів із типом `WG_CMD_GET_DEVICE`, яка завершується пакетом із типом `NLMSG_DONE`.

---

## 4. Критичні пастки системного програмування через Netlink

Під час розробки власних модулів налаштування WireGuard на мовах C та C++ слід зважати на наступні підводні камені системного API ядра Linux:

1. **Динамічний розв'язок ідентифікатора сімейства (`GENL_ID_CTRL`):**
   У реальних проєктах числове значення `nlmsg_type` для WireGuard не є статичною константою `0x10`. Воно призначається ядром динамічно при завантаженні модуля. Перед надсиланням команд застосунок повинен надіслати запит до системного контролера Generic Netlink (`GENL_ID_CTRL`, команда `CTRL_CMD_GETFAMILY`) із вказанням атрибута `CTRL_ATTR_FAMILY_NAME` = `"wireguard"`, отримати динамічний ID сімейства та використовувати його у полі `nlmsg_type`.

2. **Правила вирівнювання атрибутів Netlink (`RTA_ALIGN` / `NLMSG_ALIGN`):**
   Кожен атрибут `struct rtattr` у буфері повинен бути вирівняний за межею 4 байт. Якщо довжина атрибута (наприклад, ім'я пристрою `"wg0"`) не є кратною 4, наступний атрибут повинен починатися з вирівняного зсуву, заповненого нульовими байтами. Нехтування вирівнюванням призводить до відхилення пакета ядром із помилкою `EINVAL`.

3. **Вкладені атрибути та прапорець `NLA_F_NESTED`:**
   Контейнери атрибутів, такі як `WGDEVICE_A_PEERS` та `WGPEER_A_ALLOWEDIPS`, вимагають встановлення побітового прапорця `NLA_F_NESTED` у полі `rta_type`. Без цього прапорця ядро інтерпретує внутрішні атрибути як бінарний масив даних.

4. **Атомарне оновлення підмереж (`WGPEER_F_REPLACE_ALLOWEDIPS`):**
   Якщо при оновленні піра не вказати прапорець `WGPEER_F_REPLACE_ALLOWEDIPS`, ядро не видалить наявні підмережі даного піра з префіксного дерева `allowedips`, а об'єднає нові адреси з існуючими. Для повного заміщення конфігурації використання прапорця є обов'язковим.

5. **Паралельне зчитування статистики (`NLM_F_DUMP`):**
   При виконанні команди `WG_CMD_GET_DEVICE` для великих мереж із тисячами пірів відповідь ядра не поміщається в один мережевий пакет. Застосунок повинен надсилати запит із прапорцем `NLM_F_DUMP` та обробляти послідовність пакетів у циклі до отримання маркерного пакета `NLMSG_DONE`.

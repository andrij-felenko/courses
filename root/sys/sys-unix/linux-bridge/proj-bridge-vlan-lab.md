# ⚙️ Практикум: конфігурація VLAN Filtering та керування FDB у Linux Bridge

Практичний посібник зі створення ізольованої багатоклієнтської мережевої інфраструктури на базі програмного комутатора Linux Bridge із механізмом фільтрації VLAN (IEEE 802.1Q) та програмним керуванням таблицею комутації FDB через Netlink API на мовах C та C++.

## 1. Архітектура лабораторного стенду

Мета стенду — об'єднати чотири ізольовані мережеві простори імен (`netns`) у межах єдиного екземпляра Linux Bridge `br-core`. Така схема моделює типову архітектуру вузла віртуалізації або контейнерного хоста з підтримкою багатокористувацької ізоляції (Multi-Tenancy).

У стенді виділяються такі функціональні зони:
- `ns-blue1` та `ns-blue2` — сегмент першого клієнта Blue (VLAN 10, IP-підмережа `192.168.10.0/24`);
- `ns-red1` — сегмент другого клієнта Red (VLAN 20, IP-підмережа `192.168.20.0/24`);
- `ns-router` — шлюз або транк-порт, що приймає трафік обох віртуальних мереж у тегованому вигляді (Trunk Port) для міжмережевої маршрутизації.

```
                      +---------------------------------------+
                      |          Linux Bridge br-core         |
                      |          (vlan_filtering = 1)         |
                      +---+---------------+---------------+---+
                          | (PVID 10)     | (PVID 10)     | (PVID 20)
                          | Untagged      | Untagged      | Untagged
                          v               v               v
                     [veth-blue1-br] [veth-blue2-br] [veth-red1-br]
                          |               |               |
                     (veth pair)     (veth pair)     (veth pair)
                          |               |               |
                          v               v               v
                     [ns-blue1]      [ns-blue2]      [ns-red1]
                   192.168.10.1    192.168.10.2    192.168.20.1
```

Кожен простір імен ізольований від хостової операційної системи за допомогою віртуальних Ethernet-пар (`veth`). Один кінець пари розміщується всередині відповідного `netns` і виконує роль локального мережевого адаптера `eth0`. Другий кінець залишається в кореневому просторі хоста і підключається як підпорядкований порт (Slave Port) до моста `br-core`.

---

## 2. Покрокове розгортання стенду через утиліти `ip` та `bridge`

Розгортання стенду складається з п'яти послідовних інженерних кроків.

### Крок 1. Створення комутатора з підтримкою VLAN Filtering

Під час створення моста параметр `vlan_filtering 1` активує внутрішній механізм перевірки та модифікації тегів IEEE 802.1Q. Якщо створити звичайний міст і не увімкнути цей прапорець, комутатор пропускатиме всі теговані кадри прозоро, не виконуючи ізоляції портів.

```bash
# 1. Створюємо інтерфейс моста з увімкненою фільтрацією VLAN
sudo ip link add name br-core type bridge vlan_filtering 1

# 2. Піднімаємо інтерфейс моста
sudo ip link set dev br-core up
```

### Крок 2. Створення мережевих просторів імен та veth-пар

Кожна veth-пара працює як двосторонній віртуальний кабель: пакет, відправлений в один інтерфейс, негайно з'являється на прийомі протилежного інтерфейсу через прямий виклик `netif_rx()` у ядрі.

```bash
# Створюємо ізольовані простори імен для орендарів
sudo ip netns add ns-blue1
sudo ip netns add ns-blue2
sudo ip netns add ns-red1

# Створюємо пари віртуальних кабелів veth
sudo ip link add veth-b1 type veth peer name veth-b1-br
sudo ip link add veth-b2 type veth peer name veth-b2-br
sudo ip link add veth-r1 type veth peer name veth-r1-br

# Переносимо клієнтські кінці veth у відповідні простори імен
sudo ip link set veth-b1 netns ns-blue1
sudo ip link set veth-b2 netns ns-blue2
sudo ip link set veth-r1 netns ns-red1

# Приєднуємо хостові кінці veth до моста br-core
sudo ip link set veth-b1-br master br-core
sudo ip link set veth-b2-br master br-core
sudo ip link set veth-r1-br master br-core

# Переводимо хостові інтерфейси в активний стан (UP)
sudo ip link set dev veth-b1-br up
sudo ip link set dev veth-b2-br up
sudo ip link set dev veth-r1-br up
```

### Крок 3. Налаштування IP-адрес всередині просторів імен

Всередині кожного `netns` віртуальний інтерфейс перейменовується на `eth0` для стандартизації конфігурації. Також обов'язково активується петльовий інтерфейс `lo`.

```bash
# Налаштовуємо ns-blue1 (VLAN 10, вузол 1)
sudo ip -n ns-blue1 link set lo up
sudo ip -n ns-blue1 link set dev veth-b1 name eth0
sudo ip -n ns-blue1 addr add 192.168.10.1/24 dev eth0
sudo ip -n ns-blue1 link set dev eth0 up

# Налаштовуємо ns-blue2 (VLAN 10, вузол 2)
sudo ip -n ns-blue2 link set lo up
sudo ip -n ns-blue2 link set dev veth-b2 name eth0
sudo ip -n ns-blue2 addr add 192.168.10.2/24 dev eth0
sudo ip -n ns-blue2 link set dev eth0 up

# Налаштовуємо ns-red1 (VLAN 20, вузол 1)
sudo ip -n ns-red1 link set lo up
sudo ip -n ns-red1 link set dev veth-r1 name eth0
sudo ip -n ns-red1 addr add 192.168.20.1/24 dev eth0
sudo ip -n ns-red1 link set dev eth0 up
```

### Крок 4. Налаштування членства у VLAN (Access Ports)

За замовчуванням при створенні нового порту ядро призначає йому VLAN 1 як `pvid` та `untagged`. Щоб забезпечити строгу ізоляцію клієнтів, необхідно спочатку видалити дефолтний VLAN 1, а потім призначити цільовий VLAN для кожного порту.

- Прапорець **`pvid`** наказує мосту маркувати нетеговані вхідні пакети цим номером VLAN;
- Прапорець **`untagged`** наказує мосту видаляти заголовок 802.1Q під час виходу пакетів до клієнта.

```bash
# Налаштовуємо порт veth-b1-br для клієнта Blue (VLAN 10 Access)
sudo bridge vlan del dev veth-b1-br vid 1
sudo bridge vlan add dev veth-b1-br vid 10 pvid untagged

# Налаштовуємо порт veth-b2-br для клієнта Blue (VLAN 10 Access)
sudo bridge vlan del dev veth-b2-br vid 1
sudo bridge vlan add dev veth-b2-br vid 10 pvid untagged

# Налаштовуємо порт veth-r1-br для клієнта Red (VLAN 20 Access)
sudo bridge vlan del dev veth-r1-br vid 1
sudo bridge vlan add dev veth-r1-br vid 20 pvid untagged
```

### Крок 5. Перевірка конфігурації та тестування ізоляції

Перевіримо поточну таблицю конфігурації VLAN на портах:

```bash
bridge vlan show
```

Тестуємо зв'язок між вузлами в межах одного VLAN 10 (пакети проходять успішно):
```bash
sudo ip netns exec ns-blue1 ping -c 2 192.168.10.2
```

Тестуємо спробу взаємодії між вузлами різних клієнтів (VLAN 10 намагається пінгувати VLAN 20). Міст відкидає пакети на канальному рівні ще до спроби маршрутизації, оскільки порти не мають спільного VLAN ID:
```bash
sudo ip netns exec ns-blue1 ping -c 2 192.168.20.1 -W 1
```

---

## 3. Програмне керування FDB через Netlink API

У високонавантажених сервісах або SDN-контролерах виклик зовнішніх утиліт на зразок `bridge fdb` створює неприпустимі накладні витрати через форк процесів (`fork/exec`). Пряме керування через сокети `AF_NETLINK` (сімейство `NETLINK_ROUTE`) дозволяє динамічно вносити статичні записи в FDB за мікросекунди.

Нижче наведено робочі приклади відправки бінарного повідомлення `RTM_NEWNEIGH` із сімейством `AF_BRIDGE` та прапорцями `NUD_PERMANENT` і `NTF_MASTER`.

У прикладах продемонстровано коректне вирівнювання бінарних структур за допомогою макросів `NLMSG_ALIGN` та `RTA_ALIGN`, що є обов'язковим стандартом ABI ядра Linux для запобігання пошкодженню пам'яті на 64-бітних архітектурах. Прапорець `NLM_F_ACK` змушує ядро надіслати повідомлення-відповідь `NLMSG_ERROR` із результатом операції (0 у разі успіху або від'ємний код помилки системи).

:::tabs
```c
/* bridge_fdb_inject.c - Додавання статичного запису FDB моста через RTNETLINK */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/rtnetlink.h>
#include <linux/if_bridge.h>
#include <linux/neighbour.h>
#include <net/if.h>
#include <errno.h>

#define NL_BUF_SIZE 4096

int add_fdb_entry(int ifindex, const unsigned char mac[6], unsigned short vid) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK");
        return -1;
    }

    char buf[NL_BUF_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ndmsg));
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_REPLACE | NLM_F_ACK;
    nlh->nlmsg_type = RTM_NEWNEIGH;
    nlh->nlmsg_seq = 1;

    struct ndmsg *ndm = (struct ndmsg *)NLMSG_DATA(nlh);
    ndm->ndm_family = AF_BRIDGE;
    ndm->ndm_ifindex = ifindex;
    ndm->ndm_state = NUD_PERMANENT; /* Статичний запис (не старіє) */
    ndm->ndm_flags = NTF_MASTER;    /* Додати в FDB master-пристрою */

    /* Додаємо атрибут NDA_LLADDR (MAC-адреса) */
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = NDA_LLADDR;
    rta->rta_len = RTA_LENGTH(6);
    memcpy(RTA_DATA(rta), mac, 6);
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);

    /* Додаємо атрибут NDA_VLAN (якщо вказано VID) */
    if (vid > 0) {
        rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = NDA_VLAN;
        rta->rta_len = RTA_LENGTH(sizeof(unsigned short));
        memcpy(RTA_DATA(rta), &vid, sizeof(unsigned short));
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta->rta_len);
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto rtnetlink");
        close(fd);
        return -1;
    }

    /* Отримуємо підтвердження NLMSG_ERROR */
    char rcv_buf[NL_BUF_SIZE];
    ssize_t len = recv(fd, rcv_buf, sizeof(rcv_buf), 0);
    close(fd);

    if (len < 0) {
        perror("recv netlink");
        return -1;
    }

    struct nlmsghdr *resp = (struct nlmsghdr *)rcv_buf;
    if (resp->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(resp);
        if (err->error != 0) {
            fprintf(stderr, "Помилка Netlink FDB: %s (код %d)\n", strerror(-err->error), err->error);
            return err->error;
        }
    }

    printf("FDB запис успішно додано для ifindex=%d, vid=%d\n", ifindex, vid);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <ifname> <MAC-адреса: XX:XX:XX:XX:XX:XX> [VLAN_ID]\n", argv[0]);
        return 1;
    }

    int ifidx = if_nametoindex(argv[1]);
    if (ifidx == 0) {
        perror("if_nametoindex");
        return 1;
    }

    unsigned char mac[6];
    if (sscanf(argv[2], "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
               &mac[0], &mac[1], &mac[2], &mac[3], &mac[4], &mac[5]) != 6) {
        fprintf(stderr, "Некоректний формат MAC-адреси\n");
        return 1;
    }

    unsigned short vid = (argc >= 4) ? (unsigned short)atoi(argv[3]) : 0;
    return add_fdb_entry(ifidx, mac, vid);
}
```
```cpp
// bridge_fdb_inject.cpp - Ідіоматична C++ реалізація керування FDB моста
#include <iostream>
#include <vector>
#include <array>
#include <string>
#include <string_view>
#include <format>
#include <expected>
#include <system_error>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/rtnetlink.h>
#include <linux/if_bridge.h>
#include <linux/neighbour.h>
#include <net/if.h>

class NetlinkSocket {
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "socket(AF_NETLINK) failed");
        }
    }

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

struct MacAddress {
    std::array<uint8_t, 6> bytes{};

    static std::expected<MacAddress, std::string> from_string(std::string_view str) {
        MacAddress mac;
        int parsed = std::sscanf(str.data(), "%hhx:%hhx:%hhx:%hhx:%hhx:%hhx",
                                 &mac.bytes[0], &mac.bytes[1], &mac.bytes[2],
                                 &mac.bytes[3], &mac.bytes[4], &mac.bytes[5]);
        if (parsed != 6) {
            return std::unexpected("Invalid MAC format, expected XX:XX:XX:XX:XX:XX");
        }
        return mac;
    }
};

class BridgeController {
public:
    static std::expected<void, std::error_code> add_static_fdb(
        std::string_view ifname,
        const MacAddress& mac,
        uint16_t vid = 0)
    {
        unsigned int ifindex = ::if_nametoindex(ifname.data());
        if (ifindex == 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        NetlinkSocket nl_sock;
        std::vector<uint8_t> buffer(4096, 0);

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer.data());
        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ndmsg));
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_REPLACE | NLM_F_ACK;
        nlh->nlmsg_type = RTM_NEWNEIGH;
        nlh->nlmsg_seq = 1;

        auto* ndm = reinterpret_cast<struct ndmsg*>(NLMSG_DATA(nlh));
        ndm->ndm_family = AF_BRIDGE;
        ndm->ndm_ifindex = static_cast<int>(ifindex);
        ndm->ndm_state = NUD_PERMANENT;
        ndm->ndm_flags = NTF_MASTER;

        // Додавання MAC-адреси
        add_rtattr(buffer, nlh, NDA_LLADDR, mac.bytes.data(), mac.bytes.size());

        // Додавання VLAN ID (якщо активний)
        if (vid > 0) {
            add_rtattr(buffer, nlh, NDA_VLAN, &vid, sizeof(vid));
        }

        struct sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::sendto(nl_sock.native_handle(), nlh, nlh->nlmsg_len, 0,
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        std::array<uint8_t, 4096> recv_buf{};
        ssize_t len = ::recv(nl_sock.native_handle(), recv_buf.data(), recv_buf.size(), 0);
        if (len < 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        auto* resp = reinterpret_cast<struct nlmsghdr*>(recv_buf.data());
        if (resp->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(resp));
            if (err->error != 0) {
                return std::unexpected(std::make_error_code(static_cast<std::errc>(-err->error)));
            }
        }

        return {};
    }

private:
    static void add_rtattr(std::vector<uint8_t>& buf, struct nlmsghdr* nlh,
                           unsigned short type, const void* data, size_t data_len)
    {
        size_t rta_len = RTA_LENGTH(data_len);
        auto* rta = reinterpret_cast<struct rtattr*>(buf.data() + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(rta_len);
        std::memcpy(RTA_DATA(rta), data, data_len);
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(rta_len);
    }
};

int main(int argc, char** argv) {
    if (argc < 3) {
        std::cerr << "Використання: " << argv[0] << " <ifname> <MAC-адреса> [VLAN_ID]\n";
        return 1;
    }

    auto mac_res = MacAddress::from_string(argv[2]);
    if (!mac_res) {
        std::cerr << "Помилка: " << mac_res.error() << "\n";
        return 1;
    }

    uint16_t vid = (argc >= 4) ? static_cast<uint16_t>(std::stoi(argv[3])) : 0;
    auto res = BridgeController::add_static_fdb(argv[1], *mac_res, vid);

    if (!res) {
        std::cerr << "Помилка налаштування FDB: " << res.error().message() << "\n";
        return 1;
    }

    std::cout << "Статичний запис FDB успішно додано.\n";
    return 0;
}
```
:::

---

## 4. Діагностика, налагодження та трасування канального рівня

Під час експлуатації та діагностики комутаторів Linux Bridge виникають специфічні проблеми канального рівня: відкидання пакетів через конфлікти PVID, шторми широкомовного трафіку або блокування портами STP.

### Аналіз таблиці FDB та життєвого циклу записів

Таблиця комутації відображає поточний стан знань моста про підключені пристрої:

```bash
# Перегляд повної таблиці комутації моста
bridge fdb show

# Фільтрація записів для конкретного порту veth-b1-br
bridge fdb show dev veth-b1-br
```

Кожен рядок у виводі містить важливі прапорці ядра:
- `permanent` — статичний або локальний запис, створений ядром або адміністратором;
- `offload` — запис успішно синхронізовано з апаратним чіпом ASIC через Switchdev;
- `master br-core` — запис належить таблиці батьківського комутатора;
- `self` — запис розміщено безпосередньо в таблиці драйвера мережевої карти.

### Моніторинг подій у реальному часі

Команда `bridge monitor` використовує підписку на групу `RTNLGRP_NEIGH` для перегляду подій міграції MAC-адрес у реальному часі. Це дозволяє миттєво виявляти ситуації **MAC Flapping** — коли один і той самий MAC поперемінно надходить з двох різних портів через петлю в топології:

```bash
# Відстеження динамічного навчання, міграції та видалення MAC
bridge monitor fdb
```

### Захоплення тегованих Ethernet-кадрів через `tcpdump`

Звичайний виклик `tcpdump` приховує L2-заголовки. Прапорець `-e` (Ethernet header) у поєднанні з прапорцем `-n` (Numeric IP/port) дозволяє бачити повну структуру канального кадру, включаючи 4-байтний заголовок IEEE 802.1Q із числовим номером VLAN ID та бітами пріоритету PCP:

```bash
# Захоплення трафіку моста з детальними канальними заголовками
sudo tcpdump -e -n -i br-core
```

### Трасування скинутих пакетів ядра через `dropwatch`

Якщо комутатор скидає кадри (наприклад, через невідповідність VLAN або стан STP `BLOCKING`), діагностика на рівні L3 не дає результатів. Утиліта `dropwatch` перехоплює системні події виклику функції ядра `kfree_skb()` і показує точну назву функції в коді ядра, яка ініціювала скидання:

```bash
# Моніторинг функцій ядра, що викликають скидання буферів пакетів
sudo dropwatch -l kas
```

Типові функції скидання в підсистемі моста:
- `br_vlan_allowed()`: кадр містить VID, не дозволений у списку вхідних VLAN порту;
- `br_handle_frame()`: порт перебуває у стані `DISABLED` або `BLOCKING`;
- `br_fdb_update()`: виявлено заборонену спробу оновлення статичного запису.

### Завершення роботи та очищення ресурсів

Після завершення тестування все лабораторне середовище видаляється однією послідовністю команд, яка автоматично знищує міст, мережеві простори імен та пов'язані віртуальні інтерфейси:

```bash
sudo ip link del dev br-core
sudo ip netns del ns-blue1
sudo ip netns del ns-blue2
sudo ip netns del ns-red1
```

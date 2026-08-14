# ⚙️ Низькорівневий розбір кадрів 802.1Q на C/C++ та налаштування VLAN у Linux

Цей практичний посібник детально демонструє низькорівневий розбір Ethernet-кадрів із тегом IEEE 802.1Q через сирі сокети (raw sockets) у мовах C та C++, описує роботу апаратних фільтрів BPF та надає покрокові інструкції з конфігурації віртуальних мереж у Linux.

### 1. Низькорівнева анатомія кадру 802.1Q в системній пам'яті

При роботі із сирими мережевими сокетами сімейства `AF_PACKET` у режимі `SOCK_RAW` ядро Linux віддає застосунку повний Ethernet-кадр, починаючи з апаратного заголовка 2-го рівня. Якщо мережевий інтерфейс працює у транковому режимі і на ньому вимкнено апаратне зняття тегів (VLAN offload), після MAC-адреси відправника (`Src MAC`, байти 6–11) розташоване поле `EtherType`.

У звичайному немаркованому кадрі за адресою відправника одразу йде ідентифікатор протоколу верхнього рівня (наприклад `0x0800` для IPv4 або `0x86DD` для IPv6). Проте в маркованому кадрі 802.1Q на цьому місці знаходиться двобайтовий маркер `TPID` зі значенням `0x8100` у мережевому порядку байтів (`htons(0x8100)`). Наступні два байти містять поля TCI (`PCP`, `DEI`, `VID`), і лише після них розташоване справжнє поле `EtherType` вкладеного IP-пакета.

Схема розташування полів у байтовому масиві буфера пам'яті:
```text
  0                   1                   2                   3
  0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                     Destination MAC Address                   |
 |                        (Bytes 0 .. 5)                         |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |                        Source MAC Address                     |
 |                        (Bytes 6 .. 11)                        |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 |      TPID (0x8100)            | TCI (PCP + DEI + VID)         |
 |   [Bytes 12 .. 13]            |     [Bytes 14 .. 15]          |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
 | Real EtherType (0x0800)       | Payload ...                   |
 |   [Bytes 16 .. 17]            |                               |
 +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

Для коректного витягнення полів біти TCI розбираються за допомогою бітових зсувів та масок:
- Для витягнення ідентифікатора **VID** застосовують побітове «І» з маскою `0x0FFF`: `vid = tci & 0x0FFF`.
- Для витягнення прапорця **DEI** виконують зсув праворуч на 12 бітів і маскують 1 біт: `dei = (tci >> 12) & 0x01`.
- Для витягнення пріоритету **PCP** виконують зсув праворуч на 13 бітів і маскують 3 біти: `pcp = (tci >> 13) & 0x07`.

Оскільки всі багатобайтові значення передаються по мережі у порядку **Big-Endian** (Network Byte Order), перед виконанням маскування значення поля TCI обов'язково конвертують у порядок байтів хоста за допомогою функції `ntohs()`.

### 2. Прив'язка до мережевого інтерфейсу та режим Promiscuous

При створенні raw-сокета функція `socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))` перехоплює кадри з усіх мережевих адаптерів системи. Щоб обмежити перехоплення лише один конкретним фізичним транковим портом (наприклад `eth0`), сокет прив'язують до індексу інтерфейсу за допомогою структури `struct sockaddr_ll`:

:::tabs
```c
struct sockaddr_ll sll;
memset(&sll, 0, sizeof(sll));
sll.sll_family = AF_PACKET;
sll.sll_ifindex = if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_ALL);
bind(sock_fd, (struct sockaddr *)&sll, sizeof(sll));
```
```cpp
sockaddr_ll sll{};
sll.sll_family = AF_PACKET;
sll.sll_ifindex = ::if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_ALL);
::bind(sock_fd, reinterpret_cast<sockaddr*>(&sll), sizeof(sll));
```
:::

Крім того, за замовчуванням мережева карта відкидає кадри, призначені іншим MAC-адресам. Для перехоплення усіх кадрів у транку мережевий адаптер переводять у режим перехоплення (promiscuous mode) за допомогою системного виклику `setsockopt`:

:::tabs
```c
struct packet_mreq mr;
memset(&mr, 0, sizeof(mr));
mr.mr_ifindex = if_nametoindex("eth0");
mr.mr_type = PACKET_MR_PROMISC;
setsockopt(sock_fd, SOL_PACKET, PACKET_ADD_MEMBERSHIP, &mr, sizeof(mr));
```
```cpp
packet_mreq mr{};
mr.mr_ifindex = ::if_nametoindex("eth0");
mr.mr_type = PACKET_MR_PROMISC;
::setsockopt(sock_fd, SOL_PACKET, PACKET_ADD_MEMBERSHIP, &mr, sizeof(mr));
```
:::

### 3. Практичні реалізації аналізатора кадрів на C та C++

Наведені нижче приклади показують створення системного аналізатора мережевого трафіку. Програма відкриває сирий сокет, переводить мережеву карту в режим перехоплення та розбирає вхідні кадри Ethernet.

Обидві вкладки є суворо ідіоматичними:
- Приклад мовою **C** використовує традиційні виклики POSIX API, явне зсування покажчиків, пряму перевірку кодів помилок та ручне закриття файлових дескрипторів.
- Приклад мовою **C++** реалізує концепцію RAII для безпечного управління сокетом, використовує `std::span` для безпечного доступу до буфера без копирования пам'яті, strong enum classes та тип `std::expected` (C++23) для безпечної обробки помилок розбору.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <net/ethernet.h>
#include <netinet/in.h>

#define ETH_P_8021Q 0x8100
#define BUFFER_SIZE 2048

/* Структура 4-байтового тегу 802.1Q у пам'яті */
struct vlan_tag {
    uint16_t tpid; /* 0x8100 */
    uint16_t tci;  /* PCP(3b) + DEI(1b) + VID(12b) */
};

/* Функція розбору та виводу параметрів кадру */
void parse_ethernet_frame(const unsigned char *buffer, ssize_t len) {
    if (len < (ssize_t)sizeof(struct ether_header)) {
        printf("Занадто короткий кадр Ethernet (менше 14 байтів)\n");
        return;
    }

    const struct ether_header *eth = (const struct ether_header *)buffer;
    uint16_t ether_type = ntohs(eth->ether_type);

    printf("MAC: %02x:%02x:%02x:%02x:%02x:%02x -> %02x:%02x:%02x:%02x:%02x:%02x | ",
           eth->ether_shost[0], eth->ether_shost[1], eth->ether_shost[2],
           eth->ether_shost[3], eth->ether_shost[4], eth->ether_shost[5],
           eth->ether_dhost[0], eth->ether_dhost[1], eth->ether_dhost[2],
           eth->ether_dhost[3], eth->ether_dhost[4], eth->ether_dhost[5]);

    /* Перевірка наявність тегу 802.1Q (TPID == 0x8100) */
    if (ether_type == ETH_P_8021Q) {
        if (len < (ssize_t)(sizeof(struct ether_header) + sizeof(struct vlan_tag))) {
            printf("Помилка: занадто короткий кадр 802.1Q\n");
            return;
        }

        const struct vlan_tag *vlan = (const struct vlan_tag *)(buffer + sizeof(struct ether_header));
        uint16_t tci = ntohs(vlan->tci);

        uint8_t  pcp = (tci >> 13) & 0x07;
        uint8_t  dei = (tci >> 12) & 0x01;
        uint16_t vid = tci & 0x0FFF;

        const uint16_t *inner_type_ptr = (const uint16_t *)(buffer + sizeof(struct ether_header) + sizeof(struct vlan_tag));
        uint16_t inner_type = ntohs(*inner_type_ptr);

        printf("[VLAN TAGGED] VID: %u, PCP: %u, DEI: %u | Inner EtherType: 0x%04X\n",
               vid, pcp, dei, inner_type);
    } else {
        printf("[UNTAGGED] EtherType: 0x%04X\n", ether_type);
    }
}

int main(void) {
    /* Створення сирого сокета для перехоплення усіх кадрів Ethernet */
    int sock_fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (sock_fd < 0) {
        perror("Помилка створення raw-сокета (потрібні права root)");
        return 1;
    }

    unsigned char buffer[BUFFER_SIZE];
    printf("Запуск аналізатора кадрів 802.1Q... (Очікування 10 кадрів)\n");

    for (int i = 0; i < 10; ++i) {
        ssize_t data_size = recvfrom(sock_fd, buffer, BUFFER_SIZE, 0, NULL, NULL);
        if (data_size < 0) {
            perror("Помилка читання з сокета");
            break;
        }
        parse_ethernet_frame(buffer, data_size);
    }

    close(sock_fd);
    printf("Аналіз завершено, сокет закрито.\n");
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <span>
#include <expected>
#include <cstdint>
#include <cstring>
#include <iomanip>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <net/ethernet.h>

namespace net {

constexpr uint16_t eth_p_8021q = 0x8100;

enum class ParseError {
    FrameTooShort,
    NotVlanTagged
};

struct VlanHeaderInfo {
    uint16_t vid;
    uint8_t pcp;
    bool dei;
    uint16_t inner_ethertype;
};

// RAII обгортка для мережевого сирого сокета
class RawSocket {
    int fd_ = -1;
public:
    explicit RawSocket(uint16_t protocol) {
        fd_ = ::socket(AF_PACKET, SOCK_RAW, htons(protocol));
    }

    ~RawSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RawSocket(const RawSocket&) = delete;
    RawSocket& operator=(const RawSocket&) = delete;

    RawSocket(RawSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RawSocket& operator=(RawSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] bool isValid() const { return fd_ >= 0; }
    [[nodiscard]] int get() const { return fd_; }
};

class VlanFrameParser {
public:
    static std::expected<VlanHeaderInfo, ParseError> parse(std::span<const std::byte> frame) {
        constexpr size_t min_tagged_size = sizeof(ether_header) + 4;
        if (frame.size() < min_tagged_size) {
            return std::unexpected(ParseError::FrameTooShort);
        }

        const auto* eth = reinterpret_cast<const ether_header*>(frame.data());
        uint16_t ether_type = ntohs(eth->ether_type);

        if (ether_type != eth_p_8021q) {
            return std::unexpected(ParseError::NotVlanTagged);
        }

        uint16_t raw_tci;
        std::memcpy(&raw_tci, frame.data() + sizeof(ether_header) + 2, sizeof(uint16_t));
        uint16_t tci = ntohs(raw_tci);

        uint16_t raw_inner;
        std::memcpy(&raw_inner, frame.data() + sizeof(ether_header) + 4, sizeof(uint16_t));

        return VlanHeaderInfo{
            .vid = static_cast<uint16_t>(tci & 0x0FFF),
            .pcp = static_cast<uint8_t>((tci >> 13) & 0x07),
            .dei = static_cast<bool>((tci >> 12) & 0x01),
            .inner_ethertype = ntohs(raw_inner)
        };
    }
};

} // namespace net

int main() {
    net::RawSocket socket(ETH_P_ALL);
    if (!socket.isValid()) {
        std::cerr << "Помилка створення RAII raw-сокета. Перевірте root-права.\n";
        return 1;
    }

    std::vector<std::byte> buffer(2048);
    std::cout << "Запуск C++ RAII аналізатора кадрів...\n";

    for (int i = 0; i < 10; ++i) {
        ssize_t n = ::recvfrom(socket.get(), buffer.data(), buffer.size(), 0, nullptr, nullptr);
        if (n < 0) break;

        std::span<const std::byte> frame(buffer.data(), static_cast<size_t>(n));
        auto result = net::VlanFrameParser::parse(frame);

        if (result) {
            std::cout << "[VLAN TAGGED] VID: " << result->vid
                      << " | PCP: " << static_cast<int>(result->pcp)
                      << " | DEI: " << (result->dei ? "1" : "0")
                      << " | Inner Type: 0x" << std::hex << std::setw(4)
                      << std::setfill('0') << result->inner_ethertype
                      << std::dec << "\n";
        } else if (result.error() == net::ParseError::NotVlanTagged) {
            std::cout << "[UNTAGGED Frame]\n";
        }
    }

    return 0;
}
```
:::

### 4. Крайовий випадок: Вилучення тегів апаратним розвантаженням (VLAN Offloading)

Найпоширенішою практичною пасткою при розробці системних аналізаторів мережевого трафіку є ситуація, коли на мережевій карті увімкнено апаратне зняття тегів (`rx-vlan-offload`).

У цьому випадку мережевий контролер вирізає 4 байти тегу 802.1Q з каду до того, як передати його у буфер пам'яті. У результаті функція `recvfrom()` отримує кадр, де у полях `12-13` розташоване безпосередньо поле `EtherType` вкладеного протоколу (наприклад `0x0800`), а сам маркер `0x8100` повністю відсутній у корисних байтах!

Щоб отримати значення VID при увімкненому апаратному розвантаженні, застосунок повинен увімкнути додаткові метадані сокета `PACKET_AUXDATA`:

:::tabs
```c
int val = 1;
setsockopt(sock_fd, SOL_PACKET, PACKET_AUXDATA, &val, sizeof(val));
```
```cpp
int val = 1;
::setsockopt(sock_fd, SOL_PACKET, PACKET_AUXDATA, &val, sizeof(val));
```
:::

При зчитуванні даних через системний виклик `recvmsg()` ядро Linux передає допоміжне повідомлення типу `TPACKET_V2` або `tpacket_auxdata`, яке містить виділене значення `tp_vlan_tci`. Це дозволяє отримати VID навіть тоді, коли мережева карта вилучила тег із байтового масиву кадру.

### 5. Фільтрація кадрів 802.1Q через BPF (Berkeley Packet Filter)

При перехопленні трафіку у високонавантажених мережах передача усіх кадрів у простір користувача створює високе навантаження на процесор через постійні системні виклики та копирование пам'яті. Щоб відфільтрувати кадри конкретного VLAN безпосередньо у ядрі Linux, до сирого сокета застосовують BPF-фільтр (Berkeley Packet Filter).

Утиліта `tcpdump` компілює вираз `vlan 10` у наступний байт-код BPF:

```bash
# Перегляд байт-коду BPF для фільтрації VLAN 10
tcpdump -d 'vlan 10'
```

Вивід ассемблера BPF ядра:
```text
(000) ldh      [12]
(001) jeq      #0x8100          jt 2    jf 5
(002) ldh      [14]
(003) and      #0xfff
(004) jeq      #0xa             jt 6    jf 5
(005) ret      #0
(006) ret      #262144
```

Покроковий аналіз виконання байт-коду у ядрі:
1. Крок `000`: Інструкція `ldh [12]` завантажує два байти зі зміщення 12 каду (поле EtherType).
2. Крок `001`: Інструкція `jeq #0x8100` порівнює завантажене значення із маркером 802.1Q. Якщо збігається, виконання переходить на крок 2 (jt 2), інакше на крок 5 (jf 5).
3. Крок `002-003`: Завантажуються байти TCI (зміщення 14) та накладається маска `0x0FFF` для виділення 12 бітів VID.
4. Крок `004`: Інструкція `jeq #0xa` порівнює отриманий VID із числом 10 (`0x0A`).
5. Крок `005-006`: При невдачі повертається `0` (кадр відкидається ядром), при успіху повертається `262144` (кадр передається сокету користувача).

Застосування такого фільтра через `setsockopt(sock, SOL_SOCKET, SO_ATTACH_FILTER, &bpf_program)` дозволяє ядру Linux відсікати чужі кадри до їхнього копіювання в простір користувача, економлячи обчислювальні ресурси.

### 6. Автоматизація конфігурації у Linux

У виробничих середовищах налаштування VLAN автоматизують через системні сервіси `systemd-networkd` або декларативні конфіги `Netplan`.

#### Конфігурація через Systemd-networkd

Для створення VLAN 10 поверх фізичного адаптера `eth0` створюють три файли конфігурації у теці `/etc/systemd/network/`:

1. Опис віртуального пристрою `/etc/systemd/network/10-vlan10.netdev`:
```ini
[NetDev]
Name=eth0.10
Kind=vlan

[VLAN]
Id=10
```

2. Прив'язка до фізичного адаптера `/etc/systemd/network/20-eth0.network`:
```ini
[Match]
Name=eth0

[Network]
VLAN=eth0.10
LinkLocalAddressing=no
```

3. Налаштування мережевої адреси у `/etc/systemd/network/30-vlan10.network`:
```ini
[Match]
Name=eth0.10

[Network]
Address=192.168.10.50/24
Gateway=192.168.10.1
DNS=1.1.1.1
```

#### Конфігурація через Netplan (`/etc/netplan/01-netcfg.yaml`)

У дистрибутивах Ubuntu конфігурація задається у формате YAML:

```yaml
network:
  version: 2
  renderer: networkd
  ethernets:
    eth0:
      dhcp4: no
  vlans:
    eth0.10:
      id: 10
      link: eth0
      addresses:
        - 192.168.10.50/24
      routes:
        - to: default
          via: 192.168.10.1
```

Після збереження файла конфігурація застосовується командою `sudo netplan apply`, яка автоматично завантажує модуль `8021q` та піднімає відповідні віртуальні інтерфейси ядра.

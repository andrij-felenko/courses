# Програмні інтерфейси керування розвантаженнями: ioctl, Netlink ethtool та socket options

У ядрі Linux взаємодія користувацького простору (userspace) з підсистемою мережевих розвантажень здійснюється через три основних програмних інтерфейси:
1. Класичний **`ethtool` ioctl API** (`SIOCETHTOOL`), який базується на передачі структур даних у сокет `AF_INET`.
2. Сучасний **Netlink ethtool API** (`NETLINK_GENERIC` сімейство `ethtool`), який надає асинхронний розширюваний інтерфейс на основі атрибутів Netlink.
3. Сокетні опції **Socket Offload Control API** (`UDP_SEGMENT`, `UDP_GRO`, `SOL_UDP`), які дозволяють застосункам безпосередньо керувати GSO/GRO для окремих сокетів.

Нижче наведено детальний опис цих системних поверхневих API, механіку їхньої роботи всередині ядра Linux та ідіоматичні приклади використання мовами C та C++.

---

## 1. Класичний `ethtool` ioctl API (`SIOCETHTOOL`)

Історично першим і найпростішим способом отримання та зміни прапорців розвантаження був системний виклик `ioctl()` із командою `SIOCETHTOOL`. Цей інтерфейс існує з перших версій Linux 2.4 і залишається повністю сумісним для всіх мережевих драйверів.

### 1.1 Механіка виконання виклику ioctl у ядрі

Коли застосунок викликає `ioctl(fd, SIOCETHTOOL, &ifr)`, де `fd` — це відкритий мережевий сокет (наприклад, `AF_INET` сокет типу `SOCK_DGRAM`), відбуваються такі події:

1. Ядро виконує пошук пристрою `net_device` за іменем `ifr.ifr_name` через глобальну хеш-таблицю пристроїв ядра.
2. Перевіряються права процесу: зміна конфігурації вимагає наявності привілею `CAP_NET_ADMIN` у поточному namespace мережі.
3. Виклик передається в уніфікований обробник `dev_ethtool()`, розташований у файлі `net/ethtool/ioctl.c`.
4. Обробник розпаковує структуру `ethtool_value` або `ethtool_gfeatures` і викликає відповідний callback із таблиці операцій пристрою `net_device->ethtool_ops`.

### 1.2 Структури даних та застарілі команди

Взаємодія базується на структурі `ifreq` із заголовочного файла `<net/if.h>` та спеціалізованих структурах із `<linux/ethtool.h>` та `<linux/sockios.h>`.

В існуючому API класичні команди розділені за конкретними функціями:
- `ETHTOOL_GRXCSUM` / `ETHTOOL_SRXCSUM`: Отримання та встановлення стану апаратного обчислення RX Checksum.
- `ETHTOOL_GTXCSUM` / `ETHTOOL_STXCSUM`: Отримання та встановлення стану апаратного обчислення TX Checksum.
- `ETHTOOL_GTSO` / `ETHTOOL_STSO`: Керування TCP Segmentation Offload.
- `ETHTOOL_GGSO` / `ETHTOOL_SGSO`: Керування Generic Segmentation Offload.
- `ETHTOOL_GGRO` / `ETHTOOL_SGRO`: Керування Generic Receive Offload.
- `ETHTOOL_GLRO` / `ETHTOOL_SLRO`: Керування Large Receive Offload.

Структура `ethtool_value` має дуже простий вигляд:

```
struct ethtool_value {
    __u32   cmd;    // Команда (наприклад, ETHTOOL_GFLAGS або ETHTOOL_STSO)
    __u32   data;   // Бітова маска прапорців (1 = uвімкнено, 0 = вимкнено)
};
```

### 1.3 Сучасні команди `ETHTOOL_GFEATURES` та `ETHTOOL_SFEATURES`

Оскільки кількість фіч розвантаження перевищила 32 біти, у Linux 2.6.39 з'явився новий формат `ETHTOOL_GFEATURES`. Він використовує структуру `struct ethtool_gfeatures`:

```
struct ethtool_get_features_block {
    __u32   available;  // Маска фіч, які взагалі підтримує дане залізо
    __u32   requested;  // Маска фіч, запрошених юзерспейсом
    __u32   active;     // Поточна активна маска у ядрі
    __u32   never_changed; // Фічі, які зафіксовані драйвером [fixed]
};

struct ethtool_gfeatures {
    __u32   cmd;        // ETHTOOL_GFEATURES
    __u32   size;       // Кількість блоків у масиві features[]
    struct ethtool_get_features_block features[0];
};
```

Цей підхід дозволяє ядру динамічно повертати будь-яку кількість бітових масивів, забезпечуючи розширюваність API.

### 1.4 Приклад зчитування розвантажень через `SIOCETHTOOL`

Нижче наведено ідіоматичні приклади використання класичного ioctl API для отримання стану RX/TX Checksum та TSO.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

int check_nic_offloads_c(const char *ifname) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) {
        perror("socket");
        return -1;
    }

    struct ethtool_value eval;
    memset(&eval, 0, sizeof(eval));
    eval.cmd = ETHTOOL_GFLAGS;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    ifr.ifr_data = (caddr_t)&eval;

    if (ioctl(fd, SIOCETHTOOL, &ifr) < 0) {
        perror("ioctl SIOCETHTOOL GFLAGS");
        close(fd);
        return -1;
    }

    printf("Інтерфейс: %s\n", ifname);
    printf("  RX Checksum: %s\n", (eval.data & ETH_FLAG_RXCSUM) ? "ON" : "OFF");
    printf("  TX Checksum: %s\n", (eval.data & ETH_FLAG_TXCSUM) ? "ON" : "OFF");
    printf("  TSO:         %s\n", (eval.data & ETH_FLAG_TSO)    ? "ON" : "OFF");

    close(fd);
    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <string_view>
#include <system_error>
#include <memory>
#include <cstring>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/ethtool.h>

class UniqueFd {
    int fd_{-1};
public:
    explicit UniqueFd(int fd) : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }
    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;
    UniqueFd(UniqueFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct NicOffloadState {
    bool rx_checksum{false};
    bool tx_checksum{false};
    bool tso{false};
};

std::expected<NicOffloadState, std::error_code> query_nic_offloads(std::string_view ifname) {
    UniqueFd sock{::socket(AF_INET, SOCK_DGRAM, 0)};
    if (!sock.valid()) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::ethtool_value eval{};
    eval.cmd = ETHTOOL_GFLAGS;

    ::ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), std::min(ifname.size(), sizeof(ifr.ifr_name) - 1));
    ifr.ifr_data = reinterpret_cast<caddr_t>(&eval);

    if (::ioctl(sock.get(), SIOCETHTOOL, &ifr) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    NicOffloadState state;
    state.rx_checksum = (eval.data & ETH_FLAG_RXCSUM) != 0;
    state.tx_checksum = (eval.data & ETH_FLAG_TXCSUM) != 0;
    state.tso         = (eval.data & ETH_FLAG_TSO) != 0;

    return state;
}
```
:::

---

## 2. Сучасний Linux Netlink ethtool API (`ETHTOOL_GENL_NAME`)

Недоліки класичного ioctl API (фіксовані розміри структур, неможливість асинхронних сповіщень про зміни, складність додавання нових прапорців) призвели до того, що в Linux 5.6 було реалізовано нову підсистему **Netlink ethtool**.

Вона базується на Generic Netlink (`NETLINK_GENERIC`) з іменем сімейства `ETHTOOL_GENL_NAME` (`"ethtool"`).

### 2.1 Переваги Netlink ethtool підсистеми

1. **Асинхронні сповіщення (Notifications)**: Будь-який процес у юзерспейсі може підписатися на групу `ETHTOOL_MCGRP_MONITOR` i отримувати сповіщення в реальному часі, коли інший процес або демони мережі змінюють прапорці розвантажень.
2. **Самоописові атрибути Netlink (`nlattr`)**: Кожна фіча передається у вигляді текстової назви (наприклад, `"tx-checksum-ipv4"`, `"rx-gro-list"`), що позбавляє від жорсткої прив'язки до порядкових індексів бітових масок.
3. **Строга перевірка типів та валідація**: Використання політик Netlink в ядрі запобігає передачі пошкоджених даних або некоректних розмірів буферів.

### 2.2 Структура повідомлень та тип атрибутів

Для взаємодії з Netlink ethtool використовується сокет `socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC)`.

Основні типи повідомлень із `<linux/ethtool_netlink.h>`:
- `ETHTOOL_MSG_FEATURES_GET`: Отримання списку активних, запрошених, доступних та зафіксованих фіч.
- `ETHTOOL_MSG_FEATURES_SET`: Зміна стану окремих прапорців.
- `ETHTOOL_MSG_FEATURES_ACT_NTF`: Асинхронне сповіщення про зміну фіч на інтерфейсі.

Ієрархія атрибутів у відповіді ядра для `ETHTOOL_MSG_FEATURES_GET`:
- `ETHTOOL_A_FEATURES_HEADER`: Вкладений заголовок, що містить `ETHTOOL_A_HEADER_DEV_INDEX` або `ETHTOOL_A_HEADER_DEV_NAME`.
- `ETHTOOL_A_FEATURES_HW`: Бітова маска фіч, підтримуваних залізом.
- `ETHTOOL_A_FEATURES_ACTIVE`: Бітова маска фіч, які реально активні в ядрі зараз.
- `ETHTOOL_A_FEATURES_UNCHANGEABLE`: Маска фіч, які неможливо змінити (`[fixed]`).

---

## 3. Сокетний API розвантаження: UDP Segmentation Offload (`UDP_SEGMENT`) та `UDP_GRO`

Застосунки юзерспейсу можуть керувати розвантаженнями не лише глобально на рівні всієї мережевої карти, а й локально для конкретного мережевого сокета.

### 3.1 UDP-GSO прапорець `UDP_SEGMENT` (Transmit)

Опція сокета `UDP_SEGMENT` (з заголовочного файла `<netinet/udp.h>`) дозволяє високопродуктивним мережевим сервісам (наприклад, реалізаціям протоколу QUIC у HTTP/3, медіа-серверам WebRTC) передавати великі масиви даних за один системний виклик `sendmsg()`.

Механізм роботи:
1. Застосунок створює буфер розміром до 64 КБ (наприклад, 44 блоки по 1472 байти = 64 768 байт).
2. За допомогою допоміжної структури `cmsghdr` (ancillary data) у системний виклик `sendmsg()` додається керуюче повідомлення з рівнем `SOL_UDP` та типом `UDP_SEGMENT`.
3. Корисне значення `cmsg` містить 16-бітне число — розмір одного сегмента `segment_size = 1472`.
4. Ядро Linux створює один `sk_buff`, проводить його через весь стек маршрутизації та netfilter, а на рівні GSO розбиває на окремі UDP-пакети.

### 3.2 UDP-GRO опція `UDP_GRO` (Receive)

Опція `UDP_GRO` дозволяє сокету приймати апаратні або NAPI GRO супер-пакети UDP без їх попереднього розбиття на окремі датуграми.

Для активації сокетної опції застосунок виконує:

```
int val = 1;
setsockopt(sockfd, SOL_UDP, UDP_GRO, &val, sizeof(val));
```

Після цього виклик `recvmsg()` повертає об'єднаний буфер даних, а в супутньому повідомленні `cmsg` типу `UDP_GRO` повертається 16-бітне значення розміру оригінального сегмента.

### 3.3 Приклад відправки UDP-GSO трафіку мовами C та C++

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>
#include <arpa/inet.h>

ssize_t send_udp_gso_c(int sockfd, const struct sockaddr_in *dst_addr,
                       const void *data, size_t data_len, uint16_t segment_size) {
    struct iovec iov;
    iov.iov_base = (void *)data;
    iov.iov_len = data_len;

    char cbuf[CMSG_SPACE(sizeof(uint16_t))];
    memset(cbuf, 0, sizeof(cbuf));

    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_name = (void *)dst_addr;
    msg.msg_namelen = sizeof(*dst_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_UDP;
    cmsg->cmsg_type = UDP_SEGMENT;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));
    
    uint16_t *val_ptr = (uint16_t *)CMSG_DATA(cmsg);
    *val_ptr = segment_size;

    return sendmsg(sockfd, &msg, 0);
}
```
@tab C++
```cpp
#include <iostream>
#include <span>
#include <system_error>
#include <expected>
#include <vector>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/udp.h>

class UdpSocket {
    int fd_{-1};
public:
    explicit UdpSocket(int fd) : fd_(fd) {}
    ~UdpSocket() { if (fd_ >= 0) ::close(fd_); }
    UdpSocket(const UdpSocket&) = delete;
    UdpSocket& operator=(const UdpSocket&) = delete;
    UdpSocket(UdpSocket&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    UdpSocket& operator=(UdpSocket&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

std::expected<size_t, std::error_code> send_udp_gso(
    int sockfd,
    const sockaddr_in& dst_addr,
    std::span<const std::byte> payload,
    uint16_t segment_size)
{
    ::iovec iov{};
    iov.iov_base = const_cast<void*>(static_cast<const void*>(payload.data()));
    iov.iov_len = payload.size();

    alignas(struct cmsghdr) char cbuf[CMSG_SPACE(sizeof(uint16_t))]{};

    ::msghdr msg{};
    msg.msg_name = const_cast<sockaddr_in*>(&dst_addr);
    msg.msg_namelen = sizeof(dst_addr);
    msg.msg_iov = &iov;
    msg.msg_iovlen = 1;
    msg.msg_control = cbuf;
    msg.msg_controllen = sizeof(cbuf);

    ::cmsghdr* cmsg = CMSG_FIRSTHDR(&msg);
    cmsg->cmsg_level = SOL_UDP;
    cmsg->cmsg_type = UDP_SEGMENT;
    cmsg->cmsg_len = CMSG_LEN(sizeof(uint16_t));

    auto* val_ptr = reinterpret_cast<uint16_t*>(CMSG_DATA(cmsg));
    *val_ptr = segment_size;

    ssize_t ret = ::sendmsg(sockfd, &msg, 0);
    if (ret < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return static_cast<size_t>(ret);
}
```
:::

---

## 4. Порівняльна матриця системних інтерфейсів керування розвантаженнями

| Інтерфейс | Рівень застосування | Тип запиту | Підтримувані протоколи | Основні переваги |
| :--- | :--- | :--- | :--- | :--- |
| **`SIOCETHTOOL` (ioctl)** | Глобальний (NIC) | Синхронний блокируючий | Усі (PHY/MAC) | Простота, сумісність з усіма версіями ядра Linux |
| **Netlink ethtool** | Глобальний (NIC) | Асинхронний Netlink | Усі (PHY/MAC) | Розширюваність, детальні текстові назви фіч, сповіщення |
| **`UDP_SEGMENT` (sockopt)** | Пер-сокетний / Пер-пакетний | CMSG data в `sendmsg` | UDP / QUIC | Не вимагає CAP_NET_ADMIN, знижує CPU на 50–70% для UDP |
| **`UDP_GRO` (sockopt)** | Пер-сокетний | `setsockopt` / CMSG | UDP / QUIC | Агрегація прийнятих UDP пакетів на рівні сокета |

---

## 5. Підсумок

Різноманіття інтерфейсів керування розвантаженнями у Linux відображає еволюцію системного програмування: від простих блокуючих `ioctl` запитів 1990-х років до сучасних розширюваних Netlink-протоколів та сокетних прапорців grain-level контролю. Використання сокетних опцій `UDP_SEGMENT` та `UDP_GRO` надає розробникам прикладного ПЗ можливість досягати максимальної продуктивності мережевого io без необхідності зміни глобальних налаштувань всієї операційної системи.

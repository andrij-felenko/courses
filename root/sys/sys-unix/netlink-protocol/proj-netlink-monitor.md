# ⚙️ Практикум: розробка асинхронного монітора мережевих подій на Netlink

Цей практикум присвячено практичній розробці та детальному архітектурному аналізу високопродуктивного асинхронного монітора мережевих подій ядра Linux на мовах C та C++. Програма відкриває сокет `AF_NETLINK`, підписується на мультикаст-групи підсистеми `rtnetlink` (`RTMGRP_LINK` та `RTMGRP_IPV4_IFADDR`) і в реальному часі обробляє сповіщення про зміну стану мережевих інтерфейсів (підняття чи опущення каналу, зміна MTU, оновлення операційного стану) та додавання чи видалення IP-адрес.

## Архітектура неблокуючого обробника подій у просторі користувача

Традиційний підхід до спостереження за мережевим стеком через текстові файли псевдофайлової системи `/proc/net/dev` або періодичний виклик `ioctl(SIOCGIFCONF)` спирається на пасивний опит (англ. *polling*). При пасивному опиті програма змушена виконувати системні виклики у нескінченному циклі з фіксованим інтервалом (наприклад, щосекунди). Це створює дві фундаментальні проблеми:
1. **Висока затримка реакції (Latency)**: Якщо мережевий кабель від'єднано на початку секунди, програма дізнається про це лише наприкінці інтервалу опитування.
2. **Марна витрата процесорних ресурсів**: У стаціонарному стані, коли конфігурація мережі не змінюється роками, тисячі марних викликів `read()` даремно спалюють такти ЦП і викликають перемикання контексту процесів.

Сокетний інтерфейс Netlink принципово змінює цю парадигму. Переходячи у стан очікування за допомогою системного виклику `poll()` або `epoll_wait()`, процес користувача повністю вивільняє процесор. Потоки виконання блокуються на рівні черги сокета у ядрі. Як тільки в мережевому стеку відбувається подія (наприклад, драйвер мережевої карти повідомляє про втрату несучої частоти Ethernet-кабелю), ядро самостійно формує дейтаграму Netlink, копіює її у приймальний буфер сокета й будить процес користувача.

```
+-------------------------------------------------------------------+
|               Мережеве ядро Linux (NETLINK_ROUTE)                 |
+-------------------------------------------------------------------+
                                  |
            Мультикаст-трансляція (RTMGRP_LINK | RTMGRP_IPV4_IFADDR)
                                  |
                                  v
+-------------------------------------------------------------------+
|                      Асинхронний сокет Netlink                    |
|                        (sock_fd, AF_NETLINK)                      |
+-------------------------------------------------------------------+
                                  |
                            poll() / recvmsg()
                                  v
+-------------------------------------------------------------------+
|               Парсер дейтаграм (NLMSG_OK / RTA_OK)                |
|            - RTM_NEWLINK / RTM_DELLINK -> IFLA_IFNAME             |
|            - RTM_NEWADDR / RTM_DELADDR -> IFA_ADDRESS             |
+-------------------------------------------------------------------+
```

## Механізм прив'язки та підписки на мультикаст-групи

Для того щоб отримувати асинхронні сповіщення від ядра, програма повинна правильно налаштувати структуру адреси `struct sockaddr_nl` під час виклику `bind()`:

1. **Ідентифікатор порту (`nl_pid`)**: Заповнення поля `nl_pid = 0` повідомляє ядро про те, що воно має самостійно виділити унікальний числовий ідентифікатор порту для цього сокета. Це гарантує відсутність конфліктів `EADDRINUSE`, якщо в системі паралельно запускається кілька екземплярів монітора або якщо процес має кілька потоків. Ядро зберігає таблицю активних портів у хеш-таблиці `nl_table` і перевіряє унікальність кожного створеного сокета.
2. **Маска мультикаст-груп (`nl_groups`)**: Задає бітову маску категорій подій, на які підписується сокет. Біт `RTMGRP_LINK` (який відповідає масці `(1 << (RTM_NEWLINK - 1))`) вмикає сповіщення про створення, видалення та зміну прапорців мережевих пристроїв. Біт `RTMGRP_IPV4_IFADDR` підписує сокет на події додавання та видалення IPv4-адрес. У сучасних ядрах підписка також може виконуватися динамічно через `setsockopt(fd, SOL_NETLINK, NETLINK_ADD_MEMBERSHIP, &group, sizeof(group))`.

При отриманні даних із сокета слід враховувати, що ядро може об'єднати кілька повідомлень Netlink в один мережевий пакет. Обхід буфера виконується за допомогою макросу `NLMSG_OK(nlh, len)`, який на кожному кроці перевіряє, чи залишок прочитаних байтів `len` не менший за розмір кадру `nlh->nlmsg_len`. Перехід до наступного кадру виконується макросом `NLMSG_NEXT(nlh, len)`.

Всередині кожного кадру корисне навантаження розміщується за заголовком підсистеми (`struct ifinfomsg` або `struct ifaddrmsg`). Послідовність атрибутів TLV читається макросом `RTA_OK(rta, rta_len)`.

## Розширені сокетні опції Netlink

При побудові монітора подій виробничого рівня (англ. *production-grade*) необхідно враховувати можливість втрати повідомлень при пікових навантаженнях. Якщо ядро генерує сповіщення швидше, ніж процес користувача встигає їх зчитувати із сокета, буфер сокета переповнюється, і ядро скидає нові пакети, повертаючи помилку `ENOBUFS`.

Для керування цими крайовими випадками ядро надає спеціальні опції сокета у домені `SOL_NETLINK`:
* **`NETLINK_ADD_MEMBERSHIP` / `NETLINK_DROP_MEMBERSHIP`**: Динамічне приєднання або вихід із мультикаст-групи без повторного виклику `bind()`. Це дозволяє процесу підписуватися на події окремих VLAN чи мережевих просторів імен на ходу.
* **`NETLINK_NO_ENOBUFS`**: Пригнічує генерацію помилки `ENOBUFS`. При ввімкненні цієї опції ядро мовчки скидає пакети при переповненні буфера, не перериваючи цикл виклику `recv()`.
* **`NETLINK_GET_STRICT_CHK`**: Вмикає сувору перевірку вхідних атрибутів та фільтрацію дампа безпосередньо у ядрі.

## Реалізація монітора подій

Нижче наведено дві повноцінні реалізації асинхронного монітора мережевих подій: класичною мовою C (із використанням низькорівневих викликів POSIX) та сучасною мовою C++20 (із застосуванням шаблону RAII, безпечних зрізів `std::span` та рядкових посилань `std::string_view`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <poll.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>

#define BUFFER_SIZE 8192

static void parse_link_event(struct nlmsghdr *nlh) {
    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = IFLA_RTA(ifi);
    int rta_len = IFLA_PAYLOAD(nlh);
    char ifname[IFNAMSIZ] = "unknown";

    for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
        if (rta->rta_type == IFLA_IFNAME) {
            snprintf(ifname, sizeof(ifname), "%s", (char *)RTA_DATA(rta));
        }
    }

    const char *action = (nlh->nlmsg_type == RTM_NEWLINK) ? "NEWLINK" : "DELLINK";
    const char *state = (ifi->ifi_flags & IFF_UP) ? "UP" : "DOWN";
    const char *running = (ifi->ifi_flags & IFF_RUNNING) ? "RUNNING" : "NOT_RUNNING";

    printf("[LINK %s] Interface %s (index %d): Flags=%s,%s\n", 
           action, ifname, ifi->ifi_index, state, running);
}

static void parse_addr_event(struct nlmsghdr *nlh) {
    struct ifaddrmsg *ifa = (struct ifaddrmsg *)NLMSG_DATA(nlh);
    struct rtattr *rta = IFA_RTA(ifa);
    int rta_len = IFA_PAYLOAD(nlh);
    char ip_str[INET_ADDRSTRLEN] = "0.0.0.0";

    for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
        if (rta->rta_type == IFA_ADDRESS || rta->rta_type == IFA_LOCAL) {
            struct in_addr *addr = (struct in_addr *)RTA_DATA(rta);
            inet_ntop(AF_INET, addr, ip_str, sizeof(ip_str));
        }
    }

    const char *action = (nlh->nlmsg_type == RTM_NEWADDR) ? "ADD_ADDR" : "DEL_ADDR";
    printf("[ADDR %s] Interface index %d: IP %s/%d\n", 
           action, ifa->ifa_index, ip_str, ifa->ifa_prefixlen);
}

int main(void) {
    int sock_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (sock_fd < 0) {
        perror("socket");
        return 1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    sa.nl_pid = 0; /* Автоматичний вибір PID ядром */
    sa.nl_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR;

    if (bind(sock_fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("bind");
        close(sock_fd);
        return 1;
    }

    printf("Netlink monitor started. Listening for RTMGRP_LINK and RTMGRP_IPV4_IFADDR...\n");

    struct pollfd pfd = { .fd = sock_fd, .events = POLLIN };
    char buffer[BUFFER_SIZE];

    while (1) {
        int ret = poll(&pfd, 1, -1);
        if (ret < 0) {
            perror("poll");
            break;
        }

        if (pfd.revents & POLLIN) {
            ssize_t len = recv(sock_fd, buffer, sizeof(buffer), 0);
            if (len < 0) {
                perror("recv");
                break;
            }

            struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
            for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
                if (nlh->nlmsg_type == NLMSG_DONE) break;
                if (nlh->nlmsg_type == NLMSG_ERROR) {
                    struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(nlh);
                    fprintf(stderr, "Netlink error: %d\n", err->error);
                    continue;
                }

                if (nlh->nlmsg_type == RTM_NEWLINK || nlh->nlmsg_type == RTM_DELLINK) {
                    parse_link_event(nlh);
                } else if (nlh->nlmsg_type == RTM_NEWADDR || nlh->nlmsg_type == RTM_DELADDR) {
                    parse_addr_event(nlh);
                }
            }
        }
    }

    close(sock_fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <system_error>
#include <stdexcept>
#include <unistd.h>
#include <sys/socket.h>
#include <poll.h>
#include <arpa/inet.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>

// RAII-обгортка для файлового дескриптора сокета
class UniqueFd {
    int m_fd{-1};
public:
    explicit UniqueFd(int fd = -1) noexcept : m_fd(fd) {}
    ~UniqueFd() { reset(); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : m_fd(other.m_fd) {
        other.m_fd = -1;
    }

    UniqueFd& operator=(UniqueFd&& other) noexcept {
        if (this != &other) {
            reset();
            m_fd = other.m_fd;
            other.m_fd = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }

    void reset(int new_fd = -1) noexcept {
        if (m_fd >= 0) {
            close(m_fd);
        }
        m_fd = new_fd;
    }
};

class NetlinkMonitor {
    UniqueFd m_sock;
    static constexpr size_t BufferSize = 8192;

public:
    NetlinkMonitor() {
        int fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (fd < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }
        m_sock.reset(fd);

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;
        sa.nl_pid = 0;
        sa.nl_groups = RTMGRP_LINK | RTMGRP_IPV4_IFADDR;

        if (::bind(m_sock.get(), reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to bind netlink socket");
        }
    }

    void run() {
        std::cout << "C++20 Netlink Monitor started. Waiting for events...\n";
        std::vector<uint8_t> buffer(BufferSize);
        pollfd pfd{ .fd = m_sock.get(), .events = POLLIN, .revents = 0 };

        while (true) {
            int ret = ::poll(&pfd, 1, -1);
            if (ret < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "poll failed");
            }

            if (pfd.revents & POLLIN) {
                ssize_t bytes_read = ::recv(m_sock.get(), buffer.data(), buffer.size(), 0);
                if (bytes_read < 0) {
                    if (errno == EAGAIN || errno == EINTR) continue;
                    throw std::system_error(errno, std::generic_category(), "recv failed");
                }

                process_buffer(std::span<const uint8_t>(buffer.data(), static_cast<size_t>(bytes_read)));
            }
        }
    }

private:
    void process_buffer(std::span<const uint8_t> data) const {
        auto len = static_cast<int>(data.size());
        auto nlh = reinterpret_cast<const struct nlmsghdr*>(data.data());

        for (; NLMSG_OK(nlh, len); nlh = NLMSG_NEXT(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) break;
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                auto err = reinterpret_cast<const struct nlmsgerr*>(NLMSG_DATA(nlh));
                std::cerr << "Netlink error: " << err->error << "\n";
                continue;
            }

            if (nlh->nlmsg_type == RTM_NEWLINK || nlh->nlmsg_type == RTM_DELLINK) {
                handle_link_event(nlh);
            } else if (nlh->nlmsg_type == RTM_NEWADDR || nlh->nlmsg_type == RTM_DELADDR) {
                handle_addr_event(nlh);
            }
        }
    }

    void handle_link_event(const struct nlmsghdr* nlh) const {
        auto ifi = reinterpret_cast<const struct ifinfomsg*>(NLMSG_DATA(nlh));
        auto rta = IFLA_RTA(ifi);
        int rta_len = IFLA_PAYLOAD(nlh);
        std::string_view ifname = "unknown";

        for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
            if (rta->rta_type == IFLA_IFNAME) {
                ifname = std::string_view(reinterpret_cast<const char*>(RTA_DATA(rta)));
            }
        }

        std::string_view action = (nlh->nlmsg_type == RTM_NEWLINK) ? "NEWLINK" : "DELLINK";
        bool is_up = (ifi->ifi_flags & IFF_UP) != 0;
        bool is_running = (ifi->ifi_flags & IFF_RUNNING) != 0;

        std::cout << "[LINK " << action << "] Interface " << ifname 
                  << " (index " << ifi->ifi_index << "): State=" 
                  << (is_up ? "UP" : "DOWN") << ", Running=" 
                  << (is_running ? "YES" : "NO") << "\n";
    }

    void handle_addr_event(const struct nlmsghdr* nlh) const {
        auto ifa = reinterpret_cast<const struct ifaddrmsg*>(NLMSG_DATA(nlh));
        auto rta = IFA_RTA(ifa);
        int rta_len = IFA_PAYLOAD(nlh);
        char ip_buf[INET_ADDRSTRLEN] = "0.0.0.0";

        for (; RTA_OK(rta, rta_len); rta = RTA_NEXT(rta, rta_len)) {
            if (rta->rta_type == IFA_ADDRESS || rta->rta_type == IFA_LOCAL) {
                auto addr = reinterpret_cast<const struct in_addr*>(RTA_DATA(rta));
                ::inet_ntop(AF_INET, addr, ip_buf, sizeof(ip_buf));
            }
        }

        std::string_view action = (nlh->nlmsg_type == RTM_NEWADDR) ? "ADD_ADDR" : "DEL_ADDR";
        std::cout << "[ADDR " << action << "] Interface index " << ifa->ifa_index 
                  << ": IP " << ip_buf << "/" << static_cast<int>(ifa->ifa_prefixlen) << "\n";
    }
};

int main() {
    try {
        NetlinkMonitor monitor;
        monitor.run();
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Аналіз архітектурних відмінностей C та C++20 варіантів

Розробка системних утилит на C++20 демонструє значні переваги в надійності без жодних втрат у продуктивності:

1. **Керування ресурсами (RAII vs Manual cleanup)**: У C-версії при кожному передчасному виході з функції або обробці помилки розробник зобов'язаний пам'ятати про виклик `close(sock_fd)`. Помилка в обробці гілок помилок призводить до витоку файлових дескрипторів. У C++20 деструктор класу `UniqueFd` автоматично закриває дескриптор при виході з області видимості, навіть якщо виник виняток (англ. *exception*).
2. **Безпека типів та зрізи пам'яті (`std::span`)**: Прибічники C часто передають вказівник `char*` та окрему довжину `int len`, що створює ризик передачі неузгоджених розмірів. Шаблон `std::span<const uint8_t>` у C++20 об'єднує вказівник на буфер та його розмір в єдину неволодіючу абстракцію, що виключає переповнення буфера.
3. **Нуль-копіювання рядків (`std::string_view`)**: У C-версії для збереження назви інтерфейсу використовується `snprintf` у фіксований масив `char ifname[IFNAMSIZ]`. У C++20 `std::string_view` посилається безпосередньо на байти всередині буфера прочитаного кадри Netlink, усуваючи будь-яке копіювання чи виділення динамічної пам'яті у купі (heap).

## Діагностика сокетів Netlink у просторі користувача

Для діагностики створених сокетів Netlink та перевірки активних підписок у системі Linux розробники можуть використовувати стандартні утиліти моніторингу:

1. **Перегляд відкритих сокетів Netlink через `ss`**:
   Утиліта `ss -0 -a` показує всі активні сокети Netlink у системі, їхні порт-ідентифікатори `nl_pid` та підписані мультикаст-групи:

   ```bash
   ss -0 -a
   # Вивід показує протокол (NETLINK_ROUTE), PID процесу та маску груп (RTMGRP_LINK)
   ```

2. **Інспекція через `/proc/net/netlink`**:
   Ядро показує стан усіх активних сокетів Netlink у псевдофайлі `/proc/net/netlink`:

   ```bash
   cat /proc/net/netlink
   ```

   Кожен рядок містить адресу структури сокета у ядрі, номер протоколу (наприклад, 0 для `NETLINK_ROUTE`), `nl_pid` процесу-власника, бітову маску підписаних мультикаст-груп та поточний стан використання буферів пам'яті `rmem` / `wmem`.

3. **Трасування подій через eBPF / bpftrace**:
   Для відстеження передачі кадри Netlink на рівні ядра без модифікації коду програми можна використовувати інструмент `bpftrace`, що спирається на ядерні точечні проби (англ. *tracepoints*):

   ```bash
   sudo bpftrace -e 'tracepoint:netlink:netlink_extack { printf("ExtACK error msg: %s\n", args->msg); }'
   ```

## Збірка, тестування та трасування

Для компіляції обох варіантів монітора скористайтесь комбіляторами GCC або Clang:

```bash
# Компіляція C-версії
gcc -Wall -Wextra -O2 proj-netlink-monitor.c -o netlink_mon_c

# Компіляція C++20 версії
g++ -std=c++20 -Wall -Wextra -O2 proj-netlink-monitor.cpp -o netlink_mon_cpp
```

Для випробування запустіть скомпільований монітор у першому вікні термінала:

```bash
./netlink_mon_cpp
```

У другому вікні термінала виконайте динамічні зміни конфігурації мережі за допомогою інструменту `iproute2`:

```bash
# 1. Створення віртуальної пари інтерфейсів veth0 та veth1
sudo ip link add veth0 type veth peer name veth1

# 2. Призначення IPv4 адреси на інтерфейс veth0
sudo ip addr add 192.168.100.1/24 dev veth0

# 3. Активація інтерфейсу (переведення в стан UP)
sudo ip link set dev veth0 up

# 4. Деактивація та видалення віртуального пристрою
sudo ip link set dev veth0 down
sudo ip link del dev veth0
```

Монітор негайно виведе у термінал текстовий протокол подій, згенерованих ядром Linux у відповідь на кожну з виконаних команд.

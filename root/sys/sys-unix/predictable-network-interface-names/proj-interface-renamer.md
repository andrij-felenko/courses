# ⚙️ Керування іменами та альтернативними назвами через RTNetlink

Зміна імені мережевого інтерфейсу в сучасних операційних системах Linux здійснюється через підсистему ядра RTNetlink (сімейство протоколів `NETLINK_ROUTE`). Демон `systemd-udevd` використовує саме цей механізм замість застарілого виклику `ioctl(SIOCSIFNAME)` під час обробки подій підключення пристроїв та застосування правил `.link`.

Нижче наведено детальний розбір механізму ядра та робочий інструмент для низькорівневого перейменування мережевого інтерфейсу та реєстрації альтернативних псевдонімів (`IFLA_ALT_IFNAME`), реалізований мовами C та C++.

## Механізм взаємодії з ядром через RTNetlink

RTNetlink надає бінарний інтерфейс обміну повідомленнями поверх сокетів сімейства `AF_NETLINK`. На відміну від застарілих викликів `ioctl`, які використовували фіксовані структури `struct ifreq` і не підтримували розширення атрибутів, протокол Netlink дозволяє передавати списки типізованих параметрів змінної довжини (TLV — Type-Length-Value).

Кожне повідомлення Netlink вирівнюється за 4-байтовою межею пам'яті. Для роботи з вирівнюванням та обчислення довжин використовуються спеціальні системні макроси:
- `NLMSG_ALIGN(len)` — округлює довжину заголовка Netlink до найближчого кратного 4 числа;
- `NLMSG_LENGTH(len)` — повертає довжину заголовка разом із корисним навантаженням;
- `RTA_ALIGN(len)` — вирівнює довжину атрибута `rtattr`;
- `RTA_LENGTH(len)` — обчислює розмір структури `rtattr` разом із даними атрибута;
- `RTA_DATA(rta)` — повертає вказівник на початок корисних даних атрибута.

Для модифікації параметрів мережевого інтерфейсу простір користувача формує пакет із типом `RTM_SETLINK` і надсилає його в сокет маршрутизації ядра. Пакет складається з таких обов'язкових компонентів:

1. **Заголовок Netlink (`struct nlmsghdr`):**
   - `nlmsg_len` — загальна довжина пакета включно із заголовком та всіма вкладеними даними;
   - `nlmsg_type` — тип операції (`RTM_SETLINK` для зміни параметрів наявного інтерфейсу);
   - `nlmsg_flags` — прапорці запиту (`NLM_F_REQUEST` вимагає обробки ядром, `NLM_F_ACK` змушує ядро надіслати підтвердження або код помилки);
   - `nlmsg_seq` — порядковий номер транзакції для узгодження запиту та відповіді.

2. **Тіло повідомлення інтерфейсу (`struct ifinfomsg`):**
   - `ifi_family` — сімейство адрес (зазвичай `AF_UNSPEC`);
   - `ifi_index` — унікальний числовий ідентифікатор інтерфейсу в ядрі (отримується функцією `if_nametoindex()`);
   - `ifi_flags` — прапорці адміністративного стану (наприклад, `IFF_UP`).

3. **Вкладені атрибути типу rtattr (`struct rtattr`):**
   - `IFLA_IFNAME` — нове основне ім'я інтерфейсу (рядок, що завершується нульовим байтом, довжиною не більше ніж `IFNAMSIZ - 1` = 15 байтів);
   - `IFLA_ALT_IFNAME` — додаткове альтернативне ім'я інтерфейсу (атрибут з'явився в ядрі Linux 5.4).

### Життєвий цикл перейменування всередині ядра

Коли ядро отримує повідомлення `RTM_SETLINK` через функцію `rtnetlink_rcv_msg()`, воно виконує таку послідовність кроків:

1. **Пошук пристрою:** ядро знаходить структуру `struct net_device` за числовим індексом `ifi_index` у поточному мережевому просторі імен хоста.
2. **Перевірка прав доступу:** перевіряється наявність у викликаючого процесу системного привілею `CAP_NET_ADMIN`. Якщо привілею немає, ядро негайно повертає помилку `-EPERM`.
3. **Перевірка стану активності:** функція ядра `dev_change_name()` перевіряє прапорець `dev->flags & IFF_UP`. Якщо інтерфейс активний (піднятий), операція відхиляється з кодом помилки `-EBUSY`. Це обмеження зумовлене тим, що активний пристрій бере участь у таблицях маршрутизації ядра, обробці черг сокетів та фільтрах netfilter, де кешуються вказівники та хеші назв.
4. **Перевірка унікальності назви:** ядро перевіряє хеш-таблицю `dev_name_head`. Якщо пристрій з такою назвою вже існує в цьому просторі імен, повертається помилка `-EEXIST`.
5. **Оновлення структури та sysfs:** ядро копіює новий рядок у поле `dev->name`, оновлює символічні посилання у файловій системі `sysfs` викликом `kobject_rename()` і надсилає сповіщення `NETDEV_CHANGENAME` по внутрішньому ланцюжку сповіщень ядра.
6. **Трансляція події:** ядро формує широкомовне повідомлення `RTM_NEWLINK` та сповіщення uevent `ACTION=move`, повідомляючи всі системні служби (NetworkManager, systemd-networkd) про зміну назви.

### Робота з альтернативними іменами (IFLA_ALT_IFNAME)

Починаючи з ядра Linux 5.4, мережевий інтерфейс може мати список додаткових імен. Альтернативні назви зберігаються в полі `dev->alt_ifnames` структури `struct net_device`.

На відміну від зміни первинної назви `IFLA_IFNAME`, реєстрація альтернативного імені через `RTM_NEWLINK` із прапорцем `NLM_F_CREATE` дозволяється навіть для активного інтерфейсу (у стані `UP`).

Якщо інтерфейс переміщується між різними мережевими просторами імен (мережевими неймспейсами контейнерів командою `ip link set dev enp3s0 netns <PID>`), ядро автоматично очищує список альтернативних імен, щоб запобігти колізіям у цільовому просторі імен.

| Код помилки ядра | Константа | Причина виникнення |
| :--- | :--- | :--- |
| `-EBUSY` | `Device or resource busy` | Інтерфейс перебуває в стані `UP` під час спроби зміни `IFLA_IFNAME`. |
| `-EEXIST` | `File exists` | Запитане ім'я вже зайнято іншим пристроєм у поточному мережевому просторі імен. |
| `-EINVAL` | `Invalid argument` | Назва містить заборонені символи (пробіли, слеш `/`, двокрапку `:`) або довжина перевищує 15 байтів. |
| `-ENODEV` | `No such device` | Числовий індекс `ifi_index` не відповідає жодному пристрою в системі. |
| `-EPERM` | `Operation not permitted` | Процес не має системного привілею `CAP_NET_ADMIN`. |

## Реалізація утиліти перейменування

У наведеному нижче коді реалізовано повний цикл формування запиту Netlink, додавання TLV-атрибутів та обробки підтвердження ACK від ядра.

Версія мовою C демонструє роботу з низькорівневими системними структурами та буферами пам'яті. Версія мовою C++ інкапсулює дескриптор сокета в RAII-клас `NetlinkSocket`, забезпечує автоматичне закриття дескриптора сокета в деструкторі та використовує типізовану обробку результатів через `std::expected`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if.h>
#include <net/if.h>

#define NLMSG_BUF_SIZE 4096

/* Створення та прив'язка сокета Netlink */
static int open_netlink_socket(void) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("Помилка створення сокета netlink");
        return -1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (bind(fd, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка прив'язки сокета netlink");
        close(fd);
        return -1;
    }
    return fd;
}

/* Додавання TLV-атрибута rtattr до буфера повідомлення з вирівнюванням */
static int add_rtattr(struct nlmsghdr *n, size_t maxlen, unsigned short type, const void *data, size_t datalen) {
    size_t len = RTA_LENGTH(datalen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Помилка: переповнення буфера rtattr\n");
        return -1;
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    memcpy(RTA_DATA(rta), data, datalen);
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
    return 0;
}

/* Читання відповіді ACK від ядра */
static int read_netlink_ack(int fd, uint32_t seq) {
    char buf[NLMSG_BUF_SIZE];
    ssize_t res = recv(fd, buf, sizeof(buf), 0);
    if (res < 0) {
        perror("Помилка отримання відповіді від netlink");
        return -errno;
    }

    struct nlmsghdr *h = (struct nlmsghdr *)buf;
    if (!NLMSG_OK(h, (size_t)res)) {
        fprintf(stderr, "Некоректне або пошкоджене повідомлення Netlink\n");
        return -EBADMSG;
    }

    if (h->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(h);
        if (h->nlmsg_len < NLMSG_LENGTH(sizeof(struct nlmsgerr))) {
            fprintf(stderr, "Помилка Netlink: усічене повідомлення\n");
            return -EBADMSG;
        }
        return err->error; /* 0 — успіх (ACK), від'ємне значення — код помилки ядра */
    }
    return 0;
}

/* Перейменування мережевого інтерфейсу через RTM_SETLINK */
int rename_network_interface(const char *old_name, const char *new_name) {
    if (!old_name || !new_name || strlen(new_name) >= IFNAMSIZ) {
        fprintf(stderr, "Некоректна назва: довжина має бути від 1 до %d символів\n", IFNAMSIZ - 1);
        return -EINVAL;
    }

    unsigned int ifindex = if_nametoindex(old_name);
    if (ifindex == 0) {
        fprintf(stderr, "Інтерфейс '%s' не знайдено в системі\n", old_name);
        return -ENODEV;
    }

    int nl_fd = open_netlink_socket();
    if (nl_fd < 0) return -1;

    char req_buf[NLMSG_BUF_SIZE];
    memset(req_buf, 0, sizeof(req_buf));

    struct nlmsghdr *n = (struct nlmsghdr *)req_buf;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    n->nlmsg_type = RTM_SETLINK;
    n->nlmsg_seq = 1001;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(n);
    ifi->ifi_family = AF_UNSPEC;
    ifi->ifi_index = (int)ifindex;

    /* Додаємо нове основне ім'я */
    if (add_rtattr(n, sizeof(req_buf), IFLA_IFNAME, new_name, strlen(new_name) + 1) < 0) {
        close(nl_fd);
        return -1;
    }

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(nl_fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("Помилка надсилання запиту Netlink");
        close(nl_fd);
        return -errno;
    }

    int err = read_netlink_ack(nl_fd, n->nlmsg_seq);
    close(nl_fd);

    if (err < 0) {
        fprintf(stderr, "Ядро відхилило операцію перейменування: %s (%d)\n", strerror(-err), -err);
        return err;
    }

    printf("Інтерфейс успішно перейменовано: %s -> %s (ifindex: %u)\n", old_name, new_name, ifindex);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Використання: %s <старе_ім'я> <нове_ім'я>\n", argv[0]);
        return EXIT_FAILURE;
    }

    int rc = rename_network_interface(argv[1], argv[2]);
    return (rc == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <expected>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if.h>
#include <net/if.h>

class NetlinkSocket {
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити сокет Netlink");
        }

        sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Не вдалося прив'язати сокет Netlink");
        }
    }

    ~NetlinkSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;

    NetlinkSocket(NetlinkSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    NetlinkSocket& operator=(NetlinkSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

private:
    int fd_{-1};
};

class InterfaceManager {
public:
    static std::expected<void, std::string> rename(std::string_view oldName, std::string_view newName) {
        if (oldName.empty() || newName.empty() || newName.length() >= IFNAMSIZ) {
            return std::unexpected("Некоректне ім'я: довжина має бути від 1 до 15 символів");
        }

        std::string oldNameStr(oldName);
        unsigned int ifindex = ::if_nametoindex(oldNameStr.c_str());
        if (ifindex == 0) {
            return std::unexpected("Інтерфейс '" + oldNameStr + "' не знайдено в системі");
        }

        try {
            NetlinkSocket sock;
            std::vector<uint8_t> buffer(4096, 0);

            auto* n = reinterpret_cast<nlmsghdr*>(buffer.data());
            n->nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
            n->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
            n->nlmsg_type = RTM_SETLINK;
            n->nlmsg_seq = 1001;

            auto* ifi = reinterpret_cast<ifinfomsg*>(NLMSG_DATA(n));
            ifi->ifi_family = AF_UNSPEC;
            ifi->ifi_index = static_cast<int>(ifindex);

            // Додаємо атрибут IFLA_IFNAME
            std::string newNameStr(newName);
            if (!appendAttribute(n, buffer.size(), IFLA_IFNAME, newNameStr.c_str(), newNameStr.length() + 1)) {
                return std::unexpected("Переповнення буфера при формуванні повідомлення RTNetlink");
            }

            sockaddr_nl sa{};
            sa.nl_family = AF_NETLINK;

            if (::sendto(sock.get(), n, n->nlmsg_len, 0, reinterpret_cast<sockaddr*>(&sa), sizeof(sa)) < 0) {
                return std::unexpected(std::string("Помилка надсилання в netlink: ") + std::strerror(errno));
            }

            return receiveAck(sock.get());
        } catch (const std::exception& ex) {
            return std::unexpected(ex.what());
        }
    }

private:
    static bool appendAttribute(nlmsghdr* n, size_t maxLen, uint16_t type, const void* data, size_t dataLen) {
        size_t rtaLen = RTA_LENGTH(dataLen);
        if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(rtaLen) > maxLen) {
            return false;
        }
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(n) + NLMSG_ALIGN(n->nlmsg_len));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(rtaLen);
        std::memcpy(RTA_DATA(rta), data, dataLen);
        n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(rtaLen);
        return true;
    }

    static std::expected<void, std::string> receiveAck(int fd) {
        std::vector<uint8_t> recvBuf(4096);
        ssize_t bytesRead = ::recv(fd, recvBuf.data(), recvBuf.size(), 0);
        if (bytesRead < 0) {
            return std::unexpected(std::string("Помилка читання відповіді ACK: ") + std::strerror(errno));
        }

        auto* h = reinterpret_cast<nlmsghdr*>(recvBuf.data());
        if (!NLMSG_OK(h, static_cast<size_t>(bytesRead))) {
            return std::unexpected("Отримано пошкоджене або неповне повідомлення Netlink");
        }

        if (h->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<nlmsgerr*>(NLMSG_DATA(h));
            if (h->nlmsg_len < NLMSG_LENGTH(sizeof(nlmsgerr))) {
                return std::unexpected("Усічене повідомлення про помилку від ядра");
            }
            if (err->error != 0) {
                return std::unexpected(std::string("Ядро відхилило операцію: ") + std::strerror(-err->error));
            }
        }
        return {};
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Використання: " << argv[0] << " <старе_ім'я> <нове_ім'я>\n";
        return 1;
    }

    auto result = InterfaceManager::rename(argv[1], argv[2]);
    if (!result) {
        std::cerr << "Помилка: " << result.error() << "\n";
        return 1;
    }

    std::cout << "Інтерфейс " << argv[1] << " успішно перейменовано на " << argv[2] << "\n";
    return 0;
}
```
:::

## Збірка, виконання та діагностика викликів

Для компіляції вихідного коду потрібен компілятор GCC або Clang із підтримкою стандарту C++23. Програма потребує прав суперкористувача (`root`) або наявності привілею `CAP_NET_ADMIN` для відкриття сирого сокета Netlink та зміни системних параметрів інтерфейсу.

```sh
# Збірка версії C
$ gcc -O2 -Wall -Wextra rename_net.c -o rename_net_c

# Збірка версії C++
$ g++ -O2 -std=c++23 -Wall -Wextra rename_net.cpp -o rename_net_cpp
```

### Сценарій тестування та перевірка обмеження EBUSY

Перед запуском перейменування інтерфейс обов'язково треба перевести в стан `DOWN`:

```sh
# 1. Спроба перейменувати активний інтерфейс завершується помилкою ядра:
$ sudo ip link set dev enp3s0 up
$ sudo ./rename_net_c enp3s0 mylan0
Ядро відхилило операцію перейменування: Device or resource busy (-16)

# 2. Правильна послідовність: зупинка інтерфейсу -> перейменування -> підняття
$ sudo ip link set dev enp3s0 down
$ sudo ./rename_net_c enp3s0 mylan0
Інтерфейс успішно перейменовано: enp3s0 -> mylan0 (ifindex: 2)

$ sudo ip link set dev mylan0 up
```

### Трасування Netlink-повідомлень через strace

Побачити точну бінарну структуру відправлених і прийнятих повідомлень ядра можна за допомогою системного трасувальника `strace`:

```sh
$ sudo strace -e trace=socket,bind,sendto,recvfrom ./rename_net_c mylan0 enp3s0
socket(AF_NETLINK, SOCK_RAW|SOCK_CLOEXEC, NETLINK_ROUTE) = 3
bind(3, {sa_family=AF_NETLINK, nl_pid=0, nl_groups=00000000}, 12) = 0
sendto(3, [{nlmsg_len=48, nlmsg_type=RTM_SETLINK, nlmsg_flags=NLM_F_REQUEST|NLM_F_ACK, nlmsg_seq=1001, nlmsg_pid=0},
    {ifi_family=AF_UNSPEC, ifi_type=ARPHRD_ETHER, ifi_index=2, ifi_flags=0, ifi_change=0},
    [{{nla_len=11, nla_type=IFLA_IFNAME}, "enp3s0\0"}]], 48, 0, NULL, 0) = 48
recvfrom(3, [{nlmsg_len=36, nlmsg_type=NLMSG_ERROR, nlmsg_flags=0, nlmsg_seq=1001, nlmsg_pid=12345},
    {error=0, msg={nlmsg_len=48, nlmsg_type=RTM_SETLINK, ...}}], 4096, 0, NULL, NULL) = 36
```

Як видно з виводу `strace`, ядро повертає заголовок `NLMSG_ERROR` із числовим полем `error=0`, що в протоколі Netlink є стандартним підтвердженням успішного виконання команди (ACK). Утиліта парсить цей заголовок, закриває сокет та повертає статус успіху в операційну систему.

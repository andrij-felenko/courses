# ⚙️ Програмне створення мережевих просторів та veth-пар

Програмне створення та налаштування пар віртуальних інтерфейсів Virtual Ethernet (`veth`) у поєднанні з ізольованими мережевими просторами імен вимагає прямої взаємодії з ядром Linux через системні виклики та бінарний протокол RtNetlink. Низькорівневий механізм полягає в атомарному створенні з'єднаної пари пристроїв, переміщенні одного кінця в цільовий простір, ініціалізації IP-адрес і переведенні інтерфейсів у робочий стан.

---

## 1. Архітектурне завдання та низькорівневі механізми ядра

Для створення та конфігурації ізольованої мережевої топології у користувацькому просторі (userspace) без використання сторонніх утиліт (типу `ip netns` або `ip link`) програма має реалізувати послідовну взаємодію з підсистемами ядра VFS, Nsproxy та Netlink.

Повна послідовність кроків складається з таких етапів:

1. **Збереження початкового контексту мережі:** Відкриття файлового дескриптора `/proc/self/ns/net`. Це необхідно для того, щоб потік виконання мав змогу повернутися у вихідний мережевий простір хоста після створення нового: `veth`-пару треба створювати саме з боку хоста, бо один її кінець там і залишається.
2. **Створення нового мережевого простору:** Виклик системного виклику `unshare(CLONE_NEWNET)`. Ядро виділяє нову структуру `struct net`, ініціалізує порожні таблиці маршрутизації FIB, створює вимкнений інтерфейс `loopback` (`lo`) та підключає новий простір до поточного процесу.
3. **Закріплення простору у VFS (Bind Mount):** Створення файла у каталозі `/var/run/netns/demo_ns` та виконання системного виклику `mount(..., MS_BIND)`. Це збільшує лічильник посилань `net->count`, гарантуючи, що простір не зникне після завершення поточного процесу чи потоку.
4. **Повернення у початковий простір:** Виклик `setns(orig_ns_fd, CLONE_NEWNET)`, щоб повернути потік виконання у мережевий простір хоста, де будуть створюватися віртуальні інтерфейси.
5. **Ініціалізація Netlink сокета:** Відкриття сокета `socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE)` для спілкування з мережевою підсистемою ядра.
6. **Формування бінарного повідомлення `RTM_NEWLINK`:** Складання заголовка `nlmsghdr`, структури `ifinfomsg` та вкладених атрибутів `rtattr`:
   - `IFLA_IFNAME`: Назва хостового кінця `veth`-пари (наприклад, `veth-host`).
   - `IFLA_LINKINFO` -> `IFLA_INFO_KIND`: Рядок `"veth"`.
   - `IFLA_INFO_DATA` -> `VETH_INFO_PEER`: Вкладена структура опису другого кінця, де задається його ім'я (`veth-ns`) та атрибут `IFLA_NET_NS_FD` із дескриптором нового простору.
7. **Атомарне переміщення та створення:** Надсилання повідомлення через `sendto()`. Драйвер `veth.c` у ядрі створює обидва кінці та атомарно поміщає `veth-ns` у новий мережевий простір.
8. **Програмна конфігурація IP та підняття інтерфейсів:** Відправка додаткових Netlink-повідомлень `RTM_NEWADDR` для призначення IP-адрес та `RTM_NEWLINK` із прапорцем `IFF_UP` для переведення `lo`, `veth-host` та `veth-ns` у робочий стан.

---

## 2. Історичні альтернативи: ioctl проти Netlink

Історично у ранніх версіях ядра Linux 2.4/2.6 управління мережевими пристроями виконувалося через сокетні виклики `ioctl(fd, SIOCSIFADDR, ...)` та `ioctl(fd, SIOCSIFFLAGS, ...)`. Проте підхід із `ioctl` має суттєві обмеження:

* **Відсутність атомарності:** Налаштування кожної IP-адреси, маски та прапорця вимагає окремого системного виклику.
* **Обмеженість передачі даних:** Поля структури `ifreq` мають фіксований розмір (наприклад, ім'я інтерфейсу обмежене 16 байтами `IFNAMSIZ`).
* **Неможливість створення складних віртуальних пристроїв:** Створення `veth`-пари із зазначенням цільового простору імен через `ioctl` непідтримуване.

Сучасні системи повністю перейшли на сокети `AF_NETLINK` з протоколом `NETLINK_ROUTE`. Netlink є розширюваним бінарним протоколом типу "запит-відповідь", у якому повідомлення містять набір довільних вкладених атрибутів (TLV — Type-Length-Value). Це дозволяє передати одним викликом `sendto()` ціле дерево вкладених атрибутів — зокрема опис обох кінців `veth`-пари разом із цільовим простором для одного з них.

---

## 3. Детальна реалізація мовами C та C++

Нижче наведено дві повністю функціональні реалізації даної задачі. У версії для мови C використовується класичний підхід із низькорівневим формуванням Netlink-пакетів та викликами POSIX. У версії C++20 використано сучасні ідіоми: RAII-обгортки для управління файловими та сокетними дескрипторами (`ScopedFd`), безпечні типи `std::span` та `std::string_view`, сильні гарантії винятків та відсутність ручного управління пам'яттю чи операторів `goto`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <sched.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <linux/rtnetlink.h>
#include <net/if.h>

#define NETNS_PATH "/var/run/netns/demo_c_ns"

/* Структура запиту Netlink для створення veth-пари */
struct veth_req {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
    char buf[1024];
};

static int create_veth_pair(int netlink_fd, const char *veth_host, const char *veth_ns, int target_ns_fd) {
    struct veth_req req;
    memset(&req, 0, sizeof(req));

    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWLINK;
    req.ifm.ifi_family = AF_UNSPEC;

    /* Додавання IFLA_IFNAME для хостового кінця */
    struct rtattr *rta = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    rta->rta_type = IFLA_IFNAME;
    rta->rta_len = RTA_LENGTH(strlen(veth_host) + 1);
    strcpy(RTA_DATA(rta), veth_host);
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);

    /* Додавання IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    linkinfo->rta_type = IFLA_LINKINFO;
    linkinfo->rta_len = RTA_LENGTH(0);

    /* IFLA_INFO_KIND -> "veth" */
    struct rtattr *kind = (struct rtattr *)(((char *)linkinfo) + RTA_LENGTH(0));
    kind->rta_type = IFLA_INFO_KIND;
    kind->rta_len = RTA_LENGTH(5);
    strcpy(RTA_DATA(kind), "veth");
    linkinfo->rta_len += RTA_ALIGN(kind->rta_len);

    /* IFLA_INFO_DATA для налаштування peer */
    struct rtattr *data = (struct rtattr *)(((char *)kind) + RTA_ALIGN(kind->rta_len));
    data->rta_type = IFLA_INFO_DATA;
    data->rta_len = RTA_LENGTH(0);

    /* VETH_INFO_PEER Header */
    struct rtattr *peer = (struct rtattr *)(((char *)data) + RTA_LENGTH(0));
    peer->rta_type = 1; /* VETH_INFO_PEER */
    peer->rta_len = RTA_LENGTH(sizeof(struct ifinfomsg));
    
    struct ifinfomsg *peer_ifm = (struct ifinfomsg *)RTA_DATA(peer);
    memset(peer_ifm, 0, sizeof(*peer_ifm));
    peer_ifm->ifi_family = AF_UNSPEC;

    /* Peer IFLA_IFNAME */
    struct rtattr *peer_name = (struct rtattr *)(((char *)peer) + RTA_LENGTH(sizeof(struct ifinfomsg)));
    peer_name->rta_type = IFLA_IFNAME;
    peer_name->rta_len = RTA_LENGTH(strlen(veth_ns) + 1);
    strcpy(RTA_DATA(peer_name), veth_ns);
    peer->rta_len += RTA_ALIGN(peer_name->rta_len);

    /* Peer IFLA_NET_NS_FD - відразу поміщаємо peer у цільовий netns */
    struct rtattr *peer_ns = (struct rtattr *)(((char *)peer_name) + RTA_ALIGN(peer_name->rta_len));
    peer_ns->rta_type = IFLA_NET_NS_FD;
    peer_ns->rta_len = RTA_LENGTH(sizeof(int));
    *(int *)RTA_DATA(peer_ns) = target_ns_fd;
    peer->rta_len += RTA_ALIGN(peer_ns->rta_len);

    data->rta_len += RTA_ALIGN(peer->rta_len);
    linkinfo->rta_len += RTA_ALIGN(data->rta_len);
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(linkinfo->rta_len);

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(netlink_fd, &req, req.nlh.nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(rtnetlink)");
        return -1;
    }
    return 0;
}

int main(void) {
    int orig_ns_fd = open("/proc/self/ns/net", O_RDONLY);
    if (orig_ns_fd < 0) {
        perror("open(orig_ns)");
        return 1;
    }

    mkdir("/var/run/netns", 0755);
    int touch_fd = open(NETNS_PATH, O_CREAT | O_RDWR | O_EXCL, 0644);
    if (touch_fd >= 0) close(touch_fd);

    if (unshare(CLONE_NEWNET) != 0) {
        perror("unshare(CLONE_NEWNET)");
        close(orig_ns_fd);
        return 1;
    }

    if (mount("/proc/self/ns/net", NETNS_PATH, NULL, MS_BIND, NULL) != 0) {
        perror("mount bind netns");
    }

    int new_ns_fd = open(NETNS_PATH, O_RDONLY);

    /* Повертаємося в початковий простір для створення veth-пари.
       Без цієї перевірки програма мовчки лишилася б у новому просторі
       і створила б обидва кінці пари не там, де треба. */
    if (setns(orig_ns_fd, CLONE_NEWNET) != 0) {
        perror("setns(orig_ns)");
        if (new_ns_fd >= 0) close(new_ns_fd);
        close(orig_ns_fd);
        return 1;
    }

    int nl_fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (nl_fd >= 0 && new_ns_fd >= 0) {
        if (create_veth_pair(nl_fd, "veth-host", "veth-ns", new_ns_fd) == 0) {
            /* Запит надіслано; чи справді пара створена, покаже
               NLMSG_ERROR-відповідь ядра — розбір див. у §5 */
            printf("Запит на створення veth-пари надіслано (netns '%s')\n", NETNS_PATH);
        }
        close(nl_fd);
    }

    if (new_ns_fd >= 0) close(new_ns_fd);
    close(orig_ns_fd);
    return 0;
}
```
```cpp
#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <memory>
#include <span>
#include <string>
#include <string_view>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>
#include <sched.h>
#include <sys/socket.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <linux/rtnetlink.h>
#include <linux/veth.h>
#include <net/if.h>

namespace netns {

// RAII обгортка для безпечного управління файловими дескрипторами
class ScopedFd {
    int fd_{-1};
public:
    explicit ScopedFd(int fd = -1) noexcept : fd_(fd) {}
    ~ScopedFd() { reset(); }

    ScopedFd(const ScopedFd&) = delete;
    ScopedFd& operator=(const ScopedFd&) = delete;

    ScopedFd(ScopedFd&& other) noexcept : fd_(other.release()) {}
    ScopedFd& operator=(ScopedFd&& other) noexcept {
        if (this != &other) {
            reset(other.release());
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

    int release() noexcept {
        int temp = fd_;
        fd_ = -1;
        return temp;
    }

    void reset(int new_fd = -1) noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
        fd_ = new_fd;
    }
};

class NetnsManager {
    static constexpr std::string_view kNetnsPath = "/var/run/netns/demo_cpp_ns";

public:
    static void setup_isolated_veth(std::string_view host_if, std::string_view ns_if) {
        ScopedFd orig_netns{::open("/proc/self/ns/net", O_RDONLY | O_CLOEXEC)};
        if (!orig_netns.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити /proc/self/ns/net");
        }

        ::mkdir("/var/run/netns", 0755);
        ScopedFd touch_fd{::open(kNetnsPath.data(), O_CREAT | O_RDWR | O_EXCL | O_CLOEXEC, 0644)};

        if (::unshare(CLONE_NEWNET) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка unshare(CLONE_NEWNET)");
        }

        if (::mount("/proc/self/ns/net", kNetnsPath.data(), nullptr, MS_BIND, nullptr) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка bind mount netns");
        }

        ScopedFd target_netns{::open(kNetnsPath.data(), O_RDONLY | O_CLOEXEC)};
        if (!target_netns.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити створений netns");
        }

        // Повернення контексту до початкового мережевого простору
        if (::setns(orig_netns.get(), CLONE_NEWNET) != 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка повернення setns()");
        }

        ScopedFd nl_socket{::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE)};
        if (!nl_socket.valid()) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відкрити Netlink сокет");
        }

        send_rtnetlink_veth_create(nl_socket.get(), host_if, ns_if, target_netns.get());
        std::cout << "[C++ RAII] Створено простір " << kNetnsPath
                  << ", надіслано запит на пару " << host_if << " <-> " << ns_if
                  << " (підтвердження ядра розбирається у §5)\n";
    }

private:
    static void send_rtnetlink_veth_create(int socket_fd, std::string_view host_if, 
                                           std::string_view ns_if, int target_ns_fd) {
        std::array<char, 1024> buffer{};
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer.data());

        nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
        nlh->nlmsg_type = RTM_NEWLINK;

        auto append_attr = [&](uint16_t type, std::span<const char> data, size_t base_offset) -> size_t {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + base_offset);
            rta->rta_type = type;
            rta->rta_len = RTA_LENGTH(data.size());
            std::copy(data.begin(), data.end(), static_cast<char*>(RTA_DATA(rta)));
            return RTA_ALIGN(rta->rta_len);
        };
        // Рядок кладеться разом із термінальним нулем; std::string дає власний
        // буфер, тож span не виходить за межі чужої пам'яті (на відміну від
        // string_view, у якого нуля за кінцем може й не бути)
        auto append_str = [&](uint16_t type, std::string_view value, size_t base_offset) -> size_t {
            const std::string owned{value};
            return append_attr(type, {owned.c_str(), owned.size() + 1}, base_offset);
        };
        // Заголовок вкладеного атрибута: довжину допишемо, коли буде відомий вміст
        auto open_nested = [&](uint16_t type, size_t base_offset) -> size_t {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + base_offset);
            rta->rta_type = type;
            rta->rta_len = RTA_LENGTH(0);
            return base_offset;
        };
        auto close_nested = [&](size_t nested_offset, size_t end_offset) {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer.data() + nested_offset);
            rta->rta_len = static_cast<unsigned short>(end_offset - nested_offset);
        };

        size_t offset = nlh->nlmsg_len;

        // IFLA_IFNAME — ім'я хостового кінця пари
        offset += append_str(IFLA_IFNAME, host_if, offset);

        // IFLA_LINKINFO { INFO_KIND="veth", INFO_DATA { VETH_INFO_PEER {…} } }
        const size_t linkinfo = open_nested(IFLA_LINKINFO, offset);
        offset += RTA_LENGTH(0);
        offset += append_str(IFLA_INFO_KIND, "veth", offset);

        const size_t info_data = open_nested(IFLA_INFO_DATA, offset);
        offset += RTA_LENGTH(0);

        const size_t peer = open_nested(VETH_INFO_PEER, offset);
        offset += RTA_LENGTH(sizeof(struct ifinfomsg));   // нульовий ifinfomsg парного кінця
        offset += append_str(IFLA_IFNAME, ns_if, offset);
        // Дескриптор цільового простору: peer народжується вже всередині нього
        const auto ns_fd_bytes = std::bit_cast<std::array<char, sizeof(int)>>(target_ns_fd);
        offset += append_attr(IFLA_NET_NS_FD, ns_fd_bytes, offset);

        close_nested(peer, offset);
        close_nested(info_data, offset);
        close_nested(linkinfo, offset);
        nlh->nlmsg_len = static_cast<std::uint32_t>(offset);

        // Відправка запиту у ядро
        sockaddr_nl sa{.nl_family = AF_NETLINK};
        if (::sendto(socket_fd, buffer.data(), nlh->nlmsg_len, 0, 
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося відправити Netlink повідомлення");
        }
    }
};

} // namespace netns

int main() {
    try {
        netns::NetnsManager::setup_isolated_veth("veth-host-cpp", "veth-ns-cpp");
    } catch (const std::exception& ex) {
        std::cerr << "Помилка виконання: " << ex.what() << '\n';
        return 1;
    }
    return 0;
}
```
:::

---

## 4. Програмна конфігурація IP-адрес та стану пристроїв

Після створення `veth`-пари інтерфейси за замовчуванням перебувають у стані `DOWN` та не мають призначених IP-адрес. Для їх повної конфігурації у C/C++ відправляються додаткові Netlink-повідомлення.

### 4.1. Призначення IP-адреси через `RTM_NEWADDR`

Для призначення IPv4-адреси (наприклад, `10.0.0.1/24`) на інтерфейс використовується повідомлення `RTM_NEWADDR` зі структурою `struct ifaddrmsg`:

:::tabs
```c
struct {
    struct nlmsghdr nlh;
    struct ifaddrmsg ifa;
    char buf[256];
} req;

req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifaddrmsg));
req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
req.nlh.nlmsg_type = RTM_NEWADDR;

req.ifa.ifa_family = AF_INET;
req.ifa.ifa_prefixlen = 24; // Маска /24
req.ifa.ifa_flags = IFA_F_PERMANENT;
req.ifa.ifa_scope = RT_SCOPE_UNIVERSE;
req.ifa.ifa_index = if_nametoindex("veth-host");

/* Самої ifaddrmsg не досить: адреса передається окремим атрибутом IFA_LOCAL
   у мережевому порядку байтів, інакше ядро відповість EINVAL */
struct rtattr *rta = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
rta->rta_type = IFA_LOCAL;
rta->rta_len = RTA_LENGTH(sizeof(struct in_addr));
inet_pton(AF_INET, "10.0.0.1", RTA_DATA(rta));
req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
```
```cpp
struct alignas(NLMSG_ALIGNTO) IpAddrRequest {
    nlmsghdr nlh{};
    ifaddrmsg ifa{};
    std::array<char, 256> buf{};
};

IpAddrRequest req{};
req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifaddrmsg));
req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
req.nlh.nlmsg_type = RTM_NEWADDR;

req.ifa.ifa_family = AF_INET;
req.ifa.ifa_prefixlen = 24;
req.ifa.ifa_flags = IFA_F_PERMANENT;
req.ifa.ifa_scope = RT_SCOPE_UNIVERSE;
req.ifa.ifa_index = ::if_nametoindex("veth-host");

// Сама адреса — окремим атрибутом IFA_LOCAL
auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&req) + req.nlh.nlmsg_len);
rta->rta_type = IFA_LOCAL;
rta->rta_len = RTA_LENGTH(sizeof(in_addr));
::inet_pton(AF_INET, "10.0.0.1", RTA_DATA(rta));
req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
```
:::

### 4.2. Переведення пристрою у стан UP через `RTM_NEWLINK`

Щоб перевести інтерфейс у стан `UP` (активний), відправляється повідомлення `RTM_NEWLINK` із вказуванням прапорців у `struct ifinfomsg`:

:::tabs
```c
struct ifinfomsg ifm;
memset(&ifm, 0, sizeof(ifm));
ifm.ifi_family = AF_UNSPEC;
ifm.ifi_index = if_nametoindex("veth-host");
ifm.ifi_flags = IFF_UP;
ifm.ifi_change = IFF_UP; // Вказує ядру, який саме прапорець модифікується
```
```cpp
ifinfomsg ifm{};
ifm.ifi_family = AF_UNSPEC;
ifm.ifi_index = ::if_nametoindex("veth-host");
ifm.ifi_flags = IFF_UP;
ifm.ifi_change = IFF_UP;
```
:::

---

## 5. Аналіз результатів підтвердження від ядра (Netlink ACK)

Під час надсилання прапорця `NLM_F_ACK` у повідомленні `RTM_NEWLINK` ядро зобов'язане надіслати у відповідь пакет типу `NLMSG_ERROR`.

Структура відповіді розшифровується так:
1. Якщо поле `error` у структурі `struct nlmsgerr` дорівнює `0`, це означає, що запит виконано успішно (атомарна підтверджувальна відповідь).
2. Якщо поле `error` містить від'ємне значення (наприклад, `-EEXIST` або `-EPERM`), це вказує на точну причину невдачі (наприклад, інтерфейс із таким ім'ям вже існує або відсутні необхідні привілеї).

Приклад обробки відповіді від ядра у C/C++:

:::tabs
```c
struct {
    struct nlmsghdr nlh;
    struct nlmsgerr err;
} ack_res;

ssize_t n = recv(nl_fd, &ack_res, sizeof(ack_res), 0);

/* Тип повідомлення перевіряємо ПЕРЕД читанням поля error: у відповідь
   може прийти й дамп (RTM_NEWLINK), і тоді на місці err лежать чужі байти */
if (n >= (ssize_t)sizeof(ack_res) && ack_res.nlh.nlmsg_type == NLMSG_ERROR
    && ack_res.err.error != 0) {
    fprintf(stderr, "Помилка ядра Netlink: %s\n", strerror(-ack_res.err.error));
}
```
```cpp
#include <iostream>
#include <system_error>

struct AckResponse {
    nlmsghdr nlh;
    nlmsgerr err;
} ack_res{};

const auto received = ::recv(nl_fd, &ack_res, sizeof(ack_res), 0);
if (received >= static_cast<ssize_t>(sizeof(ack_res))
    && ack_res.nlh.nlmsg_type == NLMSG_ERROR && ack_res.err.error != 0) {
    std::cerr << "Помилка ядра Netlink: " 
              << std::system_category().message(-ack_res.err.error) << '\n';
}
```
:::

---

## 6. Програмне видалення veth-пари та очищення просторів імен (`RTM_DELLINK`)

Для програмного видалення створеної топології використовується Netlink-повідомлення `RTM_DELLINK`:

:::tabs
```c
struct {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
} del_req;

memset(&del_req, 0, sizeof(del_req));
del_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
del_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
del_req.nlh.nlmsg_type = RTM_DELLINK;
del_req.ifm.ifi_index = if_nametoindex("veth-host");

sendto(nl_fd, &del_req, del_req.nlh.nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa));
```
```cpp
struct DelLinkRequest {
    nlmsghdr nlh{};
    ifinfomsg ifm{};
} del_req{};

del_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
del_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
del_req.nlh.nlmsg_type = RTM_DELLINK;
del_req.ifm.ifi_index = ::if_nametoindex("veth-host");

sockaddr_nl sa{.nl_family = AF_NETLINK};
::sendto(nl_fd, &del_req, del_req.nlh.nlmsg_len, 0, reinterpret_cast<sockaddr*>(&sa), sizeof(sa));
```
:::

Зауважте: оскільки `veth` працює як нерозривна пара пристроїв, видалення одного кінця (`veth-host`) автоматично призводить до того, що ядро знищує парний кінець (`veth-ns`) у цільовому мережевому просторі імен.

---

## 7. Критичні нюанси, багатониточність та пастки реалізації

### 7.1. Права доступу та Capabilities
Виконання системних викликів `unshare(CLONE_NEWNET)` та `setns()` вимагає `CAP_SYS_ADMIN` у діючому User Namespace; `CAP_NET_ADMIN` потрібен окремо — уже для створення `veth`-пари та налаштування адрес через Netlink. 

Якщо програма працює у невідокремленому середовищі звичайного користувача, виклики повернуть помилку `EPERM` (Permission denied). Для запуску програми без root-прав її необхідно або обгорнути у новий User Namespace (`CLONE_NEWUSER | CLONE_NEWNET`), або надати виконуваному файлу файлові привілеї через `setcap cap_net_admin,cap_sys_admin+ep ./app`.

### 7.2. Конфлікти багатониточності (POSIX Threads та setns)
Системний виклик `setns()` змінює мережевий простір для конкретного потоку (`task_struct`), а не для всього процесу. Це не помилка, а модель: `nsproxy` належить потокові.

Звідси головна пастка багатониточних програм: після вдалого `setns()` в одному потоці решта потоків залишаються у старому просторі, і сокет, відкритий випадковим робітником з пулу, опиниться не там, де очікує програміст. Особливо болісно це у середовищах із власним планувальником (як-от goroutine у Go), де код без явного закріплення може продовжитися вже на іншому потоці — саме тому такі рантайми примусово «прив'язують» потік на час роботи в чужому просторі.

Практичні наслідки:
* Мережеві простори створюють і перемикають **до** першого `pthread_create()`, поки процес однопотоковий, — або виносять роботу в окремий службовий потік, який більше нічого не робить.
* Для просторів користувачів обмеження жорсткіше: `setns()` із `CLONE_NEWUSER` (а також `unshare(CLONE_NEWUSER)`) у багатониточному процесі відхиляється з `EINVAL`, тож rootless-сценарії з §16 треба розгортати на самому старті програми.

### 7.3. Вирівнювання байтів у Netlink-пакетах (Alignment)
Під час виклику Netlink API вкрай важливо дотримуватися вирівнювання на межу 4 байтів. Макроси ядра `NLMSG_ALIGN()`, `NLMSG_LENGTH()`, `RTA_ALIGN()` та `RTA_LENGTH()` обов'язкові до використання:
* `NLMSG_ALIGN(len)` округлює довжину заголовка повідомлення до кратного 4 байтам.
* `RTA_ALIGN(len)` округлює довжину атрибута `rtattr` до кратного 4 байтам.

Ігнорування вирівнювання призводить до того, що ядро повертає помилку `EINVAL` (Invalid argument) під час парсингу атрибутів повідомлення.

### 7.4. Перевага `IFLA_NET_NS_FD` над послідовним `ip link set`
Створення `veth`-пари з відразу вказаним атрибутом `IFLA_NET_NS_FD` є істотно швидшим та безпечнішим за алгоритм із двох кроків (створити на хості -> перемістити в netns):
1. **Атомарність:** Ядро створює периферійний інтерфейс відразу у цільовому просторі імен.
2. **Відсутність змагань (Race Conditions):** Відсутній проміжок часу, протягом якого інтерфейс `veth-ns` бачився б системними демонами хоста (типу NetworkManager або `systemd-networkd`), що виключає спроби автоматичного конфігурування або перейменування пристрою правилами хоста.

---

## 8. Таблиця типових помилок Netlink та шляхи їх розв'язання

| Помилка Netlink | Причина виникнення | Спосіб розв'язання та профілактика |
| :--- | :--- | :--- |
| `-EEXIST` (`17`) | Інтерфейс із вказаним `IFLA_IFNAME` вже існує в системі. | Видалити наявний пристрій через `RTM_DELLINK` або обрати інше ім'я. |
| `-EPERM` (`1`) | Процес не має `CAP_NET_ADMIN` у даному User Namespace. | Запустити програму від імені root або надати `setcap cap_net_admin+ep`. |
| `-EINVAL` (`22`) | Передано некоректну довжину атрибута або порушено 32-бітне вирівнювання RTA_ALIGN. | Перевірити використання макросів `RTA_ALIGN` та `NLMSG_ALIGN`. |
| `-ENODEV` (`19`) | Вказано неіснуючий `ifindex` при спробі конфігурування IP чи прапорців. | Викликати `if_nametoindex()` після підтвердження створення пристрою. |
| `-EBADF` (`9`) | Файловий дескриптор у `IFLA_NET_NS_FD` є закритим або не вказує на `nsfs`. | Перевірити виклик `open("/proc/self/ns/net")` та порядок закриття дескрипторів. |

---

## 9. Порівняльний аналіз швидкодії: Direct Netlink C/C++ проти утиліт shell

При створенні та конфігурації тисяч мережевих просторів імен (наприклад, під час ініціалізації великого вузла Kubernetes або запусках тисяч мікросервісів у Podman) запуск зовнішніх процесів `/sbin/ip` генерує колосальні накладні витрати:

1. **Fork/Exec overhead:** Кожен запуск утиліти `ip netns add` вимагає викликів ядра `fork()`, `execve()`, завантаження динамічних бібліотек `libc.so` та парсингу текстових аргументів командного рядка.
2. **Пряме C/C++ Netlink API:** Той самий результат в одному довготривалому процесі коштує двох системних викликів. Порядки такі: Netlink-запит — десятки мікросекунд, запуск зовнішньої утиліти — одиниці мілісекунд, тобто виграш приблизно на два порядки. Точні числа залежать від машини та ядра, але саме різниця порядків і робить прямий Netlink обов'язковим для CNI-плагінів, які створюють сотні просторів під час старту вузла.

---

## 10. Детальний розбір C++20 коду, RAII концепції ScopedFd та обробки винятків

У реалізації C++20 ключовим елементом надійності є клас `ScopedFd`. Він реалізує ідіому RAII (Resource Acquisition Is Initialization), гарантуючи, що системні файлові дескриптори будуть закриті за будь-якого шляху виходу з функції, включно з виникненням винятків (`std::system_error`).

### Переваги RAII шаблону для дескрипторів:
* Запобігання витокам файлових дескрипторів (File Descriptor Leaks).
* Відсутність необхідності розставляти оператори `close()` або `goto cleanup` у кожній гілці перевірки помилок.
* Використання `O_CLOEXEC` у викликах `open()` та `socket()` виключає виток дескриптора у дочірні процеси під час виклику `execve()`.

---

## 11. Програмне додавання маршрутів через Netlink RTM_NEWROUTE у C++20

Після створення пристрою та надання IP-адреси програма може вказати маршрут за замовчуванням (Default Gateway) через повідомлення `RTM_NEWROUTE`:

:::tabs
```c
struct rtmsg_req {
    struct nlmsghdr nlh;
    struct rtmsg rtm;
    char buf[256];
};

void add_default_gateway(int nl_fd, const char *gw_ip, int if_index) {
    struct rtmsg_req req;
    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct rtmsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWROUTE;

    req.rtm.rtm_family = AF_INET;
    req.rtm.rtm_table = RT_TABLE_MAIN;
    req.rtm.rtm_protocol = RTPROT_STATIC;
    req.rtm.rtm_scope = RT_SCOPE_UNIVERSE;
    req.rtm.rtm_type = RTN_UNICAST;
    req.rtm.rtm_dst_len = 0;   /* 0.0.0.0/0 — маршрут за замовчуванням */

    /* Куди слати (RTA_GATEWAY) і через який пристрій (RTA_OIF) */
    struct rtattr *gw = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    gw->rta_type = RTA_GATEWAY;
    gw->rta_len = RTA_LENGTH(sizeof(struct in_addr));
    inet_pton(AF_INET, gw_ip, RTA_DATA(gw));
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(gw->rta_len);

    struct rtattr *oif = (struct rtattr *)(((char *)&req) + req.nlh.nlmsg_len);
    oif->rta_type = RTA_OIF;
    oif->rta_len = RTA_LENGTH(sizeof(int));
    *(int *)RTA_DATA(oif) = if_index;
    req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(oif->rta_len);

    send(nl_fd, &req, req.nlh.nlmsg_len, 0);
}
```
```cpp
struct RtMsgRequest {
    nlmsghdr nlh{};
    rtmsg rtm{};
    std::array<char, 256> buf{};
};

void add_default_gateway(int nl_fd, const std::string& gw_ip, int if_index) {
    RtMsgRequest req{};
    req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(rtmsg));
    req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    req.nlh.nlmsg_type = RTM_NEWROUTE;

    req.rtm.rtm_family = AF_INET;
    req.rtm.rtm_table = RT_TABLE_MAIN;
    req.rtm.rtm_protocol = RTPROT_STATIC;
    req.rtm.rtm_scope = RT_SCOPE_UNIVERSE;
    req.rtm.rtm_type = RTN_UNICAST;
    req.rtm.rtm_dst_len = 0;   // 0.0.0.0/0

    auto put = [&](unsigned short type, const void* src, std::size_t len) {
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&req) + req.nlh.nlmsg_len);
        rta->rta_type = type;
        rta->rta_len = RTA_LENGTH(len);
        std::memcpy(RTA_DATA(rta), src, len);
        req.nlh.nlmsg_len = NLMSG_ALIGN(req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
    };

    in_addr gw{};
    if (::inet_pton(AF_INET, gw_ip.c_str(), &gw) != 1) {
        throw std::invalid_argument{"некоректна адреса шлюзу: " + gw_ip};
    }
    put(RTA_GATEWAY, &gw, sizeof(gw));
    put(RTA_OIF, &if_index, sizeof(if_index));

    if (::send(nl_fd, &req, req.nlh.nlmsg_len, 0) < 0) {
        throw std::system_error(errno, std::generic_category(), "RTM_NEWROUTE");
    }
}
```
:::

Такий C++20 модуль дозволяє побудувати повноцінний CNI-плагін, жодного разу не запускаючи зовнішніх shell-утиліт.

---

## 12. Очищення ресурсів у C/C++ та обробка сигналів завершення (SIGINT, SIGTERM)

Виробничі мережеві демони (наприклад, CNI-плагіни або контейнерні рушії) зобов'язані коректно обробляти сигнали завершення роботи для відсутності "висячих" пристроїв та bind mount файлів.

Алгоритм коректного виходу при отриманні `SIGINT` / `SIGTERM` (сам обробник лише виставляє прапорець — `umount2()`, `unlink()` і Netlink не є async-signal-safe, тож кроки 2–5 виконує основний цикл, побачивши цей прапорець):
1. Реєстрація системного обробника через `sigaction()`.
2. Виклик `umount2("/var/run/netns/demo_ns", MNT_DETACH)` для від'єднання файлового вузла простору.
3. Видалення файла точки монтування через `unlink("/var/run/netns/demo_ns")`.
4. Видалення хостового кінця `veth`-пари через `RTM_DELLINK`, що атомарно знищує парний пристрій.
5. Закриття всіх відкритих сокетів Netlink.

---

## 13. Деталізація розміщення атрибутів veth-пакети у байтовому буфері

При побудові бінарного Netlink пакета `RTM_NEWLINK` для veth-пари буфер пам'яті заповнюється за наступною строгою офсетною схемою:

```
[0x00 - 0x0F] struct nlmsghdr (nlmsg_len=0x6C, nlmsg_type=16 RTM_NEWLINK,
                               nlmsg_flags=0x605 = REQUEST|ACK|EXCL|CREATE)
[0x10 - 0x1F] struct ifinfomsg (ifi_family=0, ifi_type=0, ifi_index=0, ifi_flags=0)
[0x20 - 0x2D] struct rtattr IFLA_IFNAME (rta_len=14, rta_type=3, "veth-host\0")
[0x2E - 0x2F] Padding bytes (вирівнювання до 4 байт, RTA_ALIGN)
[0x30 - 0x33] struct rtattr IFLA_LINKINFO (rta_len=60, rta_type=18) — лише заголовок
  [0x34 - 0x3C] struct rtattr IFLA_INFO_KIND (rta_len=9, rta_type=1, "veth\0")
  [0x3D - 0x3F] Padding bytes
  [0x40 - 0x43] struct rtattr IFLA_INFO_DATA (rta_len=44, rta_type=2) — заголовок
    [0x44 - 0x47] struct rtattr VETH_INFO_PEER (rta_len=40, rta_type=1) — заголовок
      [0x48 - 0x57] struct ifinfomsg (заголовок парного кінця)
      [0x58 - 0x63] struct rtattr IFLA_IFNAME (rta_len=12, "veth-ns\0")
      [0x64 - 0x6B] struct rtattr IFLA_NET_NS_FD (rta_len=8, target_ns_fd)
```

Зверніть увагу на дві речі, на яких найчастіше збиваються. По-перше, `rta_len` вкладеного атрибута рахує **весь** його вміст разом із заголовком: 60 у `IFLA_LINKINFO` — це 4 байти заголовка плюс 56 байтів вкладених атрибутів. По-друге, довжина у полі — фактична (14, 9), а наступний атрибут починається вже з вирівняного зміщення (0x30, 0x40): у самому полі довжини вирівнювання не відображається. Послідовне використання `NLMSG_ALIGN()` та `RTA_ALIGN()` для обчислення зміщень і рятує від цих двох помилок на будь-якій архітектурі (x86_64, ARM64, RISC-V).

---

## 14. Програмна зміна MTU для veth-інтерфейсу через IFLA_MTU

Під час створення тунельних або маскувальних топологій для просторів імен виникає потреба зменшити розмір MTU (наприклад, до 1450 байтів для VXLAN тунелів):

:::tabs
```c
struct {
    struct nlmsghdr nlh;
    struct ifinfomsg ifm;
    char buf[64];
} mtu_req;

memset(&mtu_req, 0, sizeof(mtu_req));
mtu_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
mtu_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
mtu_req.nlh.nlmsg_type = RTM_NEWLINK;
mtu_req.ifm.ifi_index = if_nametoindex("veth-host");

struct rtattr *rta = (struct rtattr *)(((char *)&mtu_req) + mtu_req.nlh.nlmsg_len);
rta->rta_type = IFLA_MTU;
rta->rta_len = RTA_LENGTH(sizeof(uint32_t));
*(uint32_t *)RTA_DATA(rta) = 1450;
mtu_req.nlh.nlmsg_len = NLMSG_ALIGN(mtu_req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
```
```cpp
struct MtuRequest {
    nlmsghdr nlh{};
    ifinfomsg ifm{};
    std::array<char, 64> buf{};
};

MtuRequest mtu_req{};
mtu_req.nlh.nlmsg_len = NLMSG_LENGTH(sizeof(ifinfomsg));
mtu_req.nlh.nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
mtu_req.nlh.nlmsg_type = RTM_NEWLINK;
mtu_req.ifm.ifi_index = ::if_nametoindex("veth-host");

auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(&mtu_req) + mtu_req.nlh.nlmsg_len);
rta->rta_type = IFLA_MTU;
rta->rta_len = RTA_LENGTH(sizeof(uint32_t));
*reinterpret_cast<uint32_t*>(RTA_DATA(rta)) = 1450;
mtu_req.nlh.nlmsg_len = NLMSG_ALIGN(mtu_req.nlh.nlmsg_len) + RTA_ALIGN(rta->rta_len);
```
:::

Передавання атрибута `IFLA_MTU` безпосередньо у бінарному пакеті Netlink змінює розмір кадру атомарно без розриву сокетних з'єднань.

---

## 15. Створення віртуальних пристроїв macvlan у C++20

Окрім `veth`-пар, системні розробники можуть програмно конфігурувати пристрої `macvlan`:

:::tabs
```c
void create_macvlan_device(int nl_socket, const char *dev_name, int master_ifindex) {
    /* Встановлення IFLA_INFO_KIND -> "macvlan" */
}
```
```cpp
void create_macvlan_device(int nl_socket, std::string_view dev_name, int master_ifindex) {
    // Встановлення IFLA_INFO_KIND -> "macvlan"
    // Додавання MACVLAN_MODE_BRIDGE у атрибут IFLA_MACVLAN_MODE
}
```
:::

Пристрої `macvlan` дозволяють прив'язувати віртуальні MAC-адреси безпосередньо до фізичного інтерфейсу хоста, що зменшує накладні витрати обробки трафіку порівняно з `veth`-парами.

---

## 16. Створення непривілейованих просторів імен (Rootless Netns)

Для запуску програм без root-прав використовується комбінація прапорців `CLONE_NEWUSER | CLONE_NEWNET`:

1. Програма виконує `unshare(CLONE_NEWUSER | CLONE_NEWNET)`.
2. Встановлює UID/GID mapping у `/proc/self/uid_map` та `/proc/self/gid_map`.
3. Отримує повний набір capabilities у межах нового User Namespace (зокрема `CAP_SYS_ADMIN` для самого простору і `CAP_NET_ADMIN` для пристроїв у ньому) і конфігурує локальну мережу без втручання в інфраструктуру хоста.

---

## 17. Програмна ініціалізація правил фаєрвола nftables у ізольованому netns

Під час створення ізольованої мережевої топології розробники C/C++ часто ініціалізують базовий набір правил фільтрації та трансляції адрес (NAT) безпосередньо з коду за допомогою бібліотеки `libnftnl`:

:::tabs
```c
// Крок 1: таблиця "filter" у контексті цільового netns
// (ланцюжки forward/postrouting додаються далі через nftnl_chain_*)
struct nftnl_table *table = nftnl_table_alloc();
nftnl_table_set_str(table, NFTNL_TABLE_NAME, "filter");
nftnl_table_set_u32(table, NFTNL_TABLE_FAMILY, NFPROTO_IPV4);
```
```cpp
// Ініціалізація таблиці nftables у C++
auto* table = nftnl_table_alloc();
nftnl_table_set_str(table, NFTNL_TABLE_NAME, "filter");
nftnl_table_set_u32(table, NFTNL_TABLE_FAMILY, NFPROTO_IPV4);
```
:::

Застосування `libnftnl` у поєднанні з Netlink забезпечує повністю ізольоване середовище фаєрвола, яке не перетинається з правилами хоста та не вимагає виклику зовнішніх команд `iptables-legacy`.

---

## 18. Трасування функції ядра veth_xmit за допомогою eBPF kprobe

`veth_xmit()` — це не системний виклик, а внутрішня функція драйвера (`ndo_start_xmit` пристрою `veth`), тому дістатися до неї можна лише динамічним зондом. Для аналізу продуктивності та простеження доставки пакетів між просторами імен до неї підключають eBPF kprobe:

:::tabs
```c
SEC("kprobe/veth_xmit")
int trace_veth_xmit(struct pt_regs *ctx) {
    struct sk_buff *skb = (struct sk_buff *)PT_REGS_PARM1(ctx);
    u32 len = BPF_CORE_READ(skb, len);
    /* bpf_printk — макрос libbpf; сирий помічник bpf_trace_printk()
       додатково вимагає розмір рядка форматування */
    bpf_printk("veth_xmit: packet length = %d\n", len);
    return 0;
}
```
```cpp
// Сама eBPF-програма компілюється як C у простір ядра — вкладки C++ вона не має.
// З боку користувацького простору libbpf-скелет обгортають у RAII-власника:
// std::unique_ptr<veth_bpf, decltype(&veth_bpf__destroy)> skel{veth_bpf__open_and_load(),
//                                                             veth_bpf__destroy};
```
:::

Один kprobe на вході у функцію дає лічильник кадрів та їхні розміри на межі просторів. Щоб виміряти саме тривалість обробки, потрібна пара `kprobe`/`kretprobe`: перший запам'ятовує мітку часу в мапі за ключем `pid`, другий рахує різницю. А скинуті на межі пакети надійніше ловити не тут, а на точці трасування `skb:kfree_skb`, яка одразу повідомляє причину.

---

## 19. Взаємодія з OCI Runtime Spec (runc / crun) та systemd-nspawn

У сучасній контейнерній інфраструктурі низькорівнева конфігурація просторів імен повністю стандартизована Open Container Initiative (OCI).

Низькорівневі OCI-рушії (`runc`, `crun`):
* Зчитують специфікацію `config.json`, де у секції `namespaces` вказано тип `network`.
* Якщо вказано шлях до наявного простору (наприклад, `/var/run/netns/demo_ns`), runc виконує виклик `open()` та `setns(fd, CLONE_NEWNET)` до моменту запуску бінарного файла контейнера.
* Утиліта `systemd-nspawn` (не демон, а програма запуску контейнера) виконує аналогічну послідовність через параметри `--network-veth` або `--network-namespace-path`.

---

## 20. Інтеграція з Kubernetes CNI (Container Network Interface)

Створення мережевих просторів є базовим етапом життєвого циклу контейнерів у Kubernetes:
1. Демон `kubelet` викликає контейнерний рушій (containerd чи CRI-O) для виділення Pod.
2. CRI створює "Pause-контейнер" з новим мережевим простором `CLONE_NEWNET`.
3. Викликається CNI-плагін (наприклад, Calico чи Cilium) з аргументом `CNI_COMMAND=ADD` та `CNI_NETNS=/proc/[pid]/ns/net`.
4. CNI-плагін програмно створює `veth`-пару, переміщує периферійну частину в мережевий простір Pod, призначає IP-адресу та маршрути.

---

## 21. Рекомендації з побудови виробничих C/C++ систем ізоляції

Під час розробки власних мережевих демонів або CNI-плагінів на мовах C/C++ слід дотримуватися такого чек-листа:

* Завжди використовувати розширювані TLV-атрибути Netlink замість сирих `ioctl`.
* Перевіряти повернені відповіді ядра `NLMSG_ERROR` для кожної операції `sendto()`.
* Застосовувати ідіоми RAII (наприклад, `ScopedFd` у C++20) для автоматичного закриття дескрипторів просторів та сокетів під час обробки винятків.
* Використовувати атрибути `IFLA_NET_NS_FD` для атомарного створення пристроїв відразу в цільовому просторі імен.

---

## 22. Приклад вимірювання продуктивності за допомогою iperf3

Для вимірювання пропускної здатності створеного `veth`-каналу між просторами використовують звичайні мережеві інструменти. Обидва кінці на цей момент мають бути підняті й мати адреси (див. §4), інакше клієнт просто не знайде маршруту:

```bash
# 1. Запуск сервера iperf3 всередині ізольованого простору demo_c_ns
ip netns exec demo_c_ns iperf3 -s -D

# 2. Запуск клієнта iperf3 з хоста
iperf3 -c 10.0.0.2 -t 10
```

На сучасних процесорах x86_64 такий тест типово показує десятки Гбіт/с. Причина високих чисел у тому, що `veth` **не копіює** даних пакета: на інший бік передається той самий `sk_buff` за вказівником, а межу задає вартість обробки кадру в стеку — планування softirq, проходження хуків та поведінка кешів ЦП. Тому результат сильно залежить від того, чи опинилися обидва боки на одному ядрі ЦП, і від увімкнених offload-ів (`GSO`/`GRO`), а не від пропускної здатності пам'яті.

---

## 23. Інструкція з компіляції та перевірки реалізації

Для компіляції та тестування наведеного коду C та C++ скористайтеся стандартними компіляторами `gcc` та `g++`:

```bash
# Компіляція прикладу мовою C
gcc -O2 -Wall -Wextra demo_netns.c -o demo_netns_c

# Компіляція прикладу мовою C++20
g++ -O2 -std=c++20 -Wall -Wextra demo_netns.cpp -o demo_netns_cpp

# Запуск із правами root (необхідно для створення просторів)
sudo ./demo_netns_c
sudo ./demo_netns_cpp

# Інспекція результату у системі
ip netns list
ip netns exec demo_c_ns ip a
```

Вивід підтвердить успішне створення дескрипторів, перемикання контексту та відправку Netlink-повідомлень ядра. Для повного видалення створених тестів виконайте `sudo ip netns del demo_c_ns` та `sudo ip netns del demo_cpp_ns`.

# ⚙️ Практикум: розробка Netlink-клієнта для ethtool

Цей практикум демонструє процес створення низькорівневого мережевого клієнта мовами C та C++ для взаємодії з інтерфейсом **Generic Netlink ethtool** ядра Linux. Код розв'язує два фундаментальних інженерних завдання: запит поточних параметрів мережевого лінку (швидкість, дуплекс, автоузгодження) та асинхронне прослуховування подійної багатоадресної групи (Multicast Monitor Group) для реакції на зміну стану фізичного кабелю чи автоузгодження в реальному часі.

## 1. Архітектурне завдання та системні передумови

У сучасних хмарних платформах, SDN-контролерах та системах телеметрії високої доступності виникає потреба в низькорівневому моніторингу стану фізичних мережевих адаптерів без залучення зовнішніх утиліт на кшталт `ethtool` через `exec()`. Виклик зовнішнього бінарного файлу створює суттєві накладні витрати на виклики `fork()`/`exec()`, парсинг текстового виводу та невизначеність у разі зміни формату рядків.

Програмна взаємодія напряму через сокети Netlink забезпечує бінарну точність, мінімальну затримку (latency) та можливість обробки тисяч подій на секунду.

Для побудови повноцінного клієнта необхідно виконати послідовність з п'яти кроків:

```
[1. Відкриття AF_NETLINK сокета] ──► [2. Запит GENL_ID_CTRL (Розділення ethtool ID)]
                                                               │
[4. Обробка відповідей / NTF] ◄── [3. Формування каду з ETHTOOL_A_HEADER]
```

### Динамічне розв'язання ID сімейства через Generic Netlink Controller

На відміну від стаціонарного протоколу `rtnetlink` (де типи повідомлень на кшталт `RTM_NEWLINK` чи `RTM_NEWROUTE` є константами, вшитими в заголовки ядра), підсистема Generic Netlink є розширюваним контейнером. Під час завантаження ядра модуль `ethtool` реєструється динамічно, і ядро виділяє йому довільний ідентифікатор сімейства (Family ID, зазвичай у діапазоні від `0x0010` до `0x00fc`).

З цієї причини клієнтський додаток не може hardcode-ити номер сімейства `nlmsg_type`. Першим обов'язковим кроком є надсилання кадру до системного контролера Generic Netlink, який має фіксований ідентифікатор `GENL_ID_CTRL` (значення `0x0010`).

Запит до контролера містить команду `CTRL_CMD_GETFAMILY` та NLA-атрибут `CTRL_ATTR_FAMILY_NAME` зі значенням `"ethtool"`. У відповідь ядро повертає атрибут `CTRL_ATTR_FAMILY_ID`, який надалі використовується як `nlmsg_type` у всіх запитах до ethtool.

---

## 2. Повна реалізація клієнта (C та C++)

Нижче наведено робочі реалізації клієнта. Реалізація C++ використовує ідіому RAII для керування дескрипторами сокетів, безпечні типи `std::span` та `std::string_view` і виключення замість викликів `goto out` та `free()`.

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
#include <linux/ethtool_netlink.h>

#define BUFFER_SIZE 8192

/* Допоміжна функція для додавання NLA атрибута в буфер */
static void add_attr(struct nlmsghdr *nlh, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    struct rtattr *rta;
    if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        fprintf(stderr, "Buffer overflow adding NLA attribute\n");
        return;
    }
    rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (alen > 0)
        memcpy(RTA_DATA(rta), data, alen);
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
}

/* Розв'язання ID сімейства ethtool через Generic Netlink Controller */
static uint16_t resolve_family_id(int fd, const char *family_name) {
    char buf[BUFFER_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    nlh->nlmsg_type = GENL_ID_CTRL;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK;
    nlh->nlmsg_seq = 1;
    nlh->nlmsg_pid = getpid();

    struct genlmsghdr *ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    ghdr->cmd = CTRL_CMD_GETFAMILY;
    ghdr->version = 1;

    add_attr(nlh, sizeof(buf), CTRL_ATTR_FAMILY_NAME, family_name, strlen(family_name) + 1);

    struct sockaddr_nl nladdr = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nladdr, sizeof(nladdr)) < 0) {
        perror("sendto CTRL_CMD_GETFAMILY");
        return 0;
    }

    ssize_t ret = recv(fd, buf, sizeof(buf), 0);
    if (ret < 0) {
        perror("recv family response");
        return 0;
    }

    nlh = (struct nlmsghdr *)buf;
    if (!NLMSG_OK(nlh, ret) || nlh->nlmsg_type == NLMSG_ERROR) {
        fprintf(stderr, "Failed to resolve family ID for %s\n", family_name);
        return 0;
    }

    ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    struct rtattr *attr = (struct rtattr *)((char *)ghdr + GENL_HDRLEN);
    int attrlen = nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN);

    uint16_t family_id = 0;
    while (RTA_OK(attr, attrlen)) {
        if (attr->rta_type == CTRL_ATTR_FAMILY_ID) {
            family_id = *(uint16_t *)RTA_DATA(attr);
            break;
        }
        attr = RTA_NEXT(attr, attrlen);
    }
    return family_id;
}

/* Запит режимів лінку для інтерфейсу */
static void query_linkmodes(int fd, uint16_t family_id, const char *ifname) {
    char buf[BUFFER_SIZE];
    memset(buf, 0, sizeof(buf));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buf;
    nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    nlh->nlmsg_type = family_id;
    nlh->nlmsg_flags = NLM_F_REQUEST;
    nlh->nlmsg_seq = 2;
    nlh->nlmsg_pid = getpid();

    struct genlmsghdr *ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
    ghdr->cmd = ETHTOOL_MSG_LINKMODES_GET;
    ghdr->version = ETHTOOL_GENL_VERSION;

    /* Створення вкладеного заголовку ETHTOOL_A_HEADER */
    int header_start = nlh->nlmsg_len;
    struct rtattr *hdr_attr = (struct rtattr *)(((char *)nlh) + header_start);
    hdr_attr->rta_type = NLA_F_NESTED | ETHTOOL_A_LINKMODES_HEADER;
    hdr_attr->rta_len = RTA_LENGTH(0);
    nlh->nlmsg_len += RTA_LENGTH(0);

    add_attr(nlh, sizeof(buf), ETHTOOL_A_HEADER_DEV_NAME, ifname, strlen(ifname) + 1);
    hdr_attr->rta_len = nlh->nlmsg_len - header_start;

    struct sockaddr_nl nladdr = { .nl_family = AF_NETLINK };
    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&nladdr, sizeof(nladdr)) < 0) {
        perror("sendto ETHTOOL_MSG_LINKMODES_GET");
        return;
    }

    ssize_t ret = recv(fd, buf, sizeof(buf), 0);
    if (ret < 0) {
        perror("recv linkmodes");
        return;
    }

    nlh = (struct nlmsghdr *)buf;
    if (NLMSG_OK(nlh, ret) && nlh->nlmsg_type == family_id) {
        ghdr = (struct genlmsghdr *)NLMSG_DATA(nlh);
        if (ghdr->cmd == ETHTOOL_MSG_LINKMODES_GET || ghdr->cmd == ETHTOOL_MSG_LINKMODES_NTF) {
            struct rtattr *attr = (struct rtattr *)((char *)ghdr + GENL_HDRLEN);
            int attrlen = nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN);

            uint32_t speed = 0;
            uint8_t duplex = 0, autoneg = 0;

            while (RTA_OK(attr, attrlen)) {
                if (attr->rta_type == ETHTOOL_A_LINKMODES_SPEED) {
                    speed = *(uint32_t *)RTA_DATA(attr);
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_DUPLEX) {
                    duplex = *(uint8_t *)RTA_DATA(attr);
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_AUTONEG) {
                    autoneg = *(uint8_t *)RTA_DATA(attr);
                }
                attr = RTA_NEXT(attr, attrlen);
            }
            printf("[%s] Speed: %u Mbps, Duplex: %s, Autoneg: %s\n",
                   ifname, speed,
                   duplex == 1 ? "Full" : (duplex == 0 ? "Half" : "Unknown"),
                   autoneg ? "on" : "off");
        }
    }
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";

    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return 1;
    }

    struct sockaddr_nl local = {
        .nl_family = AF_NETLINK,
        .nl_pid = getpid()
    };
    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("bind");
        close(fd);
        return 1;
    }

    uint16_t family_id = resolve_family_id(fd, ETHTOOL_GENL_NAME);
    if (!family_id) {
        fprintf(stderr, "Ethtool Generic Netlink family not found!\n");
        close(fd);
        return 1;
    }
    printf("Resolved ethtool family ID: %u\n", family_id);

    query_linkmodes(fd, family_id, ifname);

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <memory>
#include <stdexcept>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>
#include <linux/ethtool_netlink.h>

class NetlinkSocket {
public:
    explicit NetlinkSocket(int protocol = NETLINK_GENERIC) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create AF_NETLINK socket");
        }

        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_pid = static_cast<uint32_t>(::getpid());

        if (::bind(fd_, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "Failed to bind Netlink socket");
        }
    }

    ~NetlinkSocket() {
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

    void send(std::span<const uint8_t> data) const {
        sockaddr_nl nladdr{};
        nladdr.nl_family = AF_NETLINK;

        if (::sendto(fd_, data.data(), data.size(), 0,
                     reinterpret_cast<sockaddr*>(&nladdr), sizeof(nladdr)) < 0) {
            throw std::system_error(errno, std::generic_category(), "sendto failed");
        }
    }

    std::vector<uint8_t> receive(size_t max_size = 8192) const {
        std::vector<uint8_t> buffer(max_size);
        ssize_t bytes_read = ::recv(fd_, buffer.data(), buffer.size(), 0);
        if (bytes_read < 0) {
            throw std::system_error(errno, std::generic_category(), "recv failed");
        }
        buffer.resize(static_cast<size_t>(bytes_read));
        return buffer;
    }

private:
    int fd_{-1};
};

struct LinkInfo {
    uint32_t speed{0};
    uint8_t duplex{0};
    bool autoneg{false};
};

class EthtoolNetlinkClient {
public:
    explicit EthtoolNetlinkClient(NetlinkSocket& socket)
        : socket_(socket), family_id_(resolveFamilyId(ETHTOOL_GENL_NAME)) {}

    [[nodiscard]] uint16_t family_id() const noexcept { return family_id_; }

    [[nodiscard]] LinkInfo getLinkModes(std::string_view ifname) const {
        std::vector<uint8_t> request_buf(8192, 0);

        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
        nlh->nlmsg_type = family_id_;
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_seq = 2;
        nlh->nlmsg_pid = static_cast<uint32_t>(::getpid());

        auto* ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        ghdr->cmd = ETHTOOL_MSG_LINKMODES_GET;
        ghdr->version = ETHTOOL_GENL_VERSION;

        // Вкладений заголовок ETHTOOL_A_HEADER
        size_t header_offset = nlh->nlmsg_len;
        auto* hdr_attr = reinterpret_cast<rtattr*>(request_buf.data() + header_offset);
        hdr_attr->rta_type = NLA_F_NESTED | ETHTOOL_A_LINKMODES_HEADER;
        hdr_attr->rta_len = RTA_LENGTH(0);
        nlh->nlmsg_len += RTA_LENGTH(0);

        appendAttr(nlh, request_buf.size(), ETHTOOL_A_HEADER_DEV_NAME, ifname.data(), ifname.size() + 1);
        hdr_attr->rta_len = static_cast<unsigned short>(nlh->nlmsg_len - header_offset);

        request_buf.resize(nlh->nlmsg_len);
        socket_.send(request_buf);

        auto response = socket_.receive();
        return parseLinkModes(response);
    }

private:
    NetlinkSocket& socket_;
    uint16_t family_id_{0};

    static void appendAttr(nlmsghdr* nlh, size_t maxlen, int type, const void* data, size_t alen) {
        size_t len = RTA_LENGTH(alen);
        if (NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
            throw std::runtime_error("Netlink message buffer overflow");
        }
        auto* rta = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
        rta->rta_type = static_cast<unsigned short>(type);
        rta->rta_len = static_cast<unsigned short>(len);
        if (alen > 0 && data != nullptr) {
            std::memcpy(RTA_DATA(rta), data, alen);
        }
        nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(len);
    }

    uint16_t resolveFamilyId(std::string_view family_name) {
        std::vector<uint8_t> request_buf(4096, 0);

        auto* nlh = reinterpret_cast<nlmsghdr*>(request_buf.data());
        nlh->nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
        nlh->nlmsg_type = GENL_ID_CTRL;
        nlh->nlmsg_flags = NLM_F_REQUEST;
        nlh->nlmsg_seq = 1;
        nlh->nlmsg_pid = static_cast<uint32_t>(::getpid());

        auto* ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(nlh));
        ghdr->cmd = CTRL_CMD_GETFAMILY;
        ghdr->version = 1;

        appendAttr(nlh, request_buf.size(), CTRL_ATTR_FAMILY_NAME, family_name.data(), family_name.size() + 1);
        request_buf.resize(nlh->nlmsg_len);

        socket_.send(request_buf);
        auto response = socket_.receive();

        auto* res_nlh = reinterpret_cast<nlmsghdr*>(response.data());
        if (!NLMSG_OK(res_nlh, response.size()) || res_nlh->nlmsg_type == NLMSG_ERROR) {
            throw std::runtime_error("Failed to resolve Generic Netlink family ID");
        }

        auto* res_ghdr = reinterpret_cast<genlmsghdr*>(NLMSG_DATA(res_nlh));
        auto* attr = reinterpret_cast<rtattr*>(reinterpret_cast<char*>(res_ghdr) + GENL_HDRLEN);
        int attrlen = static_cast<int>(res_nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN));

        while (RTA_OK(attr, attrlen)) {
            if (attr->rta_type == CTRL_ATTR_FAMILY_ID) {
                return *reinterpret_cast<const uint16_t*>(RTA_DATA(attr));
            }
            attr = RTA_NEXT(attr, attrlen);
        }
        throw std::runtime_error("Family ID attribute missing in response");
    }

    static LinkInfo parseLinkModes(std::span<const uint8_t> response) {
        const auto* nlh = reinterpret_cast<const nlmsghdr*>(response.data());
        LinkInfo info{};

        if (NLMSG_OK(nlh, response.size())) {
            const auto* ghdr = reinterpret_cast<const genlmsghdr*>(NLMSG_DATA(nlh));
            const auto* attr = reinterpret_cast<const rtattr*>(reinterpret_cast<const char*>(ghdr) + GENL_HDRLEN);
            int attrlen = static_cast<int>(nlh->nlmsg_len - NLMSG_LENGTH(GENL_HDRLEN));

            while (RTA_OK(attr, attrlen)) {
                if (attr->rta_type == ETHTOOL_A_LINKMODES_SPEED) {
                    info.speed = *reinterpret_cast<const uint32_t*>(RTA_DATA(attr));
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_DUPLEX) {
                    info.duplex = *reinterpret_cast<const uint8_t*>(RTA_DATA(attr));
                } else if (attr->rta_type == ETHTOOL_A_LINKMODES_AUTONEG) {
                    info.autoneg = (*reinterpret_cast<const uint8_t*>(RTA_DATA(attr)) != 0);
                }
                attr = RTA_NEXT(attr, attrlen);
            }
        }
        return info;
    }
};

int main(int argc, char* argv[]) {
    try {
        std::string_view ifname = (argc > 1) ? argv[1] : "eth0";

        NetlinkSocket socket;
        EthtoolNetlinkClient client(socket);

        std::cout << "Resolved Ethtool Generic Netlink Family ID: " << client.family_id() << "\n";

        LinkInfo info = client.getLinkModes(ifname);
        std::cout << "[" << ifname << "] Speed: " << info.speed << " Mbps, Duplex: "
                  << (info.duplex == 1 ? "Full" : "Half")
                  << ", Autoneg: " << (info.autoneg ? "on" : "off") << "\n";

    } catch (const std::exception& ex) {
        std::cerr << "Error: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 3. Детальний аналіз механіки вирівнювання пам'яті та NLA-пакування

При практичній розробці Netlink-клієнтів найчастіше виникають такі помилки:

### Вирівнювання пам'яті (Memory Alignment Rules)

Кожен атрибут NLA складається з заголовка `struct nlattr` (4 байти: 2 байти `nla_len` + 2 байти `nla_type`) та блоку корисного навантаження. За вимогами специфікації Netlink в ядрі Linux, кожен новий атрибут повинен починатися з адреси, кратної 4 байтам (32-бітне вирівнювання).

Для забезпечення цього вирівнювання використовується макрос `RTA_ALIGN(len)` або `NLA_ALIGN(len)`. Якщо корисне навантаження атрибута становить, наприклад, 5 байтів (рядок `"eth0"` з нульовим термінатором `\0`), загальний розмір атрибута без вирівнювання становить 4 + 5 = 9 байтів. Макрос `RTA_ALIGN(9)` округлює цей розмір до 12 байтів, додаючи 3 байти падінгу.

Якщо розробник додасть наступний атрибут за зсувом 9 байтів без округлення, ядро на архітектурах із суворими вимогами до вирівнювання (наприклад, ARM64 або SPARC) згенерує апаратний збій вирівнювання (Alignment Fault) або скине весь пакет Netlink із помилкою `-EINVAL`.

### Вкладені атрибути (Nested Attributes & NLA_F_NESTED)

Атрибут `ETHTOOL_A_LINKMODES_HEADER` є контейнером, усередині якого лежать інші атрибути (`DEV_INDEX`, `DEV_NAME`, `FLAGS`). При формуванні таких вкладених блоків розробник зобов'язаний встановлювати прапорець `NLA_F_NESTED` у полі `rta_type`.

```text
/* Правильне формування вкладеного атрибута */
hdr_attr->rta_type = NLA_F_NESTED | ETHTOOL_A_LINKMODES_HEADER;
```

Якщо цей прапорець не встановлено, парсер ядра `nla_parse_nested()` сприйме заголовок як простий скалярний атрибут (наприклад, ціле число чи двійковий масив) і не буде рекурсивно розгортати дочірні атрибути імені мережевої карти.

---

## 4. Порівняння архітектурних підходів C та C++

Порівняння двох наведених реалізацій демонструє еволюцію підходів до безпеки пам'яті в системному програмуванні Linux.

1. **Керування ресурсами сокета**: У версії C дескриптор сокета `fd` вимагає ручного відстеження та закриття через `close(fd)` у кожній гілці обробки помилок. У C++ класі `NetlinkSocket` деструктор автоматично звільняє файловий дескриптор при виході з області видимості (RAII), запобігаючи витокам файлових дескрипторів навіть при виникненні виключень.
2. **Безпека буферів пам'яті**: Реалізація C спирається на сирі вказівники та макроси `RTA_DATA`/`RTA_NEXT`, де будь-яка помилка в розрахунку довжини викличує вихід за межі масиву (buffer overflow). Версія C++ застосовує `std::vector<uint8_t>` для автоматичного керування розміром буфера та `std::span<const uint8_t>` для передачі неволодіючих зрізів пам'яті в парсер без зайвого копіювання.
3. **Строкові типи**: Замість небезпечних викликів `strcpy()` та класичних C-рядків `const char*`, C++ код оперує легковажними об'єктами `std::string_view`, які виключають ризик читання поза межами рядкового буфера.

---

## 5. Обробка помилок та переповнення буфера сокета (`ENOBUFS`)

При прослуховуванні Multicast сповіщень у високонавантажених системах із тисячами віртуальних інтерфейсів ядро може надсилати сотні сповіщень на секунду. Якщо сокет не встигає зчитувати дані, системний виклик `recv()` поверне помилку `ENOBUFS` (No buffer space available).

Розробник зобов'язаний обробляти `ENOBUFS`, збільшувати розмір сокетного буфера через `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &bufsize, sizeof(bufsize))` або заново запитувати повний стан інтерфейсів після втрати кадру через виклик запиту з прапорцем `NLM_F_DUMP`.

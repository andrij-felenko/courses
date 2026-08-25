# ⚙️ Практична реалізація: керування bonding-інтерфейсом через rtnetlink у C та C++

Створення, налаштування та динамічна конфігурація агрегованих мережевих інтерфейсів у сучасному ядрі Linux здійснюється шляхом надсилання бінарних повідомлень через системний сокет `NETLINK_ROUTE` (пакет сімейства `AF_NETLINK`). Програмний інтерфейс Rtnetlink надає розробникам мережевих служб та системним інженерам можливість атомарно створити логічний master-пристрій (наприклад, `bond0`), задати бажаний режим агрегації трафіку (наприклад, LACP 802.3ad або Active-Backup), розрахувати параметри моніторингу носія та приєднати фізичні порти.

При роботі з сокетами `AF_NETLINK` бінарні запити пакуються у послідовність вирівняних за вимогами `NLMSG_ALIGN` структур `nlmsghdr` та вкладених атрибутів `rtattr`. Для пристроїв агрегації використовується двошарова вкладеність:
1. Зовнішній атрибут `IFLA_LINKINFO` визначає тип драйвера в ядрі за допомогою рядка `IFLA_INFO_KIND` (для bonding це `"bond"`, для team — `"team"`).
2. Внутрішній атрибут `IFLA_INFO_DATA` виконує роль контейнера для специфічних налаштувань (режим `IFLA_BOND_MODE`, інтервал перевірки `IFLA_BOND_MIIMON`, політика хешування `IFLA_BOND_XMIT_HASH_POLICY`).

Низькорівнева взаємодія вимагає суворого дотримання макросів `RTA_LENGTH()`, `RTA_DATA()` та `RTA_NEXT()`, оскільки невирівняний зсув атрибута призведе до відхилення пакета ядром з помилкою `EINVAL`. Крім того, створення пристрою супроводжується передачею прапорів `NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK`. Прапор `NLM_F_ACK` примушує ядро відправити зворотне повідомлення з результатом операції. Якщо код помилки у повідомленні `NLMSG_ERROR` дорівнює нулю, ядро успішно створило віртуальний інтерфейс та зареєструвало його в глобальній таблиці `struct net_device`.

---

## 1. Анатомія Rtnetlink повідомлення для агрегації

Кожен системний запит до Rtnetlink починається із загального заголовка `struct nlmsghdr`, за яким іде специфічна для родини повідомлень структура. Для операцій з мережевими посиланнями (`RTM_NEWLINK`, `RTM_DELLINK`, `RTM_GETLINK`) такою структурою є `struct ifinfomsg`:

```
+-------------------------------------------------------------------+
| struct nlmsghdr                                                   |
|   nlmsg_len   = 4096 (загальний розмір буфера)                    |
|   nlmsg_type  = RTM_NEWLINK                                       |
|   nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | ACK     |
|   nlmsg_seq   = 1 (послідовний номер)                             |
|   nlmsg_pid   = 0 (призначено для ядра)                           |
+-------------------------------------------------------------------+
| struct ifinfomsg                                                  |
|   ifi_family  = AF_UNSPEC                                         |
|   ifi_type    = 0                                                 |
|   ifi_index   = 0 (для нового) або ifindex (для існуючого)        |
|   ifi_flags   = 0                                                 |
|   ifi_change  = 0                                                 |
+-------------------------------------------------------------------+
| Атрибут: IFLA_IFNAME ("bond0")                                    |
+-------------------------------------------------------------------+
| Вкладений атрибут: IFLA_LINKINFO                                  |
|   +-- Атрибут: IFLA_INFO_KIND ("bond")                            |
|   +-- Вкладений атрибут: IFLA_INFO_DATA                           |
|         +-- Атрибут: IFLA_BOND_MODE (BOND_MODE_8023AD = 4)       |
|         +-- Атрибут: IFLA_BOND_MIIMON (100 ms)                   |
+-------------------------------------------------------------------+
```

### 1.1. Налаштування параметрів LACP та MII моніторингу

При збірці бінарного пакета атрибути пакуються послідовно у вкладений контейнер `IFLA_INFO_DATA`. Для цього спочатку за допомогою функції `nested_attr_begin()` фіксується поточний зсув у буфері та записується заголовок `struct rtattr` із типом `IFLA_INFO_DATA` та нульовою довжиною. Після додавання всіх необхідних атрибутів (`IFLA_BOND_MODE`, `IFLA_BOND_MIIMON`, `IFLA_BOND_XMIT_HASH_POLICY`) функція `nested_attr_end()` розраховує підсумкову кількість доданих байтів та оновлює поле `rta_len`.

Якщо підсумковий розмір пакета з урахуванням вирівнювання `NLMSG_ALIGN` перевищує виділений розмір буфера `NL_BUF_SIZE`, операція завершується з помилкою недостатнього обсягу буфера.

### 1.2. Прив'язка підпорядкованого порту (Enslaving a Slave Interface)

Прив'язка фізичного підпорядкованого порту (slave) здійснюється окремим системним викликом `RTM_NEWLINK`. На відміну від створення master-пристрою, при прив'язці підпорядкованого порту:
- У структурі `struct ifinfomsg` значення поля `ifi_index` встановлюється рівним індексу фізичного інтерфейсу (отриманому через системну функцію `if_nametoindex("eth0")`).
- У повідомлення додається атрибут `IFLA_MASTER`, чиє значення дорівнює `ifindex` логічного пристрою `bond0`.
- Також додається вкладений атрибут `IFLA_LINKINFO` з типом `IFLA_INFO_KIND` = `"bond_slave"`.

Якщо фізичний інтерфейс вже приєднаний до іншого master-пристрою (наприклад, `bridge0` або іншого `bond`), ядро відхилить запит з кодом помилки `-EBUSY`. Для виконання операцій потрібні привілеї адміністратора (`CAP_NET_ADMIN`).

---

## 2. Повний сирцевий код програми (C та C++)

Нижче наведено порівняльний аналіз реалізації у системній мові C та в сучасній ідіоматичній мові C++20. Повна програма створює віртуальний мережевий пристрій `bond0` у режимі стандарту IEEE 802.3ad (Mode 4), налаштовує MII-моніторинг на 100 мілісекунд і обробляє підтвердження `NLMSG_ERROR` від ядра.

:::tabs
```c
/* netlink_bond.c — C реалізація створення bonding-інтерфейсу через rtnetlink */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_bonding.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція для додавання атрибутів типу rtattr */
static int add_attr(struct nlmsghdr *n, int maxlen, int type, const void *data, int alen) {
    int len = RTA_LENGTH(alen);
    if (NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len) > maxlen) {
        return -1;
    }
    struct rtattr *rta = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = len;
    if (alen > 0 && data != NULL) {
        memcpy(RTA_DATA(rta), data, alen);
    }
    n->nlmsg_len = NLMSG_ALIGN(n->nlmsg_len) + RTA_ALIGN(len);
    return 0;
}

/* Допоміжна функція для відкриття контейнера атрибутів */
static struct rtattr *nested_attr_begin(struct nlmsghdr *n, int maxlen, int type) {
    struct rtattr *nested = (struct rtattr *)(((char *)n) + NLMSG_ALIGN(n->nlmsg_len));
    if (add_attr(n, maxlen, type, NULL, 0) < 0) {
        return NULL;
    }
    return nested;
}

/* Завершення та коригування довжини вкладеного контейнера */
static void nested_attr_end(struct nlmsghdr *n, struct rtattr *nested) {
    nested->rta_len = (char *)n + NLMSG_ALIGN(n->nlmsg_len) - (char *)nested;
}

int create_bond_interface(const char *bond_name, uint8_t mode, uint32_t miimon_ms) {
    int fd = socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *n = (struct nlmsghdr *)buffer;
    n->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    n->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    n->nlmsg_type = RTM_NEWLINK;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(n);
    ifi->ifi_family = AF_UNSPEC;

    /* Назва логічного інтерфейсу bond */
    if (add_attr(n, sizeof(buffer), IFLA_IFNAME, bond_name, strlen(bond_name) + 1) < 0) {
        close(fd);
        return -1;
    }

    /* Відкриваємо вкладений атрибут IFLA_LINKINFO */
    struct rtattr *linkinfo = nested_attr_begin(n, sizeof(buffer), IFLA_LINKINFO);
    if (!linkinfo) {
        close(fd);
        return -1;
    }

    /* Тип створюваного інтерфейсу — "bond" */
    const char *kind = "bond";
    if (add_attr(n, sizeof(buffer), IFLA_INFO_KIND, kind, strlen(kind) + 1) < 0) {
        close(fd);
        return -1;
    }

    /* Відкриваємо вкладений атрибут IFLA_INFO_DATA з параметрами bonding */
    struct rtattr *infodata = nested_attr_begin(n, sizeof(buffer), IFLA_INFO_DATA);
    if (!infodata) {
        close(fd);
        return -1;
    }

    /* Встановлюємо режим Bonding (наприклад, Mode 4 - 802.3ad) */
    if (add_attr(n, sizeof(buffer), IFLA_BOND_MODE, &mode, sizeof(mode)) < 0) {
        close(fd);
        return -1;
    }

    /* Встановлюємо інтервал MII моніторингу у мілісекундах */
    if (add_attr(n, sizeof(buffer), IFLA_BOND_MIIMON, &miimon_ms, sizeof(miimon_ms)) < 0) {
        close(fd);
        return -1;
    }

    nested_attr_end(n, infodata);
    nested_attr_end(n, linkinfo);

    /* Надсилаємо запит у ядро */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, n, n->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(AF_NETLINK)");
        close(fd);
        return -1;
    }

    /* Отримуємо відповідь-підтвердження (ACK) від ядра */
    char ack_buf[NL_BUF_SIZE];
    ssize_t status = recv(fd, ack_buf, sizeof(ack_buf), 0);
    if (status < 0) {
        perror("recv(ACK)");
        close(fd);
        return -1;
    }

    struct nlmsghdr *ack_hdr = (struct nlmsghdr *)ack_buf;
    if (ack_hdr->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(ack_hdr);
        if (err->error != 0) {
            fprintf(stderr, "Помилка Rtnetlink: %s (%d)\n", strerror(-err->error), err->error);
            close(fd);
            return -1;
        }
    }

    close(fd);
    printf("Bonding пристрій '%s' успішно створено (Mode: %d, MII: %d ms)\n", bond_name, mode, miimon_ms);
    return 0;
}

int main(void) {
    /* Створюємо bond0 у режимі BOND_MODE_8023AD (4) із miimon 100мс */
    if (create_bond_interface("bond0", BOND_MODE_8023AD, 100) < 0) {
        fprintf(stderr, "Не вдалося створити bonding пристрій\n");
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
```cpp
// netlink_bond.cpp — C++20 ідіоматична реалізація з RAII та std::expected
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <span>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_bonding.h>

namespace netlink {

// RAII обгортка для мережевого сокета
class NetlinkSocket {
    int fd_{-1};
public:
    explicit NetlinkSocket(int protocol) {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW | SOCK_CLOEXEC, protocol);
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

    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Програмована збірка Rtnetlink повідомлення
class NetlinkMessageBuilder {
    std::vector<uint8_t> buffer_;

public:
    explicit NetlinkMessageBuilder(uint16_t msg_type, uint16_t flags) {
        buffer_.resize(NLMSG_HDRLEN + sizeof(struct ifinfomsg), 0);
        auto* hdr = header();
        hdr->nlmsg_type = msg_type;
        hdr->nlmsg_flags = flags;
        hdr->nlmsg_len = static_cast<uint32_t>(buffer_.size());

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(buffer_.data() + NLMSG_HDRLEN);
        ifi->ifi_family = AF_UNSPEC;
    }

    void add_attribute(uint16_t type, std::span<const uint8_t> data) {
        const uint16_t len = RTA_LENGTH(data.size());
        const size_t old_size = buffer_.size();
        const size_t aligned_size = NLMSG_ALIGN(old_size) + RTA_ALIGN(len);

        buffer_.resize(aligned_size, 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + NLMSG_ALIGN(old_size));
        rta->rta_type = type;
        rta->rta_len = len;

        if (!data.empty()) {
            std::memcpy(RTA_DATA(rta), data.data(), data.size());
        }

        header()->nlmsg_len = static_cast<uint32_t>(aligned_size);
    }

    void add_string_attribute(uint16_t type, std::string_view str) {
        std::vector<uint8_t> bytes(str.begin(), str.end());
        bytes.push_back('\0');
        add_attribute(type, bytes);
    }

    template <typename T>
    void add_scalar_attribute(uint16_t type, T value) {
        static_assert(std::is_trivially_copyable_v<T>);
        const auto* ptr = reinterpret_cast<const uint8_t*>(&value);
        add_attribute(type, std::span<const uint8_t>(ptr, sizeof(T)));
    }

    class NestedAttribute {
        NetlinkMessageBuilder& builder_;
        size_t offset_;
    public:
        NestedAttribute(NetlinkMessageBuilder& builder, uint16_t type)
            : builder_(builder), offset_(NLMSG_ALIGN(builder.buffer_.size())) {
            builder_.add_attribute(type, {});
        }

        ~NestedAttribute() {
            auto* rta = reinterpret_cast<struct rtattr*>(builder_.buffer_.data() + offset_);
            rta->rta_len = static_cast<unsigned short>(builder_.buffer_.size() - offset_);
        }
    };

    [[nodiscard]] std::nested_container_tag create_nested(uint16_t type) {
        return {};
    }

    [[nodiscard]] std::span<const uint8_t> data() const noexcept {
        return buffer_;
    }

    [[nodiscard]] struct nlmsghdr* header() noexcept {
        return reinterpret_cast<struct nlmsghdr*>(buffer_.data());
    }
};

// Створення bonding-інтерфейсу
std::expected<void, std::string> create_bonding_device(std::string_view name, uint8_t mode, uint32_t miimon_ms) {
    NetlinkSocket socket(NETLINK_ROUTE);
    if (!socket.valid()) {
        return std::unexpected("Не вдалося відкрити AF_NETLINK сокет: " + std::string(strerror(errno)));
    }

    NetlinkMessageBuilder builder(RTM_NEWLINK, NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK);
    builder.add_string_attribute(IFLA_IFNAME, name);

    {
        NetlinkMessageBuilder::NestedAttribute linkinfo(builder, IFLA_LINKINFO);
        builder.add_string_attribute(IFLA_INFO_KIND, "bond");

        {
            NetlinkMessageBuilder::NestedAttribute infodata(builder, IFLA_INFO_DATA);
            builder.add_scalar_attribute(IFLA_BOND_MODE, mode);
            builder.add_scalar_attribute(IFLA_BOND_MIIMON, miimon_ms);
        }
    }

    struct sockaddr_nl sa{};
    sa.nl_family = AF_NETLINK;

    const auto msg_data = builder.data();
    if (::sendto(socket.get(), msg_data.data(), msg_data.size(), 0,
                 reinterpret_cast<const struct sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected("Помилка відправки sendto: " + std::string(strerror(errno)));
    }

    std::vector<uint8_t> ack_buf(4096);
    const ssize_t len = ::recv(socket.get(), ack_buf.data(), ack_buf.size(), 0);
    if (len < 0) {
        return std::unexpected("Помилка прийому ACK від ядра: " + std::string(strerror(errno)));
    }

    const auto* ack_hdr = reinterpret_cast<const struct nlmsghdr*>(ack_buf.data());
    if (ack_hdr->nlmsg_type == NLMSG_ERROR) {
        const auto* err = reinterpret_cast<const struct nlmsgerr*>(NLMSG_DATA(ack_hdr));
        if (err->error != 0) {
            return std::unexpected("Помилка ядра Rtnetlink: " + std::string(strerror(-err->error)));
        }
    }

    return {};
}

} // namespace netlink

int main() {
    constexpr std::string_view bond_name = "bond0";
    constexpr uint8_t bond_mode = BOND_MODE_8023AD; // Mode 4 LACP
    constexpr uint32_t mii_interval = 100;           // 100 ms

    auto result = netlink::create_bonding_device(bond_name, bond_mode, mii_interval);
    if (!result) {
        std::cerr << "Створення пристрою не вдалося: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Пристрій '" << bond_name << "' успішно створено через C++ Rtnetlink API!\n";
    return 0;
}
```
:::

---

## 3. Крайові випадки та обробка помилок у сокетах Rtnetlink

При практичній розробці мережевих демонів або оркестраторів контейнерів (наприклад, CNI плагінів) розробник зіштовхується із низкою специфічних крайових випадків у сокетах `NETLINK_ROUTE`:

1. **Переповнення сокетного буфера (`ENOBUFS`)**: При високій інтенсивності подій мережевого стеку (масове створення veth-парів або підключення десятків slave-портів) ядро може скинути повідомлення статусу. Для запобігання цьому розробники повинні збільшувати розмір сокетного буфера прийому за допомогою `setsockopt(fd, SOL_SOCKET, SO_RCVBUF, &bufsize, sizeof(bufsize))`.
2. **Перевірка послідовних номерів (`nlmsg_seq`)**: У мультипоточних програмах підтвердження ACK від ядра необхідно звіряти за унікальним полем `nlmsg_seq` у заголовку `nlmsghdr`. Це унеможливлює обробку застарілих відповідей від попередніх команд.
3. **Межі мережевих просторів імен (Network Namespaces)**: Сокет `NETLINK_ROUTE` прив'язується до того мережевого простору імен (netns), у якому знаходиться покроковий потік. Створення bonding-пристрою в одному netns та його переміщення у контейнер вимагає додаткового атрибута `IFLA_NET_NS_FD` або `IFLA_NET_NS_PID`.

---

## 4. Порівняльний аналіз підходів C та C++

1. **Управління ресурсами та файловими дескрипторами**:
   - У прикладі мовою **C** файловий дескриптор `int fd` вимагає явного виклику `close(fd)` у кожній гілці обробки помилок, що підвищує ризик витоку ресурсів (FD leak) при ускладненні логіки.
   - У прикладі мовою **C++** застосовано паттерн **RAII** у класі `NetlinkSocket`. Деструктор автоматично викличе `close()` при виході об'єкта зі сфери видимості, гарантуючи виняткову безпеку ресурсів.

2. **Формування та вирівнювання бінарних буферів**:
   - Реалізація мовою **C** спирається на фіксований стек-буфер `char buffer[NL_BUF_SIZE]` та ручний розрахунок зсуву вказівників за допомогою макросів `RTA_LENGTH()` та `RTA_ALIGN()`.
   - Реалізація мовою **C++** використовує класи `std::vector<uint8_t>` та `std::span<const uint8_t>` для автоматичного керування розміром пам'яті. Вкладені атрибути керуються за допомогою конструкторів та деструкторів шаблону `NestedAttribute`, що усуває помилки підрахунку підсумкової довжини заголовок-структур.

3. **Семантика обробки помилок**:
   - У мові **C** відношення до помилок є процедурним: повернення значення `-1` та встановлення `errno`.
   - У мові **C++20** використовується монотип `std::expected<void, std::string>`, який явним чином зобов'язує викликача перевірити результат виконання без застосування важких винятків або небезпечних кодів повернення.

# ⚙️ Програмне створення інтерфейсів Macvlan через RTNetlink

Програмне керування мережевими пристроями в ядрі Linux здійснюється через підсистему **RTNetlink** (Route Netlink). Це спеціалізоване сімейство сокетів `AF_NETLINK` з протоколом `NETLINK_ROUTE`, яке замінило застарілі `ioctl`-виклики (`SIOCSIFADDR`, `SIOCADDMULTI`). У той час як консольні утиліти з пакета `iproute2` (наприклад `ip link add`) надають зручний текстовий інтерфейс користувача, низькорівневі системні сервіси, контейнерні рантайми (OCI runtimes, containerd, CRI-O) та CNI-плагіни взаємодіють з ядром напряму через бінарні сокети Netlink.

Цей розділ розбирає повний цикл програмного створення віртуального інтерфейсу Macvlan у ядрі Linux, від формування бінарних заголовків та вкладених атрибутів `rtattr` до обробки підтверджень (ACK) від ядра мовами C та C++.

---

## Архітектурний механізм RTNetlink та структура RTM_NEWLINK

Протокол Netlink побудований як обмін повідомленнями за принципом «запит-відповідь» або асинхронне розсилання подій (multicast group events). Для маніпуляцій з мережевими інтерфейсами використовується протокольне сімейство `NETLINK_ROUTE`.

Для створення будь-якого віртуального мережевого пристрою (Macvlan, Macvtap, veth, bridge, dummy) у ядро надсилається сокетне повідомлення типу `RTM_NEWLINK`. Повідомлення супроводжується прапорцями створення `NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL`:

- `NLM_F_REQUEST` — обов'язковий прапорець для всіх запитів напрямку «простір користувача → ядро». Без нього ядро відкине повідомлення.
- `NLM_F_ACK` — вимагає від ядра надіслати у відповідь пакет підтвердження (`NLMSG_ERROR` із кодом помилки `error = 0` при успіху або від'ємним значенням `error` при збої). Це єдиний спосіб дізнатися, чи успішно пройшла операція створення інтерфейсу.
- `NLM_F_CREATE` — вказує ядру створити новий мережевий пристрій, якщо він відсутній у системній таблиці пристроїв.
- `NLM_F_EXCL` — вимагає від ядра повернути помилку `EEXIST`, якщо мережевий пристрій із вказаним ім'ям уже існує у системному просторі імен.

### Структура корисного навантаження (Payload)

Бінарний буфер записується у строгій послідовності alignment-вирівняних блоків:

1. **Заголовок повідомлення `struct nlmsghdr`:** визначає загальну довжину `nlmsg_len`, тип `nlmsg_type = RTM_NEWLINK` та прапорці `nlmsg_flags`.
2. **Заголовок мережевого інтерфейсу `struct ifinfomsg`:** містить сімейство адрес `ifi_family = AF_UNSPEC`, тип апаратного пристрою `ifi_type` та індекс `ifi_index`.
3. **Атрибути верхнього рівня `struct rtattr`:**
   - `IFLA_IFNAME`: текстовий рядок із нульовим завершенням (null-terminated string), що визначає ім'я нового віртуального інтерфейсу (наприклад `"macvlan0"`).
   - `IFLA_LINK`: 32-бітове ціле число (`uint32_t`), яке містить системний індекс батьківського фізичного мережевого адаптера `ifindex` (одержується через виклик `if_nametoindex("eth0")`).
   - `IFLA_LINKINFO`: вкладений атрибут-контейнер (`nested rtattr`), який описує специфічний драйвер та його параметри.

### Вкладені атрибути всередині IFLA_LINKINFO

Підсистема драйверів ядра аналізує вкладений вміст `IFLA_LINKINFO` за допомогою внутрішньої функції `nla_parse_nested()`:
- `IFLA_INFO_KIND`: рядок `"macvlan"` (або `"macvtap"`), який вказує ядру, який саме модуль підсистеми `net/core/` повинен обробляти запит і створювати структуру `macvlan_dev`.
- `IFLA_INFO_DATA`: ще один вкладений контейнер атрибутів, специфічних для обраного драйвера. У випадку Macvlan сюди додається атрибут `IFLA_MACVLAN_MODE` (тип `uint32_t`), де передається одне зі значень `MACVLAN_MODE_BRIDGE`, `MACVLAN_MODE_VEPA`, `MACVLAN_MODE_PRIVATE` або `MACVLAN_MODE_PASSTHROUGH`.

---

## Правила бінарного вирівнювання Netlink

Повідомлення Netlink вимагають вирівнювання кожного атрибута та заголовка за межею 4 байт (32 біти). Це пов'язано з тим, що ядро обробляє атрибути як послідовність 32-бітових слів. Якщо атрибут має неузгоджену довжину (наприклад ім'я інтерфейсу з 5 символів), решта байтів вирівнювання повинна заповнюватися нулями.

Для вирівнювання ядро надає стандартні макроси у файлі `<linux/rtnetlink.h>`:

- `NLMSG_ALIGN(len)` — заокруглює довжину заголовка до найближчого кратного 4 значення вгору.
- `NLMSG_LENGTH(len)` — повертає довжину заголовка плюс вирівняний розмір корисних даних.
- `RTA_LENGTH(len)` — повертає довжину структури `struct rtattr` плюс вирівняна довжина атрибута.
- `RTA_DATA(rta)` — повертає вказівник на початок даних атрибута одразу за заголовком `rtattr`.

Нехтування макросами вирівнювання призведе до того, що ядро не зможе розпарсити Netlink-повідомлення і повернути помилку `EINVAL` (Invalid argument).

---

## Покроковий аналіз виконання у ядрі Linux

Коли сокетне повідомлення `RTM_NEWLINK` відправляється у сокет `AF_NETLINK`, ядро виконує наступну послідовність дій:

1. **Прийом у сокетному шарі (`af_netlink.c`):** Перевіряється автентичність відправника (чи має процес ефемерну портову адресу Netlink `nl_pid`).
2. **Маршрутизація до RTNetlink (`rtnetlink.c`):** Функція `rtnetlink_rcv_msg()` перевіряє прав `CAP_NET_ADMIN` у даному просторі імен. Якщо процес не є привілейованим, повертається `EPERM`.
3. **Парсинг атрибутів:** Функція `rtnl_newlink()` аналізує верхньорівневі атрибути `IFLA_IFNAME` та `IFLA_LINK`. Якщо вказаний індекс батьківського пристрою `IFLA_LINK` відсутній у системі, запит відхиляється з помилкою `ENODEV`.
4. **Виклик драйвера Macvlan (`macvlan.c`):** Драйвер реєструє модуль `macvlan_link_ops`. Викликається функція `macvlan_newlink()`, яка виділяє структуру `macvlan_dev`, створює `macvlan_port` на батьківському пристрої (якщо це перший Macvlan) і реєструє обробник `macvlan_handle_frame()`.
5. **Надсилання підтвердження (ACK):** При успішному виділенні пристрою ядро генерує відповідь `NLMSG_ERROR` із `error = 0` і відправляє її назад у сокет користувача.

---

## Практична реалізація створення Macvlan

Нижче наведено дві повноцінні, повністю робочі реалізації створення інтерфейсу Macvlan у ядрі Linux мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція додавання атрибута Netlink із правильним 4-байтовим вирівнюванням */
static void add_attr(struct nlmsghdr *nlh, int type, const void *data, int len) {
    int attr_len = RTA_LENGTH(len);
    struct rtattr *rta = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = attr_len;
    if (len > 0 && data) {
        memcpy(RTA_DATA(rta), data, len);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(attr_len);
}

/* Основна функція створення інтерфейсу Macvlan */
int create_macvlan_interface(const char *parent_ifname, const char *macvlan_ifname, uint32_t mode) {
    /* Отримання системного індексу батьківського пристрою */
    unsigned int parent_idx = if_nametoindex(parent_ifname);
    if (parent_idx == 0) {
        perror("if_nametoindex failed");
        return -1;
    }

    /* Відкриття сокета AF_NETLINK для роботи з маршрутизацією та лінками */
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket AF_NETLINK failed");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    /* Ініціалізація заголовка nlmsghdr */
    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    nlh->nlmsg_type = RTM_NEWLINK;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL;
    nlh->nlmsg_seq = 1;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    ifi->ifi_family = AF_UNSPEC;

    /* 1. Атрибут імені нового інтерфейсу */
    add_attr(nlh, IFLA_IFNAME, macvlan_ifname, strlen(macvlan_ifname) + 1);

    /* 2. Атрибут індексу батьківського фізичного NIC */
    add_attr(nlh, IFLA_LINK, &parent_idx, sizeof(parent_idx));

    /* 3. Вкладений атрибут IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_LINKINFO, NULL, 0);

    /* 3a. Вказівка типу драйвера IFLA_INFO_KIND = "macvlan" */
    const char *kind = "macvlan";
    add_attr(nlh, IFLA_INFO_KIND, kind, strlen(kind) + 1);

    /* 3b. Вкладений атрибут IFLA_INFO_DATA */
    struct rtattr *infodata = (struct rtattr *)((char *)nlh + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_INFO_DATA, NULL, 0);

    /* 3c. Режим Macvlan (IFLA_MACVLAN_MODE) */
    add_attr(nlh, IFLA_MACVLAN_MODE, &mode, sizeof(mode));

    /* Зафіксуємо підсумкові довжини вкладених rtattr */
    infodata->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)infodata;
    linkinfo->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)linkinfo;

    /* Відправка пакета у ядро Linux */
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto failed");
        close(fd);
        return -1;
    }

    /* Отримання підтвердження (ACK або повідомлення про помилку) */
    char ack_buf[NL_BUF_SIZE];
    ssize_t ret = recv(fd, ack_buf, sizeof(ack_buf), 0);
    close(fd);

    if (ret < 0) {
        perror("recv failed");
        return -1;
    }

    struct nlmsghdr *ack_nlh = (struct nlmsghdr *)ack_buf;
    if (ack_nlh->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(ack_nlh);
        if (err->error != 0) {
            fprintf(stderr, "Netlink error: %s (%d)\n", strerror(-err->error), err->error);
            return -1;
        }
    }

    printf("Успішно створено Macvlan інтерфейс '%s' (mode=%u) на батькові '%s'\n",
           macvlan_ifname, mode, parent_ifname);
    return 0;
}

int main(void) {
    /* MACVLAN_MODE_BRIDGE = 2 */
    return create_macvlan_interface("eth0", "mvlan0", 2) == 0 ? 0 : 1;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string_view>
#include <expected>
#include <cstring>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <net/if.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>

namespace netlink {

// RAII обгортка для управління ресурсами файлового дескриптора сокета
class SocketFd {
    int fd_{-1};
public:
    explicit SocketFd(int fd) : fd_(fd) {}
    ~SocketFd() {
        if (fd_ >= 0) ::close(fd_);
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& o) noexcept : fd_(o.fd_) { o.fd_ = -1; }
    SocketFd& operator=(SocketFd&& o) noexcept {
        if (this != &o) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = o.fd_;
            o.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

// Будівельник Netlink повідомлень із безпечною роботою з пам'яттю
class MacvlanBuilder {
    std::vector<uint8_t> buffer_;

    void add_attr(uint16_t type, const void* data, size_t len) {
        size_t attr_len = RTA_LENGTH(len);
        size_t old_size = buffer_.size();
        buffer_.resize(NLMSG_ALIGN(old_size) + RTA_ALIGN(attr_len), 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + NLMSG_ALIGN(old_size));
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(attr_len);

        if (len > 0 && data) {
            std::memcpy(RTA_DATA(rta), data, len);
        }

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<uint32_t>(buffer_.size());
    }

public:
    MacvlanBuilder() {
        buffer_.resize(NLMSG_LENGTH(sizeof(struct ifinfomsg)), 0);
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = sizeof(struct nlmsghdr) + sizeof(struct ifinfomsg);
        nlh->nlmsg_type = RTM_NEWLINK;
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_ACK | NLM_F_CREATE | NLM_F_EXCL;
        nlh->nlmsg_seq = 1;

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(NLMSG_DATA(nlh));
        ifi->ifi_family = AF_UNSPEC;
    }

    std::expected<void, std::string> create(std::string_view parent_if, std::string_view macvlan_if, uint32_t mode) {
        unsigned int parent_idx = ::if_nametoindex(parent_if.data());
        if (parent_idx == 0) {
            return std::unexpected("Невідомий батьківський інтерфейс: " + std::string(parent_if));
        }

        add_attr(IFLA_IFNAME, macvlan_if.data(), macvlan_if.size() + 1);
        add_attr(IFLA_LINK, &parent_idx, sizeof(parent_idx));

        size_t linkinfo_off = buffer_.size();
        add_attr(IFLA_LINKINFO, nullptr, 0);

        std::string_view kind = "macvlan";
        add_attr(IFLA_INFO_KIND, kind.data(), kind.size() + 1);

        size_t infodata_off = buffer_.size();
        add_attr(IFLA_INFO_DATA, nullptr, 0);

        add_attr(IFLA_MACVLAN_MODE, &mode, sizeof(mode));

        // Фіксуємо підсумкові довжини вкладених rtattr
        auto* infodata = reinterpret_cast<struct rtattr*>(buffer_.data() + infodata_off);
        infodata->rta_len = static_cast<unsigned short>(buffer_.size() - infodata_off);

        auto* linkinfo = reinterpret_cast<struct rtattr*>(buffer_.data() + linkinfo_off);
        linkinfo->rta_len = static_cast<unsigned short>(buffer_.size() - linkinfo_off);

        int sock_raw = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
        if (sock_raw < 0) {
            return std::unexpected("Помилка створення сокета AF_NETLINK: " + std::string(strerror(errno)));
        }
        SocketFd sock(sock_raw);

        struct sockaddr_nl sa{};
        sa.nl_family = AF_NETLINK;

        if (::sendto(sock.get(), buffer_.data(), buffer_.size(), 0,
                     reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
            return std::unexpected("Помилка sendto у Netlink: " + std::string(strerror(errno)));
        }

        std::vector<uint8_t> ack_buf(4096);
        ssize_t ret = ::recv(sock.get(), ack_buf.data(), ack_buf.size(), 0);
        if (ret < 0) {
            return std::unexpected("Помилка прийому ACK від ядра: " + std::string(strerror(errno)));
        }

        auto* ack_nlh = reinterpret_cast<struct nlmsghdr*>(ack_buf.data());
        if (ack_nlh->nlmsg_type == NLMSG_ERROR) {
            auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(ack_nlh));
            if (err->error != 0) {
                return std::unexpected("Помилка Netlink від ядра: " + std::string(strerror(-err->error)));
            }
        }

        return {};
    }
};

} // namespace netlink

int main() {
    netlink::MacvlanBuilder builder;
    // MACVLAN_MODE_BRIDGE = 2
    auto res = builder.create("eth0", "mvlan0", 2);
    if (!res) {
        std::cerr << "Помилка: " << res.error() << std::endl;
        return 1;
    }
    std::cout << "Успішно створено Macvlan через C++20 RTNetlink API!" << std::endl;
    return 0;
}
```
:::

---

## Порівняльний аналіз реалізацій C та C++

Обробка RTNetlink мовою C вимагає ручного обчислення зміщень вказівників, виконання приведення типів `char*` та коректного закриття файлових дескрипторів сокетів перед кожною точкою виходу при помилці.

Реалізація мовою C++20 надає наступні архітектурні переваги:

1. **Управління ресурсами через RAII (`SocketFd`):** Клас `SocketFd` унеможливлює витоки дескрипторів сокета при виникненні помилок передачі або прийому даних. Деструктор гарантовано закриє сокет при виході з області видимості.
2. **Динамічний автоматично розширюваний буфер (`std::vector<uint8_t>`):** Замість сирого масиву фіксованого розміру `char buffer[4096]`, вектор гарантує відсутність переповнення буфера (buffer overflow) і динамічно масштабується під будь-яку глибину вкладеності атрибутів `rtattr`.
3. **Безпечна робота зі рядками (`std::string_view`):** Використання `std::string_view` дозволяє передавати імена інтерфейсів без зайвого копіювання пам'яті.
4. **Сучасна обробка помилок (`std::expected<void, std::string>`):** Замість повернення цілочисельних кодів `-1` та виводу в `stderr` через `perror()`, клас `MacvlanBuilder::create()` повертає монадний тип `std::expected`. Це дозволяє викликаючій стороні безпечно обробляти помилки без використання винятків (exceptions).

---

## Особливості обробки помилок та збоїв ядра

Під час відправки повідомлення `RTM_NEWLINK` ядро виконує цілий комплекс перевірок у підсистемі `macvlan_newlink()`:

1. **Перевірка прав привілейованості:** Процес повинен мати мандат `CAP_NET_ADMIN` у мережевому просторі імен. Якщо права відсутні, ядро поверне `EPERM` (Operation not permitted).
2. **Перевірка наявності батьківського пристрою:** Якщо індекс `IFLA_LINK` вказує на неіснуючий пристрій, повертається `ENODEV`.
3. **Перевірка режиму Passthrough:** Якщо створюється інтерфейс у режимі `MACVLAN_MODE_PASSTHROUGH`, а на батьківському пристрої вже існує інший Macvlan-інтерфейс, ядро поверне помилку `EBUSY` (Device or resource busy).
4. **Обмеження пам'яті:** При нестачі системної пам'яті для виділення внутрішньої структури `macvlan_port` повертається `ENOMEM`.

Усі ці помилки повертаються ядром у полі `err->error` структури `struct nlmsgerr` в ACK-пакеті відповіді. Коректне зчитування та логування цього поля є критично важливим для надійної роботи мережевих служб.

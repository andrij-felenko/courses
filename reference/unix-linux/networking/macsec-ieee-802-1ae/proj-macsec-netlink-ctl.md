# ⚙️ Програмування MACsec: налаштування SA та ключів через Netlink

Пряма взаємодія з ядром Linux для створення віртуальних мережевих пристроїв MACsec та управління криптографічними ключами SAK/CAK з власного програмного забезпечення виконується через мережеві сокети **Netlink** (`NETLINK_ROUTE`). Використання системного API усуває залежність від зовнішніх утиліт на кшталт `iproute2` та дозволяє вбудовувати управління MACsec безпосередньо у власні демони автентифікації, мережеві контролери CNI у хмарних середовищах Kubernetes або вбудовані агенти моніторингу.

У ядрі Linux інтерфейс `RTNETLINK` оперує бінарними повідомленнями, кожне з яких складається зі стандартизованого заголовка `struct nlmsghdr`, опису сімейства мережевого об'єкта `struct ifinfomsg` та довільної кількості вкладених атрибутів `struct rtattr`. Оскільки конфігурація MACsec вимагає передачі складних ієрархічних структур (ідентифікатора SCI, прапорців шифрування, режимів розвантаження та криптографічних ключів), ці дані упаковуються у вкладені контейнери Netlink (`IFLA_LINKINFO` -> `IFLA_INFO_DATA`).

Нижче детально розглянуто архітектуру низькорівневого формування цих повідомлень та наведено реалізації двома мовами: класичною C із прямим управлінням пам'яттю та ідіоматичною C++20 із застосуванням концепції RAII, вирівняних контейнерів пам'яті та обробки помилок через `std::expected`.

## Принцип вирівнювання пам'яті та інкапсуляції атрибутів

Під час роботи з Netlink сокетами ключовим вимогою є суворе дотримання 4-байтного вирівнювання для кожного заголовка та атрибута. Ядро Linux очікує, що кожен атрибут `struct rtattr` вирівняно за допомогою макросів `RTA_ALIGN()` та `NLMSG_ALIGN()`. Якщо додаток передасть непакований або невирівняний буфер, ядро поверне помилку `EINVAL` або зчитає сміття з пам'яті.

Послідовність конструювання запиту створення MACsec включає наступні кроки:
1. Ініціалізація заголовка `nlmsghdr` із типом `RTM_NEWLINK` та прапорцями `NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK`. Прапорець `NLM_F_ACK` є обов'язковим, якщо додаток бажає отримати від ядра підтвердження про успішне створення пристрою або корисний код помилки (наприклад, `EEXIST` чи `ENODEV`).
2. Заповнення структури `struct ifinfomsg`, де вказується тип сімейства `AF_UNSPEC`.
3. Додавання базових атрибутів link-рівня: `IFLA_IFNAME` (назва нового пристрою, наприклад `"macsec0"`) та `IFLA_LINK` (числовий індекс батьківського фізичного мережевого адаптера, наприклад `eth0`).
4. Відкриття вкладеного контейнера `IFLA_LINKINFO`, всередині якого вказується атрибут `IFLA_INFO_KIND` зі значенням рядка `"macsec"`.
5. Відкриття другого рівня вкладеності `IFLA_INFO_DATA`, куди упаковуються конкретні константи MACsec: `IFLA_MACSEC_SCI`, `IFLA_MACSEC_ENCRYPT`, `IFLA_MACSEC_WINDOW` тощо.
6. Динамічний перерахунок та закриття довжин `rta_len` для всіх відкритих вкладених контейнерів від внутрішнього до зовнішнього.

:::tabs
```c
/* macsec_control.c — C-реалізація створення та перевірки MACsec через Netlink */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>
#include <linux/if_macsec.h>
#include <net/if.h>

#define NL_BUF_SIZE 4096

/* Допоміжна функція для додавання атрибута Netlink у буфер */
static void add_attr(struct nlmsghdr *nlh, int type, const void *data, int len) {
    int attr_len = RTA_LENGTH(len);
    struct rtattr *rta = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    rta->rta_type = type;
    rta->rta_len = attr_len;
    if (len > 0 && data != NULL) {
        memcpy(RTA_DATA(rta), data, len);
    }
    nlh->nlmsg_len = NLMSG_ALIGN(nlh->nlmsg_len) + RTA_ALIGN(attr_len);
}

/* Створення віртуального пристрою macsec0 поверх eth0 */
int create_macsec_interface(const char *ifname, unsigned int parent_ifindex, uint64_t sci) {
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    if (fd < 0) {
        perror("socket(AF_NETLINK)");
        return -1;
    }

    char buffer[NL_BUF_SIZE];
    memset(buffer, 0, sizeof(buffer));

    struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
    nlh->nlmsg_len = NLMSG_LENGTH(sizeof(struct ifinfomsg));
    nlh->nlmsg_type = RTM_NEWLINK;
    nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
    nlh->nlmsg_seq = 1;

    struct ifinfomsg *ifi = (struct ifinfomsg *)NLMSG_DATA(nlh);
    ifi->ifi_family = AF_UNSPEC;

    /* Назва нового інтерфейсу */
    add_attr(nlh, IFLA_IFNAME, ifname, strlen(ifname) + 1);
    
    /* Базовий батьківський пристрій (eth0) */
    add_attr(nlh, IFLA_LINK, &parent_ifindex, sizeof(parent_ifindex));

    /* Вкладена конфігурація IFLA_LINKINFO */
    struct rtattr *linkinfo = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_LINKINFO, NULL, 0);

    /* Тип посилання: macsec */
    const char *kind = "macsec";
    add_attr(nlh, IFLA_INFO_KIND, kind, strlen(kind) + 1);

    /* Дані конфігурації MACsec */
    struct rtattr *infodata = (struct rtattr *)(((char *)nlh) + NLMSG_ALIGN(nlh->nlmsg_len));
    add_attr(nlh, IFLA_INFO_DATA, NULL, 0);

    /* Встановлення SCI та увімкнення шифрування */
    add_attr(nlh, IFLA_MACSEC_SCI, &sci, sizeof(sci));
    
    uint8_t encrypt = 1;
    add_attr(nlh, IFLA_MACSEC_ENCRYPT, &encrypt, sizeof(encrypt));

    /* Закриваємо довжини вкладених атрибутів */
    infodata->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)infodata;
    linkinfo->rta_len = (char *)nlh + nlh->nlmsg_len - (char *)linkinfo;

    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    if (sendto(fd, nlh, nlh->nlmsg_len, 0, (struct sockaddr *)&sa, sizeof(sa)) < 0) {
        perror("sendto(AF_NETLINK)");
        close(fd);
        return -1;
    }

    /* Читання відповіді ACK від ядра */
    ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
    close(fd);

    if (len < 0) {
        perror("recv(AF_NETLINK)");
        return -1;
    }

    struct nlmsghdr *res = (struct nlmsghdr *)buffer;
    if (res->nlmsg_type == NLMSG_ERROR) {
        struct nlmsgerr *err = (struct nlmsgerr *)NLMSG_DATA(res);
        if (err->error != 0) {
            fprintf(stderr, "Помилка ядра Netlink: %s (%d)\n", strerror(-err->error), err->error);
            return -1;
        }
    }

    printf("Інтерфейс %s успішно створено у ядрі.\n", ifname);
    return 0;
}

int main(void) {
    unsigned int parent_idx = if_nametoindex("eth0");
    if (parent_idx == 0) {
        fprintf(stderr, "Базовий інтерфейс eth0 не знайдено.\n");
        return 1;
    }

    /* SCI: MAC 00:11:22:33:44:55, Port 1 -> 0x0011223344550001ULL */
    uint64_t sci = 0x0011223344550001ULL;
    return create_macsec_interface("macsec0", parent_idx, sci) == 0 ? 0 : 1;
}
```
```cpp
// macsec_control.cpp — Ідіоматична C++20-реалізація з RAII, std::span та std::expected
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <span >
#include <memory>
#include <cstring>
#include <cstdint>
#include <system_error>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/rtnetlink.h>
#include <linux/if_link.h>
#include <linux/if_macsec.h>
#include <net/if.h>

namespace sysnet {

class NetlinkSocket {
    int fd_{-1};
public:
    NetlinkSocket() {
        fd_ = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_ROUTE);
    }
    ~NetlinkSocket() {
        if (fd_ >= 0) ::close(fd_);
    }
    NetlinkSocket(const NetlinkSocket&) = delete;
    NetlinkSocket& operator=(const NetlinkSocket&) = delete;
    NetlinkSocket(NetlinkSocket&& o) noexcept : fd_{o.fd_} { o.fd_ = -1; }

    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int native_handle() const noexcept { return fd_; }
};

class MacsecBuilder {
    std::vector<std::uint8_t> buffer_;

    void add_attribute(std::uint16_t type, std::span<const std::uint8_t> data) {
        auto old_len = buffer_.size();
        std::size_t attr_len = RTA_LENGTH(data.size());
        buffer_.resize(old_len + RTA_ALIGN(attr_len), 0);

        auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + old_len);
        rta->rta_type = type;
        rta->rta_len = static_cast<unsigned short>(attr_len);

        if (!data.empty()) {
            std::memcpy(RTA_DATA(rta), data.data(), data.size());
        }

        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<std::uint32_t>(buffer_.size());
    }

public:
    MacsecBuilder() {
        buffer_.resize(NLMSG_ALIGN(sizeof(struct nlmsghdr) + sizeof(struct ifinfomsg)), 0);
        auto* nlh = reinterpret_cast<struct nlmsghdr*>(buffer_.data());
        nlh->nlmsg_len = static_cast<std::uint32_t>(buffer_.size());
        nlh->nlmsg_type = RTM_NEWLINK;
        nlh->nlmsg_flags = NLM_F_REQUEST | NLM_F_CREATE | NLM_F_EXCL | NLM_F_ACK;
        nlh->nlmsg_seq = 1;

        auto* ifi = reinterpret_cast<struct ifinfomsg*>(NLMSG_DATA(nlh));
        ifi->ifi_family = AF_UNSPEC;
    }

    void add_ifname(std::string_view name) {
        std::vector<std::uint8_t> data(name.begin(), name.end());
        data.push_back(0);
        add_attribute(IFLA_IFNAME, data);
    }

    void add_link(std::uint32_t parent_idx) {
        auto ptr = reinterpret_cast<const std::uint8_t*>(&parent_idx);
        add_attribute(IFLA_LINK, {ptr, sizeof(parent_idx)});
    }

    void build_macsec_payload(std::uint64_t sci, bool encrypt) {
        std::size_t linkinfo_off = buffer_.size();
        add_attribute(IFLA_LINKINFO, {});

        std::string_view kind = "macsec";
        std::vector<std::uint8_t> kind_bytes(kind.begin(), kind.end());
        kind_bytes.push_back(0);
        add_attribute(IFLA_INFO_KIND, kind_bytes);

        std::size_t infodata_off = buffer_.size();
        add_attribute(IFLA_INFO_DATA, {});

        // IFLA_MACSEC_SCI
        auto sci_ptr = reinterpret_cast<const std::uint8_t*>(&sci);
        add_attribute(IFLA_MACSEC_SCI, {sci_ptr, sizeof(sci)});

        // IFLA_MACSEC_ENCRYPT
        std::uint8_t enc = encrypt ? 1 : 0;
        add_attribute(IFLA_MACSEC_ENCRYPT, {&enc, 1});

        // Оновлюємо внутрішні довжини rta_len для вкладених атрибутів
        auto update_len = [this](std::size_t offset) {
            auto* rta = reinterpret_cast<struct rtattr*>(buffer_.data() + offset);
            rta->rta_len = static_cast<unsigned short>(buffer_.size() - offset);
        };

        update_len(infodata_off);
        update_len(linkinfo_off);
    }

    [[nodiscard]] std::span<const std::uint8_t> data() const noexcept {
        return buffer_;
    }
};

[[nodiscard]] std::expected<void, std::string> create_macsec(std::string_view ifname,
                                                              std::string_view parent_ifname,
                                                              std::uint64_t sci) {
    NetlinkSocket nl_sock;
    if (!nl_sock.valid()) {
        return std::unexpected("Не вдалося створити сокет AF_NETLINK");
    }

    unsigned int parent_idx = ::if_nametoindex(parent_ifname.data());
    if (parent_idx == 0) {
        return std::unexpected("Базовий пристрій не знайдено");
    }

    MacsecBuilder builder;
    builder.add_ifname(ifname);
    builder.add_link(parent_idx);
    builder.build_macsec_payload(sci, true);

    auto msg = builder.data();
    struct sockaddr_nl sa{};
    sa.nl_family = AF_NETLINK;

    if (::sendto(nl_sock.native_handle(), msg.data(), msg.size(), 0,
                 reinterpret_cast<struct sockaddr*>(&sa), sizeof(sa)) < 0) {
        return std::unexpected(std::strerror(errno));
    }

    std::vector<std::uint8_t> rx_buf(4096);
    ssize_t len = ::recv(nl_sock.native_handle(), rx_buf.data(), rx_buf.size(), 0);
    if (len < 0) {
        return std::unexpected("Помилка читання з Netlink сокета");
    }

    auto* nlh = reinterpret_cast<struct nlmsghdr*>(rx_buf.data());
    if (nlh->nlmsg_type == NLMSG_ERROR) {
        auto* err = reinterpret_cast<struct nlmsgerr*>(NLMSG_DATA(nlh));
        if (err->error != 0) {
            return std::unexpected(std::strerror(-err->error));
        }
    }

    return {};
}

} // namespace sysnet

int main() {
    constexpr std::uint64_t sci = 0x0011223344550001ULL;
    auto result = sysnet::create_macsec("macsec0", "eth0", sci);
    
    if (!result) {
        std::cerr << "Помилка конфігурації MACsec: " << result.error() << '\n';
        return 1;
    }

    std::cout << "Інтерфейс macsec0 успішно сконфігуровано через C++ Netlink API.\n";
    return 0;
}
```
:::

## Додавання сесійних ключів SAK та захист криптографічних секретів у пам'яті

Після створення віртуального мережевого інтерфейсу наступним кроком є додавання криптографічних ключів **SAK (Secure Association Key)** для шифрування вихідного (TX) та дешифрування вхідного (RX) трафіку.

Передача ключів у ядро виконується додатковим запитом Netlink із типом `RTM_NEWLINK` або `RTM_SETLINK`. У цьому випадку у контейнер `IFLA_INFO_DATA` додається вкладений атрибут `IFLA_MACSEC_SA_CONFIG`. Усередині цього вкладеного контейнера передаються наступні обов'язкові параметри:
1. `MACSEC_SA_ATTR_AN`: Номер слота асоціації (`u8`, значення від `0` до `3`).
2. `MACSEC_SA_ATTR_ACTIVE`: Прапорець активації ключа (`u8`, `1` для включення, `0` для підготовки стоячого ключа).
3. `MACSEC_SA_ATTR_PN`: Початковий номер пакета (`u32` або `u64` для XPN, зазвичай починається з `1`).
4. `MACSEC_SA_ATTR_KEYID`: 16-байтний ідентифікатор ключа (Key ID або CKN).
5. `MACSEC_SA_ATTR_KEY`: Сирий бінарний масив секретного ключа (16 байт для AES-128 або 32 байти для AES-256).

### Гігієна безпеки пам'яті системного процесу

При написанні сервісів, які конфігурують MACsec, важливу роль відіграє захист самого матеріалу ключів у просторі користувача. Сирі ключі SAK та CAK не повинні потрапляти у файли зліпків пам'яті (core dumps) чи витіснятися у файл підкачки (swap).

У C та C++ для забезпечення гігієни пам'яті застосовуються наступні практики:
- **Блокування пам'яті `mlock()`**: Одразу після виділення буфера під ключі додаток викликає `mlock(key_buffer, key_size)`, забороняючи операційній системі вивантажувати цю область пам'яті на диск.
- **Очищення секретів `explicit_bzero()` / `std::fill()`**: Після того як повідомлення Netlink сформовано та відправлено в ядро через системний виклик `sendto()`, локальні буфери ключів у юзерспейсі повинні бути негайно перезаписані нулями за допомогою `explicit_bzero()` (у C) або `std::fill_n(std::atomic_signal_fence)` (у C++). Застосування звичайного `memset()` є небезпечним, оскільки компілятори C/C++ під час оптимізації `-O2/-O3` часто повністю вилучають виклики `memset()`, якщо виділена пам'ять далі не читається програмою.

## Аналіз відмінностей між мовними реалізаціями та крайові випадки

Порівнюючи наведені варіанти реалізації, легко бачити фундаментальну різницю в підходах до управління ресурсами операційної системи.

### C-реалізація та ручний контроль ресурсів

У C-варіанті робота з сокетом `AF_NETLINK` вимагає явного відстеження всіх точок виходу з функції. При виникненні помилки системного виклику `sendto()` або `recv()` програміст повинен самостійно виконати `close(fd)`. Окрім цього, використання сирого байтового масиву `char buffer[NL_BUF_SIZE]` опирається на ручне приведення вказівників `(struct nlmsghdr *)` та `(struct rtattr *)`, що створює ризик помилок типу strict-aliasing або виходу за межі виділеного стекового буфера у випадку складних глибоко вкладених конфігурацій.

### C++20-реалізація: об'єктна безпека та RAII

Версія C++20 усуває перелічені проблеми на рівні компіляції:
1. **Автоматичне управління файловим дескриптором (RAII)**: Клас `NetlinkSocket` гарантує, що файловий дескриптор сокета буде закритий деструктором при виході з функції за будь-яких умов (включаючи повернення помилки або генерацію винятків).
2. **Динамічний безпечний буфер `std::vector<std::uint8_t>`**: Клас `MacsecBuilder` використовує динамічний вектор, який автоматично виділяє необхідний обсяг пам'яті під вкладені атрибути без ризику переповнення буфера.
3. **Безпечні зрізи `std::span`**: Замість сирих вказівників і довжин `(void*, size_t)` C++20 використовує `std::span<const std::uint8_t>`, що унеможливлює передачу некоректного розміру блоку даних.
4. **Прозоре повернення помилок `std::expected`**: Замість негативних кодових чисел або використання глобального `errno` функція повертає `std::expected<void, std::string>`, змушуючи викликаючий код явно обробити результат або прочитати зрозумілий текстовий опис помилки.

### Типові крайові випадки та помилки ядра при роботі з Netlink

Під час програмування конфігурації MACsec розробники найчастіше зіштовхуються з наступними кодами помилок ядра:
- **`EEXIST` (-17)**: Віртуальний пристрій з назвою `macsec0` вже існує в даному мережевому просторі імен (netns).
- **`ENODEV` (-19)**: Батьківський фізичний пристрій (наприклад `eth0`) не знайдено за вказаним `IFLA_LINK` індексом.
- **`EINVAL` (-22)**: Некоректний розмір атрибута (наприклад, довжина ключа SAK не відповідає обраній криптосвіті або значення SCI передано з помилковим вирівнюванням).
- **`EOPNOTSUPP` (-95)**: Модуль ядра `macsec.ko` не завантажено, або була зроблена спроба увімкнути `offload mac` на мережевій карті, драйвер якої не реалізує структуру `macsec_ops`.

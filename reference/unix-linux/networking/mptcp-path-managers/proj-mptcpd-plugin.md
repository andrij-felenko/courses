# ⚙️ Реалізація плагіна mptcpd та аналізатора подій Netlink

У цій вставці наведено розширені практичні приклади коду та вичерпний покроковий посібник зі створення власного плагіна керування шляхами для демона `mptcpd`, а також розбір побудови автономного низькорівневого аналізатора та контролера Generic Netlink подій MPTCP без залучення демонів.

---

## 1. Архітектура та принципи розробки плагінів для mptcpd

Системний демон `mptcpd` слугує мостом між мультикаст-подіями Generic Netlink ядра Linux та прикладною логікою керування мережевими шляхами. Основний бінарний файл `mptcpd` реалізує лише загальну інфраструктуру: з'єднання із сокетом Netlink, парсинг бінарних атрибутів NLA та завантаження плагінів.

Вся бізнес-логіка прийняття рішень (наприклад, "відкрити підпотік через 5G лише тоді, коли Wi-Fi сигнал нижчий за -80 dBm") виноситься у динамічні плагіни (Plugins).

### Життєвий цикл та збірка плагіна

Плагін `mptcpd` являє собою динамічну бібліотеку (`.so`), яка повинна відповідати наступним вимогам:

1. **Експорт символів C ABI**: навіть якщо плагін написаний мовою C++, точка входу та структура опису плагіна мають компілюватися з макросом `extern "C"` та використовувати стандартну таблицю манглінгу C.
2. **Реєстрація через макрос `MPTCPD_PLUGIN_REGISTER`**: цей макрос формує спеціальну секцію метаданих у ELF-файлі бібліотеки, яку `mptcpd` зчитує під час виклику `dlopen()`.
3. **Обробка подій без блокування основного потоку**: callbacks плагіна викликаються в контексті головного циклу подій демона (Event Loop на базі бібліотеки `ell` або `glib`). Якщо обробник виконує тривалі блокуючі операції (наприклад, синхронний HTTP-запит до сервера), це призведе до зависання обробки нових пакетів Netlink.

---

## 2. Реалізація плагіна мовами C та C++

Нижче наведено ідіоматичні реалізації плагіна для `mptcpd`. Плагін перехоплює події оголошення нових віддалених IP-адрес (`MPTCP_EVENT_ANNOUNCED`), виконує перевірку безпеки мережевого діапазону та надсилає ядру наказ відкрити новий підпотік.

### Розбір C-реалізації
У версії мовою C виклик `mptcpd_pm_add_subflow()` отримує покажчики на вихідні структури `struct sockaddr`. Обробка рядків виконана через безпечну POSIX-функцію `inet_ntop()`, а помилки аналізуються через повернений цілочисельний код `errno`.

### Розбір C++-реалізації
У версії мовою C++23 код інкапсульовано у стани класи `PathPolicyEngine`. Замість винятків або сирих кодових помилок використовується `std::expected<T, E>`, що гарантує відсутність накладних витрат на unwinding стека. Зрізи рядків обробляються через `std::string_view`, а IP-адреси зберігаються у статично розміщених масивах `std::array<char, N>`.

:::tabs
```c
/* C Implementation: Modern mptcpd plugin */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <arpa/inet.h>
#include <mptcpd/plugin.h>
#include <mptcpd/pm.h>

static void handle_new_address(struct mptcpd_pm *pm,
                               uint32_t token,
                               mptcpd_aid_t remote_id,
                               struct sockaddr const *remote_addr,
                               void *user_data)
{
    (void)user_data;
    char ip_str[INET6_ADDRSTRLEN] = {0};
    uint16_t port = 0;

    if (remote_addr->sa_family == AF_INET) {
        struct sockaddr_in const *in = (struct sockaddr_in const *)remote_addr;
        inet_ntop(AF_INET, &in->sin_addr, ip_str, sizeof(ip_str));
        port = ntohs(in->sin_port);
    } else if (remote_addr->sa_family == AF_INET6) {
        struct sockaddr_in6 const *in6 = (struct sockaddr_in6 const *)remote_addr;
        inet_ntop(AF_INET6, &in6->sin6_addr, ip_str, sizeof(ip_str));
        port = ntohs(in6->sin6_port);
    }

    printf("[mptcpd-c-plugin] Connection 0x%08x: New remote address ID %u -> %s:%u\n",
           token, remote_id, ip_str, port);

    /* Фільтрація безпеки: ігнорувати оголошення з тестових мереж 192.168.99.0/24 */
    if (strncmp(ip_str, "192.168.99.", 11) == 0) {
        printf("[mptcpd-c-plugin] Ignoring address %s per security filter\n", ip_str);
        return;
    }

    /* Наказ ядру створити новий підпотік з локального ID 0 */
    mptcpd_aid_t const local_id = 0;
    struct sockaddr_in local_addr;
    memset(&local_addr, 0, sizeof(local_addr));
    local_addr.sin_family = AF_INET;
    local_addr.sin_addr.s_addr = INADDR_ANY;

    int const error = mptcpd_pm_add_subflow(pm,
                                            token,
                                            local_id,
                                            remote_id,
                                            (struct sockaddr const *)&local_addr,
                                            remote_addr,
                                            false); /* backup = false */

    if (error != 0) {
        fprintf(stderr, "[mptcpd-c-plugin] Failed to order subflow creation: %s\n",
                strerror(error));
    }
}

static struct mptcpd_plugin_ops const pm_ops = {
    .new_address = handle_new_address
};

MPTCPD_PLUGIN_REGISTER(c_custom_policy, &pm_ops, NULL, NULL)
```
```cpp
// C++ Implementation: Modern idiomatic mptcpd plugin with RAII & std::expected
#include <iostream>
#include <string_view>
#include <array>
#include <expected>
#include <system_error>
#include <arpa/inet.h>
#include <mptcpd/plugin.h>
#include <mptcpd/pm.h>

namespace mptcp::policy {

class PathPolicyEngine {
public:
    static void on_new_address(mptcpd_pm* pm,
                              uint32_t token,
                              mptcpd_aid_t remote_id,
                              sockaddr const* remote_addr,
                              void* /* user_data */) noexcept 
    {
        auto const addr_info = parse_address(remote_addr);
        if (!addr_info) {
            std::cerr << "[mptcpd-cpp-plugin] Error parsing remote address structure\n";
            return;
        }

        auto const [ip_view, port] = *addr_info;
        std::cout << "[mptcpd-cpp-plugin] Connection 0x" << std::hex << token
                  << std::dec << ": Remote address ID " << static_cast<int>(remote_id)
                  << " -> " << ip_view << ":" << port << "\n";

        // Політика: не створювати підпотік до адрес з ізольованої підмережі
        if (ip_view.starts_with("192.168.99.")) {
            std::cout << "[mptcpd-cpp-plugin] Ignoring subnet 192.168.99.x per policy\n";
            return;
        }

        sockaddr_in local_addr{};
        local_addr.sin_family = AF_INET;
        local_addr.sin_addr.s_addr = INADDR_ANY;

        mptcpd_aid_t constexpr local_id = 0;
        bool constexpr is_backup = false;

        int const err = mptcpd_pm_add_subflow(pm,
                                              token,
                                              local_id,
                                              remote_id,
                                              reinterpret_cast<sockaddr const*>(&local_addr),
                                              remote_addr,
                                              is_backup);
        if (err != 0) {
            std::cerr << "[mptcpd-cpp-plugin] Error ordering subflow: " 
                      << std::generic_category().message(err) << "\n";
        }
    }

private:
    struct EndpointInfo {
        std::string ip;
        uint16_t port;
    };

    static std::expected<EndpointInfo, std::errc> parse_address(sockaddr const* addr) noexcept {
        if (!addr) return std::unexpected(std::errc::invalid_argument);

        std::array<char, INET6_ADDRSTRLEN> buffer{};
        uint16_t port = 0;

        if (addr->sa_family == AF_INET) {
            auto const* in = reinterpret_cast<sockaddr_in const*>(addr);
            if (!inet_ntop(AF_INET, &in->sin_addr, buffer.data(), buffer.size())) {
                return std::unexpected(std::errc::address_family_not_supported);
            }
            port = ntohs(in->sin_port);
        } else if (addr->sa_family == AF_INET6) {
            auto const* in6 = reinterpret_cast<sockaddr_in6 const*>(addr);
            if (!inet_ntop(AF_INET6, &in6->sin6_addr, buffer.data(), buffer.size())) {
                return std::unexpected(std::errc::address_family_not_supported);
            }
            port = ntohs(in6->sin6_port);
        } else {
            return std::unexpected(std::errc::address_family_not_supported);
        }

        return EndpointInfo{ std::string(buffer.data()), port };
    }
};

} // namespace mptcp::policy

extern "C" {
    static mptcpd_plugin_ops const cpp_pm_ops = {
        .new_address = &mptcp::policy::PathPolicyEngine::on_new_address
    };

    MPTCPD_PLUGIN_REGISTER(cpp_custom_policy, &cpp_pm_ops, nullptr, nullptr)
}
```
:::

---

## 3. Покрокова збірка та інсталяція плагіна

Для компіляції плагінів необхідна наявність заголовочних файлів бібліотеки `libmptcpd` (пакет `libmptcpd-dev` у Debian/Ubuntu або `mptcpd-devel` у Fedora/RHEL).

### Компіляція C-плагіна:

```bash
gcc -shared -fPIC -O2 -Wall \
    -o libmptcpd_c_policy.so c_plugin.c \
    $(pkg-config --cflags --libs mptcpd)
```

### Компіляція C++ плагіна (з підтримкою C++23):

```bash
g++ -shared -fPIC -O2 -std=c++23 -Wall \
    -o libmptcpd_cpp_policy.so cpp_plugin.cpp \
    $(pkg-config --cflags --libs mptcpd)
```

### Розміщення та налаштування демона:

1. Скопіюйте створений файл `.so` у системний каталог плагінів `mptcpd`:
   ```bash
   sudo cp libmptcpd_cpp_policy.so /usr/lib/x86_64-linux-gnu/mptcpd/
   ```
2. Вкажіть ім'я завантажуваного плагіна у конфігураційному файлі `/etc/mptcpd/mptcpd.conf`:
   ```ini
   [mptcpd]
   plugin=cpp_custom_policy
   ```
3. Перезапустіть демон `mptcpd` та перевірте журнали `journalctl`:
   ```bash
   sudo systemctl restart mptcpd
   sudo journalctl -u mptcpd -f
   ```

---

## 4. Автономний низькорівневий сокетний аналізатор Generic Netlink

У вбудованих системах із обмеженими ресурсами (наприклад, маршрутизаторах OpenWrt) встановлення демона `mptcpd` може бути небажаним через додаткові залежності від бібліотек `glib` або `ell`.

У таких випадках розробник може реалізувати автономний слухач Netlink, який створює сирий сокет `AF_NETLINK`, підписується на мультикаст-групу `subflow` та самостійно розпаковує NLA-атрибути.

### Особливості сокетного аналізатора
Під час ініціалізації сокета у структурі `sockaddr_nl` встановлюється бітова маска `nl_groups = 0x1`. Це підключає сокет до першої мультикаст-групи сімейства Generic Netlink.

У C++ версії реалізовано клас `NetlinkSocket`, який повністю слідує принципу RAII (Resource Acquisition Is Initialization): конструктор приймає дескриптор, а деструктор гарантує виклик `close()` при виході з області видимості чи обробці винятків.

:::tabs
```c
/* C Implementation: Standalone POSIX Netlink event monitor */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>

#define MPTCP_GENL_NAME "mptcp"
#define MPTCP_GENL_EV_GRP "subflow"

int create_netlink_mptcp_socket(void)
{
    int fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
    if (fd < 0) {
        perror("[c-netlink] socket AF_NETLINK");
        return -1;
    }

    struct sockaddr_nl local;
    memset(&local, 0, sizeof(local));
    local.nl_family = AF_NETLINK;
    local.nl_groups = 0x1; /* Підписка на мультикаст-групу подій MPTCP */

    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0) {
        perror("[c-netlink] bind netlink");
        close(fd);
        return -1;
    }

    return fd;
}

void process_event_stream(int fd)
{
    char buffer[8192];
    while (1) {
        ssize_t len = recv(fd, buffer, sizeof(buffer), 0);
        if (len < 0) {
            perror("[c-netlink] recv netlink");
            break;
        }

        struct nlmsghdr *nlh = (struct nlmsghdr *)buffer;
        while (NLMSG_OK(nlh, len)) {
            if (nlh->nlmsg_type == NLMSG_DONE) break;
            if (nlh->nlmsg_type == NLMSG_ERROR) {
                fprintf(stderr, "[c-netlink] Received Netlink error payload\n");
                break;
            }

            struct genlmsghdr *genl = (struct genlmsghdr *)NLMSG_DATA(nlh);
            printf("[c-netlink] Event Generic Netlink Cmd ID: %u, Version: %u\n",
                   genl->cmd, genl->version);

            nlh = NLMSG_NEXT(nlh, len);
        }
    }
}
```
```cpp
// C++ Implementation: RAII Modern Standalone Netlink socket monitor
#include <iostream>
#include <vector>
#include <memory>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <linux/genetlink.h>

namespace mptcp::netlink {

class NetlinkSocket {
public:
    explicit NetlinkSocket(int fd) noexcept : fd_(fd) {}

    ~NetlinkSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    NetlinkSocket(NetlinkSocket const&) = delete;
    NetlinkSocket& operator=(NetlinkSocket const&) = delete;

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

    [[nodiscard]] static std::expected<NetlinkSocket, std::error_code> create(uint32_t multicast_group) noexcept {
        int fd = ::socket(AF_NETLINK, SOCK_RAW, NETLINK_GENERIC);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        sockaddr_nl local{};
        local.nl_family = AF_NETLINK;
        local.nl_groups = multicast_group;

        if (::bind(fd, reinterpret_cast<sockaddr*>(&local), sizeof(local)) < 0) {
            int const err = errno;
            ::close(fd);
            return std::unexpected(std::error_code(err, std::generic_category()));
        }

        return NetlinkSocket{ fd };
    }

    void listen_loop() const {
        std::vector<uint8_t> buffer(8192);

        while (true) {
            ssize_t const bytes_read = ::recv(fd_, buffer.data(), buffer.size(), 0);
            if (bytes_read < 0) {
                std::cerr << "[cpp-netlink-mon] Receive error: " 
                          << std::generic_category().message(errno) << "\n";
                break;
            }

            auto* nlh = reinterpret_cast<nlmsghdr*>(buffer.data());
            auto remaining = static_cast<size_t>(bytes_read);

            while (NLMSG_OK(nlh, remaining)) {
                if (nlh->nlmsg_type == NLMSG_DONE) break;
                if (nlh->nlmsg_type == NLMSG_ERROR) {
                    std::cerr << "[cpp-netlink-mon] Netlink payload error message\n";
                    break;
                }

                auto const* genl = static_cast<genlmsghdr const*>(NLMSG_DATA(nlh));
                std::cout << "[cpp-netlink-mon] Received MPTCP Event Cmd ID: " 
                          << static_cast<int>(genl->cmd) << "\n";

                nlh = NLMSG_NEXT(nlh, remaining);
            }
        }
    }

private:
    int fd_ = -1;
};

} // namespace mptcp::netlink
```
:::

---

## 5. Обробка помилок та гонитва станів (Race Conditions)

При розробці виробничих плагінів необхідно враховувати асинхронну природу мережевого стека Linux.

### Гонитва станів при флаппінгу інтерфейсів (Interface Flapping)
Якщо мережевий адаптер (наприклад, Wi-Fi) швидкісно перепідключається, ядро надсилає події `MPTCP_EVENT_ANNOUNCED` та `MPTCP_EVENT_REMOVED` послідовно із мінімальними інтервалами. 

Якщо плагін відправить команду `MPTCP_PM_CMD_SUBFLOW_CREATE` в момент, коли віддалена адреса вже стала недоступною, ядро поверне помилку Netlink `-ECONNREFUSED` або `-ETIMEDOUT`. Плагін повинен корисно обробляти ці помилки і не накопичувати висячі запити в пам'яті.

### Життєвий цикл токена (Token Lifetime)
Токен з'єднання (`token`) існує лише доти, доки MPTCP-з'єднання перебуває в активному стані. Як тільки приходить подія `MPTCP_EVENT_CLOSED`, токен видаляється з хеш-таблиці ядра. Будь-які наступні команди з цим токеном будуть мовчки відхилені ядром із помилкою `-ENOENT`.

---

## 6. Налагодження та діагностика плагінів

Для відлагодження написаних плагінів демон `mptcpd` можна запустити в інтерактивному режимі з розширеним журналюванням:

```bash
sudo mptcpd --debug --log=stdout
```

Для аналізу витоків пам'яті у плагіні використовується `valgrind`:

```bash
sudo valgrind --leak-check=full --show-leak-kinds=all mptcpd --log=stdout
```

А для зупинки процесу на точках зупинки (breakpoints) у callback-функціях плагіна використовується відлагоджувач `gdb`:

```bash
sudo gdb --args mptcpd --log=stdout
(gdb) b handle_new_address
(gdb) run
```

---

## 7. Порівняльний аналіз підходів до розробки

1. **Плагіни mptcpd**: надають готовий високорівневий C API, автоматично беруть на себе роботу з резолюцією Generic Netlink ID та маршалінгом атрибутів. Оптимальний вибір для стандартних дистрибутивів Linux (Ubuntu, Debian, RHEL).
2. **Прямий сокет Netlink**: забезпечує абсолютний контроль, відсутність сторонніх залежностей та мінімальний розмір підсумкового бінарного файлу. Оптимальний вибір для закритих прошивок та систем реального часу.

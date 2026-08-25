# ⚙️ Низькорівневий зонд NDP: розв'язання L2-адреси через сокети ICMPv6

У класичних мережах IPv4 діагностичні утиліти на зразок `arping` змушені працювати безпосередньо з канальним рівнем: відкривати сокети сімейства `AF_PACKET` у режимі `SOCK_RAW`, вручну формувати 14-байтовий заголовок кадру Ethernet (з кодом типу протоколу `ETH_P_ARP = 0x0806`), заповнювати поля структури `struct ether_arp` та самостійно керувати мережевими кільцевими буферами мережевої карти. Такий підхід вимагає прямої прив'язки до формату конкретного канального середовища і не працює на інтерфейсах без заголовків Ethernet (наприклад, у тунелях або віртуальних інтерфейсах).

У протоколі IPv6 архітектуру розв'язання адрес було докорінно переосмислено. Замість окремого протоколу L2 операції Neighbor Discovery Protocol (NDP) реалізовані як складова частина протоколу мережевого рівня ICMPv6 (`IPPROTO_ICMPV6`, код 58). Це дає розробнику можливість створювати системні інструменти зондування, моніторингу та інвентаризації мережевих сусідів через стандартні сокети `AF_INET6` типу `SOCK_RAW`, довіряючи ядру маршрутизацію та інкапсуляцію пакетів, але повністю контролюючи логіку протоколу та розбір опцій.

---

### Архітектура та математика розрахунку адрес

Процес розв'язання адреси складається з трьох строго визначених фаз: обчислення цільової адреси групової розсилки, формування корисного навантаження ICMPv6 із канальними опціями та забезпечення обов'язкових інваріантів безпеки каналу.

#### 1. Обчислення адреси Solicited-Node Multicast

У мережах IPv4 запит ARP надсилався на широкомовну адресу `255.255.255.255` (канальний MAC `ff:ff:ff:ff:ff:ff`). Кожен комп'ютер у сегменті змушений був переривати центральний процесор, передавати кадр у стек ОС і лише там відкидати його, якщо IP не збігалася.

У IPv6 широкомовлення повністю скасоване. Запит Neighbor Solicitation (NS) відправляється на спеціальну групову адресу **Solicited-Node Multicast**, яка обчислюється за формулою:

```
Solicited-Node Адреса = ff02::1:ff00:0/104 ∪ (Цільова IPv6-адреса & 0x00ffffff)
```

Старші 104 біти є фіксованими (`ff02:0000:0000:0000:0001:ff00::/104`), а молодші 24 біти беруться без змін із цільової адреси, яку ми зондуємо. Наприклад, якщо цільова адреса дорівнює `2001:db8::12:3456`, то останні три байти становлять `0x12, 0x34, 0x56`. Результуюча адреса групової розсилки набуває вигляду `ff02::1:ff12:3456`.

Мережевий адаптер цільового вузла при призначенні адреси автоматично підписується на цю групу в мікросхемі контролера (через хеш-таблицю фільтрації мультикасту). Усі інші вузли сегмента, у яких молодші 24 біти адреси відрізняються, відкидають такий кадр на рівні кремнію мережевої карти без залучення операційної системи та процесора.

#### 2. Формування структури пакета та опції Source Link-Layer Address

Пакет Neighbor Solicitation складається з базового заголовка повідомлення `struct nd_neighbor_solicit` (тип 135, підкод 0, 4 байти зарезервованого поля та 16 байтів цільової адреси) і допоміжної опції Source Link-Layer Address (тип опції 1, довжина 1 блок = 8 байтів). 

В опцію обов'язково записується 6-байтова апаратна MAC-адреса інтерфейсу відправника. Отримавши запит, цільовий вузол негайно зберігає MAC-адресу джерела у своєму системному кеші сусідів і надсилає відповідь Neighbor Advertisement (тип 136) уже прямим адресним пакетом (Unicast) без повторного розв'язання адрес.

#### 3. Інваріант ліміту переходів (Hop Limit = 255)

Відповідно до розділу 6.1.1 стандарту RFC 4861, ядро приймача зобов'язане перевірити поле `Hop Limit` у заголовку IPv6. Якщо значення менше ніж 255, пакет вважається згенерованим віддаленим зловмисником через маршрутизатор і негайно скидається. При створенні сокета `SOCK_RAW` операційна система за замовчуванням може підставляти системне значення `Hop Limit` (наприклад, 64). Тому програма зобов'язана явно викликати `setsockopt` з параметрами `IPV6_MULTICAST_HOPS = 255` та `IPV6_UNICAST_HOPS = 255`.

---

### Системні виклики та взаємодія з ядром Linux

Для коректної роботи сирого сокета ICMPv6 програма взаємодіє з трьома підсистемами ядра Linux:

1. **Підсистема керування інтерфейсами (SIOCGIFHWADDR):** Для заповнення опції Source Link-Layer Address необхідно знати фізичну MAC-адресу локального адаптера. Програма викликає системний виклик `ioctl` із командою `SIOCGIFHWADDR` над структурою `struct ifreq`. Сучасні сервіси також можуть використовувати сокети Netlink `NETLINK_ROUTE` та повідомлення `RTM_GETLINK`, проте `ioctl` лишається найпростішим і найнадійнішим POSIX-сумісним способом отримання MAC-адреси.
2. **Прив'язка до пристрою (SO_BINDTODEVICE):** Оскільки пакети Link-Local та Multicast мають локальну область дії каналу (Scope ID), маршрутизатор без явної вказівки інтерфейсу не знає, через яку фізичну карту відправляти пакет. Опція сокета `SO_BINDTODEVICE` жорстко прив'язує сокет до імені інтерфейсу (наприклад, `eth0`), що унеможливлює витік діагностичних зондів на сторонні інтерфейси.
3. **Обробка фільтрації ICMPv6 у ядрі:** Ядро Linux автоматично розраховує 16-бітну контрольну суму для всіх вихідних пакетів через сокети `IPPROTO_ICMPV6`. При цьому вхідні повідомлення ICMPv6 проходять через спільний обробник ядра `icmpv6_rcv()` у файлі `net/ipv6/icmp.c`, який дублює пакет усім відкритим сирим сокетам з відповідним типом протоколу.

---

### Реалізація утиліти зондування `ndp_probe`

Нижче наведено повний вихідний код утиліти двома мовами: на чистому C (з використанням системних структур Linux UAPI) та на ідіоматичному C++20 (із застосуванням RAII для дескрипторів, `std::span` для безпечного розбору байтових опцій, типізованих контейнерів та `std::format`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/icmp6.h>
#include <arpa/inet.h>

#define SOLICITED_NODE_PREFIX "ff02::1:ff00:0"
#define PACKET_BUFFER_SIZE 1500

/* Отримання апаратної MAC-адреси локального мережевого інтерфейсу */
static int get_interface_mac(int sock, const char *ifname, uint8_t *mac_out) {
    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);

    if (ioctl(sock, SIOCGIFHWADDR, &ifr) < 0) {
        perror("ioctl(SIOCGIFHWADDR)");
        return -1;
    }
    memcpy(mac_out, ifr.ifr_hwaddr.sa_data, 6);
    return 0;
}

/* Розрахунок адреси Solicited-Node Multicast за цільовою IPv6 */
static void make_solicited_node_addr(const struct in6_addr *target, struct in6_addr *solicited_out) {
    inet_pton(AF_INET6, SOLICITED_NODE_PREFIX, solicited_out);
    /* Підставляємо молодші 24 біти (останні 3 байти) цільової адреси */
    solicited_out->s6_addr[13] = target->s6_addr[13];
    solicited_out->s6_addr[14] = target->s6_addr[14];
    solicited_out->s6_addr[15] = target->s6_addr[15];
}

int main(int argc, char *argv[]) {
    if (argc < 3) {
        fprintf(stderr, "Використання: %s <інтерфейс> <цільова-IPv6-адреса>\n", argv[0]);
        return 1;
    }

    const char *ifname = argv[1];
    const char *target_ip_str = argv[2];

    struct in6_addr target_ip;
    if (inet_pton(AF_INET6, target_ip_str, &target_ip) != 1) {
        fprintf(stderr, "Помилка: некоректний формат IPv6-адреси: %s\n", target_ip_str);
        return 1;
    }

    unsigned int ifindex = if_nametoindex(ifname);
    if (ifindex == 0) {
        fprintf(stderr, "Помилка: не знайдено мережевий інтерфейс %s\n", ifname);
        return 1;
    }

    /* Створення raw-сокета для протоколу ICMPv6 */
    int sock = socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6);
    if (sock < 0) {
        perror("socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6)");
        fprintf(stderr, "Примітка: для роботи з сирими сокетами потрібні привілеї root (sudo).\n");
        return 1;
    }

    uint8_t local_mac[6];
    if (get_interface_mac(sock, ifname, local_mac) < 0) {
        close(sock);
        return 1;
    }

    /* Встановлення обов'язкового ліміту переходів Hop Limit = 255 */
    int hops = 255;
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_MULTICAST_HOPS, &hops, sizeof(hops)) < 0) {
        perror("setsockopt(IPV6_MULTICAST_HOPS)");
        close(sock);
        return 1;
    }
    if (setsockopt(sock, IPPROTO_IPV6, IPV6_UNICAST_HOPS, &hops, sizeof(hops)) < 0) {
        perror("setsockopt(IPV6_UNICAST_HOPS)");
        close(sock);
        return 1;
    }

    /* Таймаут очікування відповіді на сокеті (2 секунди) */
    struct timeval tv = { .tv_sec = 2, .tv_usec = 0 };
    if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
        perror("setsockopt(SO_RCVTIMEO)");
        close(sock);
        return 1;
    }

    /* Прив'язка сокета до конкретного фізичного інтерфейсу */
    if (setsockopt(sock, SOL_SOCKET, SO_BINDTODEVICE, ifname, strlen(ifname)) < 0) {
        perror("setsockopt(SO_BINDTODEVICE)");
        close(sock);
        return 1;
    }

    /* Формування пакетного буфера: заголовок NS + опція Source Link-Layer */
    struct {
        struct nd_neighbor_solicit ns_hdr;
        struct nd_opt_hdr opt_hdr;
        uint8_t mac[6];
    } __attribute__((packed)) probe_pkt;

    memset(&probe_pkt, 0, sizeof(probe_pkt));
    probe_pkt.ns_hdr.nd_ns_type = ND_NEIGHBOR_SOLICIT;
    probe_pkt.ns_hdr.nd_ns_code = 0;
    probe_pkt.ns_hdr.nd_ns_target = target_ip;

    /* Опція 1: Source Link-Layer Address (довжина 1 блок = 8 байтів) */
    probe_pkt.opt_hdr.nd_opt_type = ND_OPT_SOURCE_LINKADDR;
    probe_pkt.opt_hdr.nd_opt_len = 1;
    memcpy(probe_pkt.mac, local_mac, 6);

    /* Формування адреси призначення */
    struct sockaddr_in6 dst_addr;
    memset(&dst_addr, 0, sizeof(dst_addr));
    dst_addr.sin6_family = AF_INET6;
    dst_addr.sin6_scope_id = ifindex;
    make_solicited_node_addr(&target_ip, &dst_addr.sin6_addr);

    char solicited_str[INET6_ADDRSTRLEN];
    inet_ntop(AF_INET6, &dst_addr.sin6_addr, solicited_str, sizeof(solicited_str));
    printf("Надсилання Neighbor Solicitation для %s на %s%%%s...\n",
           target_ip_str, solicited_str, ifname);

    ssize_t sent = sendto(sock, &probe_pkt, sizeof(probe_pkt), 0,
                          (struct sockaddr *)&dst_addr, sizeof(dst_addr));
    if (sent < 0) {
        perror("sendto");
        close(sock);
        return 1;
    }

    /* Цикл отримання та аналізу відповідей NA */
    uint8_t recv_buf[PACKET_BUFFER_SIZE];
    while (1) {
        struct sockaddr_in6 src_addr;
        socklen_t addr_len = sizeof(src_addr);
        ssize_t recvd = recvfrom(sock, recv_buf, sizeof(recv_buf), 0,
                                 (struct sockaddr *)&src_addr, &addr_len);
        if (recvd < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                fprintf(stderr, "Час очікування вичерпано: вузол %s не відповів.\n", target_ip_str);
            } else {
                perror("recvfrom");
            }
            close(sock);
            return 1;
        }

        if (recvd < (ssize_t)sizeof(struct nd_neighbor_advert)) {
            continue;
        }

        struct nd_neighbor_advert *na = (struct nd_neighbor_advert *)recv_buf;
        if (na->nd_na_type != ND_NEIGHBOR_ADVERT || na->nd_na_code != 0) {
            continue;
        }

        /* Звіряємо, чи це відповідь саме на нашу цільову адресу */
        if (memcmp(&na->nd_na_target, &target_ip, sizeof(struct in6_addr)) != 0) {
            continue;
        }

        char responder_ip[INET6_ADDRSTRLEN];
        inet_ntop(AF_INET6, &src_addr.sin6_addr, responder_ip, sizeof(responder_ip));

        printf("Отримано Neighbor Advertisement від %s!\n", responder_ip);
        printf("Прапорці: [Router=%d, Solicited=%d, Override=%d]\n",
               (na->nd_na_flags_reserved & ND_NA_FLAG_ROUTER) ? 1 : 0,
               (na->nd_na_flags_reserved & ND_NA_FLAG_SOLICITED) ? 1 : 0,
               (na->nd_na_flags_reserved & ND_NA_FLAG_OVERRIDE) ? 1 : 0);

        /* Парсинг ланцюжка опцій: шукаємо Target Link-Layer Address (Type 2) */
        uint8_t *opts = recv_buf + sizeof(struct nd_neighbor_advert);
        ssize_t opts_len = recvd - sizeof(struct nd_neighbor_advert);
        int mac_found = 0;

        while (opts_len >= 8) {
            uint8_t opt_type = opts[0];
            uint8_t opt_len_units = opts[1];
            if (opt_len_units == 0) break;
            size_t opt_bytes = (size_t)opt_len_units * 8;
            if (opt_bytes > (size_t)opts_len) break;

            if (opt_type == ND_OPT_TARGET_LINKADDR && opt_bytes >= 8) {
                uint8_t *target_mac = opts + 2;
                printf("Знайдено MAC-адресу: %02x:%02x:%02x:%02x:%02x:%02x\n",
                       target_mac[0], target_mac[1], target_mac[2],
                       target_mac[3], target_mac[4], target_mac[5]);
                mac_found = 1;
                break;
            }
            opts += opt_bytes;
            opts_len -= opt_bytes;
        }

        if (!mac_found) {
            printf("У відповіді NA відсутня опція Target Link-Layer Address.\n");
        }

        break;
    }

    close(sock);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <format>
#include <chrono>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <net/if.h>
#include <netinet/in.h>
#include <netinet/icmp6.h>
#include <arpa/inet.h>

namespace net {

/* RAII-обгортка для автоматичного керування життєвим циклом сокета */
class UniqueSocket {
public:
    UniqueSocket() noexcept : fd_(-1) {}
    explicit UniqueSocket(int fd) noexcept : fd_(fd) {}
    ~UniqueSocket() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    UniqueSocket(const UniqueSocket&) = delete;
    UniqueSocket& operator=(const UniqueSocket&) = delete;

    UniqueSocket(UniqueSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    UniqueSocket& operator=(UniqueSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }

private:
    int fd_;
};

/* Отримання апаратної адреси MAC інтерфейсу */
inline std::array<uint8_t, 6> get_interface_mac(int sock_fd, std::string_view ifname) {
    struct ifreq ifr{};
    std::strncpy(ifr.ifr_name, ifname.data(), IFNAMSIZ - 1);

    if (::ioctl(sock_fd, SIOCGIFHWADDR, &ifr) < 0) {
        throw std::system_error(errno, std::generic_category(), "ioctl(SIOCGIFHWADDR) завершився помилкою");
    }

    std::array<uint8_t, 6> mac{};
    std::memcpy(mac.data(), ifr.ifr_hwaddr.sa_data, 6);
    return mac;
}

/* Формування адреси Solicited-Node Multicast */
inline in6_addr make_solicited_node_address(const in6_addr& target) noexcept {
    in6_addr solicited{};
    ::inet_pton(AF_INET6, "ff02::1:ff00:0", &solicited);
    solicited.s6_addr[13] = target.s6_addr[13];
    solicited.s6_addr[14] = target.s6_addr[14];
    solicited.s6_addr[15] = target.s6_addr[15];
    return solicited;
}

} // namespace net

int main(int argc, char* argv[]) {
    try {
        if (argc < 3) {
            std::cerr << "Використання: " << argv[0] << " <інтерфейс> <цільова-IPv6-адреса>\n";
            return 1;
        }

        const std::string_view ifname = argv[1];
        const std::string_view target_ip_str = argv[2];

        in6_addr target_ip{};
        if (::inet_pton(AF_INET6, target_ip_str.data(), &target_ip) != 1) {
            std::cerr << "Помилка: некоректний формат адреси: " << target_ip_str << "\n";
            return 1;
        }

        unsigned int ifindex = ::if_nametoindex(ifname.data());
        if (ifindex == 0) {
            std::cerr << "Помилка: мережевий інтерфейс " << ifname << " не знайдено\n";
            return 1;
        }

        net::UniqueSocket sock(::socket(AF_INET6, SOCK_RAW, IPPROTO_ICMPV6));
        if (!sock.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка відкриття raw-сокета (потрібен sudo)");
        }

        const auto local_mac = net::get_interface_mac(sock.get(), ifname);

        int hops = 255;
        if (::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_MULTICAST_HOPS, &hops, sizeof(hops)) < 0 ||
            ::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_UNICAST_HOPS, &hops, sizeof(hops)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Не вдалося встановити Hop Limit = 255");
        }

        struct timeval tv{ .tv_sec = 2, .tv_usec = 0 };
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(SO_RCVTIMEO) failed");
        }

        if (::setsockopt(sock.get(), SOL_SOCKET, SO_BINDTODEVICE, ifname.data(), ifname.size()) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(SO_BINDTODEVICE) failed");
        }

        struct ProbePacket {
            struct nd_neighbor_solicit ns_hdr;
            struct nd_opt_hdr opt_hdr;
            uint8_t mac[6];
        } __attribute__((packed));

        ProbePacket pkt{};
        pkt.ns_hdr.nd_ns_type = ND_NEIGHBOR_SOLICIT;
        pkt.ns_hdr.nd_ns_code = 0;
        pkt.ns_hdr.nd_ns_target = target_ip;
        pkt.opt_hdr.nd_opt_type = ND_OPT_SOURCE_LINKADDR;
        pkt.opt_hdr.nd_opt_len = 1;
        std::memcpy(pkt.mac, local_mac.data(), 6);

        sockaddr_in6 dst_addr{};
        dst_addr.sin6_family = AF_INET6;
        dst_addr.sin6_scope_id = ifindex;
        dst_addr.sin6_addr = net::make_solicited_node_address(target_ip);

        char solicited_buf[INET6_ADDRSTRLEN]{};
        ::inet_ntop(AF_INET6, &dst_addr.sin6_addr, solicited_buf, sizeof(solicited_buf));
        std::cout << "Надсилання Neighbor Solicitation для " << target_ip_str
                  << " на " << solicited_buf << "%" << ifname << "...\n";

        ssize_t sent = ::sendto(sock.get(), &pkt, sizeof(pkt), 0,
                                reinterpret_cast<const sockaddr*>(&dst_addr), sizeof(dst_addr));
        if (sent < 0) {
            throw std::system_error(errno, std::generic_category(), "sendto failed");
        }

        std::array<uint8_t, 1500> recv_buf{};
        while (true) {
            sockaddr_in6 src_addr{};
            socklen_t addr_len = sizeof(src_addr);
            ssize_t recvd = ::recvfrom(sock.get(), recv_buf.data(), recv_buf.size(), 0,
                                       reinterpret_cast<sockaddr*>(&src_addr), &addr_len);
            if (recvd < 0) {
                if (errno == EAGAIN || errno == EWOULDBLOCK) {
                    std::cerr << "Час очікування вичерпано: сусід не відповів на зонд.\n";
                    return 1;
                }
                throw std::system_error(errno, std::generic_category(), "recvfrom failed");
            }

            if (recvd < static_cast<ssize_t>(sizeof(struct nd_neighbor_advert))) {
                continue;
            }

            const auto* na = reinterpret_cast<const struct nd_neighbor_advert*>(recv_buf.data());
            if (na->nd_na_type != ND_NEIGHBOR_ADVERT || na->nd_na_code != 0) {
                continue;
            }

            if (std::memcmp(&na->nd_na_target, &target_ip, sizeof(in6_addr)) != 0) {
                continue;
            }

            char resp_buf[INET6_ADDRSTRLEN]{};
            ::inet_ntop(AF_INET6, &src_addr.sin6_addr, resp_buf, sizeof(resp_buf));
            std::cout << "Отримано Neighbor Advertisement від " << resp_buf << "!\n";

            std::span<const uint8_t> options(recv_buf.data() + sizeof(struct nd_neighbor_advert),
                                             recvd - sizeof(struct nd_neighbor_advert));
            bool mac_found = false;

            while (options.size() >= 8) {
                uint8_t opt_type = options[0];
                uint8_t opt_len_units = options[1];
                if (opt_len_units == 0) break;
                size_t opt_bytes = static_cast<size_t>(opt_len_units) * 8;
                if (opt_bytes > options.size()) break;

                if (opt_type == ND_OPT_TARGET_LINKADDR && opt_bytes >= 8) {
                    const auto* target_mac = options.data() + 2;
                    std::cout << std::format("Знайдено MAC-адресу: {:02x}:{:02x}:{:02x}:{:02x}:{:02x}:{:02x}\n",
                                             target_mac[0], target_mac[1], target_mac[2],
                                             target_mac[3], target_mac[4], target_mac[5]);
                    mac_found = true;
                    break;
                }
                options = options.subspan(opt_bytes);
            }

            if (!mac_found) {
                std::cout << "У відповіді NA опція MAC-адреси відсутня.\n";
            }
            break;
        }

        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
}
```
:::

---

### Покроковий розбір виконання та діагностика

Збірка утиліти виконується стандартними компіляторами GCC або Clang:

```bash
# Компіляція версії C:
gcc -O2 -Wall -Wextra ndp_probe.c -o ndp_probe_c

# Компіляція версії C++20:
g++ -O2 -std=c++20 -Wall -Wextra ndp_probe.cpp -o ndp_probe_cpp
```

Запуск вимагає прав суперкористувача для створення сирого сокета `SOCK_RAW`:

```bash
sudo ./ndp_probe_cpp eth0 2001:db8:1::42
```

Приклад виводу програми в консолі:
```text
Надсилання Neighbor Solicitation для 2001:db8:1::42 на ff02::1:ff00:42%eth0...
Отримано Neighbor Advertisement від fe80::5054:ff:fe12:3456!
Прапорці: [Router=1, Solicited=1, Override=1]
Знайдено MAC-адресу: 52:54:00:12:34:56
```

Паралельний моніторинг через утиліту `tcpdump` надійно ілюструє повний цикл обміну повідомленнями:

```bash
sudo tcpdump -i eth0 -vv -n "icmp6 and (ip6[40] == 135 or ip6[40] == 136)"
```

У дампах чітко видно:
1. Запит `ICMP6, neighbor solicitation, who has 2001:db8:1::42, length 32`: пакет прямує на групову адресу `ff02::1:ff00:42`, має `hlim 255` та містить опцію `source link-address: 52:54:00:aa:bb:cc`.
2. Відповідь `ICMP6, neighbor advertisement, tgt is 2001:db8:1::42, length 32`: пакет повертається безпосередньо як unicast, містить прапорці `(rtr, solicited, override)` та опцію `target link-address: 52:54:00:12:34:56`.

---

### Детальний аналіз обробки пакетів у ядрі

Коли ядро отримує відповідь Neighbor Advertisement, воно виконує строгу валідацію за стандартом RFC 4861:

1. **Перевірка довжини та контрольної суми:** Загальна довжина пакета ICMPv6 повинна бути не меншою за 24 байти (розмір `struct nd_neighbor_advert`). Контрольна сума перевіряється апаратно мережевою картою (Rx Checksum Offloading) або програмно в `icmpv6_rcv()`.
2. **Перевірка поля Hop Limit:** Якщо `Hop Limit != 255`, пакет відкидається без надсилання будь-яких ICMP-помилок назад відправнику.
3. **Перевірка поля Target Address:** Цільова адреса не повинна бути адресою групової розсилки (Multicast). Якщо вона починається з префікса `ff00::/8`, пакет вважається шкідливим і відкидається.
4. **Валідація прапорців (R, S, O):** Якщо встановлено прапорець `S = 1`, ядро шукає відповідний запис у кеші зі станом `INCOMPLETE` або `PROBE`. Якщо запис знайдено, він негайно переводиться у стан `REACHABLE`, а черга відкладених пакетів відправляється сусідові.

---

### Допоміжні керуючі дані сокета (Ancillary Control Data)

У професійних мережевих демонах для отримання точного значення `Hop Limit` та індексу інтерфейсу використовують виклик `recvmsg()` з керуючими повідомленнями ядра (`struct cmsghdr`). Для цього на сокеті вмикають опції `IPV6_RECVHOPLIMIT` та `IPV6_RECVPKTINFO`:

:::tabs
```c
int on = 1;
if (setsockopt(sock, IPPROTO_IPV6, IPV6_RECVHOPLIMIT, &on, sizeof(on)) < 0 ||
    setsockopt(sock, IPPROTO_IPV6, IPV6_RECVPKTINFO, &on, sizeof(on)) < 0) {
    perror("setsockopt ancillary flags");
}
```
```cpp
int on = 1;
if (::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_RECVHOPLIMIT, &on, sizeof(on)) < 0 ||
    ::setsockopt(sock.get(), IPPROTO_IPV6, IPV6_RECVPKTINFO, &on, sizeof(on)) < 0) {
    throw std::system_error(errno, std::generic_category(), "Failed to set ancillary control flags");
}
```
:::

При читанні повідомлення через `recvmsg()` ядро додає в допоміжний буфер блок керування `IP6PO_HOPLIMIT`, де програма може безпосередньо у просторі користувача верифікувати, що отримане повідомлення не прийшло ззовні через підроблений маршрутизатор.

---

### Асинхронний моніторинг подій сусідів через Netlink (RTMGRP_NEIGH)

Окрім активного зондування через сирі сокети, сучасні демони маршрутизації (FRRouting, BIRD) та агенти спостереження за інфраструктурою (Prometheus Node Exporter) використовують асинхронні сокети ядра Netlink. Замість періодичного опитування таблиці сусідів через `/proc/net` програма підписується на мультикаст-групу ядра `RTMGRP_NEIGH`.

При зміні стану будь-якого запису в кеші (наприклад, перехід із `REACHABLE` у `STALE` або `FAILED`) підсистема `net/core/neighbour.c` генерує подію `RTM_NEWNEIGH` або `RTM_DELNEIGH`. Структура повідомлення Netlink містить заголовок `struct nlmsghdr`, після якого слідує заголовок сусіда `struct ndmsg` та атрибути `NDA_DST`, `NDA_LLADDR` і `NDA_CACHEINFO`. Це дозволяє програмі в реальному часі реагувати на втрату фізичного зв'язку з сусідом без створення паразитного трафіку на каналі.

---

### Статуси інтерфейсів під час автоконфігурації (Tentative та DAD)

При створенні системного демона слід враховувати стан адрес самого локального інтерфейсу. Коли на адаптері з'являється нова Link-Local або Global адреса через механізм SLAAC, вона не стає активною миттєво. Операційна система позначає її системним прапорцем `IFA_F_TENTATIVE` (у Linux це перевіряється через структуру `ifaddrmsg` у відповідях Netlink).

У цей період (тривалістю зазвичай 1 секунду) адреса перебуває на перевірці унікальності DAD (Duplicate Address Detection). Стек відправляє власний зонд Neighbor Solicitation із невизначеною адресою джерела `::`. Якщо протягом таймауту надійшла відповідь Neighbor Advertisement (або зустрічний запит NS з такою самою цільовою адресою), фіксується колізія: адреса переходить у стан `IFA_F_DADFAILED` і вимикається. Якщо відповідей не надійшло, прапорець `IFA_F_TENTATIVE` знімається, і стек дозволяє сокетам відкривати з'єднання з цієї адреси.

---

### Особливості зондування Anycast-адрес та серверних кластерів

У протоколі IPv6 широко використовується адресація Anycast (RFC 4291): одна й та сама глобальна або локальна IPv6-адреса призначається кільком різним серверам чи маршрутизаторам у межах одного або різних сегментів для балансування навантаження (наприклад, для кореневих DNS-серверів або шлюзів резервування).

При роботі зонда NDP з anycast-адресами виникають специфічні протокольні відмінності, зафіксовані в RFC 4861:

1. **Заборона адреси Anycast як джерела:** Вузол, що відповідає на запит NS для anycast-адреси, ніколи не має права ставити цю anycast-адресу в поле джерела IPv6 Source. Він зобов'язаний використовувати власну унікальну Unicast-адресу (наприклад, Link-Local `fe80::...`).
2. **Прапорець Override (`O = 0`):** У відповіді Neighbor Advertisement на anycast-запит прапорець `Override` **обов'язково скидається в 0**. Це критично важливо: якщо кілька серверів у локальному сегменті відповідають на один і той самий NS-запит своїми різними MAC-адресами, отримувач записує в кеш першу отриману відповідь і не перезаписує її наступними пакетами. Це запобігає постійному «тремтінню» (flapping) L2-кешу при розв'язанні кластерних адрес.
3. **Випадкова затримка відповіді:** Щоб уникнути колізій у фізичному каналі, коли сотні хостів одночасно відповідають на запит anycast або групової розсилки, стандарт вимагає від вузла робити випадкову затримку перед відправленням NA в діапазоні від 0 до `MAX_RTR_SOLICITATION_DELAY` (зазвичай 0–500 мс).

---

### Порівняння продуктивності: розв'язання адрес у залізі (ASIC)

У сучасних комутаторах ядра та дата-центрів (Broadcom Tomahawk, Cisco Cloud Scale, Marvell Prestera) обробка пакетів розв'язання адрес здійснюється на апаратному рівні:

* **IPv4 ARP:** Широкомовні кадри надходять у так звану чергу винятків процесора (CPU Exception Queue / CoPP — Control Plane Policing). Коли в L2-домені на 10 000 хостів трапляється широкомовний шторм, процесор комутатора перевантажується на 100%, викликаючи падіння протоколів BGP та OSPF.
* **IPv6 NDP:** Групова розсилка Solicited-Node Multicast обробляється апаратною таблицею точного збігу L2 Multicast (EM / TCAM). Комутатор за допомогою апаратного хешування пересилає кадр NS виключно на той порт, де зареєстрований отримувач даної мультикаст-групи. Це повністю захищає магістральні процесори та інші сервери стійки від побічного паразитного навантаження.

---

### Типові пастки та крайові випадки при реалізації NDP

Під час практичної розробки мережевого програмного забезпечення та низькорівневих зондів протоколу NDP виникає низка специфічних інженерних проблем:

1. **Контрольна сума в сокетах `IPPROTO_ICMPV6`:**
   У сокетах IPv4 для протоколів вищого рівня розробник повинен був вручну розраховувати 16-бітну контрольну суму або вмикати спеціальні опції. У сокетах `IPPROTO_ICMPV6` ядро Linux **завжди самостійно** розраховує та записує контрольну суму ICMPv6 перед передачею кадру драйверу. Якщо програміст спробує заповнити поле `nd_ns_cksum` вручну, ядро розрахує суму повторно над уже зміненими даними, що призведе до спотворення пакета і його відкидання цільовим вузлом.

2. **Вплив фільтрації MLD (Multicast Listener Discovery) на комутаторах:**
   У корпоративних керованих мережах комутатори L2 за замовчуванням мають увімкнену функцію **MLD Snooping** (аналог IGMP Snooping для IPv6). Комутатор відстежує повідомлення MLDv2 і пересилає мультикаст-кадри `33:33:xx:xx:xx:xx` лише на ті порти, які явно заявили про членство у групі. Якщо цільовий сервер через збій у демоні мережі не відправив MLD Report для своєї solicited-node адреси, комутатор заблокує доставку запиту NS, і зонд завершиться помилкою таймауту, хоча фізичний зв'язок присутній.

3. **Блокування ICMPv6 міжмережевими екранами (Firewalls):**
   Часта помилка системних адміністраторів — копіювання старих правил iptables з IPv4, де весь протокол ICMP блокувався з міркувань приховування хостів. У IPv6 блокування типів ICMPv6 133–137 (NDP) та 143 (MLD) призводить до повної втрати зв'язності: вузли не можуть з'ясувати MAC-адреси сусідів, адреси зависають у стані `NUD_INCOMPLETE`, а процес SLAAC перестає отримувати префікси підмережі.

4. **Атаки вичерпання кешу сусідів (NDP Table Exhaustion):**
   Оскільки стандартна підмережа IPv6 містить 2⁶⁴ адрес (18 квінтильйонів), зловмисник може надсилати потоки пакетів на випадкові псевдовипадкові адреси всередині локальної підмережі. Маршрутизатор на кожен такий пакет змушений генерувати NS-запит і створювати запис у стані `INCOMPLETE`. Для захисту від вичерпання оперативної пам'яті ядра системні адміністратори тюнінгують параметри збирача сміття (Garbage Collector):
   ```bash
   sudo sysctl -w net.ipv6.neigh.default.gc_thresh1=1024
   sudo sysctl -w net.ipv6.neigh.default.gc_thresh2=2048
   sudo sysctl -w net.ipv6.neigh.default.gc_thresh3=4096
   ```
   При досягненні порога `gc_thresh3` ядро негайно починає агресивно відкидати нові спроби створення непідтверджених записів.

5. **Безпека каналу та підробка оголошень (RA Guard / SAVI):**
   У незахищених сегментах будь-який вузол може надіслати підроблене повідомлення Router Advertisement, оголосивши себе пріоритетним шлюзом за замовчуванням (атака Rogue RA / Man-in-the-Middle). Для запобігання цьому на портах комутаторів впроваджують технологію **IPv6 RA Guard** (RFC 6105), яка блокує повідомлення типу 134 на клієнтських портах доступу, дозволяючи їх проходження лише з довірених портів маршрутизаторів.

6. **Криптографічний захист SEND (Secure Neighbor Discovery, RFC 3971):**
   Для математичного захисту від підробки адрес було розроблено протокол SEND на основі криптографічно згенерованих адрес CGA (Cryptographically Generated Addresses, RFC 3972). У CGA молодші 64 біти адреси (Interface ID) обчислюються як криптографічний хеш відкритого ключа вузла RSA/ECC та випадкового модифікатора. Кожне повідомлення NDP містить цифровий підпис (RSA Signature Option) та відкритий ключ. Отримувач перевіряє, що відправник дійсно володіє закритим ключем, який відповідає даній IPv6-адресі, що повністю виключає можливість підробки MAC або IP сусіда навіть за відсутності централізованого посвідчувального центру (CA).

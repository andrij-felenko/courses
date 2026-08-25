# ⚙️ Реалізація користувацького мережевого інтерфейсу та тунелю

У цій практичній роботі розглянуто повноцінний приклад створення та обробки користувацького мережевого пристрою TUN у системі Linux. Програма ініціалізує віртуальний інтерфейс `tun0`, переходить у неблокуючий режим I/O, реєструє файловий дескриптор у циклі обробки подій `epoll` та впорскує відповіді ICMP Echo Reply (ping) безпосередньо в мережевий стек ядра.

## Архітектура та принцип роботи неблокуючого маршрутизатора

Створення користувацького тунелю або віртуального маршрутизатора спирається на три фундаментальні концепції системного програмування в Linux:
1. **Динамічне виділення мережевого пристрою:** Програма відкриває символьний пристрій `/dev/net/tun` і за допомогою системного виклику `ioctl(fd, TUNSETIFF, &ifr)` запитує створення інтерфейсу `tun0`. Прапорець `IFF_TUN` позначає пристрій рівнем L3 (IP-пакети), а прапорець `IFF_NO_PI` відключає додавання 4-байтового метазаголовка `struct tun_pi`, забезпечуючи роботу з чистими IP-пакетами.
2. **Асинхронний неблокуючий режим:** За замовчуванням виклик `read()` на файловому дескрипторі `/dev/net/tun` блокує виконання потоку, якщо черга прийому порожня. Для забезпечення високої продуктивності дескриптор переводиться у неблокуючий режим за допомогою `fcntl(fd, F_SETFL, O_NONBLOCK)`. Якщо при спробі читання кадри відсутні, ядро негайно повертає помилку `EAGAIN` або `EWOULDBLOCK`.
3. **Мультиплексування подій I/O через `epoll`:** Замість постійного опитування (polling) у нескінченному циклі, що даремно завантажує процесор, програма реєструє дескриптор у механізмі `epoll` з прапорцями `EPOLLIN` (наявність даних для читання) та `EPOLLET` (Edge-Triggered режим). У режимі `EPOLLET` ядро сповіщає потік про надходження даних лише один раз при зміні стану черги, що вимагає вичитування всіх доступних пакетів у циклі до отримання `EAGAIN`.

## Механізм обробки та модифікації пакетів

Коли локальний процес або зовнішній вузол відправляє ICMP Echo Request (команда `ping 10.0.0.2`), ядро спрямовує пакет через пристрій `tun0`. Програма зчитує пакет з дескриптора і виконує наступну послідовність кроків:
- **Перевірка заголовка IPv4:** Програма аналізує перші байти буфера. Вона перевіряє версію IP (повинна дорівнювати 4) та тип протоколу верхнього рівня (`iph->protocol == IPPROTO_ICMP`).
- **Розрахунок зсуву заголовка:** Довжина заголовка IP визначається полем `ihl` (Internet Header Length), яке вказує кількість 32-бітних слів. Зсув до заголовка ICMP обчислюється як `ip_hdr_len = iph->ihl * 4`.
- **Аналіз ICMP-заголовка:** Програма перевіряє поле `icmph->type`. Якщо воно дорівнює `ICMP_ECHO` (значення 8), пакет підлягає обробці.
- **Модифікація та перерахунок контрольних сум:**
  - IP-адреси відправника (`saddr`) та одержувача (`daddr`) міняються місцями.
  - Поле типу ICMP змінюється з `ICMP_ECHO` (8) на `ICMP_ECHOREPLY` (0).
  - Контрольні суми в заголовках IP та ICMP обнуляються і перераховуються за формулою доповнення до одиниці (One's Complement Sum) 16-бітних слів.
- **Впорскування відповіді:** Модифікований буфер записується назад у дескриптор за допомогою системного виклику `write(tun_fd, buf, len)`. Ядро сприймає цей пакет як вхідний кадр із мережі і доставляє його у вихідний сокет `ping`.

## Внутрішня динаміка сокетних буферів sk_buff та пам'яті ядра

Під час виконання викликів `read()` та `write()` над файловим дескриптором `/dev/net/tun` усередині ядра відбуваються складні маніпуляції з пам'яттю:
- При записі `write(tun_fd, buf, len)` драйвер ядра викликає функцію `tun_alloc_skb()`, яка запитує з ядерного слаб-алокатора (SLAB/SLUB) структуру `struct sk_buff`.
- Пам'ять для тіла пакета виділяється з урахуванням вирівнювання за межами кеш-ліній процесора (Cache Line Alignment) та можливих заголовків розвантаження `struct virtio_net_hdr`.
- Функція `copy_from_user()` виконує безпечне перенесення байтів із простору користувача у ядерний буфер `skb->data`. Якщо адреса буфера користувача виявляється невалідною або нерозміченою у сторінках пам'яті, системний виклик переривається з помилкою `EFAULT`.
- Після формування заголовків драйвер викликає `netif_rx(skb)`. Ця функція поміщає `sk_buff` у чергу вхідних пакетів поточного ядра ЦП (`softnet_data.input_pkt_queue`) і генерує програмне переривання `NET_RX_SOFTIRQ`.

## Практична реалізація: C та C++

Нижче наведено паралельні реалізації віртуального маршрутизатора у вигляді мульти-вкладки. Версія на C++20 надає повноцінну RAII-обгортку над дескриптором пристрою та `epoll`, усуває витоки ресурсів та використовує `std::span` для безпечної роботи зі зрізами пам'яті.

:::tabs
```c
/* tun_router.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <linux/if.h>
#include <linux/if_tun.h>

#define MAX_EVENTS 8
#define BUF_SIZE 2048

/* Обчислення контрольної суми IP/ICMP за формулою доповнення до одиниці */
static uint16_t checksum(const void *data, size_t len) {
    const uint16_t *buf = (const uint16_t *)data;
    uint32_t sum = 0;
    while (len > 1) {
        sum += *buf++;
        len -= 2;
    }
    if (len == 1) {
        sum += *(const uint8_t *)buf;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}

/* Відкриття та налаштування TUN пристрою */
static int tun_alloc(char *dev, int flags) {
    struct ifreq ifr;
    int fd, err;

    if ((fd = open("/dev/net/tun", O_RDWR)) < 0) {
        perror("Failed to open /dev/net/tun");
        return -1;
    }

    memset(&ifr, 0, sizeof(ifr));
    ifr.ifr_flags = flags;

    if (*dev) {
        strncpy(ifr.ifr_name, dev, IFNAMSIZ - 1);
    }

    if ((err = ioctl(fd, TUNSETIFF, (void *)&ifr)) < 0) {
        perror("ioctl(TUNSETIFF) failed");
        close(fd);
        return -1;
    }

    strcpy(dev, ifr.ifr_name);
    return fd;
}

/* Переведення файлового дескриптора в неблокуючий режим */
static int set_nonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) return -1;
    return fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

/* Обробка IPv4 пакета та генерація ICMP Echo Reply */
static void process_packet(int tun_fd, uint8_t *buf, ssize_t len) {
    if (len < (ssize_t)sizeof(struct iphdr)) return;

    struct iphdr *iph = (struct iphdr *)buf;
    if (iph->version != 4 || iph->protocol != IPPROTO_ICMP) return;

    size_t ip_hdr_len = iph->ihl * 4;
    if (len < (ssize_t)(ip_hdr_len + sizeof(struct icmphdr))) return;

    struct icmphdr *icmph = (struct icmphdr *)(buf + ip_hdr_len);

    /* Перевіряємо, чи це ICMP Echo Request */
    if (icmph->type == ICMP_ECHO) {
        /* Міняємо місцями Src IP та Dst IP */
        uint32_t tmp_ip = iph->saddr;
        iph->saddr = iph->daddr;
        iph->daddr = tmp_ip;

        /* Міняємо тип ICMP на Echo Reply */
        icmph->type = ICMP_ECHOREPLY;
        icmph->checksum = 0;
        
        /* Перераховуємо контрольну суму ICMP */
        size_t icmp_len = len - ip_hdr_len;
        icmph->checksum = checksum(icmph, icmp_len);

        /* Перераховуємо контрольну суму IP */
        iph->check = 0;
        iph->check = checksum(iph, ip_hdr_len);

        /* Відправляємо пакет назад у TUN */
        ssize_t written = write(tun_fd, buf, len);
        if (written > 0) {
            printf("[C] ICMP Echo Reply sent back (%zd bytes)\n", written);
        }
    }
}

int main(void) {
    char dev_name[IFNAMSIZ] = "tun0";
    int tun_fd = tun_alloc(dev_name, IFF_TUN | IFF_NO_PI);
    if (tun_fd < 0) return EXIT_FAILURE;

    printf("[C] TUN interface %s created (fd=%d)\n", dev_name, tun_fd);
    if (set_nonblocking(tun_fd) < 0) {
        perror("Failed to set non-blocking");
        close(tun_fd);
        return EXIT_FAILURE;
    }

    int epoll_fd = epoll_create1(0);
    if (epoll_fd < 0) {
        perror("epoll_create1 failed");
        close(tun_fd);
        return EXIT_FAILURE;
    }

    struct epoll_event ev, events[MAX_EVENTS];
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = tun_fd;

    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, tun_fd, &ev) < 0) {
        perror("epoll_ctl failed");
        close(epoll_fd);
        close(tun_fd);
        return EXIT_FAILURE;
    }

    uint8_t buffer[BUF_SIZE];
    printf("[C] Event loop started. Run in terminal:\n");
    printf("    sudo ip link set %s up\n", dev_name);
    printf("    sudo ip addr add 10.0.0.1/24 dev %s\n", dev_name);
    printf("    ping 10.0.0.2\n");

    for (int i = 0; i < 5; ++i) { /* Обробляємо кілька подій для демонстрації */
        int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 5000);
        if (nfds < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait error");
            break;
        }

        for (int n = 0; n < nfds; ++n) {
            if (events[n].data.fd == tun_fd) {
                while (1) {
                    ssize_t bytes_read = read(tun_fd, buffer, sizeof(buffer));
                    if (bytes_read < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                        perror("read from tun failed");
                        break;
                    }
                    process_packet(tun_fd, buffer, bytes_read);
                }
            }
        }
    }

    close(epoll_fd);
    close(tun_fd);
    printf("[C] TUN router finished cleanly.\n");
    return EXIT_SUCCESS;
}
```
```cpp
// tun_router.cpp — Ідіоматична реалізація C++20 (RAII, span, std::expected/exceptions)
#include <iostream>
#include <vector>
#include <span>
#include <memory>
#include <system_error>
#include <string_view>
#include <cstring>
#include <cstdint>

#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <linux/if.h>
#include <linux/if_tun.h>

namespace tuntap {

// RAII обгортка над дескриптором TUN-пристрою
class TunDevice {
private:
    int fd_{-1};
    std::string name_;

public:
    explicit TunDevice(std::string_view dev_name, int flags = IFF_TUN | IFF_NO_PI) {
        fd_ = ::open("/dev/net/tun", O_RDWR | O_NONBLOCK);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to open /dev/net/tun");
        }

        struct ifreq ifr{};
        ifr.ifr_flags = static_cast<short>(flags);
        if (!dev_name.empty()) {
            std::strncpy(ifr.ifr_name, dev_name.data(), IFNAMSIZ - 1);
        }

        if (::ioctl(fd_, TUNSETIFF, reinterpret_cast<void*>(&ifr)) < 0) {
            ::close(fd_);
            throw std::system_error(errno, std::generic_category(), "ioctl(TUNSETIFF) failed");
        }

        name_ = ifr.ifr_name;
    }

    ~TunDevice() noexcept {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    TunDevice(const TunDevice&) = delete;
    TunDevice& operator=(const TunDevice&) = delete;

    TunDevice(TunDevice&& other) noexcept : fd_(other.fd_), name_(std::move(other.name_)) {
        other.fd_ = -1;
    }

    TunDevice& operator=(TunDevice&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            name_ = std::move(other.name_);
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }
    [[nodiscard]] const std::string& name() const noexcept { return name_; }

    [[nodiscard]] std::ssize_t read(std::span<std::uint8_t> buffer) const {
        return ::read(fd_, buffer.data(), buffer.size());
    }

    [[nodiscard]] std::ssize_t write(std::span<const std::uint8_t> packet) const {
        return ::write(fd_, packet.data(), packet.size());
    }
};

// RAII обгортка над epoll
class EpollSelector {
private:
    int epoll_fd_{-1};

public:
    EpollSelector() {
        epoll_fd_ = ::epoll_create1(0);
        if (epoll_fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_create1 failed");
        }
    }

    ~EpollSelector() noexcept {
        if (epoll_fd_ >= 0) ::close(epoll_fd_);
    }

    void add_fd(int fd, std::uint32_t events) {
        struct epoll_event ev{};
        ev.events = events;
        ev.data.fd = fd;
        if (::epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, fd, &ev) < 0) {
            throw std::system_error(errno, std::generic_category(), "epoll_ctl ADD failed");
        }
    }

    [[nodiscard]] int wait(std::span<struct epoll_event> events_out, int timeout_ms) const {
        return ::epoll_wait(epoll_fd_, events_out.data(), static_cast<int>(events_out.size()), timeout_ms);
    }
};

// Обчислення контрольної суми
uint16_t calculate_checksum(std::span<const std::uint8_t> data) {
    std::uint32_t sum = 0;
    std::size_t i = 0;
    while (i + 1 < data.size()) {
        std::uint16_t word = static_cast<std::uint16_t>(data[i]) | (static_cast<std::uint16_t>(data[i+1]) << 8);
        sum += word;
        i += 2;
    }
    if (i < data.size()) {
        sum += data[i];
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<std::uint16_t>(~sum);
}

void process_icmp_reply(const TunDevice& tun, std::span<std::uint8_t> pkt) {
    if (pkt.size() < sizeof(struct iphdr)) return;

    auto* iph = reinterpret_cast<struct iphdr*>(pkt.data());
    if (iph->version != 4 || iph->protocol != IPPROTO_ICMP) return;

    std::size_t ip_hdr_len = iph->ihl * 4;
    if (pkt.size() < ip_hdr_len + sizeof(struct icmphdr)) return;

    auto* icmph = reinterpret_cast<struct icmphdr*>(pkt.data() + ip_hdr_len);
    if (icmph->type == ICMP_ECHO) {
        std::swap(iph->saddr, iph->daddr);
        icmph->type = ICMP_ECHOREPLY;
        icmph->checksum = 0;

        icmph->checksum = calculate_checksum(pkt.subspan(ip_hdr_len));
        iph->check = 0;
        iph->check = calculate_checksum(pkt.subspan(0, ip_hdr_len));

        std::ssize_t sent = tun.write(pkt);
        if (sent > 0) {
            std::cout << "[C++] Generated ICMP Echo Reply (" << sent << " bytes)\n";
        }
    }
}

} // namespace tuntap

int main() {
    try {
        tuntap::TunDevice tun("tun0");
        std::cout << "[C++] Virtual interface initialized: " << tun.name() << "\n";

        tuntap::EpollSelector selector;
        selector.add_fd(tun.native_handle(), EPOLLIN | EPOLLET);

        std::vector<std::uint8_t> buffer(2048);
        std::vector<struct epoll_event> events(8);

        for (int i = 0; i < 5; ++i) {
            int nfds = selector.wait(events, 5000);
            for (int n = 0; n < nfds; ++n) {
                if (events[n].data.fd == tun.native_handle()) {
                    while (true) {
                        std::ssize_t nread = tun.read(buffer);
                        if (nread < 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) break;
                            perror("read error");
                            break;
                        }
                        tuntap::process_icmp_reply(tun, std::span<std::uint8_t>(buffer.data(), nread));
                    }
                }
            }
        }
    } catch (const std::exception& ex) {
        std::cerr << "Fatal error: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

## Покроковий порядок компіляції та налагодження

Щоб запустити та продіагностувати роботу програму у реальному середовищі Linux:

1. **Компіляція вихідного коду:**
   ```bash
   # Компіляція версії C
   gcc -O2 -Wall tun_router.c -o tun_router_c

   # Компіляція версії C++20
   g++ -std=c++20 -O2 -Wall tun_router.cpp -o tun_router_cpp
   ```

2. **Запуск із необхідними привілеями:**
   Створення віртуальних мережевих пристроїв вимагає привілеїв суперкористувача або наявності ролі `CAP_NET_ADMIN`:
   ```bash
   sudo ./tun_router_cpp
   ```

3. **Конфігурація інтерфейсу в іншому терміналі:**
   У той час як програма утримує відкритим файловий дескриптор, інтерфейс `tun0` з'являється у списку пристроїв ядра. Його необхідно підняти та надати IP-адресу:
   ```bash
   sudo ip link set tun0 up
   sudo ip addr add 10.0.0.1/24 dev tun0
   ```

4. **Тестування обміну пакетами:**
   Надішліть ICMP запит на будь-яку IP-адресу з виділеної підмережі (наприклад, `10.0.0.2`):
   ```bash
   ping -c 4 10.0.0.2
   ```

5. **Спостереження через підсистеми ядра та простеження (Tracing):**
   Ви можете простежити проходження пакетів через лічильники ядра та файлову систему `/proc`:
   ```bash
   # Перегляд статистики пакетів інтерфейсу tun0
   cat /proc/net/dev | grep tun0

   # Моніторинг подій у реальному часі через tcpdump
   sudo tcpdump -n -i tun0

   # Відстеження виклику netif_rx у ядрі через tracepoints
   sudo trace-cmd record -e net:netif_rx -e net:net_dev_xmit
   ```

## Наслідки та крайові випадки (Edge Cases)

При розробці виробничих тунелів на базі TUN/TAP необхідно враховувати наступні крайові випадки:
- **Переповнення черги ядра (Buffer Overflow):** Якщо програма користувача не встигає зчитувати кадри з файлового дескриптора, черга `tx_array` в ядрі заповнюється до ліміту `txqueuelen` (за замовчуванням 500 або 1000 пакетів). Після цього ядро починає скидати нові пакети (packet drops), що відображається у лічильнику `dropped` у `/proc/net/dev`.
- **Розмір MTU та фрагментація:** Стандартний розмір MTU для TUN-інтерфейсу становить 1500 байт. Якщо програма додає власний заголовок шифрування (наприклад, 40 байт для UDP/IP/Crypto в OpenVPN), підсумковий зовнішній пакет перевищить MTU фізичного інтерфейсу `eth0`, що призведе до IP-фрагментації або скидання через налаштований прапор `DF` (Don't Fragment). Для запобігання цьому MTU віртуального пристрою зменшують (наприклад, до `1420` байт).
- **Раптове завершення процесу:** Якщо процес завершується аварійно (сигнал `SIGKILL`), ядро автоматично закриває файловий дескриптор і видаляє тимчасовий пристрій `tun0` разом із прив'язаними маршрутами. Якщо ж інтерфейс було зроблено постійним (`TUNSETPERSIST`), він залишається в системі у стані `DOWN`.
- **Багатопотокова синхронізація в epoll:** У багатопотокових реакторах при використанні `EPOLLET` кілька робочих потоків можуть одночасно спробувати читати з одного дескриптора, що вимагає використання прапорця `EPOLLONESHOT` та повторної реєстрації дескриптора після вичитування черги.

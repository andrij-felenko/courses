# ⚙️ Практична реалізація SSM-клієнта й сервера та діагностика в Linux

Підключення до каналу Source-Specific Multicast (SSM) на рівні системного сокетного програмування вимагає принципово іншого підходу, ніж робота з класичними відкритими групами Any-Source Multicast (ASM). Замість простої підписки на групову адресу `G` клієнтська програма зобов'язана явно зареєструвати в мережевому стеку операційної системи впорядковану пару `(S, G)`, використовуючи спеціалізовані структури керування джерелами. Цей практичний посібник містить повну реалізацію клієнта-приймача та сервера мовлення мовами C та C++, розгортання повноцінного тестового стенду в ізольованих мережевих просторах імен Linux (Network Namespaces), налаштування статичної та динамічної мультикаст-маршрутизації (FRRouting), аналіз бінарних дампів сигналізації у `tcpdump`, генерацію довільних тестових пакетів через Scapy, а також детальний розбір підводних каменів високопродуктивної обробки потокових даних, апаратного таймстемпінгу, динамічної зміни фільтрів джерел та резервування каналів зв'язку.

---

### 1. Архітектурні особливості та життєвий цикл сокета SSM

Процес отримання мультикаст-трафіку з фільтрацією за джерелом складається з кількох взаємопов'язаних етапів на стику простору користувача (User Space) та ядра операційної системи (Kernel Space):

1. **Створення сокета та налаштування повторного використання порту:** для прийому датаграм створюється сокет типу `SOCK_DGRAM`. Оскільки в системах потокового мовлення (наприклад, на серверах обробки біржових стрічок або абонентських приставках IPTV) на одному хості можуть паралельно працювати кілька процесів, що обробляють різні канали на одному UDP-порті, обов'язковим є встановлення прапорця `SO_REUSEADDR` (або `SO_REUSEPORT`).
2. **Прив'язка до порту (`bind`):** прив'язка здійснюється або до універсальної адреси `INADDR_ANY` (`0.0.0.0`), або до конкретної групової IP-адреси каналу (наприклад, `232.1.1.1`).
3. **Реєстрація джерела через `setsockopt`:** програма викликає системний виклик із параметром `IP_ADD_SOURCE_MEMBERSHIP`, передаючи структуру `struct ip_mreq_source`. У цей момент ядро:
   - Створює запис у локальній таблиці фільтрації сокета (Socket Filter State) у режимі `INCLUDE`.
   - Обчислює оновлений агрегований стан для фізичного мережевого інтерфейсу (`/proc/net/mcfilter`).
   - Генерує та надсилає у фізичну мережу пакет **IGMPv3 Membership Report** із типом запису `CHANGE_TO_INCLUDE_MODE` або `ALLOW_NEW_SOURCES`.
4. **Прийом даних та апаратна фільтрація:** вхідні UDP-пакети проходять перевірку у мережевому драйвері та ядрі. Датаграми від дозволеного джерела `S` поміщаються у чергу сокета, тоді як пакети від будь-яких інших відправників відкидаються ядром ще до пробудження системного виклику `recvfrom()`.
5. **Коректне завершення та відписка:** при завершенні роботи програма надсилає виклик із параметром `IP_DROP_SOURCE_MEMBERSHIP`, що змушує ядро оновити стан інтерфейсу та згенерувати IGMPv3 звіт `BLOCK_OLD_SOURCES` або `TO_IN(порожній)`.

---

### 2. Реалізація клієнта-приймача SSM (SSM Receiver)

Нижче наведено робочі реалізації приймача мовами C та C++. У версії C++ управління дескриптором сокета та життєвим циклом підписки на мультикаст-групу реалізовано за ідіомою RAII (Resource Acquisition Is Initialization), що гарантує своєчасну відписку від каналу навіть у разі виникнення виняткових ситуацій.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define MCAST_PORT 5004
#define MCAST_ADDR "232.1.1.1"
#define SOURCE_ADDR "198.51.100.1"
#define IFACE_ADDR  "192.0.2.50"
#define BUFFER_SIZE 2048

int main(void) {
    int sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    int reuse = 1;
    if (setsockopt(sock_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
        perror("Помилка встановлення SO_REUSEADDR");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(MCAST_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock_fd, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        perror("Помилка прив'язки bind()");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* Налаштування фільтрації за джерелом: приєднуємося до (S, G) */
    struct ip_mreq_source mreq;
    memset(&mreq, 0, sizeof(mreq));
    inet_pton(AF_INET, MCAST_ADDR, &mreq.imr_multiaddr);
    inet_pton(AF_INET, SOURCE_ADDR, &mreq.imr_sourceaddr);
    inet_pton(AF_INET, IFACE_ADDR, &mreq.imr_interface);

    if (setsockopt(sock_fd, IPPROTO_IP, IP_ADD_SOURCE_MEMBERSHIP, &mreq, sizeof(mreq)) < 0) {
        perror("Помилка IP_ADD_SOURCE_MEMBERSHIP");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    printf("Успішно підписано на SSM канал (%s, %s) через інтерфейс %s\n",
           SOURCE_ADDR, MCAST_ADDR, IFACE_ADDR);

    char buffer[BUFFER_SIZE];
    struct sockaddr_in sender_addr;
    socklen_t addr_len = sizeof(sender_addr);

    while (1) {
        ssize_t received = recvfrom(sock_fd, buffer, sizeof(buffer) - 1, 0,
                                    (struct sockaddr *)&sender_addr, &addr_len);
        if (received < 0) {
            perror("Помилка читання recvfrom()");
            break;
        }

        buffer[received] = '\0';
        char sender_ip[INET_ADDRSTRLEN];
        inet_ntop(AF_INET, &sender_addr.sin_addr, sender_ip, sizeof(sender_ip));

        printf("Отримано %zd байтів від %s:%d -> %s\n",
               received, sender_ip, ntohs(sender_addr.sin_port), buffer);
    }

    /* Коректне відключення від каналу */
    setsockopt(sock_fd, IPPROTO_IP, IP_DROP_SOURCE_MEMBERSHIP, &mreq, sizeof(mreq));
    close(sock_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <span>
#include <array>
#include <stdexcept>
#include <system_error>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class SsmReceiver {
public:
    SsmReceiver(std::string_view mcast_group,
                std::string_view source_ip,
                std::string_view iface_ip,
                uint16_t port)
        : m_port(port) {
        m_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        int reuse = 1;
        if (::setsockopt(m_fd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "SO_REUSEADDR failed");
        }

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(port);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

        if (::bind(m_fd, reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "bind() failed");
        }

        m_mreq = {};
        if (::inet_pton(AF_INET, mcast_group.data(), &m_mreq.imr_multiaddr) <= 0 ||
            ::inet_pton(AF_INET, source_ip.data(), &m_mreq.imr_sourceaddr) <= 0 ||
            ::inet_pton(AF_INET, iface_ip.data(), &m_mreq.imr_interface) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректний формат IP-адрес для SSM");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_ADD_SOURCE_MEMBERSHIP, &m_mreq, sizeof(m_mreq)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_ADD_SOURCE_MEMBERSHIP failed");
        }

        std::cout << "C++ SSM Receiver підписано на (" << source_ip << ", "
                  << mcast_group << ") порт " << port << '\n';
    }

    ~SsmReceiver() noexcept {
        if (m_fd >= 0) {
            ::setsockopt(m_fd, IPPROTO_IP, IP_DROP_SOURCE_MEMBERSHIP, &m_mreq, sizeof(m_mreq));
            ::close(m_fd);
        }
    }

    SsmReceiver(const SsmReceiver&) = delete;
    SsmReceiver& operator=(const SsmReceiver&) = delete;

    SsmReceiver(SsmReceiver&& other) noexcept
        : m_fd(other.m_fd), m_mreq(other.m_mreq), m_port(other.m_port) {
        other.m_fd = -1;
    }

    void run() {
        std::vector<char> buffer(4096);
        while (true) {
            sockaddr_in sender_addr{};
            socklen_t addr_len = sizeof(sender_addr);

            ssize_t bytes = ::recvfrom(m_fd, buffer.data(), buffer.size() - 1, 0,
                                       reinterpret_cast<sockaddr*>(&sender_addr), &addr_len);
            if (bytes < 0) {
                if (errno == EINTR) continue;
                throw std::system_error(errno, std::generic_category(), "recvfrom() failed");
            }

            buffer[bytes] = '\0';
            std::array<char, INET_ADDRSTRLEN> ip_buf{};
            ::inet_ntop(AF_INET, &sender_addr.sin_addr, ip_buf.data(), ip_buf.size());

            std::cout << "[Отримано " << bytes << " Б від " << ip_buf.data()
                      << ":" << ntohs(sender_addr.sin_port) << "] "
                      << std::string_view(buffer.data(), static_cast<size_t>(bytes)) << '\n';
        }
    }

private:
    int m_fd{-1};
    ip_mreq_source m_mreq{};
    uint16_t m_port{0};
};

int main() {
    try {
        SsmReceiver receiver("232.1.1.1", "198.51.100.1", "192.0.2.50", 5004);
        receiver.run();
    } catch (const std::exception& ex) {
        std::cerr << "Критична помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

### 3. Реалізація відправника SSM (SSM Sender)

Сервер мовлення відправляє звичайні UDP-датаграми на мультикаст-адресу з виділеного діапазону `232.0.0.0/8`. Щоб потік успішно подолав маршрутизатори мережі, відправник зобов'язаний налаштувати два системні параметри:
1. **Вихідний мережевий інтерфейс (`IP_MULTICAST_IF`):** явна прив'язка до IP-адреси конкретного мережевого адаптера гарантує, що пакети підуть у потрібний фізичний лінк, а ядро встановить правильну IP-адресу джерела `S` у заголовку IPv4.
2. **Час життя пакета (`IP_MULTICAST_TTL`):** за замовчуванням значення TTL для мультикаст-пакетів дорівнює `1` (мовлення лише в межах локального сегмента). Для передачі через корпоративну мережу або інтернет TTL слід збільшити (типово 16, 32 або 64).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

#define MCAST_PORT 5004
#define MCAST_ADDR "232.1.1.1"
#define IFACE_ADDR "198.51.100.1"

int main(void) {
    int sock_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock_fd < 0) {
        perror("Помилка створення сокета");
        return EXIT_FAILURE;
    }

    /* Вказуємо вихідний інтерфейс */
    struct in_addr iface;
    inet_pton(AF_INET, IFACE_ADDR, &iface);
    if (setsockopt(sock_fd, IPPROTO_IP, IP_MULTICAST_IF, &iface, sizeof(iface)) < 0) {
        perror("Помилка IP_MULTICAST_IF");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    /* Встановлюємо TTL для проходження через маршрутизатори */
    unsigned char ttl = 16;
    if (setsockopt(sock_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl)) < 0) {
        perror("Помилка IP_MULTICAST_TTL");
        close(sock_fd);
        return EXIT_FAILURE;
    }

    struct sockaddr_in target_addr;
    memset(&target_addr, 0, sizeof(target_addr));
    target_addr.sin_family = AF_INET;
    target_addr.sin_port = htons(MCAST_PORT);
    inet_pton(AF_INET, MCAST_ADDR, &target_addr.sin_addr);

    printf("Початок мовлення у SSM групу %s:%d з інтерфейсу %s...\n",
           MCAST_ADDR, MCAST_PORT, IFACE_ADDR);

    int counter = 0;
    char payload[256];

    while (1) {
        snprintf(payload, sizeof(payload), "SSM_STREAM_PACKET #%d [Time=%ld]", ++counter, time(NULL));
        ssize_t sent = sendto(sock_fd, payload, strlen(payload), 0,
                              (struct sockaddr *)&target_addr, sizeof(target_addr));
        if (sent < 0) {
            perror("Помилка sendto()");
            break;
        }

        printf("Надіслано пакет #%d (%zd байтів)\n", counter, sent);
        sleep(1);
    }

    close(sock_fd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <chrono>
#include <thread>
#include <system_error>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>

class SsmSender {
public:
    SsmSender(std::string_view mcast_group, std::string_view iface_ip, uint16_t port, uint8_t ttl = 16) {
        m_fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (m_fd < 0) {
            throw std::system_error(errno, std::generic_category(), "socket() failed");
        }

        in_addr iface{};
        if (::inet_pton(AF_INET, iface_ip.data(), &iface) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректний IP інтерфейсу");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_MULTICAST_IF, &iface, sizeof(iface)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_MULTICAST_IF failed");
        }

        if (::setsockopt(m_fd, IPPROTO_IP, IP_MULTICAST_TTL, &ttl, sizeof(ttl)) < 0) {
            ::close(m_fd);
            throw std::system_error(errno, std::generic_category(), "IP_MULTICAST_TTL failed");
        }

        m_target = {};
        m_target.sin_family = AF_INET;
        m_target.sin_port = htons(port);
        if (::inet_pton(AF_INET, mcast_group.data(), &m_target.sin_addr) <= 0) {
            ::close(m_fd);
            throw std::invalid_argument("Некоректна групова адреса SSM");
        }
    }

    ~SsmSender() noexcept {
        if (m_fd >= 0) ::close(m_fd);
    }

    SsmSender(const SsmSender&) = delete;
    SsmSender& operator=(const SsmSender&) = delete;

    void send_loop(std::chrono::milliseconds interval) {
        uint64_t seq = 0;
        while (true) {
            std::string msg = "SSM_DATA_SEQ=" + std::to_string(++seq);
            ssize_t sent = ::sendto(m_fd, msg.data(), msg.size(), 0,
                                    reinterpret_cast<const sockaddr*>(&m_target), sizeof(m_target));
            if (sent < 0) {
                throw std::system_error(errno, std::generic_category(), "sendto() failed");
            }

            std::cout << "C++ SSM Sender відправив пакет #" << seq << " (" << sent << " байтів)\n";
            std::this_thread::sleep_for(interval);
        }
    }

private:
    int m_fd{-1};
    sockaddr_in m_target{};
};

int main() {
    try {
        SsmSender sender("232.1.1.1", "198.51.100.1", 5004, 16);
        sender.send_loop(std::chrono::milliseconds(1000));
    } catch (const std::exception& ex) {
        std::cerr << "Помилка відправника: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
```
:::

---

### 4. Динамічне управління списками джерел під час роботи

У багатьох сценаріях додаток не завершує роботу, а динамічно змінює перелік активних джерел (наприклад, перемикається між резервними кодерами або додає новий потік котирувань).

#### 1. Додавання додаткового джерела `S2` до активної групи `G`:
Програма викликає `setsockopt()` з опцією `IP_ADD_SOURCE_MEMBERSHIP`, вказуючи нову IP-адресу `198.51.100.2`. Ядро автоматично генерує звіт IGMPv3 **`ALLOW_NEW_SOURCES`** (`Record Type = 5`), що містить лише адресу `198.51.100.2`. Маршрутизатор додає це джерело до свого дерева мовлення, не перериваючи прийом даних від першого джерела `198.51.100.1`.

#### 2. Видалення старого джерела `S1`:
Програма викликає `setsockopt()` з опцією `IP_DROP_SOURCE_MEMBERSHIP` для адреси `198.51.100.1`. Ядро Linux генерує звіт IGMPv3 **`BLOCK_OLD_SOURCES`** (`Record Type = 6`), повідомляючи маршрутизатор про припинення зацікавленості у джерелі `S1`. Маршрутизатор негайно відправляє повідомлення `PIM Prune (S1, G)` у бік джерела `S1`, зберігаючи трансляцію для `S2`.

#### 3. Вимкнення локального зворотного циклу (`IP_MULTICAST_LOOP`):
Якщо сервер мовлення та клієнт-приймач запущені на одному фізичному комп'ютері для тестування, ядро за замовчуванням створює локальну копію кожного надісланого пакета і повертає її у сокет приймача. У промислових високошвидкісних серверах цей зворотний цикл вимикають для економії циклів центрального процесора викликом `setsockopt(sock_fd, IPPROTO_IP, IP_MULTICAST_LOOP, &loop, sizeof(loop))`, де змінна `loop = 0`.

---

### 5. Лабораторний стенд у Network Namespaces Linux

Для тестування роботи SSM на одному комп'ютері без фізичного мережевого обладнання створимо віртуальну топологію з трьох ізольованих просторів імен: відправник (`ns_sender`), транзитний маршрутизатор (`ns_router`) та отримувач (`ns_receiver`).

```
 [ns_sender]                     [ns_router]                    [ns_receiver]
198.51.100.10 -------- veth_sr1 ---------- veth_r1r2 -------- 192.0.2.50
(SSM Джерело)          198.51.100.1        192.0.2.1          (SSM Приймач)
```

#### Скрипт створення віртуальної мережі:

```bash
#!/bin/bash
set -e

# 1. Створення ізольованих просторів імен
ip netns add ns_sender
ip netns add ns_router
ip netns add ns_receiver

# 2. Створення віртуальних Ethernet-пар (veth)
ip link add veth_s type veth peer name veth_sr
ip link add veth_r type veth peer name veth_rr

# 3. Розподіл інтерфейсів по просторах імен
ip link set veth_s netns ns_sender
ip link set veth_sr netns ns_router
ip link set veth_rr netns ns_router
ip link set veth_r netns ns_receiver

# 4. Налаштування IP-адресації та маршрутів за замовчуванням
ip -n ns_sender addr add 198.51.100.10/24 dev veth_s
ip -n ns_sender link set veth_s up
ip -n ns_sender link set lo up
ip -n ns_sender route add default via 198.51.100.1

ip -n ns_router addr add 198.51.100.1/24 dev veth_sr
ip -n ns_router addr add 192.0.2.1/24 dev veth_rr
ip -n ns_router link set veth_sr up
ip -n ns_router link set veth_rr up
ip -n ns_router link set lo up

ip -n ns_receiver addr add 192.0.2.50/24 dev veth_r
ip -n ns_receiver link set veth_r up
ip -n ns_receiver link set lo up
ip -n ns_receiver route add default via 192.0.2.1

# 5. Увімкнення одноадресної та багатоадресної маршрутизації в ядрі Linux
ip netns exec ns_router sysctl -w net.ipv4.ip_forward=1
ip netns exec ns_router sysctl -w net.ipv4.conf.all.mc_forwarding=1
ip netns exec ns_router sysctl -w net.ipv4.conf.veth_sr.mc_forwarding=1
ip netns exec ns_router sysctl -w net.ipv4.conf.veth_rr.mc_forwarding=1

# 6. Примусове встановлення протоколу IGMPv3 на всіх вузлах
ip netns exec ns_router sysctl -w net.ipv4.conf.all.force_igmp_version=3
ip netns exec ns_receiver sysctl -w net.ipv4.conf.all.force_igmp_version=3
```

#### Налаштування статичної мультикаст-маршрутизації через `smcroute`:

Для пересилання мультикаст-пакетів через проміжний маршрутизатор `ns_router` скористаємося легковажним демоном `smcroute`:

```bash
# Запуск демона smcroute у просторі маршрутизатора
ip netns exec ns_router smcroute -d

# Додавання статичного правила пересилання для SSM-каналу (S, G):
# Трафік від джерела 198.51.100.10 на групу 232.1.1.1, що приходить у veth_sr,
# пересилати у вихідний інтерфейс veth_rr
ip netns exec ns_router smcroutectl add veth_sr 198.51.100.10 232.1.1.1 veth_rr
```

Перевірити стан ядра можна командою:
```bash
ip netns exec ns_router ip mroute show
```
Вивід команди покаже активний запис таблиці багатоадресної маршрутизації:
```
(198.51.100.10, 232.1.1.1)       Iif: veth_sr    Oifs: veth_rr
```

#### Налаштування динамічної маршрутизації через FRRouting (PIM-SSM):

У промислових мережах замість статичного `smcroute` використовується стек динамічної маршрутизації FRRouting (`frr`). Для увімкнення чистого режиму PIM-SSM конфігураційний файл `frr.conf` маршрутизатора містить такі директиви:

```text
router pim
  ip pim ssm prefix-list SSM_RANGE

ip prefix-list SSM_RANGE seq 10 permit 232.0.0.0/8

interface veth_sr
  ip pim
  ip igmp version 3

interface veth_rr
  ip pim
  ip igmp version 3
```

Завдяки вказівці префікс-листа `232.0.0.0/8` демон PIM повністю вимикає обробку точок рандеву (RP) та спільних дерев `(*, G)` для цього адресного простору, обробляючи виключно прямі запити `(S, G)`. Стан маршрутизації перевіряється в інтерактивній оболонці `vtysh`:
```text
ns_router# show ip pim state 232.1.1.1
Source          Group           IIF      OIL
198.51.100.10   232.1.1.1       veth_sr  veth_rr(J)
```
Позначка `(J)` біля вихідного інтерфейсу `veth_rr` вказує на активне приєднання хоста за допомогою повідомлення IGMPv3 Join.

---

### 6. Діагностика через `tcpdump` та аналіз бінарних звітів IGMPv3

Запустимо перехоплення пакетів на інтерфейсі отримувача:

```bash
ip netns exec ns_receiver tcpdump -i veth_r -nn -vv "igmp or udp"
```

Коли клієнт викликає системний виклик `setsockopt(..., IP_ADD_SOURCE_MEMBERSHIP, ...)`, утиліта `tcpdump` фіксує такий бінарний звіт:

```
16:15:30.102345 IP (tos 0xc0, ttl 1, id 0, offset 0, flags [DF], proto IGMP (2), length 40, options (RA))
    192.0.2.50 > 224.0.0.22: igmp v3 report, 1 group record(s)
    [gaddr 232.1.1.1 to_in, 1 src(s) { 198.51.100.10 }]
```

#### Детальний розбір структури перехопленого кадру:
- **`tos 0xc0` (DSCP CS6 / Internetwork Control):** пакет сигналізації IGMP позначається найвищим мережевим пріоритетом для запобігання втратам у чергах комутаторів.
- **`ttl 1`:** суворо обмежує поширення звіту локальним фізичним сегментом Ethernet.
- **`proto IGMP (2)`:** номер протоколу в заголовку IPv4.
- **`options (RA)`:** активовано обов'язкову IP-опцію Router Alert (`0x94040000`).
- **`224.0.0.22`:** пакет адресовано спеціальній групі всіх локальних маршрутизаторів IGMPv3.
- **`to_in` (`CHANGE_TO_INCLUDE_MODE`):** інтерфейс перейшов у режим отримання трафіку виключно від зазначених джерел.
- **`1 src(s) { 198.51.100.10 }`:** у масиві джерел передано точну IP-адресу сервера мовлення.

---

### 7. Практична демонстрація захисту від несанкціонованого джерела (Anti-DoS)

Перевіримо головну перевагу SSM над відкритим мультикастом ASM — повну ізоляцію від стороннього спаму та неавторизованих потоків.

1. У просторі `ns_receiver` запускаємо скомпільовану програму приймача:
   ```bash
   ip netns exec ns_receiver ./ssm_receiver
   ```
2. У просторі `ns_sender` запускаємо легітимний передавач з IP `198.51.100.10`:
   ```bash
   ip netns exec ns_sender ./ssm_sender
   ```
   Приймач негайно починає друкувати прийняті датаграми:
   ```
   [Отримано 42 Б від 198.51.100.10:5004] SSM_STREAM_PACKET #1 [Time=1723985000]
   ```
3. Створимо в просторі `ns_sender` додатковий тестовий інтерфейс з IP `198.51.100.99` (незареєстроване джерело-зловмисник) і почнемо генерувати високошвидкісний потік сміттєвих UDP-пакетів на групу `232.1.1.1:5004`:
   ```bash
   ip netns exec ns_sender python3 -c '
   import socket, time
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   while True:
       s.sendto(b"ATTACK_SPAM_PAYLOAD_XYZ", ("232.1.1.1", 5004))
       time.sleep(0.01)
   '
   ```
4. **Аналіз результату:** на боці приймача не з'являється жодного пошкодженого пакета, а завантаження процесора приймача залишається нульовим.
5. **Механізм блокування в ядрі:** транзитний маршрутизатор `ns_router` та ядро приймача перевіряють вхідну пару `(198.51.100.99, 232.1.1.1)`. Оскільки в таблиці маршрутизації багатоадресного мовлення `mroute` та списку фільтрів `/proc/net/mcfilter` відсутній стан `INCLUDE` для адреси `198.51.100.99`, ядро миттєво відкидає пакети зловмисника на етапі функції ядра `ip_rcv_finish()`, збільшуючи лічильник відкинутих пакетів `InDiscards` у файлі `/proc/net/snmp`.

---

### 8. Генерація довільних звітів IGMPv3 через Python Scapy

Для стрес-тестування маршрутизаторів та перевірки реакції комутаторів на нестандартні комбінації джерел зручно використовувати бібліотеку Scapy:

```python
from scapy.all import IP, IPOption_RouterAlert, send
from scapy.contrib.igmpv3 import IGMPv3, IGMPv3mr, IGMPv3gr

# Створення IGMPv3 Membership Report з кількома записами Group Record
pkt = IP(dst="224.0.0.22", ttl=1, options=[IPOption_RouterAlert()]) / \
      IGMPv3() / \
      IGMPv3mr(records=[
          # Запис 1: Режим INCLUDE для двох джерел
          IGMPv3gr(rtype=1, maddr="232.1.1.1", srcaddrs=["198.51.100.1", "198.51.100.2"]),
          # Запис 2: Зміна режиму на EXCLUDE з одним виключенням
          IGMPv3gr(rtype=4, maddr="232.2.2.2", srcaddrs=["198.51.100.99"])
      ])

send(pkt, iface="eth0", verbose=True)
```

Цей скрипт дозволяє інженеру генерувати будь-які послідовності переходів станів і перевіряти коректність оновлення апаратних TCAM-таблиць на комутаторах ядра.

---

### 9. Високопродуктивна оптимізація та резервування потоків (A/B Feed Arbitration)

При розробці високонавантажених систем (фінансові біржові шлюзи OPRA, Nasdaq ITCH, CME MDP 3.0 та сервери відеомовлення 4K/8K) необхідно враховувати специфічні системні обмеження та архітектуру відмовостійкості:

#### 1. Збільшення системних сокетних буферів (`SO_RCVBUF`):
Під час відкриття біржових торгів інтенсивність мультикаст-потоків може зростати до мільйонів пакетів на секунду (Microbursts). Стандартного буфера сокета Linux (212 КБ) недостатньо, що призводить до втрати UDP-пакетів у чергах ядра. Для налаштування буфера 64 МБ викликається функція `setsockopt()` з опцією `SO_RCVBUF`, а також збільшуються системні ліміти операційної системи:

```bash
sysctl -w net.core.rmem_max=67108864
sysctl -w net.core.rmem_default=33554432
```

#### 2. Пакетне читання через `recvmmsg` та апаратне штампування часу (Hardware Timestamping):
У біржовій інфраструктурі кожен системний виклик `recvfrom()` створює накладні витрати на перемикання контексту ядра (близько 300–500 наносекунд). Щоб мінімізувати затримку, застосовується системний виклик `recvmmsg()`, який за один виклик вичитує з черги ядра до 64 або 128 датаграм у масив `struct mmsghdr`.

Для точного вимірювання затримок обробки на сокеті активується опція `SO_TIMESTAMPING`. При цьому мережева карта записує апаратну мітку часу прибуття кадру на рівні фізичного трансивера (PHY Layer), передаючи її в заголовок керування `struct cmsghdr` (тип повідомлення `SCM_TIMESTAMPING`). Це дозволяє зафіксувати точний час потрапляння котирування в систему з точністю до одиниць наносекунд без впливу джитера планувальника завдань Linux.

#### 3. Резервування потоків за моделлю A/B Feed Arbitration (RFC 7567):
Оскільки протокол UDP не гарантує доставку пакетів, у критично важливих фінансових системах використовується подвійна паралельна трансляція:
- **Feed A:** потік `(198.51.100.10, 232.1.1.1)` через незалежну фізичну мережу A.
- **Feed B:** потік `(198.51.100.20, 232.1.1.2)` через незалежну фізичну мережу B.

Клієнтський додаток підключається до обох SSM-каналів одночасно, зчитує 64-бітний порядковий номер пакета (Sequence Number) у заголовку повідомлення та передає у бізнес-логіку перший прибулий екземпляр пакета, безмовно відкидаючи дублікат. Це гарантує безперервну роботу торгової системи навіть при фізичному обриві одного з оптичних лінків або перезавантаженні транзитного комутатора.

#### 4. Асинхронний ввід-вивід та Kernel Bypass:
Для мінімізації затримок обробки (Latency) у C++ системах застосовується мультиплексування дескрипторів за допомогою `epoll` у режимі Edge-Triggered (`EPOLLET`), системні виклики пакетного читання `recvmmsg()`, або технології прямого доступу до мережевої карти без участі ядра (Kernel Bypass) на базі `AF_XDP` та бібліотеки DPDK.

---

### 10. Порівняння затримок доставки (Latency Benchmark) між ASM та SSM

Практичні вимірювання часу встановлення сесії мовлення та доставки першого корисного пакета показують колосальну перевагу SSM над класичним ASM:

1. **Час доставки першого пакета (First Packet Latency):**
   - **У моделі ASM:** затримка старту потоку становить від `350` до `1200` мілісекунд. Це зумовлено необхідністю відправки джерелом повідомлення `PIM Register` на точку рандеву RP, розпаковки трафіку, передачі по спільному дереву `(*, G)` та подальшого виконання перемикання SPT Switchover на пряме дерево `(S, G)`.
   - **У моделі SSM:** затримка старту складає лише `15–45` мілісекунд (рівно один час кругового обігу сигналу RTT між клієнтом і джерелом `S`), оскільки PIM Join надсилається безпосередньо по дереву найкоротшого шляху без участі проміжних серверів координації.
2. **Споживання пам'яті в таблицях маршрутизації (RIB/FIB Footprint):**
   - **ASM:** вимагає дублювання станів `(*, G)` для спільних дерев, `(S, G)` для дерев найкоротшого шляху, а також підтримки SA-кешу протоколу MSDP.
   - **SSM:** потребує підтримки виключно лінійних записів `(S, G)` без додаткових оверлейних структур, що зменшує навантаження на TCAM-пам'ять комутаторів у 4–8 разів.

---

### 11. Моніторинг та зняття метрик із ядра Linux

Діагностика втрат мультикаст-трафіку вимагає зіставлення лічильників на різних рівнях мережевого стека:

1. **Рівень мережевого інтерфейсу (`ethtool -S`):**
   ```bash
   ethtool -S eth0 | grep -E "drop|discard|fifo|miss"
   ```
   Якщо лічильники `rx_discards_phy` або `rx_missed_errors` зростають, це свідчить про переповнення апаратного кільцевого буфера мережевої карти (RX Ring Buffer). Розмір кільця збільшується командою `ethtool -G eth0 rx 4096`.
2. **Рівень мережевого стека ядра (`/proc/net/snmp`):**
   ```bash
   cat /proc/net/snmp | grep -E "Udp|Ip"
   ```
   Поле `InMcastPkts` показує загальну кількість прийнятих мультикаст-пакетів, а `RcvbufErrors` та `SndbufErrors` фіксують переповнення буферів у просторі ядра.
3. **Рівень таблиць маршрутизації (`ip -s mroute show`):**
   ```bash
   ip -s mroute show
   ```
   Команда відображає кількість пересланих байтів та пакетів для кожної активної пари `(S, G)`, а також інтерфейси введення (`iif`) та виведення (`oifs`).

---

### 12. Типові пастки та підводні камені реалізації

1. **Пастка прив'язки `bind(INADDR_ANY)` проти `bind(Group_IP)`:**
   Якщо хост підписаний на декілька SSM-каналів з однаковим номером UDP-порту (наприклад, потік новин `(198.51.100.1, 232.1.1.1):5004` та потік котирувань `(198.51.100.2, 232.1.1.2):5004`), прив'язка сокетів до `INADDR_ANY` призведе до того, що пакети обох груп потраплятимуть у перший створений сокет. Щоб розділити потоки на рівні ядра, кожен сокет зобов'язаний прив'язуватися строго до своєї групової IP-адреси.
2. **Пастка вибору інтерфейсу в багатомережевих серверах (Multi-homed Hosts):**
   Якщо в системі встановлено кілька мережевих карт, передача `INADDR_ANY` у полі `imr_interface` змушує ядро обирати інтерфейс за замовчуванням з основної таблиці маршрутизації. Якщо цей інтерфейс не підключений до мультикаст-сегмента, звіт IGMPv3 піде в неправильний кабель. Завжди вказуйте точну IP-адресу локального адаптера (`imr_interface.s_addr = inet_addr("192.0.2.50")`) або використовуйте протокольно-незалежний інтерфейс `group_source_req` з числовим індексом порту `if_nametoindex("eth1")`. Також на рівні сокета Linux підтримує жорстку прив'язку дескриптора до мережевої карти через опцію `SO_BINDTODEVICE` (`setsockopt(sock_fd, SOL_SOCKET, SO_BINDTODEVICE, "eth1", 4)`), що гарантує ізоляцію трафіку навіть при зміні системних одноадресних маршрутів.
3. **Пастка перевірки RPF (Reverse Path Forwarding):**
   Якщо маршрутизатор отримує запит на побудову дерева `(S, G)`, але зворотний одноадресний маршрут до джерела `S` вказує на інший фізичний інтерфейс, ніж той, звідки фізично надходять пакети (асиметрична маршрутизація), перевірка RPF зазнає невдачі, і маршрутизатор безмовно відкине всі мультикаст-пакети. Перевіряйте таблицю одноадресних маршрутів командою `ip route get <IP_Джерела>`.
4. **Пастка відсутності підтримки IGMPv3 на комутаторах L2:**
   Якщо проміжний комутатор виконує IGMP Snooping, але налаштований лише на версію IGMPv2, він не розпізнає адреси призначення `224.0.0.22` для звітів IGMPv3 Report. У результаті комутатор блокує запити підписки, і трафік не потрапляє до клієнтського порту.
5. **Блокування Router Alert фаєрволом (iptables/nftables):**
   Базові правила мережевого екрана, що блокують невідомі IP-опції, призводять до дропу звітів IGMPv3. Для коректної роботи необхідно явно дозволити транзит протоколу IGMP:
   ```bash
   iptables -A INPUT -p igmp -j ACCEPT
   iptables -A OUTPUT -p igmp -j ACCEPT
   ```

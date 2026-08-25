# ⚙️ Практична реалізація багатопотокового сніфера на TPACKET_V3 та PACKET_FANOUT

У цьому практичному розділі детально розбирається створення високопродуктивної утиліти для перехоплення та аналізу мережевого трафіку у ядрі Linux. Проект показує використання сокетів `AF_PACKET`, перемикання режиму в `TPACKET_V3`, виділення кільцевого буфера через спільну пам'ять `mmap()`, масштабування обробки через `PACKET_FANOUT_HASH` та коректне вивільнення ресурсів при завершенні.

---

## 1. Архітектурний огляд та вимоги до системи

Для роботи зі сокетами `AF_PACKET` та механізмом PACKET_MMAP програмі вимагаються привілеї `CAP_NET_RAW` та `CAP_IPC_LOCK` у системі (або запуск від імені суперкористувача `root`). Прапорець `CAP_IPC_LOCK` необхідний для фіксації сторінок виділеної оперативної пам'яті за допомогою `MAP_LOCKED` або виклику `mlock()`, щоб запобігти вивантаженню кільцевого буфера у swap.

Програма реалізує повний цикл роботи з TPACKET_V3 та складається з наступних ключових етапів:

1. **Створення привілейованого сокета:** Програма відкриває сирий сокет канального рівня `socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))`. Протокол `ETH_P_ALL` гарантує, що ядро передаватиме у сокет абсолютно всі вхідні та вихідні Ethernet-кадри (IP, ARP, VLAN, IPv6).
2. **Перемикання версії API:** За допомогою системного виклику `setsockopt(..., SOL_PACKET, PACKET_VERSION, ...)` сокет переводють у режим TPACKET_V3. Ця операція є обов'язковою першою дією і має виконуватися до будь-яких налаштувань розмірів буфера.
3. **Розрахунок геометрії пам'яті:** Ініціалізується структура `tpacket_req3`. Задаються розміри безперервних блоків (1 MB) та їх кількість (64 блоки = 64 MB загальної оперативної пам'яті). Також задається таймер віддачі частково заповнених блоків `tp_retire_blk_tov = 10` мс та прапорець запиту апаратного хешу `TP_FT_REQ_FILL_RXHASH`.
4. **Відображення пам'яті (`mmap`):** За допомогою системного виклику `mmap()` виділений ядром буфер відображається в адресний простір користувача. Прапорець `MAP_SHARED` робить модифікації статусу блоків видимими для ядра, а `MAP_LOCKED` блокує сторінки у фізичній RAM.
5. **Прив'язка до мережевого інтерфейсу:** За допомогою викликів `if_nametoindex()` та `bind()` сокет прив'язується до конкретної мережевої карти (наприклад, `eth0`). Тільки після виклику `bind()` ядро починає записати кадри у виділений буфер.
6. **Приєднання до Fanout-групи:** Опція `PACKET_FANOUT_HASH` приєднує сокет до групи балансування 4-tuple. Це дозволяє розпаралелювати обробку трафіку між кількома незалежними потоками без ризику розриву контексту TCP-сесій.
7. **Основний цикл пакетної обробки:** Програма ітерується по масиву блоків, перевіряючи атомарне поле `block_status`. Коли блок отримує статус `TP_STATUS_USER`, програма послідовно вичитає всі кадри блоку через відносний зсув `tp_next_offset`. Після завершення обробки блок повертається ядру присвоєнням `TP_STATUS_KERNEL`.
8. **Безаварійне завершення:** При отриманні сигналів `SIGINT` або `SIGTERM` програма виходить із циклу, звільняє пам'ять через `munmap()` та закриває сокет.

---

## 2. Повна реалізація у коді (C та C++)

:::tabs
```c
/* tpacket_v3_sniffer.c — Повна реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/poll.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <linux/if_packet.h>

static volatile int keep_running = 1;

static void sig_handler(int sig) {
    (void)sig;
    keep_running = 0;
}

int main(int argc, char **argv) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <мережевий_інтерфейс>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *ifname = argv[1];
    signal(SIGINT, sig_handler);
    signal(SIGTERM, sig_handler);

    /* 1. Створення RAW сокета AF_PACKET */
    int fd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (fd < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    /* 2. Встановлення версії TPACKET_V3 */
    int version = TPACKET_V3;
    if (setsockopt(fd, SOL_PACKET, PACKET_VERSION, &version, sizeof(version)) < 0) {
        perror("setsockopt PACKET_VERSION");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 3. Налаштування параметрів кільцевого буфера */
    struct tpacket_req3 req;
    memset(&req, 0, sizeof(req));
    req.tp_block_size = 1024 * 1024;    /* 1 MB на блок (кратне PAGE_SIZE) */
    req.tp_block_nr = 64;               /* 64 блоки = 64 MB сумарно */
    req.tp_frame_size = 2048;           /* Верхня межа snaplen кадру */
    req.tp_frame_nr = (req.tp_block_size * req.tp_block_nr) / req.tp_frame_size;
    req.tp_retire_blk_tov = 10;         /* Таймаут віддачі блоку: 10 мс */
    req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

    if (setsockopt(fd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req)) < 0) {
        perror("setsockopt PACKET_RX_RING");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 4. mmap() відображення спільної пам'яті ядра у простір користувача */
    size_t ring_bytes = (size_t)req.tp_block_size * req.tp_block_nr;
    uint8_t *ring = mmap(NULL, ring_bytes, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_LOCKED, fd, 0);
    if (ring == MAP_FAILED) {
        perror("mmap");
        close(fd);
        return EXIT_FAILURE;
    }

    /* 5. Прив'язка сокета до мережевого інтерфейсу */
    struct sockaddr_ll sll;
    memset(&sll, 0, sizeof(sll));
    sll.sll_family = AF_PACKET;
    sll.sll_protocol = htons(ETH_P_ALL);
    sll.sll_ifindex = if_nametoindex(ifname);
    if (sll.sll_ifindex == 0) {
        fprintf(stderr, "Помилка: мережевий інтерфейс %s не знайдено\n", ifname);
        munmap(ring, ring_bytes);
        close(fd);
        return EXIT_FAILURE;
    }

    if (bind(fd, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
        perror("bind");
        munmap(ring, ring_bytes);
        close(fd);
        return EXIT_FAILURE;
    }

    /* 6. Приєднання до Fanout групи за хешем 4-tuple */
    uint32_t fanout_arg = (42 & 0xffff) | (PACKET_FANOUT_HASH << 16);
    if (setsockopt(fd, SOL_PACKET, PACKET_FANOUT, &fanout_arg, sizeof(fanout_arg)) < 0) {
        perror("setsockopt PACKET_FANOUT");
    }

    printf("Сніфер C запущено на %s (TPACKET_V3, 64MB ring)... Натисніть Ctrl+C для зупинки.\n", ifname);

    unsigned int block_idx = 0;
    uint64_t total_packets = 0;

    struct pollfd pfd;
    memset(&pfd, 0, sizeof(pfd));
    pfd.fd = fd;
    pfd.events = POLLIN | POLLERR;

    /* 7. Основний цикл пакетної обробки блоків */
    while (keep_running) {
        struct block_desc *pbd = (struct block_desc *)(ring + (block_idx * req.tp_block_size));

        /* Перевірка атомарного статусу блоку */
        if ((pbd->h1.block_status & TP_STATUS_USER) == 0) {
            poll(&pfd, 1, 10); /* Засинаємо не більше ніж на 10 мс при відсутності даних */
            continue;
        }

        /* Ітерація по всіх пакетах всередині блоку */
        uint32_t num_pkts = pbd->h1.num_pkts;
        uint8_t *pkt_ptr = (uint8_t *)pbd + pbd->h1.offset_to_first_pkt;

        for (uint32_t i = 0; i < num_pkts; ++i) {
            struct tpacket3_hdr *hdr = (struct tpacket3_hdr *)pkt_ptr;
            uint8_t *eth_data = (uint8_t *)hdr + hdr->tp_mac;

            /* Розбір Ethernet заголовка */
            struct ethhdr *eth = (struct ethhdr *)eth_data;
            if (ntohs(eth->h_proto) == ETH_P_IP) {
                struct iphdr *ip = (struct iphdr *)(eth_data + sizeof(struct ethhdr));
                char src_ip[INET_ADDRSTRLEN], dst_ip[INET_ADDRSTRLEN];
                inet_ntop(AF_INET, &ip->saddr, src_ip, sizeof(src_ip));
                inet_ntop(AF_INET, &ip->daddr, dst_ip, sizeof(dst_ip));
                (void)src_ip; (void)dst_ip;
            }

            total_packets++;
            pkt_ptr += hdr->tp_next_offset; /* Перехід до наступного кадру */
        }

        /* Повертаємо блок ядру */
        pbd->h1.block_status = TP_STATUS_KERNEL;
        block_idx = (block_idx + 1) % req.tp_block_nr;
    }

    printf("\nЗупинено. Всього оброблено пакетів: %lu\n", total_packets);

    /* 8. Звільнення ресурсів */
    munmap(ring, ring_bytes);
    close(fd);
    return EXIT_SUCCESS;
}
```
```cpp
// tpacket_v3_sniffer.cpp — Ідіоматична реалізація C++20 з RAII
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <memory>
#include <system_error>
#include <atomic>
#include <csignal>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/mman.h>
#include <sys/poll.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <linux/if_packet.h>

namespace net {

static std::atomic<bool> g_running{true};

void signal_handler(int) {
    g_running.store(false, std::memory_order_relaxed);
}

// RAII-обгортка для керування сокетом
class SocketFd {
    int m_fd{-1};
public:
    explicit SocketFd(int fd) : m_fd(fd) {}
    ~SocketFd() {
        if (m_fd >= 0) {
            ::close(m_fd);
        }
    }
    SocketFd(const SocketFd&) = delete;
    SocketFd& operator=(const SocketFd&) = delete;
    SocketFd(SocketFd&& other) noexcept : m_fd(other.m_fd) { other.m_fd = -1; }
    
    [[nodiscard]] int get() const noexcept { return m_fd; }
    [[nodiscard]] bool valid() const noexcept { return m_fd >= 0; }
};

// RAII-обгортка для змонтованої пам'яті mmap
class MmappedRing {
    std::span<std::byte> m_region;
public:
    MmappedRing(void* addr, size_t size) 
        : m_region(static_cast<std::byte*>(addr), size) {}
    
    ~MmappedRing() {
        if (!m_region.empty() && m_region.data() != MAP_FAILED) {
            ::munmap(m_region.data(), m_region.size());
        }
    }

    MmappedRing(const MmappedRing&) = delete;
    MmappedRing& operator=(const MmappedRing&) = delete;
    
    [[nodiscard]] std::span<std::byte> get() const noexcept { return m_region; }
    [[nodiscard]] std::byte* data() const noexcept { return m_region.data(); }
};

class PacketSnifferV3 {
    SocketFd m_sock;
    tpacket_req3 m_req{};
    std::unique_ptr<MmappedRing> m_ring;
    std::string m_ifname;

public:
    explicit PacketSnifferV3(std::string_view ifname) 
        : m_sock(::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))), m_ifname(ifname) 
    {
        if (!m_sock.valid()) {
            throw std::system_error(errno, std::generic_category(), "Помилка створення AF_PACKET сокета");
        }

        // Встановлення версії TPACKET_V3
        int version = TPACKET_V3;
        if (::setsockopt(m_sock.get(), SOL_PACKET, PACKET_VERSION, &version, sizeof(version)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt PACKET_VERSION");
        }

        m_req.tp_block_size = 1024 * 1024; // 1 MB
        m_req.tp_block_nr = 64;            // 64 MB всього
        m_req.tp_frame_size = 2048;
        m_req.tp_frame_nr = (m_req.tp_block_size * m_req.tp_block_nr) / m_req.tp_frame_size;
        m_req.tp_retire_blk_tov = 10;      // 10 мс timeout
        m_req.tp_feature_req_word = TP_FT_REQ_FILL_RXHASH;

        if (::setsockopt(m_sock.get(), SOL_PACKET, PACKET_RX_RING, &m_req, sizeof(m_req)) < 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt PACKET_RX_RING");
        }

        size_t total_bytes = static_cast<size_t>(m_req.tp_block_size) * m_req.tp_block_nr;
        void* addr = ::mmap(nullptr, total_bytes, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_LOCKED, m_sock.get(), 0);
        if (addr == MAP_FAILED) {
            throw std::system_error(errno, std::generic_category(), "mmap ring buffer");
        }
        m_ring = std::make_unique<MmappedRing>(addr, total_bytes);

        sockaddr_ll sll{};
        sll.sll_family = AF_PACKET;
        sll.sll_protocol = htons(ETH_P_ALL);
        sll.sll_ifindex = ::if_nametoindex(m_ifname.c_str());
        if (sll.sll_ifindex == 0) {
            throw std::runtime_error("Мережевий інтерфейс " + m_ifname + " не знайдено");
        }

        if (::bind(m_sock.get(), reinterpret_cast<sockaddr*>(&sll), sizeof(sll)) < 0) {
            throw std::system_error(errno, std::generic_category(), "bind socket");
        }
    }

    void run() {
        unsigned int block_idx = 0;
        uint64_t packet_count = 0;
        pollfd pfd{.fd = m_sock.get(), .events = POLLIN | POLLERR, .revents = 0};

        while (g_running.load(std::memory_order_relaxed)) {
            auto* block_ptr = m_ring->data() + (block_idx * m_req.tp_block_size);
            auto* pbd = reinterpret_cast<block_desc*>(block_ptr);

            if ((pbd->h1.block_status & TP_STATUS_USER) == 0) {
                ::poll(&pfd, 1, 10);
                continue;
            }

            uint32_t num_pkts = pbd->h1.num_pkts;
            auto* pkt_ptr = reinterpret_cast<uint8_t*>(pbd) + pbd->h1.offset_to_first_pkt;

            for (uint32_t i = 0; i < num_pkts; ++i) {
                auto* hdr = reinterpret_cast<tpacket3_hdr*>(pkt_ptr);
                auto* eth = reinterpret_cast<ethhdr*>(pkt_ptr + hdr->tp_mac);

                if (ntohs(eth->h_proto) == ETH_P_IP) {
                    // Витягнення IPv4 пакету у C++20 span
                    std::span<const std::byte> pkt_span(
                        reinterpret_cast<const std::byte*>(pkt_ptr + hdr->tp_net), 
                        hdr->tp_snaplen
                    );
                    (void)pkt_span;
                }

                packet_count++;
                pkt_ptr += hdr->tp_next_offset;
            }

            pbd->h1.block_status = TP_STATUS_KERNEL;
            block_idx = (block_idx + 1) % m_req.tp_block_nr;
        }

        std::cout << "\nЗупинено. Оброблено пакетів: " << packet_count << std::endl;
    }
};

} // namespace net

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <мережевий_інтерфейс>\n";
        return EXIT_FAILURE;
    }

    std::signal(SIGINT, net::signal_handler);
    std::signal(SIGTERM, net::signal_handler);

    try {
        net::PacketSnifferV3 sniffer(argv[1]);
        std::cout << "Сніфер C++ TPACKET_V3 запущено на " << argv[1] << "...\n";
        sniffer.run();
    } catch (const std::exception& ex) {
        std::cerr << "Фатальна помилка: " << ex.what() << '\n';
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний розбір механіки роботи коду

### 3.1. Обчислення адрес та зміщень у блоці

При обробці блоку у C та C++ коді критично важливо правильно виконувати арифметику вказівників. Заголовок блоку `struct block_desc` розташований на початку кожного блоку завдовжки `tp_block_size`.

Зміщення до першого кадру отримується виразом:
`uint8_t *pkt_ptr = (uint8_t *)pbd + pbd->h1.offset_to_first_pkt;`

Усередині циклу переход до наступного пакета виконується додаванням відносного зміщення `hdr->tp_next_offset`:
`pkt_ptr += hdr->tp_next_offset;`

Якщо `tp_next_offset` дорівнює `0`, це означає, що поточний пакет є останнім у блоці, і цикл обробки блоку завершується.

---

## 4. Оптимізації для продуктивних середовищ

При розгортанні даної реалізації у продуктовому середовищі на швидкостях 10 Gbps+ слід виконати додаткові налаштування:

### 4.1. Керування афінністю CPU (Thread CPU Affinity)
Драйвери мережевої карти генерують переривання на конкретних ядрах процесора. Якщо потік обробки TPACKET буде мігрувати між ядрами, виникне деградація продуктивності через постійні промахи L1/L2 кешу. Рекомендується фіксувати потік обробки за допомогою виклику `pthread_setaffinity_np()`.

### 4.2. Налаштування розмірів системних буферів `sysctl`
За замовчуванням ядро Linux має обмеження на максимальні розміри буферів сокетів прийому (`rmem_max`). Для запобігання втратам пакетів при сплесках трафіку необхідно збільшити розміри буферів у системі:

```bash
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.rmem_default=67108864
```

### 4.3. Вирівнювання пам'яті при роботі з `std::span`
У C++ реалізації використання `std::span` дозволяє працювати з безперервним фрагментом пам'яті кадру без створення копій `std::vector` або `std::string`. Це зберігає zero-copy семантику на всьому шляху обробки пакету.

### 4.4. Обробка помилок та втрат пакетів у реальному часі
У високозавантажених системах слід періодично опитувати статистику втрат через `getsockopt(fd, SOL_PACKET, PACKET_STATISTICS, ...)` та реєструвати події `tp_drops`. Зростання лічильника `tp_drops` сигналізує про необхідність збільшення `tp_block_nr` або виділення додаткових worker-потоків у Fanout-групі.

---

## 5. Інтеграція класичного BPF-фільтра

Перед ініціалізацією кільцевого буфера до сокета можна приєднати зкомпільований BPF-фільтр за допомогою системного виклику `setsockopt(SOL_SOCKET, SO_ATTACH_FILTER, ...)`.

Наприклад, для перехоплення лише TCP-трафіку на порту 80 створюється масив інструкцій `struct sock_filter`:

:::tabs
```c
struct sock_filter bpf_code[] = {
    { 0x28, 0, 0, 0x0000000c },
    { 0x15, 0, 1, 0x00000800 },
    { 0x30, 0, 0, 0x00000017 },
    { 0x15, 0, 3, 0x00000006 },
    { 0x28, 0, 0, 0x00000014 },
    { 0x45, 1, 0, 0x00001fff },
    { 0xb1, 0, 0, 0x0000000e },
    { 0x48, 0, 0, 0x0000000e },
    { 0x15, 2, 0, 0x00000050 },
    { 0x48, 0, 0, 0x00000010 },
    { 0x15, 0, 1, 0x00000050 },
    { 0x6, 0, 0, 0x00040000 },
    { 0x6, 0, 0, 0x00000000 },
};

struct sock_fprog bpf_prog;
bpf_prog.len = sizeof(bpf_code) / sizeof(bpf_code[0]);
bpf_prog.filter = bpf_code;

if (setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, &bpf_prog, sizeof(bpf_prog)) < 0) {
    perror("setsockopt SO_ATTACH_FILTER");
}
```
```cpp
std::array<sock_filter, 13> bpf_code{{
    { 0x28, 0, 0, 0x0000000c },
    { 0x15, 0, 1, 0x00000800 },
    { 0x30, 0, 0, 0x00000017 },
    { 0x15, 0, 3, 0x00000006 },
    { 0x28, 0, 0, 0x00000014 },
    { 0x45, 1, 0, 0x00001fff },
    { 0xb1, 0, 0, 0x0000000e },
    { 0x48, 0, 0, 0x0000000e },
    { 0x15, 2, 0, 0x00000050 },
    { 0x48, 0, 0, 0x00000010 },
    { 0x15, 0, 1, 0x00000050 },
    { 0x6, 0, 0, 0x00040000 },
    { 0x6, 0, 0, 0x00000000 },
}};

sock_fprog bpf_prog{
    .len = static_cast<unsigned short>(bpf_code.size()),
    .filter = bpf_code.data()
};

if (::setsockopt(fd, SOL_SOCKET, SO_ATTACH_FILTER, &bpf_prog, sizeof(bpf_prog)) < 0) {
    throw std::system_error(errno, std::generic_category(), "setsockopt SO_ATTACH_FILTER");
}
```
:::

Завдяки цьому ядро Linux фільтруватиме пакети на рівні NAPI SoftIRQ до їх запису в блоки TPACKET_V3. Це суттєво економить пам'ять та зменшує навантаження на кільцевий буфер.

---

## 6. Багатопотокове масштабування та потокові інваріанти

При розгортанні сніфера в архітектурі з багатьма worker-потоками кожен потік створює власний екземпляр сокета та власний кільцевий буфер. Використання опції `PACKET_FANOUT_HASH` гарантує, що ядро обчислює хеш на основі 4-кортежу (IP адреси джерела та призначення, порти джерела та призначення).

Завдяки цьому всі пакети, які належать одному TCP-з'єднанню або UDP-сесії, завжди потрапляють в той самий сокет і обробляються тим самим потоком CPU. Це позбавляє від потреби використовувати міжпотокові міжузли або системні локи для синхронізації стану аналізатора (stateful inspection), що дозволяє масштабувати обробку трафіку практично лінійно з ростом кількості ядер процесора.

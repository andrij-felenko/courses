# ⚙️ Детектор маніпуляцій middlebox: зондування опцій TCP та виявлення модифікацій заголовків

Для виявлення прихованого втручання транзитних пристроїв (Middlebox) у мережевий трафік застосовують методи активного зондування, при яких клієнтська програма конструює сирі IP-пакети з експериментальними опціями TCP, відправляє їх у бік тестового сервера та аналізує побітові відмінності в заголовках отриманих відповідей для діагностики занулення опцій (*Option Stripping*), примусового зменшення MSS (*MSS Clamping*) або нелінійної підміни початкових номерів послідовності (*ISN Rewriting*).

---

### Архітектура та фізичний принцип роботи детектора

Стандартний мережевий стек операційної системи (системні виклики `connect()`, `send()` та `recv()`) повністю абстрагує прикладного програміста від низькорівневих службових заголовків транспортного рівня. Операційна система автоматично генерує псевдовипадкові початкові номери послідовності (ISN), розраховує бінарну контрольну суму, керує розміром вікна прийому та додає стандартний фіксований набір опцій TCP (MSS, Window Scale, SACK-Permitted, Timestamps).

Для прямого виявлення втручання проміжних пристроїв необхідно вийти за межі стандартного сокетного API й перейти до використання **сирих сокетів** (англ. *Raw Sockets*, `SOCK_RAW`) з активованим прапорцем `IP_HDRINCL` (*IP Header Included*). Це надає прикладній програмі повний побайтовий контроль над формуванням кожного біта заголовків IPv4 та TCP.

```text
               Схема активного зондування мережевого тракту
               
    [Клієнтський зонд (Raw Socket)]          [Транзитний Middlebox]          [Тестовий сервер]
                  │                                   │                              │
    1. Формує SYN │ ─── TCP SYN (MSS=1460, ───────► │ Перевіряє TCP-опції:         │
       з опціями  │     Opt=30 [MPTCP], ISN)          │ • Затирає Opt 30 (NOP)       │
                  │                                   │ • Clamping MSS → 1400        │
                  │                                   │ ─── Змінений SYN ──────────► │
                  │                                   │                              │
                  │                                   │ ◄── TCP SYN-ACK ──────────── │
                  │ ◄── Отримує відповідь ─────────── │ (Ack=ISN+1, MSS=1400)        │
                  │                                   │                              │
    2. Порівняння:                                                                   
       • Опцію MPTCP вирізано (Option Stripping виявлено!)                           
       • MSS зменшено з 1460 до 1400 (MSS Clamping виявлено!)                        
```

#### Анатомія формування кастомного TCP-сегмента

Процес формування тестового пакета складається з п'яти строго регламентованих етапів:

1. **Кодування та вирівнювання опцій TCP**: Опції TCP розташовуються безпосередньо після фіксованих 20 байтів базового заголовка TCP. Кожна опція кодується у форматі TLV (*Type-Length-Value*):
   * Однобайтні опції без параметрів: `0x00` (`EOL` — кінець списку опцій) та `0x01` (`NOP` — байт заповнення для вирівнювання);
   * Багатобайтні опції: перший байт — `Kind` (ідентифікатор опції), другий байт — `Length` (загальна довжина опції в байтах, включаючи поля Kind та Length), решта байтів — корисне значення `Value`.
   
   Загальна довжина заголовка TCP фіксується в 4-бітному полі `Data Offset` (`doff`) і вимірюється в 32-бітних словах (4-байтних блоках). Якщо сумарна довжина опцій не кратна 4 байтам, у кінець списку обов'язково додаються байти `NOP`, інакше мережевий стек віддаленого сервера вважатиме пакет структурно пошкодженим.

2. **Порядок байтів та конвертація Endianness**: Архітектури процесорів x86-64 та ARM використовують зворотний порядок байтів (*Little-Endian*), тоді як усі протоколи сімейства TCP/IP використовують прямий мережевий порядок (*Big-Endian / Network Byte Order*). Програма зобов'язана виконувати явне перетворення за допомогою макросів `htons()` (для 16-бітних полів: портів, довжини, ідентифікаторів) та `htonl()` (для 32-бітних полів: адрес, номерів послідовності). Пропуск конвертації навіть одного поля призводить до відправки пакета з некоректними даними.

3. **Формування псевдозаголовка та розрахунок контрольної суми TCP (RFC 1071)**: На відміну від заголовка IPv4, де контрольна сума покриває лише власні 20 байтів L3, алгоритм розрахунку контрольної суми TCP включає в себе **псевдозаголовок IPv4**. Псевдозаголовок містить 4 байти вихідної IP-адреси, 4 байти цільової IP-адреси, нульовий байт заповнення, байт номера протоколу (`6`) та 2 байти загальної довжини TCP-сегмента (заголовок плюс корисне навантаження):

```text
+─────────────────────────────────────────────────────────────+
|               Структура псевдозаголовка IPv4                |
+──────────────────────────────+──────────────────────────────+
| Source IP Address (4 байти)  | Destination IP (4 байти)     |
+──────────────+───────────────+──────────────────────────────+
| Zero (1 байт)| Proto=6 (1 B) | TCP Segment Length (2 байти) |
+──────────────+───────────────+──────────────────────────────+
```

4. **Захист від колізії з локальним ядром Linux (Kernel RST Suppression)**: Коли віддалений сервер отримує наш зондувальний пакет `SYN`, він відповідає стандартним пакетом `SYN-ACK`. Оскільки сирий сокет не створює повноцінного запису в таблиці сокетів ядра (`struct sock`), підсистема TCP локального ядра розцінює отриманий `SYN-ACK` як неочікувану відповідь на неіснуюче з'єднання і миттєво генерує у відповідь пакет `TCP RST`, руйнуючи з'єднання ще до того, як прикладний зонд зчитає дані. Для блокування цієї поведінки перед запуском зонду додається правило Netfilter:
   ```bash
   sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --sport <src_port> -j DROP
   ```

5. **Локалізація точки втручання за допомогою TTL (Методологія Tracebox)**: Якщо необхідно дізнатися, який саме транзитний маршрутизатор на шляху спотворює заголовки, зондування виконується в циклі зі збільшенням поля `TTL` (Hop Limit) від 1 до 30. Коли пакет досягає проміжного вузла з `TTL=1`, маршрутизатор знищує його і повертає пакет `ICMP Time Exceeded (Type 11 Code 0)`. Згідно з RFC 792, пакет ICMP містить цитату початкового IP-заголовка та перших 8 байтів корисного навантаження. Порівнюючи відправлений заголовок із процитованим у повідомленні ICMP, зонд точно визначає IP-адресу вузла, який модифікував або скинув пакет.

6. **Альтернатива через eBPF / AF_XDP**: У сучасних ядрах Linux високоефективним аналогом сирих сокетів є технологія **eBPF / XDP** (*eXpress Data Path*). Програма XDP завантажується безпосередньо в драйвер мережевої карти, що дозволяє інспектувати вхідні кадри ще до їх потрапляння в підсистему Netfilter conntrack і уникати будь-яких колізій з ядром без необхідності налаштування iptables.

---

### Програмна реалізація зондувального комплексу

Нижче наведено повні вихідні коди зонду мовами C та ідіоматичною C++:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/time.h>

#define PACKET_BUFFER_SIZE 4096
#define TEST_TCP_MSS 1460
#define EXPERIMENTAL_OPT_KIND 30 /* MPTCP option kind */

/* Псевдозаголовок для розрахунку контрольної суми TCP */
struct pseudo_header {
    uint32_t src_ip;
    uint32_t dst_ip;
    uint8_t  placeholder;
    uint8_t  protocol;
    uint16_t tcp_length;
};

/* Обчислення Інтернет-контрольної суми (RFC 1071) */
static uint16_t calculate_checksum(const uint16_t *addr, int count) {
    uint32_t sum = 0;
    while (count > 1) {
        sum += *addr++;
        count -= 2;
    }
    if (count > 0) {
        sum += *(const uint8_t *)addr;
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return (uint16_t)(~sum);
}

/* Формування та відправка сирого TCP SYN із нестандартними опціями */
int send_probe_syn(int raw_sock, const char *src_ip, const char *dst_ip,
                   uint16_t src_port, uint16_t dst_port, uint32_t isn) {
    char packet[PACKET_BUFFER_SIZE];
    memset(packet, 0, sizeof(packet));

    struct iphdr *iph = (struct iphdr *)packet;
    struct tcphdr *tcph = (struct tcphdr *)(packet + sizeof(struct iphdr));
    uint8_t *options = (uint8_t *)(packet + sizeof(struct iphdr) + sizeof(struct tcphdr));

    /* Додавання TCP Options */
    int opt_idx = 0;

    /* Опція 1: MSS (Kind=2, Length=4, Value=1460) */
    options[opt_idx++] = 2;
    options[opt_idx++] = 4;
    options[opt_idx++] = (TEST_TCP_MSS >> 8) & 0xFF;
    options[opt_idx++] = TEST_TCP_MSS & 0xFF;

    /* Опція 2: MPTCP (Kind=30, Length=4, Value=0xDEAD) */
    options[opt_idx++] = EXPERIMENTAL_OPT_KIND;
    options[opt_idx++] = 4;
    options[opt_idx++] = 0xDE;
    options[opt_idx++] = 0xAD;

    /* Вирівнювання заголовка TCP до кратності 4 байтам (NOP + EOL) */
    options[opt_idx++] = 1; /* NOP */
    options[opt_idx++] = 0; /* EOL */
    while (opt_idx % 4 != 0) {
        options[opt_idx++] = 0;
    }

    int tcp_hdr_len = sizeof(struct tcphdr) + opt_idx;
    int total_len = sizeof(struct iphdr) + tcp_hdr_len;

    /* Заповнення полів IPv4 */
    iph->ihl = 5;
    iph->version = 4;
    iph->tos = 0;
    iph->tot_len = htons((uint16_t)total_len);
    iph->id = htons(54321);
    iph->frag_off = htons(0x4000); /* DF bit */
    iph->ttl = 64;
    iph->protocol = IPPROTO_TCP;
    iph->saddr = inet_addr(src_ip);
    iph->daddr = inet_addr(dst_ip);
    iph->check = calculate_checksum((uint16_t *)iph, sizeof(struct iphdr));

    /* Заповнення полів TCP */
    tcph->source = htons(src_port);
    tcph->dest = htons(dst_port);
    tcph->seq = htonl(isn);
    tcph->ack_seq = 0;
    tcph->doff = (uint8_t)(tcp_hdr_len / 4);
    tcph->syn = 1;
    tcph->window = htons(65535);
    tcph->check = 0;
    tcph->urg_ptr = 0;

    /* Розрахунок контрольної суми TCP з псевдозаголовком */
    struct pseudo_header psh;
    psh.src_ip = iph->saddr;
    psh.dst_ip = iph->daddr;
    psh.placeholder = 0;
    psh.protocol = IPPROTO_TCP;
    psh.tcp_length = htons((uint16_t)tcp_hdr_len);

    char pseudo_block[PACKET_BUFFER_SIZE];
    memcpy(pseudo_block, &psh, sizeof(struct pseudo_header));
    memcpy(pseudo_block + sizeof(struct pseudo_header), tcph, tcp_hdr_len);

    tcph->check = calculate_checksum((uint16_t *)pseudo_block,
                                     sizeof(struct pseudo_header) + tcp_hdr_len);

    struct sockaddr_in sin;
    memset(&sin, 0, sizeof(sin));
    sin.sin_family = AF_INET;
    sin.sin_port = htons(dst_port);
    sin.sin_addr.s_addr = iph->daddr;

    if (sendto(raw_sock, packet, total_len, 0,
               (struct sockaddr *)&sin, sizeof(sin)) < 0) {
        perror("Помилка sendto raw_sock");
        return -1;
    }

    printf("[PROBE] SYN надіслано до %s:%u (ISN=%u, MSS=%u, OptKind=%u)\n",
           dst_ip, dst_port, isn, TEST_TCP_MSS, EXPERIMENTAL_OPT_KIND);
    return 0;
}

/* Отримання та аналіз відповіді SYN-ACK */
int listen_and_analyze(int raw_sock, const char *expected_src, uint16_t expected_port, uint32_t sent_isn) {
    char buffer[PACKET_BUFFER_SIZE];
    struct timeval tv = { .tv_sec = 3, .tv_usec = 0 };
    setsockopt(raw_sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    while (1) {
        ssize_t len = recvfrom(raw_sock, buffer, sizeof(buffer), 0, NULL, NULL);
        if (len < 0) {
            printf("[TIMEOUT] Не отримано відповіді протягом 3 секунд (можливе блокування middlebox)\n");
            return -1;
        }

        struct iphdr *iph = (struct iphdr *)buffer;
        if (iph->protocol != IPPROTO_TCP) continue;

        int ip_hdr_len = iph->ihl * 4;
        if (len < ip_hdr_len + (int)sizeof(struct tcphdr)) continue;

        struct tcphdr *tcph = (struct tcphdr *)(buffer + ip_hdr_len);
        struct in_addr src_addr = { .s_addr = iph->saddr };

        if (strcmp(inet_ntoa(src_addr), expected_src) == 0 &&
            ntohs(tcph->source) == expected_port) {

            printf("\n--- РЕЗУЛЬТАТ АНАЛІЗУ СИРОГО ПАКЕТА ВІДПОВІДІ ---\n");
            printf("Прапорці TCP: %s%s\n", tcph->syn ? "SYN " : "", tcph->ack ? "ACK " : "");
            
            uint32_t recv_ack = ntohl(tcph->ack_seq);
            printf("Acknowledgment Number: %u (Очікувалось: %u)\n", recv_ack, sent_isn + 1);
            if (recv_ack != sent_isn + 1) {
                printf("  [!] ВИЯВЛЕНО ПІДМІНУ ISN / СЕКВЕНЦІЇ транзитним пристроєм!\n");
            } else {
                printf("  [OK] Номер підтвердження узгоджено коректно.\n");
            }

            int tcp_hdr_len = tcph->doff * 4;
            int opt_len = tcp_hdr_len - (int)sizeof(struct tcphdr);

            if (opt_len > 0) {
                const uint8_t *opts = (const uint8_t *)(buffer + ip_hdr_len + sizeof(struct tcphdr));
                int i = 0;
                int found_experimental = 0;

                while (i < opt_len) {
                    uint8_t kind = opts[i];
                    if (kind == 0) break; /* EOL */
                    if (kind == 1) { i++; continue; } /* NOP */

                    if (i + 1 >= opt_len) break;
                    uint8_t length = opts[i + 1];
                    if (length < 2 || i + length > opt_len) break;

                    if (kind == 2 && length == 4) {
                        uint16_t mss = (opts[i + 2] << 8) | opts[i + 3];
                        printf("Опція MSS у відповіді: %u\n", mss);
                    } else if (kind == EXPERIMENTAL_OPT_KIND) {
                        found_experimental = 1;
                        printf("  [OK] Експериментальну опцію (Kind=%u) пропущено мережею!\n", kind);
                    }
                    i += length;
                }

                if (!found_experimental) {
                    printf("  [!] Експериментальну опцію Kind=%u НЕ виявлено у відповіді (Option Stripping).\n",
                           EXPERIMENTAL_OPT_KIND);
                }
            } else {
                printf("  [!] Усі опції TCP видалено із заголовка відповіді.\n");
            }
            return 0;
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc < 5) {
        fprintf(stderr, "Використання: %s <src_ip> <dst_ip> <src_port> <dst_port>\n", argv[0]);
        return 1;
    }

    int raw_sock = socket(AF_INET, SOCK_RAW, IPPROTO_RAW);
    if (raw_sock < 0) {
        perror("Потрібні права root / CAP_NET_RAW для створення SOCK_RAW");
        return 1;
    }

    int one = 1;
    if (setsockopt(raw_sock, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
        perror("Помилка IP_HDRINCL");
        close(raw_sock);
        return 1;
    }

    uint16_t src_port = (uint16_t)atoi(argv[3]);
    uint16_t dst_port = (uint16_t)atoi(argv[4]);
    uint32_t probe_isn = 0x12345678;

    if (send_probe_syn(raw_sock, argv[1], argv[2], src_port, dst_port, probe_isn) == 0) {
        /* Для читання потрібен сокет з IPPROTO_TCP */
        int recv_sock = socket(AF_INET, SOCK_RAW, IPPROTO_TCP);
        if (recv_sock >= 0) {
            listen_and_analyze(recv_sock, argv[2], dst_port, probe_isn);
            close(recv_sock);
        }
    }

    close(raw_sock);
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <span>
#include <cstring>
#include <cstdint>
#include <unistd.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <netinet/tcp.h>
#include <sys/socket.h>
#include <sys/time.h>

namespace netprobe {

constexpr size_t kPacketBufferSize = 4096;
constexpr uint16_t kTestMss = 1460;
constexpr uint8_t kExperimentalOptKind = 30; // MPTCP Kind

struct PseudoHeader {
    uint32_t src_ip{0};
    uint32_t dst_ip{0};
    uint8_t  placeholder{0};
    uint8_t  protocol{IPPROTO_TCP};
    uint16_t tcp_length{0};
};

enum class ProbeError {
    SocketCreationFailed,
    OptionSetFailed,
    SendFailed,
    Timeout,
    InvalidPacket
};

class UniqueSocket {
public:
    explicit UniqueSocket(int fd) : fd_(fd) {}
    ~UniqueSocket() {
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
    int fd_{-1};
};

[[nodiscard]] uint16_t calculate_checksum(std::span<const uint8_t> data) noexcept {
    uint32_t sum = 0;
    size_t count = data.size();
    const auto* ptr = reinterpret_cast<const uint16_t*>(data.data());

    while (count > 1) {
        sum += *ptr++;
        count -= 2;
    }
    if (count > 0) {
        sum += *reinterpret_cast<const uint8_t*>(ptr);
    }
    while (sum >> 16) {
        sum = (sum & 0xFFFF) + (sum >> 16);
    }
    return static_cast<uint16_t>(~sum);
}

class MiddleboxScanner {
public:
    static std::expected<UniqueSocket, ProbeError> create_raw_socket(int protocol, bool ip_hdrincl = false) {
        int fd = ::socket(AF_INET, SOCK_RAW, protocol);
        if (fd < 0) {
            return std::unexpected(ProbeError::SocketCreationFailed);
        }
        if (ip_hdrincl) {
            int one = 1;
            if (::setsockopt(fd, IPPROTO_IP, IP_HDRINCL, &one, sizeof(one)) < 0) {
                ::close(fd);
                return std::unexpected(ProbeError::OptionSetFailed);
            }
        }
        return UniqueSocket(fd);
    }

    static std::expected<void, ProbeError> send_probe(
        const UniqueSocket& sock,
        std::string_view src_ip,
        std::string_view dst_ip,
        uint16_t src_port,
        uint16_t dst_port,
        uint32_t isn)
    {
        std::vector<uint8_t> packet(kPacketBufferSize, 0);

        auto* iph = reinterpret_cast<struct iphdr*>(packet.data());
        auto* tcph = reinterpret_cast<struct tcphdr*>(packet.data() + sizeof(struct iphdr));
        uint8_t* options = packet.data() + sizeof(struct iphdr) + sizeof(struct tcphdr);

        size_t opt_idx = 0;
        // MSS Option
        options[opt_idx++] = 2;
        options[opt_idx++] = 4;
        options[opt_idx++] = (kTestMss >> 8) & 0xFF;
        options[opt_idx++] = kTestMss & 0xFF;

        // Experimental MPTCP Option
        options[opt_idx++] = kExperimentalOptKind;
        options[opt_idx++] = 4;
        options[opt_idx++] = 0xDE;
        options[opt_idx++] = 0xAD;

        // Padding
        options[opt_idx++] = 1; // NOP
        options[opt_idx++] = 0; // EOL
        while (opt_idx % 4 != 0) {
            options[opt_idx++] = 0;
        }

        const size_t tcp_hdr_len = sizeof(struct tcphdr) + opt_idx;
        const size_t total_len = sizeof(struct iphdr) + tcp_hdr_len;

        // IP Header
        iph->ihl = 5;
        iph->version = 4;
        iph->tos = 0;
        iph->tot_len = htons(static_cast<uint16_t>(total_len));
        iph->id = htons(54321);
        iph->frag_off = htons(0x4000); // DF
        iph->ttl = 64;
        iph->protocol = IPPROTO_TCP;
        iph->saddr = ::inet_addr(src_ip.data());
        iph->daddr = ::inet_addr(dst_ip.data());
        iph->check = calculate_checksum(std::span<const uint8_t>(packet.data(), sizeof(struct iphdr)));

        // TCP Header
        tcph->source = htons(src_port);
        tcph->dest = htons(dst_port);
        tcph->seq = htonl(isn);
        tcph->ack_seq = 0;
        tcph->doff = static_cast<uint8_t>(tcp_hdr_len / 4);
        tcph->syn = 1;
        tcph->window = htons(65535);
        tcph->check = 0;
        tcph->urg_ptr = 0;

        // TCP Checksum calculation with PseudoHeader
        PseudoHeader psh{};
        psh.src_ip = iph->saddr;
        psh.dst_ip = iph->daddr;
        psh.placeholder = 0;
        psh.protocol = IPPROTO_TCP;
        psh.tcp_length = htons(static_cast<uint16_t>(tcp_hdr_len));

        std::vector<uint8_t> pseudo_block(sizeof(PseudoHeader) + tcp_hdr_len);
        std::memcpy(pseudo_block.data(), &psh, sizeof(PseudoHeader));
        std::memcpy(pseudo_block.data() + sizeof(PseudoHeader), tcph, tcp_hdr_len);

        tcph->check = calculate_checksum(pseudo_block);

        sockaddr_in sin{};
        sin.sin_family = AF_INET;
        sin.sin_port = htons(dst_port);
        sin.sin_addr.s_addr = iph->daddr;

        if (::sendto(sock.get(), packet.data(), total_len, 0,
                     reinterpret_cast<sockaddr*>(&sin), sizeof(sin)) < 0) {
            return std::unexpected(ProbeError::SendFailed);
        }

        std::cout << "[PROBE C++] SYN надіслано до " << dst_ip << ":" << dst_port
                  << " (ISN=" << isn << ", MSS=" << kTestMss << ")\n";
        return {};
    }

    static std::expected<void, ProbeError> receive_and_inspect(
        const UniqueSocket& sock,
        std::string_view expected_src,
        uint16_t expected_port,
        uint32_t sent_isn)
    {
        std::vector<uint8_t> buffer(kPacketBufferSize);
        timeval tv{ .tv_sec = 3, .tv_usec = 0 };
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

        while (true) {
            ssize_t len = ::recvfrom(sock.get(), buffer.data(), buffer.size(), 0, nullptr, nullptr);
            if (len < 0) {
                return std::unexpected(ProbeError::Timeout);
            }

            const auto* iph = reinterpret_cast<const struct iphdr*>(buffer.data());
            if (iph->protocol != IPPROTO_TCP) continue;

            const size_t ip_hdr_len = iph->ihl * 4;
            if (static_cast<size_t>(len) < ip_hdr_len + sizeof(struct tcphdr)) continue;

            const auto* tcph = reinterpret_cast<const struct tcphdr*>(buffer.data() + ip_hdr_len);
            in_addr src_addr{ .s_addr = iph->saddr };
            std::string_view src_ip_str(::inet_ntoa(src_addr));

            if (src_ip_str == expected_src && ntohs(tcph->source) == expected_port) {
                std::cout << "\n--- АНАЛІЗ РЕЗУЛЬТАТІВ ЗОНДУВАННЯ (C++) ---\n";
                std::cout << "Отримано прапорці: " << (tcph->syn ? "SYN " : "")
                          << (tcph->ack ? "ACK " : "") << "\n";

                uint32_t recv_ack = ntohl(tcph->ack_seq);
                std::cout << "Ack Seq: " << recv_ack << " (Очікувано: " << sent_isn + 1 << ")\n";

                if (recv_ack != sent_isn + 1) {
                    std::cout << "  [!] ВИЯВЛЕНО ПІДМІНУ ISN / СЕКВЕНЦІЇ!\n";
                } else {
                    std::cout << "  [OK] Послідовність підтверджень збережена.\n";
                }

                const size_t tcp_hdr_len = tcph->doff * 4;
                if (tcp_hdr_len > sizeof(struct tcphdr)) {
                    const size_t opt_len = tcp_hdr_len - sizeof(struct tcphdr);
                    std::span<const uint8_t> opts(buffer.data() + ip_hdr_len + sizeof(struct tcphdr), opt_len);

                    size_t i = 0;
                    bool found_opt = false;
                    while (i < opts.size()) {
                        uint8_t kind = opts[i];
                        if (kind == 0) break;
                        if (kind == 1) { i++; continue; }
                        if (i + 1 >= opts.size()) break;
                        uint8_t opt_sz = opts[i + 1];
                        if (opt_sz < 2 || i + opt_sz > opts.size()) break;

                        if (kind == 2 && opt_sz == 4) {
                            uint16_t mss = (opts[i + 2] << 8) | opts[i + 3];
                            std::cout << "Опція MSS сервера: " << mss << "\n";
                        } else if (kind == kExperimentalOptKind) {
                            found_opt = true;
                            std::cout << "  [OK] Експериментальна опція Kind=" << static_cast<int>(kind)
                                      << " успішно пройшла шлях без видалення!\n";
                        }
                        i += opt_sz;
                    }
                    if (!found_opt) {
                        std::cout << "  [!] Опцію Kind=" << static_cast<int>(kExperimentalOptKind)
                                  << " вирізано проміжним вузлом (Option Stripping).\n";
                    }
                }
                return {};
            }
        }
    }
};

} // namespace netprobe

int main(int argc, char* argv[]) {
    if (argc < 5) {
        std::cerr << "Використання: %s <src_ip> <dst_ip> <src_port> <dst_port>\n";
        return 1;
    }

    auto raw_sock = netprobe::MiddleboxScanner::create_raw_socket(IPPROTO_RAW, true);
    if (!raw_sock) {
        std::cerr << "Помилка створення сирого сокета (потрібен root / sudo)\n";
        return 1;
    }

    const uint16_t src_port = static_cast<uint16_t>(std::stoi(argv[3]));
    const uint16_t dst_port = static_cast<uint16_t>(std::stoi(argv[4]));
    constexpr uint32_t kProbeIsn = 0xABCDEF01;

    auto send_res = netprobe::MiddleboxScanner::send_probe(*raw_sock, argv[1], argv[2], src_port, dst_port, kProbeIsn);
    if (!send_res) {
        std::cerr << "Помилка відправки SYN-пакета\n";
        return 1;
    }

    auto recv_sock = netprobe::MiddleboxScanner::create_raw_socket(IPPROTO_TCP, false);
    if (recv_sock) {
        auto recv_res = netprobe::MiddleboxScanner::receive_and_inspect(*recv_sock, argv[2], dst_port, kProbeIsn);
        if (!recv_res) {
            std::cout << "[ЗБІЙ] Тайм-аут отримання відповіді.\n";
        }
    }

    return 0;
}
```
:::

---

### Компіляція, виконання та верифікація результатів

Для роботи з сирими сокетами програма вимагає привілеїв суперкористувача (`CAP_NET_RAW`) або запуску через `sudo`:

```bash
# 1. Компіляція бінарного файлу C++23
g++ -O2 -std=c++23 -Wall -Wextra proj-middlebox-probe.cpp -o probe_scanner

# 2. Надання бінарнику дозволу на сирі сокети без root-прав (опціонально)
sudo setcap cap_net_raw+ep probe_scanner

# 3. Блокування автоматичних RST локального ядра Linux
sudo iptables -A OUTPUT -p tcp --tcp-flags RST RST --sport 54321 -j DROP

# 4. Запуск зондування цільового сервера
./probe_scanner 192.168.1.50 93.184.216.34 54321 80
```

#### Інтерпретація діагностичних сценаріїв:

* **Сценарій 1: Ідеальний прозорий тракт**.
  ```text
  [PROBE C++] SYN надіслано до 93.184.216.34:80 (ISN=2882400001, MSS=1460)

  --- АНАЛІЗ РЕЗУЛЬТАТІВ ЗОНДУВАННЯ (C++) ---
  Отримано прапорці: SYN ACK 
  Ack Seq: 2882400002 (Очікувано: 2882400002)
    [OK] Послідовність підтверджень збережена.
  Опція MSS сервера: 1460
    [OK] Експериментальна опція Kind=30 успішно пройшла шлях без видалення!
  ```
  Усі опції збережено, початковий номер послідовності не зазнав зміщення, транзитні маршрутизатори працюють у чистому безстановому режимі L3.

* **Сценарій 2: Виявлено активне занулення опцій (Option Stripping)**.
  ```text
  [!] Опцію Kind=30 вирізано проміжним вузлом (Option Stripping).
  ```
  Цей результат беззаперечно доводить, що провайдерський або корпоративний фаєрвол інспектує заголовок TCP і затирає невідомі поля розширення, змушуючи з'єднання деградувати до базового однопотокового режиму.

* **Сценарій 3: Виявлено підміну початкового номера послідовності (ISN Randomization)**.
  ```text
  [!] ВИЯВЛЕНО ПІДМІНУ ISN / СЕКВЕНЦІЇ!
  ```
  Транзитний пристрій перехоплює транспортний діалог і модифікує лічильники байтів, що унеможливлює наскрізну синхронізацію прикладних протоколів без явного узгодження з проксі.

* **Сценарій 4: Виявлено затискання розміру сегмента (MSS Clamping)**.
  ```text
  Опція MSS сервера: 1412
  ```
  Якщо сервер було налаштовано на роботу зі стандартним `MSS=1460`, зменшення значення до `1412` або `1452` свідчить про те, що транзитний вузол (PPPoE, GRE або VPN-шлюз) модифікував значення опції на льоту для узгодження з вузьким MTU тунельного інтерфейсу.

---

### Аналіз та фільтрація в Wireshark / tcpdump

Для незалежної верифікації модифікацій заголовків паралельно із зондом запускається утиліта `tcpdump`:

```bash
# Захоплення лише трафіку зондування на інтерфейсі eth0
sudo tcpdump -i eth0 -nn -vvv "tcp port 54321 or icmp"
```

Корисні фільтри відображення у Wireshark:
* `tcp.options`: показує всі пакети, що містять опції TCP;
* `tcp.options.mss_val < 1460`: фільтрує пакети, де розмір MSS було примусово затиснуто проміжним обладнанням;
* `tcp.flags.reset == 1`: показує пакети аварійного розриву з'єднання (дозволяє виявити фальшиву інжекцію RST від DPI);
* `icmp.type == 11`: знаходить відповіді TTL Exceeded для визначення географічного та мережевого положення цензурного або модифікуючого вузла.

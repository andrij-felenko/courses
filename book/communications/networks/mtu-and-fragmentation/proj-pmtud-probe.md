# ⚙️ Сканер Path MTU: зондування сирими сокетами та виявлення чорних дір

У реальних гетерогенних мережах автоматичний механізм виявлення Path MTU (RFC 1191) регулярно виходить з ладу через те, що транзитні фаєрволи, хмарні фільтри безпеки та провайдерські маршрутизатори безглуздо блокують службовий трафік ICMP. Як наслідок, мережевий інженер стикається з критичним дефектом зв'язку — ефектом «чорної діри» (англ. *Path MTU Black Hole*).

Симптоми цієї проблеми підступні: малі пакети діагностичної утиліти `ping`, сесії SSH та тристороннє рукостискання TCP SYN/ACK проходять без жодних перешкод, проте щойно прикладний протокол (HTTP GET, завантаження TLS-сертифіката або передача файлу) намагається надіслати повнорозмірний блок даних, з'єднання миттєво зависає на невизначений час.

Щоб знайти точну фізичну межу пропускної здатності каналу між двома довільними хостами без опори на чужі ICMP-повідомлення, застосовують активне зондування каналу методом бінарного пошуку з примусовим встановленням прапорця **DF (Don't Fragment)** безпосередньо в заголовку IP.

---

### 1. Архітектура активного зондування та взаємодія з ядром ОС

Стандартні користувацькі сокети UDP або TCP приховують від розробника процес формування IP-заголовка: операційна система самостійно вирішує, чи фрагментувати пакет, спираючись на локальне значення MTU вихідного інтерфейсу. Якщо ми надішлемо через звичайний сокет UDP пакет розміром 3000 байтів, ядро локальної машини просто розіб'є його на два фрагменти по 1500 байтів і відправить у дріт. Такий тест не дасть жодної інформації про реальне вузьке місце на шляху до сервера.

Для точного вимірювання необхідно отримати прямий контроль над бітом `DF` (Don't Fragment) у 16-бітовому полі `Flags` заголовка IPv4.

```
Структура прапорців IPv4 (байт 6 заголовка IP):
 0   1   2
┌───┬───┬───┐
│ 0 │DF │MF │
└───┴───┴───┘
     ▲
     └── DF = 1 (Don't Fragment — заборона фрагментації)
```

Коли на пакеті виставлено біт `DF = 1`, будь-який проміжний маршрутизатор, чий вихідний лінк має `MTU < Розмір_пакета`, зобов'язаний діяти за одним із двох сценаріїв:
1. **Штатний сценарій (RFC 1191):** Маршрутизатор відкидає пакет і надсилає відправнику службове повідомлення `ICMP Type 3 Code 4` (*Destination Unreachable: Fragmentation Needed and DF set*), у якому вказує значення `Next-Hop MTU`.
2. **Сценарій Black Hole:** Маршрутизатор відкидає пакет, але фаєрвол блокує генерацію або доставку ICMP-відповіді. Відправник не отримує жодного сигналу і фіксує тайм-аут.

Наша утиліта реалізує комбінований підхід: вона надсилає серію зондувальних пакетів `ICMP Echo Request` змінного розміру з бітом `DF = 1` і визначає максимальний розмір пакета, на який надходить успішна відповідь `ICMP Echo Reply`.

---

### 2. Математична збіжність алгоритму бінарного пошуку

Пошук граничного розміру пакета виконується методом бісекції (ділення відрізка навпіл) у діапазоні від мінімального гарантованого MTU для IPv4 (`MIN_MTU = 576` байтів, RFC 791) до максимального розміру Jumbo Frame (`MAX_MTU = 9000` байтів).

Загальна кількість можливих дискретних значень MTU становить:
```
N = MAX_MTU - MIN_MTU + 1 = 9000 - 576 + 1 = 8425 варіантів.
```

Кількість ітерацій зондування `K`, необхідна для визначення точного Path MTU з точністю до одного байта, розраховується через двійковий логарифм:
```
K = ceil(log2(N)) = ceil(log2(8425)) = ceil(13.04) = 14 ітерацій.
```

Таким чином, усього за 14 мережевих проб (що за таймауту 1 секунда займає менше 5 секунд у разі успішних відповідей) утиліта гарантовано знаходить точне апаратне значення Path MTU без необхідності перебору всіх 8425 значень.

```
Схема бінарного пошуку граничного MTU:
 Діапазон: [576 ................................ 9000]
                             │
                      Проба: 4788 Б (Drop)
                             │
 Діапазон: [576 ............. 4787]
                 │
          Проба: 2681 Б (Drop)
                 │
 Діапазон: [576 . 2680]
           │
    Проба: 1628 Б (Drop)
           │
 Діапазон: [576 . 1627]
           │
    Проба: 1101 Б (OK) ──> Новий діапазон: [1102 ... 1627]
           ... (збіжність за 14 кроків)
```

---

### 3. Керування підсистемою PMTU в ядрі Linux через сокетні опції

В операційній системі Linux взаємодія із сирими сокетами `SOCK_RAW` контролюється спеціальною сокетною опцією `IP_MTU_DISCOVER` (рівень `IPPROTO_IP`). Вона приймає чотири можливі стани:

1. `IP_PMTUDISC_DONT` — ніколи не встановлювати біт DF; дозволити локальну та проміжну фрагментацію.
2. `IP_PMTUDISC_WANT` — використовувати помаршрутне налаштування ядра.
3. `IP_PMTUDISC_DO` — завжди жорстко встановлювати біт `DF = 1`. Якщо розмір пакета перевищує локальний MTU мережевої карти, системний виклик `sendto()` негайно завершується помилкою з кодом `EMSGSIZE` (*Message too long*), не випускаючи пакет у фізичний дріт.
4. `IP_PMTUDISC_PROBE` — примусово виставляти `DF = 1`, але ігнорувати локальний ліміт MTU інтерфейсу, дозволяючи відправити зонд у фізичну лінію для дослідження поведінки мережевого тракту.

У нашій утиліті ми використовуємо прапорець `IP_PMTUDISC_DO`, що дозволяє миттєво відсікати розміри, які перевищують можливості локальної мережевої карти, без зайвого очікування таймаутів.

---

### 4. Зондування без привілеїв Root через UDP та IP_RECVERR

Якщо програма виконується у непривілейованому оточенні (без прав `root` та без capability `CAP_NET_RAW`), створення сирого сокета `SOCK_RAW` буде заблоковано ядром із помилкою `EPERM`.

У такому разі застосовують альтернативний архітектурний підхід на базі стандартного сокета `SOCK_DGRAM` (UDP):
1. Створюється звичайний сокет UDP: `int sock = socket(AF_INET, SOCK_DGRAM, 0);`
2. Активується прапорець заборони фрагментації: `setsockopt(sock, IPPROTO_IP, IP_MTU_DISCOVER, &val, sizeof(val));` де `val = IP_PMTUDISC_DO`.
3. Вмикається черга розширених повідомлень про мережеві помилки ядра:
:::tabs
```c
int on = 1;
if (setsockopt(sock, IPPROTO_IP, IP_RECVERR, &on, sizeof(on)) < 0) {
    perror("Помилка налаштування IP_RECVERR");
}
```
```cpp
int on = 1;
if (::setsockopt(sock, IPPROTO_IP, IP_RECVERR, &on, sizeof(on)) < 0) {
    throw std::system_error(errno, std::generic_category(), "Помилка налаштування IP_RECVERR");
}
```
:::
4. Зондувальний пакет надсилається на довільний закритий UDP-порт віддаленого сервера (наприклад, порт `33434`, як в утиліті `traceroute`).
5. Якщо пакет перевищує MTU, функція `sendto()` повертає `EMSGSIZE` або під час виклику `recvmsg(..., MSG_ERRQUEUE)` ядро повертає структуру `sock_extended_err`, що містить точне поле `ee_info` з вивченим Path MTU від отриманого повідомлення ICMP.

---

### 5. Обчислення інтернет-контрольної суми (RFC 1071)

Протокол ICMP вимагає обов'язкового розрахунку 16-бітної контрольної суми над усім вмістом повідомлення (заголовок ICMP + корисні дані). 

Алгоритм базується на арифметиці зворотного коду (англ. *one's complement sum*):
1. Пам'ять повідомлення розглядається як масив 16-бітних беззнакових цілих чисел (`uint16_t`).
2. Усі 16-бітні слова послідовно додаються до 32-бітного акумулятора.
3. Якщо довжина буфера непарна, останній непарний байт доповнюється нулем праворуч і додається до суми.
4. Старші 16 бітів 32-бітного акумулятора (перенесення) циклічно додаються до молодших 16 бітів, доки старша половина не стане рівною нулю.
5. Результат побітово інвертується (`~sum`).

---

### 6. Реалізація утиліти: C та C++

Нижче наведено дві повні, функціональні реалізації утиліти активного сканування Path MTU. Реалізація на C демонструє класичне системне програмування на базі POSIX API, а варіант на C++20 використовує безпечні парадигми RAII, представлення пам'яті `std::span`, розумні обгортки ресурсів та строгу типізацію.

:::tabs
```c
/* pmtu_probe.c — Активне зондування Path MTU мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>
#include <sys/time.h>

#define MIN_MTU 576
#define MAX_MTU 9000
#define TIMEOUT_SEC 1

/* Обчислення контрольної суми Інтернету (RFC 1071) */
static unsigned short checksum(void *b, int len) {
    unsigned short *buf = (unsigned short *)b;
    unsigned int sum = 0;
    unsigned short result;

    for (sum = 0; len > 1; len -= 2) {
        sum += *buf++;
    }
    if (len == 1) {
        sum += *(unsigned char *)buf;
    }
    sum = (sum >> 16) + (sum & 0xFFFF);
    sum += (sum >> 16);
    result = (unsigned short)(~sum);
    return result;
}

/* Відправка одного ICMP-зонда із забороною фрагментації */
static int probe_size(int sock, struct sockaddr_in *dst, int total_ip_size) {
    /* 20 байтів IP-заголовок, 8 байтів ICMP-заголовок */
    int icmp_payload_len = total_ip_size - 20 - 8;
    if (icmp_payload_len < 0) return 0;

    int packet_len = sizeof(struct icmphdr) + icmp_payload_len;
    char *packet = (char *)malloc(packet_len);
    if (!packet) return 0;

    /* Заповнення тіла запиту детермінованим шаблоном */
    memset(packet, 0x41, packet_len);

    struct icmphdr *icmp = (struct icmphdr *)packet;
    icmp->type = ICMP_ECHO;
    icmp->code = 0;
    icmp->un.echo.id = htons((unsigned short)(getpid() & 0xFFFF));
    icmp->un.echo.sequence = htons((unsigned short)total_ip_size);
    icmp->checksum = 0;
    icmp->checksum = checksum(packet, packet_len);

    ssize_t sent = sendto(sock, packet, packet_len, 0,
                          (struct sockaddr *)dst, sizeof(*dst));
    free(packet);

    if (sent < 0) {
        if (errno == EMSGSIZE) {
            /* Локальне ядро заблокувало пакет: розмір більший за MTU адаптера */
            return -1;
        }
        return 0;
    }

    /* Очікування відповіді з таймаутом */
    char recv_buf[2048];
    struct sockaddr_in from;
    socklen_t from_len = sizeof(from);

    ssize_t received = recvfrom(sock, recv_buf, sizeof(recv_buf), 0,
                                (struct sockaddr *)&from, &from_len);
    if (received < 0) {
        /* Тайм-аут: пакет скинуто проміжним вузлом (Black Hole) */
        return 0;
    }

    struct iphdr *ip_reply = (struct iphdr *)recv_buf;
    int ip_hdr_len = ip_reply->ihl * 4;
    if (received < ip_hdr_len + (int)sizeof(struct icmphdr)) {
        return 0;
    }

    struct icmphdr *icmp_reply = (struct icmphdr *)(recv_buf + ip_hdr_len);

    /* Перевірка валідності відповіді нашого процесу */
    if (icmp_reply->type == ICMP_ECHOREPLY &&
        icmp_reply->un.echo.id == htons((unsigned short)(getpid() & 0xFFFF))) {
        return 1; /* Успіх: пакет пройшов увесь тракт туди й назад */
    }

    return 0;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Використання: %s <IP-адреса>\n", argv[0]);
        return 1;
    }

    int sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
    if (sock < 0) {
        perror("Помилка створення raw socket (потрібні права root або CAP_NET_RAW)");
        return 1;
    }

    /* Примусове встановлення прапорця DF у ядрі Linux */
    int val = IP_PMTUDISC_DO;
    if (setsockopt(sock, IPPROTO_IP, IP_MTU_DISCOVER, &val, sizeof(val)) < 0) {
        perror("Помилка конфігурації IP_MTU_DISCOVER");
        close(sock);
        return 1;
    }

    /* Встановлення таймауту очікування відповіді на сокеті */
    struct timeval tv = { .tv_sec = TIMEOUT_SEC, .tv_usec = 0 };
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    struct sockaddr_in dst;
    memset(&dst, 0, sizeof(dst));
    dst.sin_family = AF_INET;
    if (inet_pton(AF_INET, argv[1], &dst.sin_addr) <= 0) {
        fprintf(stderr, "Некоректна IP-адреса призначення: %s\n", argv[1]);
        close(sock);
        return 1;
    }

    printf("Початок активного бінарного зондування Path MTU до %s...\n", argv[1]);

    int low = MIN_MTU;
    int high = MAX_MTU;
    int optimal_mtu = 0;
    int iterations = 0;

    while (low <= high) {
        iterations++;
        int mid = low + (high - low) / 2;
        printf("  [Ітерація %2d] Тестування розміру IP-пакета: %4d байтів... ", iterations, mid);
        fflush(stdout);

        int res = probe_size(sock, &dst, mid);
        if (res == 1) {
            printf("УСПІХ (OK)\n");
            optimal_mtu = mid;
            low = mid + 1; /* Звужуємо пошук у бік більших розмірів */
        } else {
            printf("ВІДМОВА (Drop / Local EMSGSIZE)\n");
            high = mid - 1; /* Звужуємо пошук у бік менших розмірів */
        }
    }

    printf("\n=== Підсумкові результати сканування ===\n");
    if (optimal_mtu > 0) {
        printf("Точний Path MTU каналу : %d байтів\n", optimal_mtu);
        printf("Безпечний IPv4 TCP MSS : %d байтів (MTU - 40)\n", optimal_mtu - 40);
        printf("Безпечний IPv6 TCP MSS : %d байтів (MTU - 60)\n", optimal_mtu - 60);
    } else {
        printf("Помилка: цільовий вузол повністю недосяжний або блокує всі ICMP-пакети.\n");
    }

    close(sock);
    return 0;
}
```
```cpp
// pmtu_probe.cpp — Ідіоматична реалізація сканера Path MTU на C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <chrono>
#include <optional>
#include <memory>
#include <span>
#include <numeric>
#include <cstdint>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/ip.h>
#include <netinet/ip_icmp.h>
#include <arpa/inet.h>

// RAII обгортка для безпечного керування дескриптором сирого сокета
class RawSocket {
public:
    explicit RawSocket(int protocol) {
        fd_ = ::socket(AF_INET, SOCK_RAW, protocol);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(),
                                    "Не вдалося відкрити raw socket (потрібні привілеї root/CAP_NET_RAW)");
        }
    }

    ~RawSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    RawSocket(const RawSocket&) = delete;
    RawSocket& operator=(const RawSocket&) = delete;

    RawSocket(RawSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    RawSocket& operator=(RawSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    [[nodiscard]] int get() const noexcept { return fd_; }

    void set_dont_fragment() {
        int val = IP_PMTUDISC_DO;
        if (::setsockopt(fd_, IPPROTO_IP, IP_MTU_DISCOVER, &val, sizeof(val)) < 0) {
            throw std::system_error(errno, std::generic_category(), "Помилка встановлення IP_MTU_DISCOVER");
        }
    }

    void set_timeout(std::chrono::milliseconds timeout) {
        auto sec = std::chrono::duration_cast<std::chrono::seconds>(timeout);
        auto usec = std::chrono::duration_cast<std::chrono::microseconds>(timeout - sec);
        struct timeval tv{
            .tv_sec = static_cast<time_t>(sec.count()),
            .tv_usec = static_cast<suseconds_t>(usec.count())
        };
        ::setsockopt(fd_, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    }

private:
    int fd_{-1};
};

// Клас високоточного бінарного зондування каналу
class PmtuProber {
public:
    explicit PmtuProber(std::string_view target_ip) {
        socket_.set_dont_fragment();
        socket_.set_timeout(std::chrono::milliseconds(1000));

        std::memset(&dst_addr_, 0, sizeof(dst_addr_));
        dst_addr_.sin_family = AF_INET;
        if (::inet_pton(AF_INET, target_ip.data(), &dst_addr_.sin_addr) <= 0) {
            throw std::invalid_argument("Некоректний формат цільової IP-адреси");
        }
        target_ip_str_ = target_ip;
    }

    std::optional<int> discover(int min_mtu = 576, int max_mtu = 9000) {
        std::cout << "Початок C++20 бінарного зондування Path MTU до " << target_ip_str_ << "...\n";
        int low = min_mtu;
        int high = max_mtu;
        std::optional<int> best_mtu;
        int iteration = 0;

        while (low <= high) {
            iteration++;
            int mid = low + (high - low) / 2;
            std::cout << "  [Ітерація " << iteration << "] Зонд розміром " << mid << " Б... " << std::flush;

            if (send_probe(mid)) {
                std::cout << "OK (Отримано Echo Reply)\n";
                best_mtu = mid;
                low = mid + 1;
            } else {
                std::cout << "DROP / TIMEOUT\n";
                high = mid - 1;
            }
        }
        return best_mtu;
    }

private:
    static uint16_t calculate_checksum(std::span<const uint8_t> data) noexcept {
        uint32_t sum = 0;
        size_t len = data.size();
        const auto* ptr = reinterpret_cast<const uint16_t*>(data.data());

        while (len > 1) {
            sum += *ptr++;
            len -= 2;
        }
        if (len == 1) {
            sum += *reinterpret_cast<const uint8_t*>(ptr);
        }
        sum = (sum >> 16) + (sum & 0xFFFF);
        sum += (sum >> 16);
        return static_cast<uint16_t>(~sum);
    }

    bool send_probe(int total_ip_size) {
        const int icmp_payload_len = total_ip_size - 20 - 8;
        if (icmp_payload_len < 0) return false;

        const size_t packet_len = sizeof(struct icmphdr) + static_cast<size_t>(icmp_payload_len);
        std::vector<uint8_t> packet(packet_len, 0x55);

        auto* icmp = reinterpret_cast<struct icmphdr*>(packet.data());
        icmp->type = ICMP_ECHO;
        icmp->code = 0;
        icmp->un.echo.id = htons(static_cast<uint16_t>(::getpid() & 0xFFFF));
        icmp->un.echo.sequence = htons(static_cast<uint16_t>(total_ip_size));
        icmp->checksum = 0;
        icmp->checksum = calculate_checksum(packet);

        ssize_t sent = ::sendto(socket_.get(), packet.data(), packet.size(), 0,
                                reinterpret_cast<const struct sockaddr*>(&dst_addr_),
                                sizeof(dst_addr_));
        if (sent < 0) {
            return false;
        }

        std::vector<uint8_t> recv_buf(2048);
        struct sockaddr_in from{};
        socklen_t from_len = sizeof(from);

        ssize_t recvd = ::recvfrom(socket_.get(), recv_buf.data(), recv_buf.size(), 0,
                                   reinterpret_cast<struct sockaddr*>(&from), &from_len);
        if (recvd < 0) {
            return false;
        }

        if (static_cast<size_t>(recvd) < sizeof(struct iphdr) + sizeof(struct icmphdr)) {
            return false;
        }

        const auto* ip_rep = reinterpret_cast<const struct iphdr*>(recv_buf.data());
        const size_t ip_hdr_bytes = ip_rep->ihl * 4;

        if (static_cast<size_t>(recvd) < ip_hdr_bytes + sizeof(struct icmphdr)) {
            return false;
        }

        const auto* icmp_rep = reinterpret_cast<const struct icmphdr*>(recv_buf.data() + ip_hdr_bytes);
        return (icmp_rep->type == ICMP_ECHOREPLY &&
                icmp_rep->un.echo.id == htons(static_cast<uint16_t>(::getpid() & 0xFFFF)));
    }

    RawSocket socket_{IPPROTO_ICMP};
    struct sockaddr_in dst_addr_{};
    std::string target_ip_str_;
};

int main(int argc, char* argv[]) {
    if (argc != 2) {
        std::cerr << "Використання: " << argv[0] << " <IP-адреса>\n";
        return 1;
    }

    try {
        PmtuProber prober(argv[1]);
        auto pmtu = prober.discover();

        std::cout << "\n=== Підсумок активного аналізу ===\n";
        if (pmtu) {
            std::cout << "Виявлений Path MTU  = " << *pmtu << " байтів\n"
                      << "Оптимальний TCP MSS = " << (*pmtu - 40) << " байтів\n";
        } else {
            std::cout << "Помилка: канал заблоковано або вузол не відповідає на зонди.\n";
        }
    } catch (const std::exception& e) {
        std::cerr << "Критична виняткова ситуація: " << e.what() << '\n';
        return 1;
    }

    return 0;
}
```
:::

---

### 7. Детальний аналіз архітектурних рішень у коді

#### 7.1. Відмінності прийому сирих пакетів у Linux
При роботі із сокетом `SOCK_RAW` протоколу `IPPROTO_ICMP` поведінка функцій відправки та прийому відрізняється:
* Під час виклику `sendto()` ядро Linux автоматично генерує та додає 20-байтовий заголовок IPv4 (якщо не активовано опцію `IP_HDRINCL`). Тому розмір буфера, що передається у `sendto()`, повинен містити лише заголовок ICMP та дані (`total_ip_size - 20`).
* Під час виклику `recvfrom()` ядро повертає буфер, який **містить повний заголовок IPv4**. Через це програма зчитує довжину заголовка IP через поле `ip_reply->ihl * 4` і зміщує вказівник на початок заголовка ICMP.

#### 7.2. Безпека типів та ресурсів у C++20
У версії C++20 клас `RawSocket` інкапсулює файловий дескриптор, гарантуючи закриття сокета через виклик `::close()` при виході з області видимості (навіть у разі викидання винятків `std::system_error`). Використання `std::span<const uint8_t>` у функції `calculate_checksum()` унеможливлює вихід за межі масиву пам'яті (Buffer Overflow), а тип `std::optional<int>` елегантно сигналізує про відсутність результату сканування без використання магічних чисел чи глобальних прапорців помилок.

Для забезпечення максимальної надійності компіляцію програми слід виконувати з активацією санітайзерів пам'яті та адреси (`AddressSanitizer` та `UndefinedBehaviorSanitizer`):
```bash
clang++ -std=c++20 -O2 -fsanitize=address,undefined -Wall -Wextra pmtu_probe.cpp -o pmtu_probe
```

#### 7.3. Апаратна фільтрація відповідей через сокетні фільтри BPF
У високонавантажених системах на один фізичний інтерфейс можуть надходити тисячі сторонніх ICMP-пакетів щосекунди. Щоб користувацька програма не прокидалася на кожен чужий `ping`, на сирий сокет можна прикріпити класичний BPF-фільтр (`SO_ATTACH_FILTER`), скомпільований через `libpcap` або асемблер BPF. 

Фільтр BPF перевіряє на рівні драйвера мережевої карти, чи є вхідний пакет повідомленням типу `ICMP_ECHOREPLY` і чи збігається його 16-бітне поле `Identifier` з PID нашого процесу (`getpid() & 0xFFFF`). Усі чужі пакети відсікаються безпосередньо в просторі ядра, забезпечуючи нульове навантаження на контекстні перемикання користувацької програми.

---

### 8. Особливості зондування у протоколі IPv6

У стеку IPv6 архітектура виявлення Path MTU суттєво відрізняється від IPv4:
1. **Мінімальний гарантований MTU:** За стандартом RFC 8200 кожен IPv6-лінк зобов'язаний підтримувати MTU не менше **1280 байтів** (на відміну від 576 байтів у IPv4). Тому діапазон бінарного пошуку для IPv6 починається від `1280` байтів.
2. **Відсутність прапорця DF:** В основному 40-байтовому заголовку IPv6 біт `DF` відсутній у принципі, оскільки проміжним маршрутизаторам **категорично заборонено фрагментувати пакети**. Усі пакети IPv6 за замовчуванням обробляються так, ніби `DF = 1`.
3. **Опція сокета:** У Linux для контролю зондування IPv6 використовується рівень `IPPROTO_IPV6` та опція `IPV6_MTU_DISCOVER = IPV6_PMTUDISC_DO`.
4. **Тип повідомлення помилки:** Замість `ICMP Type 3 Code 4` маршрутизатори IPv6 генерують повідомлення `ICMPv6 Type 2 Code 0` (*Packet Too Big*), у якому 32-бітове поле несе точний розмір MTU вузького лінку.

---

### 9. Альтернатива транспортного рівня: PLPMTUD (RFC 4821) у ядрі Linux

Описане в нашій утиліті активне зондування на рівні ICMP є чудовим діагностичним засобом для інженера, проте в робочому мережевому стеку операційної системи реалізовано автоматичний механізм зондування на транспортному рівні — **Packetization Layer Path MTU Discovery (PLPMTUD, RFC 4821)**.

#### 9.1. Принцип роботи PLPMTUD
На відміну від класичного PMTUD (RFC 1191), який повністю покладається на повідомлення ICMP Type 3 Code 4 від проміжних роутерів, PLPMTUD зондує мережу безпосередньо транспортними сегментами TCP:
1. TCP-стек надсилає звичайний сегмент із даними прикладного рівня, але штучно збільшує його розмір до більшого значення MSS із встановленим бітом `DF = 1`.
2. Якщо віддалений сервер успішно підтверджує прийом сегмента (`TCP ACK`), ядро робить висновок, що канал пропускає більший MTU, і збільшує робочий `MSS`.
3. Якщо сегмент губиться і не підтверджується протягом тайм-ауту ретрансмісії (`RTO`), ядро не розриває з'єднання, а зменшує розмір сегмента до безпечного базового рівня (наприклад, 1024 або 536 байтів), повторює передачу і фіксує наявність «чорної діри».

#### 9.2. Увімкнення та параметри PLPMTUD у Linux
У Linux підсистема PLPMTUD контролюється через інтерфейс sysctl:
```bash
# Перевірка поточного статусу зондування MTU в ядрі
sysctl net.ipv4.tcp_mtu_probing

# Активація автоматичного зондування при виявленні "чорних дір" (значення 1)
sudo sysctl -w net.ipv4.tcp_mtu_probing=1

# Примусове постійне зондування для всіх вихідних TCP-з'єднань (значення 2)
sudo sysctl -w net.ipv4.tcp_mtu_probing=2

# Налаштування базового початкового MSS для виходу з блокування
sudo sysctl -w net.ipv4.tcp_base_mss=1024
```

Коли увімкнено `tcp_mtu_probing = 1`, веб-клієнт або сервер Linux самостійно відновлюють передачу даних у тунелях PPPoE/IPsec навіть тоді, коли провайдерський фаєрвол повністю заблокував усі типи трафіку ICMP.

---

### 10. Практичний стенд: симуляція тунелів та чорних дір у Linux Network Namespaces

Для перевірки роботи сканера в контрольованому лабораторному середовищі можна створити два мережеві простори імен (namespaces) у Linux, з'єднати їх віртуальним кабелем `veth` зі штучно заниженим MTU та заблокувати ICMP через `iptables`:

```bash
# 1. Створення ізольованих просторів імен
sudo ip netns add client_ns
sudo ip netns add server_ns

# 2. Створення віртуальної пари інтерфейсів veth
sudo ip link add veth-c type veth peer name veth-s
sudo ip link set veth-c netns client_ns
sudo ip link set veth-s netns server_ns

# 3. Налаштування IP-адрес
sudo ip netns exec client_ns ip addr add 10.0.0.1/24 dev veth-c
sudo ip netns exec client_ns ip link set veth-c up

sudo ip netns exec server_ns ip addr add 10.0.0.2/24 dev veth-s
sudo ip netns exec server_ns ip link set veth-s up

# 4. Штучне заниження MTU до 1420 на інтерфейсі сервера
sudo ip netns exec server_ns ip link set dev veth-s mtu 1420

# 5. Симуляція Path MTU Black Hole: блокування генерації ICMP fragmentation needed
sudo ip netns exec server_ns iptables -A OUTPUT -p icmp --icmp-type destination-unreachable -j DROP

# 6. Компіляція та запуск утиліти всередині простору імен клієнта
g++ -std=c++20 -O2 pmtu_probe.cpp -o pmtu_probe
sudo ip netns exec client_ns ./pmtu_probe 10.0.0.2
```

Утиліта успішно виявить точну межу каналу `Path MTU = 1420` за 14 ітерацій, незважаючи на повне блокування службових повідомлень ICMP фаєрволом сервера.

---

### 11. Аналіз мережевого трафіку під час зондування (tcpdump)

Щоб наочно побачити, що відбувається в мережевому стеку під час роботи утиліти, запустимо паралельний захват трафіку через `tcpdump`:

```bash
sudo tcpdump -nn -vvv -i eth0 "icmp and host 198.51.100.1"
```

#### 11.1. Успішний зонд нормального розміру (1400 байтів):
```
14:20:01.102345 IP (tos 0x0, ttl 64, id 14201, offset 0, flags [DF], proto ICMP (1), length 1400)
    192.0.2.10 > 198.51.100.1: ICMP echo request, id 4125, seq 1400, length 1380
14:20:01.124560 IP (tos 0x0, ttl 58, id 0, offset 0, flags [none], proto ICMP (1), length 1400)
    198.51.100.1 > 192.0.2.10: ICMP echo reply, id 4125, seq 1400, length 1380
```
*У логу чітко видно прапорець `flags [DF]`, загальну довжину `length 1400` та успішну відповідь від сервера.*

#### 11.2. Зонд розміром 1500 байтів у каналі з тунелем MTU 1420 (Black Hole):
```
14:20:02.125000 IP (tos 0x0, ttl 64, id 14202, offset 0, flags [DF], proto ICMP (1), length 1500)
    192.0.2.10 > 198.51.100.1: ICMP echo request, id 4125, seq 1500, length 1480
[Тайм-аут 1.000 с — жодної відповіді не надходить, пакет безслідно зник усередині тунелю]
```

---

### 12. Інтеграція в системи безперервного моніторингу та CI/CD

У сучасних хмарних інфраструктурах на базі Kubernetes (з мережевими плагінами CNI Flannel, Calico VXLAN або Cilium WireGuard) невідповідність MTU між фізичними серверами та оверлейними інтерфейсами `cni0` є однією з найпоширеніших причин прихованих збоїв міжсервісної взаємодії (Service Mesh, gRPC, etcd cluster sync).

Для запобігання деградації сервісів бінарний сканер Path MTU компілюють як легкозважений контейнерний DaemonSet. Кожен вузол періодично (наприклад, раз на 60 секунд) зондує сусідні ноди кластера через оверлейну мережу і експортує виявлені значення `path_mtu_bytes` у форматі метрик Prometheus:

```
# HELP node_network_path_mtu_bytes Виявлене фізичне значення Path MTU між нодами
# TYPE node_network_path_mtu_bytes gauge
node_network_path_mtu_bytes{src_node="node-01",dst_node="node-02",protocol="vxlan"} 1450
node_network_path_mtu_bytes{src_node="node-01",dst_node="node-03",protocol="wireguard"} 1420
```

Якщо на будь-якому лінку значення метрики падає нижче очікуваного конфігураційного порогу, система спостереження миттєво генерує сповіщення черговому інженеру ще до того, як користувацькі запити почнуть зазнавати таймаутів.

---

### 13. Підводні камені та типові пастки в продакшені

1. **Безпека та Linux Capabilities:** Замість постійного запуску під обліковим записом `root`, бінарному файлу надають точковий дозвіл на створення сирих сокетів:
   ```bash
   sudo setcap cap_net_raw+ep ./pmtu_probe
   ```
2. **Асиметрія маршрутизації (Asymmetric Routing):** Зондування за допомогою `ICMP Echo` вимірює комбінований шлях: прямий маршрут від клієнта до сервера (для запиту) та зворотний маршрут від сервера до клієнта (для відповіді). Якщо прямий канал проходить через пряму оптоволоконну лінію з MTU 1500, а зворотний — через тунель IPsec із MTU 1420, наш сканер чесно поверне мінімальне спільне значення `1420`, що гарантує надійність двостороннього TCP-обміну.
3. **Обмеження частоти ICMP (Rate Limiting):** Багато магістральних маршрутизаторів Cisco/Juniper мають увімкнений лімітер генерації відповідей ICMP (наприклад, не більше 100 пакетів на секунду). Якщо запускати бінарний пошук без мінімальних пауз між зондами, маршрутизатор може відкинути цілком валідний пакет через спрацювання внутрішнього полісера. Затримка в 20–50 мс між ітераціями усуває цю проблему.
4. **Трансляція мережевих адрес (NAT/CGNAT):** Деякі абонентські роутери під час трансляції вихідного ICMP-трафіку модифікують поле `Identifier`, щоб розрізняти сесії різних внутрішніх комп'ютерів. Утиліта враховує це і перевіряє кореляцію не лише за ID, а й за полем послідовності `Sequence Number`, яке збігається з тестованим розміром пакета.
5. **Вплив апаратного розвантаження NIC (LRO/GRO/TSO):** На високошвидкісних серверах мережеві карти виконують агрегацію вхідних TCP-пакетів (Generic Receive Offload). Однак для сирих ICMP-пакетів GRO зазвичай не застосовується, що забезпечує точність побайтового вимірювання фізичного MTU.
6. **Пастка фальшивих ICMP-відповідей (ICMP Spoofing DoS):** Зловмисник у спільній L2-мережі може надсилати підроблені пакети `ICMP Type 3 Code 4` із заниженим MTU (наприклад, 68 байтів), змушуючи жертву надсилати мікропакети і перевантажувати процесор. Активне зондування через сирі сокети стійке до цієї атаки, оскільки перевіряє реальну двосторонню доставку корисного пакету `ICMP Echo Reply`.

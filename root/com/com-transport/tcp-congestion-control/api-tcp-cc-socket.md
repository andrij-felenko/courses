# 📋 Керування заторами TCP у системних викликах Linux та розширенні eBPF

Операційна система Linux надає розширений системний інтерфейс для перегляду, вибору, моніторингу та детальної інспекції станів алгоритмів керування заторами TCP на кількох рівнях: загальносистемному (через подсистему `sysctl` / `procfs`), на рівні окремого сокета (через системні виклики `setsockopt` / `getsockopt`), а також на рівні розширення ядра (через модулі ядра `.ko` та програмовані хуки eBPF `struct_ops`).

Цей довідник містить повну специфікацію конфігураційних параметрів ядра, структуру `struct tcp_info`, правила виклику системних функцій у C та C++, механіка роботи eBPF-структур, а також інструменти трасування та діагностики у просторі користувача.

---

## 1. Системний інтерфейс sysctl (/proc/sys/net/ipv4/)

Ядро Linux відкриває глобальні конфігураційні параметри TCP через віртуальну файлову систему `/proc/sys/net/ipv4/`. Зміна цих параметрів впливає на всі нові сокети, що створюються у відповідному мережевому просторі імен (Network Namespace).

### Специфікація параметрів sysctl

| Параметр sysctl | Опис та допустимі значення | Права доступу | Значення за замовчуванням |
|---|---|---|---|
| `net.ipv4.tcp_congestion_control` | Рядок із назвою алгоритму за замовчуванням для нових сокетів (`cubic`, `bbr`, `reno`). | Read / Write (CAP_NET_ADMIN) | `cubic` (у сучасних ядрах `bbr`) |
| `net.ipv4.tcp_available_congestion_control` | Рядок із переліком усіх алгоритмів, завантажених у ядро (через статичну збірку або модулі `.ko`). | Read Only | `cubic reno bbr` |
| `net.ipv4.tcp_allowed_congestion_control` | Список алгоритмів, які непривілейовані процеси мають право ставити на власні сокети без прав root. | Read / Write (CAP_NET_ADMIN) | `cubic reno` |
| `net.ipv4.tcp_ecn` | Конфігурація явного повідомлення про затор ECN (0 — вимкнено, 1 — увімкнено для вхідних і вихідних, 2 — лише на прохання клієнта). | Read / Write (CAP_NET_ADMIN) | `2` |
| `net.ipv4.tcp_moderate_rcvbuf` | Прапор автоматичного підлаштування розміру приймального буфера (`rwnd`). | Read / Write (CAP_NET_ADMIN) | `1` (увімкнено) |

### Механізм обробки та привілеї

Коли процес створює новий сокет за допомогою системного виклику `socket(AF_INET, SOCK_STREAM, 0)`, ядро автоматично присвоює сокету алгоритм керування заторами з параметра `net.ipv4.tcp_congestion_control`.

Якщо процес намагається змінити алгоритм для конкретного сокета через `setsockopt`:
- Ядро перевіряє, чи входить запитаний алгоритм у список `tcp_allowed_congestion_control`. Якщо входить — виклик дозволяється для будь-якого користувача.
- Якщо алгоритм присутній у `tcp_available_congestion_control`, але відсутній у `tcp_allowed_congestion_control`, ядро перевіряє наявність привілею `CAP_NET_ADMIN` у діючому мандаті процесу. За відсутності привілею виклик повертає помилку `-1` із кодом `EPERM` (Operation not permitted).

### Приклади команд адміністрування sysctl

Переглянути поточні налаштування алгоритмів керування заторами можна за допомогою утиліти `sysctl` або прямого читання файлів `/proc/sys/`:

```bash
# Переглянути алгоритм за замовчуванням
sysctl net.ipv4.tcp_congestion_control

# Переглянути завантажені алгоритми у ядрі
cat /proc/sys/net/ipv4/tcp_available_congestion_control

# Переглянути дозволені для непривілейованих користувачів алгоритми
cat /proc/sys/net/ipv4/tcp_allowed_congestion_control

# Динамічно переключити глобальний алгоритм на BBR (потрібні права root / sudo)
sudo sysctl -w net.ipv4.tcp_congestion_control=bbr

# Додати BBR до списку дозволених для всіх користувачів
sudo sysctl -w net.ipv4.tcp_allowed_congestion_control="cubic reno bbr"
```

---

## 2. Сокетний API: виклики setsockopt та getsockopt

Програми користувацького простору (user-space) можуть індивідуально налаштовувати та інспектувати алгоритм керування заторами для кожного окремого TCP-сокета.

### Зміна алгоритму заторами для конкретного сокета (setsockopt)

Для зміни алгоритму використовується системний виклик `setsockopt` з опцією `TCP_CONGESTION` на рівні `IPPROTO_TCP` (або `SOL_TCP`).

Детальна специфікація аргументів виклику:
- **`sockfd`:** Файловий дескриптор відкритого TCP-сокета.
- **`level`:** Константа `IPPROTO_TCP` (числове значення 6 у Linux).
- **`optname`:** Опція `TCP_CONGESTION` (числове значення 13 у Linux).
- **`optval`:** Вказівник на буфер у пам'яті, що містить нуль-термінований ASCII-рядок із назвою алгоритму (наприклад, `"bbr"`, `"cubic"`, `"reno"`).
- **`optlen`:** Довжина рядка назви алгоритму у байтах (включаючи нульовий символ термінації `\0`).

:::tabs
```c
const char *algo = "bbr";
if (setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, algo, strlen(algo) + 1) < 0) {
    perror("setsockopt TCP_CONGESTION failed");
}
```
```cpp
#include <string_view>
#include <system_error>
#include <sys/socket.h>
#include <netinet/tcp.h>

void set_congestion(int sockfd, std::string_view algo) {
    if (::setsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, algo.data(), algo.size() + 1) < 0) {
        throw std::system_error(errno, std::generic_category(), "setsockopt TCP_CONGESTION failed");
    }
}
```
:::

Якщо запитаний алгоритм відсутній у завантажених модулях ядра, ядро Linux спробує автоматично завантажити відповідний модуль ядра з назвою `tcp_<name>` через механізм `kmod` (якщо процес має права `CAP_SYS_MODULE`). Якщо завантаження неможливе, `setsockopt` повертає помилку `-1` із кодом `ENOENT` (No such file or directory).

### Отримання детальної метрики стану сокета через struct tcp_info

Для перевірки поточних метрик з'єднання (розмір вікна заторів `cwnd`, поріг `ssthresh`, час RTT, швидкість пейсингу, обсяг втрачених пакетів) використовується опція `TCP_INFO`. Заголовок `<netinet/tcp.h>` визначає структуру `struct tcp_info`.

Повний опис та призначення полів structures `struct tcp_info`:

```c
struct tcp_info {
    uint8_t   tcpi_state;           /* Стан TCP з'єднання (TCP_ESTABLISHED, TCP_SYN_SENT тощо) */
    uint8_t   tcpi_ca_state;        /* Стан автомата заторів (TCP_CA_Open, TCP_CA_Disorder, TCP_CA_Recovery, TCP_CA_Loss) */
    uint8_t   tcpi_retransmits;     /* Кількість послідовних незавершених повторних передач */
    uint8_t   tcpi_probes;          /* Кількість надісланих зондувальних пакетів keepalive */
    uint8_t   tcpi_backoff;         /* Ступінь експоненціального відкату таймера RTO */
    uint8_t   tcpi_options;         /* Прапорці активних опцій TCP (Window Scale, SACK, Timestamps) */
    uint8_t   tcpi_snd_wscale : 4,  /* Масштаб вікна відправника (Window Scaling Factor) */
              tcpi_rcv_wscale : 4;  /* Масштаб вікна приймача (Window Scaling Factor) */

    uint32_t  tcpi_rto;             /* Поточне значення тайм-ауту RTO (у мікросекундах) */
    uint32_t  tcpi_ato;             /* Затримка відкладеного підтвердження ACK (у μs) */
    uint32_t  tcpi_snd_mss;         /* Максимальний розмір сегмента відправника (MSS у байтах) */
    uint32_t  tcpi_rcv_mss;         /* Максимальний розмір сегмента приймача (MSS у байтах) */

    uint32_t  tcpi_unacked;         /* Кількість пакетів у польоті, ще не підтверджених ACK */
    uint32_t  tcpi_sacked;          /* Кількість пакетів, підтверджених через вибірковий SACK */
    uint32_t  tcpi_lost;            /* Кількість пакетів, позначених як втрачені у мережі */
    uint32_t  tcpi_retrans;         /* Кількість повторно надісланих пакетів, що перебувають у польоті */
    uint32_t  tcpi_fackets;         /* Кількість пакетів між найвищим SACK та розривом */

    /* Динамічні часові позначки */
    uint32_t  tcpi_last_data_sent;  /* Час із моменту відправки останнього пакета даних (мс) */
    uint32_t  tcpi_last_ack_sent;   /* Час із моменту відправки останнього ACK (мс) */
    uint32_t  tcpi_last_data_recv;  /* Час із моменту отримання останнього пакета даних (мс) */
    uint32_t  tcpi_last_ack_recv;   /* Час із моменту отримання останнього ACK (мс) */

    uint32_t  tcpi_pmtu;            /* Визначений Path MTU для сокета */
    uint32_t  tcpi_rcv_ssthresh;    /* Поріг ssthresh приймача */
    uint32_t  tcpi_rtt;             /* Середній RTT у мікросекундах (μs) */
    uint32_t  tcpi_rttvar;          /* Варіація RTT (дисперсія затримки) у μs */
    uint32_t  tcpi_snd_ssthresh;    /* Поточний поріг ssthresh у сегментах MSS */
    uint32_t  tcpi_snd_cwnd;        /* Поточний розмір вікна заторів cwnd (у сегментах MSS) */
    uint32_t  tcpi_advmss;          /* Анонсований MSS */
    uint32_t  tcpi_reordering;      /* Поріг переупорядкування пакетів */

    uint32_t  tcpi_rcv_rtt;         /* RTT приймача (μs) */
    uint32_t  tcpi_rcv_space;       /* Поточний обсяг приймального буфера */

    uint32_t  tcpi_total_retrans;   /* Загальна кількість повторів за весь час життя з'єднання */

    uint64_t  tcpi_pacing_rate;     /* Поточна швидкість пейсингу (байтів на секунду) */
    uint64_t  tcpi_max_pacing_rate; /* Максимальна дозволена швидкість пейсингу */
    uint64_t  tcpi_bytes_acked;     /* Загальна кількість підтверджених байтів даних */
    uint64_t  tcpi_bytes_received;  /* Загальна кількість прийнятих байтів даних */
    uint32_t  tcpi_notsent_bytes;   /* Обсяг даних у буфері запису, ще не надісланих у мережу */
    uint32_t  tcpi_min_rtt;         /* Мінімальний виміряний RTT (чистий RTprop) у μs */
    uint32_t  tcpi_data_segs_in;    /* Загальна кількість вхідних сегментів із даними */
    uint32_t  tcpi_data_segs_out;   /* Загальна кількість вихідних сегментів із даними */

    uint64_t  tcpi_delivery_rate;   /* Виміряна швидкість доставки BBR (байтів на секунду) */
};
```

---

## 3. Приклади використання API мовами C та C++

У цьому розділі наведено реальні робочі приклади використання сокетного API керування заторами. Приклад мовою C демонструє прямі системні виклики та низькорівневу обробку помилок, тоді як приклад мовою C++20 показує ідіоматичний підхід з обгорткою RAII, винятками `std::system_error` та строгим контролем ресурсів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

void inspect_tcp_socket(int sockfd) {
    char name_buf[32] = {0};
    socklen_t name_len = sizeof(name_buf);

    /* Читання поточного названого алгоритму */
    if (getsockopt(sockfd, IPPROTO_TCP, TCP_CONGESTION, name_buf, &name_len) == 0) {
        printf("Поточний алгоритм CC: %s\n", name_buf);
    } else {
        perror("getsockopt TCP_CONGESTION");
    }

    /* Отримання детальної метрики tcp_info */
    struct tcp_info info;
    socklen_t info_len = sizeof(info);
    if (getsockopt(sockfd, IPPROTO_TCP, TCP_INFO, &info, &info_len) == 0) {
        printf("Метрики TCP_INFO:\n");
        printf("  - cwnd:          %u MSS (у байтах: %u)\n", 
               info.tcpi_snd_cwnd, info.tcpi_snd_cwnd * info.tcpi_snd_mss);
        printf("  - ssthresh:      %u\n", info.tcpi_snd_ssthresh);
        printf("  - RTT:           %.2f ms (var: %.2f ms)\n", 
               info.tcpi_rtt / 1000.0, info.tcpi_rttvar / 1000.0);
        printf("  - Min RTT:       %.2f ms\n", info.tcpi_min_rtt / 1000.0);
        printf("  - Pacing rate:   %.2f Mbit/s\n", 
               (info.tcpi_pacing_rate * 8.0) / 1000000.0);
        printf("  - Delivery rate: %.2f Mbit/s\n", 
               (info.tcpi_delivery_rate * 8.0) / 1000000.0);
    } else {
        perror("getsockopt TCP_INFO");
    }
}

int main(void) {
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    if (fd < 0) {
        perror("socket failed");
        return 1;
    }

    /* Встановлення алгоритму CUBIC */
    const char *algo = "cubic";
    if (setsockopt(fd, IPPROTO_TCP, TCP_CONGESTION, algo, strlen(algo) + 1) != 0) {
        perror("setsockopt TCP_CONGESTION failed");
    }

    inspect_tcp_socket(fd);

    close(fd);
    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <system_error>
#include <array>
#include <cstdint>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netinet/tcp.h>

class TcpSocket {
public:
    TcpSocket() {
        fd_ = ::socket(AF_INET, SOCK_STREAM, 0);
        if (fd_ < 0) {
            throw std::system_error(errno, std::generic_category(), "Failed to create TCP socket");
        }
    }

    ~TcpSocket() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }

    TcpSocket(const TcpSocket&) = delete;
    TcpSocket& operator=(const TcpSocket&) = delete;

    TcpSocket(TcpSocket&& other) noexcept : fd_(other.fd_) {
        other.fd_ = -1;
    }

    TcpSocket& operator=(TcpSocket&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }

    void set_congestion_algorithm(std::string_view name) {
        if (::setsockopt(fd_, IPPROTO_TCP, TCP_CONGESTION, name.data(), name.size() + 1) != 0) {
            throw std::system_error(errno, std::generic_category(), "setsockopt(TCP_CONGESTION) failed");
        }
    }

    [[nodiscard]] std::string get_congestion_algorithm() const {
        std::array<char, 32> buf{};
        socklen_t len = buf.size();
        if (::getsockopt(fd_, IPPROTO_TCP, TCP_CONGESTION, buf.data(), &len) != 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt(TCP_CONGESTION) failed");
        }
        return std::string(buf.data());
    }

    [[nodiscard]] ::tcp_info get_info() const {
        ::tcp_info info{};
        socklen_t len = sizeof(info);
        if (::getsockopt(fd_, IPPROTO_TCP, TCP_INFO, &info, &len) != 0) {
            throw std::system_error(errno, std::generic_category(), "getsockopt(TCP_INFO) failed");
        }
        return info;
    }

    [[nodiscard]] int native_handle() const noexcept { return fd_; }

private:
    int fd_{-1};
};

int main() {
    try {
        TcpSocket sock;
        sock.set_congestion_algorithm("cubic");

        std::cout << "Заданий алгоритм: " << sock.get_congestion_algorithm() << "\n";

        auto info = sock.get_info();
        std::cout << "Поточний cwnd: " << info.tcpi_snd_cwnd << " MSS\n";
        std::cout << "Поточний RTT:  " << (info.tcpi_rtt / 1000.0) << " ms\n";
        std::cout << "Min RTT:       " << (info.tcpi_min_rtt / 1000.0) << " ms\n";
    } catch (const std::exception& e) {
        std::cerr << "Помилка: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

---

## 4. Ядровий інтерфейс: struct tcp_congestion_ops та eBPF struct_ops

Усередині ядра Linux кожен алгоритм контролю заторів реєструється як модуль за допомогою структури `struct tcp_congestion_ops` (визначеної в заголовку ядра `<net/tcp.h>`):

```c
struct tcp_congestion_ops {
    struct list_head list;
    char name[TCP_CA_NAME_MAX];

    /* Ініціалізація та знищення стану сокета */
    void (*init)(struct sock *sk);
    void (*release)(struct sock *sk);

    /* Обчислення ssthresh при виявленні втрати */
    u32  (*ssthresh)(struct sock *sk);

    /* Основний крок зростання cwnd при отриманні ACK */
    void (*cong_avoid)(struct sock *sk, u32 ack, u32 acked);

    /* Зміна стану кінцевого автомата (Open, Disorder, Recovery, Loss) */
    void (*set_state)(struct sock *sk, u8 new_state);

    /* Реагування на скасування помилкових втрат (DSACK) */
    u32  (*undo_cwnd)(struct sock *sk);

    /* Обробка підтверджених пакетів (для BBR / pacing) */
    void (*pkts_acked)(struct sock *sk, const struct ack_sample *sample);

    /* Обчислення швидкості пейсингу */
    void (*cong_control)(struct sock *sk, const struct rate_sample *rs);

    struct module *owner;
};
```

Детальний опис функціонального призначення зворотних викликів (callbacks):
- **`init(sk)`:** Викликається при зв'язуванні сокета з даним алгоритмом. Виділяє пам'ять під приватні структури сокета (наприклад, `struct cubic` або `struct bbr`).
- **`ssthresh(sk)`:** Викликається ядром у момент виявлення втрати пакетів. Повертає нове знижене значення порогу `ssthresh` у сегментах MSS.
- **`cong_avoid(sk, ack, acked)`:** Основна функція розширення вікна. Викликається при отриманні кожного підтвердження ACK. Саме тут реалізується формула експоненціального розгону Slow Start чи лінійного розширення Congestion Avoidance.
- **`set_state(sk, new_state)`:** Інформує модуль алгоритму про перехід кінцевого автомата між станами `TCP_CA_Open` (нормальний потік), `TCP_CA_Disorder` (виявлено дублікати ACK), `TCP_CA_Recovery` (активна швидка повторна передача), `TCP_CA_Loss` (спрацював тайм-аут RTO).
- **`undo_cwnd(sk)`:** Викликається, якщо ядро виявляє, що втрата була помилковою (наприклад, через відновлення за допомогою DSACK). Повертає попереднє значення `cwnd`.

### Динамічне завантаження алгоритмів через eBPF struct_ops

Починаючи з версії ядра Linux 5.6, розробникам більше не потрібно збирати важкі модулі ядра `.ko` для експериментів із контролем заторів. За допомогою механізму **eBPF struct_ops** структуру `tcp_congestion_ops` можна реалізувати у вигляді програми eBPF і динамічно завантажити в ядро за допомогою системного виклику `bpf()`:

```c
/* Приклад eBPF-програми для кастомного контролера заторів */
SEC("struct_ops")
void BPF_PROG(bpf_custom_cong_avoid, struct sock *sk, u32 ack, u32 acked)
{
    struct tcp_sock *tp = tcp_sk(sk);
    if (!tcp_is_cwnd_limited(sk))
        return;

    if (tcp_in_slow_start(tp)) {
        acked = tcp_slow_start(tp, acked);
        if (!acked)
            return;
    }
    /* Кастомне лінійне розширення вікна */
    tcp_cong_avoid_ai(tp, tp->snd_cwnd, acked);
}

SEC(".struct_ops")
struct tcp_congestion_ops bpf_custom_ops = {
    .cong_avoid = (void *)bpf_custom_cong_avoid,
    .name       = "bpf_custom",
};
```

Життєвий цикл eBPF-модуля заторів:
1. Компіляція у формат ELF за допомогою Clang/LLVM (`clang -O2 -target bpf -c bpf_cc.c -o bpf_cc.o`).
2. Завантаження програми у ядро утилітою `bpftool` (`bpftool struct_ops register bpf_cc.o`).
3. Верифікатор ядра (eBPF Verifier) перевіряє безпеку типів та гарантує відсутність зависань чи некоректних доступів до пам'яті ядра.
4. Після реєстрації новий алгоритм `bpf_custom` з'являється у списку `/proc/sys/net/ipv4/tcp_available_congestion_control` і може бути вибраний викликом `setsockopt` з будь-якої програми користувача.

---

## 5. Інструменти діагностики та трасування (ss, bpftrace, tc)

Для моніторингу та аналізу роботи алгоритмів заторів у реальному часі в операційній системі Linux використовуються такі інструменти:

### 1. Утиліта ss (Socket Statistics)
Команда `ss` із прапорцем `-i` (internal info) виводить детальні метрики `tcp_info` для всіх активних сокетів у системі:

```bash
# Вивести розширені метрики TCP для всіх встановлених з'єднань
ss -ti

# Приклад виводу ss:
# ESTAB      0      0   192.168.1.50:443   192.168.1.10:52341
#      cubic wscale:7,7 rto:200 rtt:14.2/0.8 cwnd:32 ssthresh:24 pacing_rate 12.8Mbps delivery_rate 11.5Mbps
```

### 2. Трасування за допомогою bpftrace
Ядро Linux надає точки трасування `tracepoint:tcp:tcp_probe`, які викликаються при кожній зміні розміру вікна заторів `cwnd`:

```bash
# Трасування змін вікна заторів у реальному часі
sudo bpftrace -e 'tracepoint:tcp:tcp_probe { printf("Час: %s | Алгоритм/Сокет -> cwnd:%d ssthresh:%d rtt:%d\n", elapsed, args->snd_cwnd, args->ssthresh, args->srtt >> 3); }'
```

### 3. Управління дисциплінами черг (tc qdisc)
Інструмент `tc` з пакета `iproute2` дозволяє переглядати та налаштовувати активне керування чергами (AQM) на мережевих інтерфейсах:

```bash
# Переглянути поточну дисципліну черг на інтерфейсі eth0
tc qdisc show dev eth0

# Встановити справедливу чергу FQ з алгоритмом CoDel (FQ-CoDel)
sudo tc qdisc add dev eth0 root fq_codel
```

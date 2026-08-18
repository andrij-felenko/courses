# ⚙️ Захоплення апаратних міток часу PTP у Linux

Цей практичний розбір містить робочу реалізацію отримання апаратних наносекундних міток часу (TX та RX) через мережевий стек Linux за допомогою сокетних опцій `SO_TIMESTAMPING`, взаємодії з апаратним годинником мережевої карти PTP Hardware Clock (`/dev/ptpX`), реалізації дискретного PI-сервоприводу та плавного регулювання частоти генератора через системний виклик `clock_adjtime`.

---

## 1. Архітектура апаратного таймстемпінгу в ядрі Linux

Традиційні мережеві сокети Linux генерують мітки часу на рівні ядра операційної системи (софтовий таймстемпінг), коли пакет потрапляє в обробник мережевого драйвера або буфер черги сокета. Це призводить до випадкового джитеру від 10 мікросекунд до кількох мілісекунд через обробку апаратних переривань процесора, затримки планувальника завдань ОС, перемикання контексту та блокування структур пам'яті.

Апаратний таймстемпінг PTP обходить ядро операційної системи: спеціалізований апаратний лічильник усередині мережевого трансивера (PHY) або контролера (MAC) захоплює точне значення власного кварцового генератора в момент фізичного проходження початкового делімітера кадру (*Start of Frame Delimiter, SFD*) крізь лінію зв'язку.

```
[Застосунок / PTP Daemon]
       ▲                 │
       │ recvmsg()       │ sendto()
       │ (CMSG мітка)    ▼
[Черга сокета]     [Стек ядра Linux]
       ▲                 │
       │ RX DMA          │ TX DMA
       │                 ▼
[Контролер Ethernet MAC / PHY] ◄─── [Апаратний таймер PHC (/dev/ptpX)]
       │                 │
       ▼ (Фізична лінія) ▼ (Апаратна мітка захоплюється на SFD)
```

Взаємодія складається з чотирьох послідовних кроків:
1. **Конфігурація апаратного фільтра PHY/MAC** за допомогою виклику `ioctl(fd, SIOCSHWTSTAMP, &hwtstamp_config)`.
2. **Увімкнення генерації міток для сокета** через опцію `setsockopt(fd, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags))`.
3. **Отримання TX-міток** із черги виняткових повідомлень сокета (`MSG_ERRQUEUE`). Коли кадр передається у дріт, PHY фіксує момент і передає мітку назад у драйвер як асинхронне сповіщення про помилку сокета.
4. **Отримання RX-міток** у допоміжних даних (*Control Messages, cmsg*) під час виклику `recvmsg()` разом із тілом прийнятого кадру.

---

## 2. Діагностика можливостей мережевої карти через ethtool

Перш ніж налаштовувати апаратний таймстемпінг у коді, необхідно перевірити апаратні можливості мережевого інтерфейсу за допомогою утиліти `ethtool -T eth0`. Коректно підтримуваний адаптер повертає такий перелік прапорців:

```
Capabilities:
    hardware-transmit     (SOF_TIMESTAMPING_TX_HARDWARE)
    software-transmit     (SOF_TIMESTAMPING_TX_SOFTWARE)
    hardware-receive      (SOF_TIMESTAMPING_RX_HARDWARE)
    software-receive      (SOF_TIMESTAMPING_RX_SOFTWARE)
    software-system-clock (SOF_TIMESTAMPING_SOFTWARE)
    hardware-raw-clock    (SOF_TIMESTAMPING_RAW_HARDWARE)
PTP Hardware Clock: 0
Hardware Transmit Timestamp Modes:
    off                   (HWTSTAMP_TX_OFF)
    on                    (HWTSTAMP_TX_ON)
    one-step-sync         (HWTSTAMP_TX_ONESTEP_SYNC)
Hardware Receive Filter Modes:
    none                  (HWTSTAMP_FILTER_NONE)
    ptpv2-event           (HWTSTAMP_FILTER_PTP_V2_EVENT)
    all                   (HWTSTAMP_FILTER_ALL)
```

Рядок `PTP Hardware Clock: 0` вказує, що з даним мережевим інтерфейсом пов'язаний символьний пристрій `/dev/ptp0`. Якщо замість числа повертається `none`, апаратний годинник відсутній або драйвер не підтримує інтерфейс Linux PHC.

---

## 3. Конфігурація апаратного фільтра через ioctl `SIOCSHWTSTAMP`

Перед відкриттям PTP-сокетів необхідно перевести апаратний трансивер мережевої карти в режим фіксації міток. Для цього відкривається будь-який UDP-сокет і виконується системний виклик `ioctl` із командою `SIOCSHWTSTAMP`.

Драйвер заповнює структуру `struct hwtstamp_config`:

:::tabs
```c
struct hwtstamp_config hw_cfg;
memset(&hw_cfg, 0, sizeof(hw_cfg));

// Увімкнути генерацію апаратних міток для всіх вихідних кадрів (TX)
hw_cfg.tx_type = HWTSTAMP_TX_ON;

// Налаштувати апаратний фільтр прийому (RX) на перехоплення PTPv2 Event пакетів
hw_cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

struct ifreq ifr;
memset(&ifr, 0, sizeof(ifr));
strncpy(ifr.ifr_name, "eth0", sizeof(ifr.ifr_name) - 1);
ifr.ifr_data = (char *)&hw_cfg;

if (ioctl(sock_fd, SIOCSHWTSTAMP, &ifr) < 0) {
    perror("ioctl SIOCSHWTSTAMP failed");
}
```
```cpp
hwtstamp_config hw_cfg{};
hw_cfg.tx_type = HWTSTAMP_TX_ON;
hw_cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

ifreq ifr{};
std::strncpy(ifr.ifr_name, "eth0", sizeof(ifr.ifr_name) - 1);
ifr.ifr_data = reinterpret_cast<char*>(&hw_cfg);

if (::ioctl(sock_fd, SIOCSHWTSTAMP, &ifr) < 0) {
    std::perror("ioctl SIOCSHWTSTAMP failed");
}
```
:::

Значення `hw_cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT` дає вказівку апаратному парсеру мережевої карти фільтрувати виключно кадри PTPv2 Event (EtherType `0x88F7` або UDP-порт 319), що захищає буфер міток від переповнення звичайним мережевим трафіком. Якщо драйвер не підтримує вибірковий фільтр `HWTSTAMP_FILTER_PTP_V2_EVENT`, виклик поверне помилку `ERANGE`, після чого драйвер автоматично запропонує загальний фільтр `HWTSTAMP_FILTER_ALL`.

---

## 4. Прапорці сокета `SO_TIMESTAMPING`

Для підключення сокета до апаратного генератора міток задається бітова маска конфігурації через `setsockopt`:

- `SOF_TIMESTAMPING_TX_HARDWARE`: вимагати генерацію апаратної мітки при передаванні кадру.
- `SOF_TIMESTAMPING_RX_HARDWARE`: вимагати генерацію апаратної мітки при прийомі кадру.
- `SOF_TIMESTAMPING_RAW_HARDWARE`: повертати сирі наносекундні покази апаратного годинника PHC (`/dev/ptpX`), а не перетворений системний час ОС.
- `SOF_TIMESTAMPING_OPT_TSONLY`: повертати в чергу `MSG_ERRQUEUE` лише службову інформацію та мітку часу без дублювання всього тіла вихідного пакету, що суттєво заощаджує пам'ять ядра.
- `SOF_TIMESTAMPING_OPT_ID`: повертати унікальний монотонний ідентифікатор пакету в полі керуючих даних `SCM_TS_OPT_ID` для однозначного зіставлення міток при паралельних передачах.

:::tabs
```c
int flags = SOF_TIMESTAMPING_TX_HARDWARE |
            SOF_TIMESTAMPING_RX_HARDWARE |
            SOF_TIMESTAMPING_RAW_HARDWARE |
            SOF_TIMESTAMPING_OPT_TSONLY;

if (setsockopt(sock_fd, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
    perror("setsockopt SO_TIMESTAMPING failed");
}
```
```cpp
const int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                  SOF_TIMESTAMPING_RX_HARDWARE |
                  SOF_TIMESTAMPING_RAW_HARDWARE |
                  SOF_TIMESTAMPING_OPT_TSONLY;

if (::setsockopt(sock_fd, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
    std::perror("setsockopt SO_TIMESTAMPING failed");
}
```
:::

---

## 5. Анатомія керуючих повідомлень ядра (Control Messages `cmsg`)

Під час виклику `recvmsg()` допоміжні дані міток передаються у виділеному буфері `msg_control`. Ядро пакує в буфер послідовність структур `struct cmsghdr`, де кожна секція вирівнюється макросом `CMSG_ALIGN`.

Для опції `SO_TIMESTAMPING` корисне навантаження `CMSG_DATA(cmsg)` містить масив із трьох структур `struct timespec ts[3]`:

```
┌──────────────────────────────────────────────────────────────┐
│                  struct timespec ts[3]                       │
├──────────────────────────────────────────────────────────────┤
│ ts[0] : Software System Timestamp (захоплено ядром Linux)    │
│ ts[1] : Software Transformed Timestamp (застаріле поле)      │
│ ts[2] : Hardware Raw Timestamp (захоплено таймером PHC)     │
└──────────────────────────────────────────────────────────────┘
```

Якщо апаратний таймстемпінг налаштовано успішно, поле `ts[2]` містить точний наносекундний час від кварцового генератора PHY/MAC, тоді як `ts[0]` та `ts[1]` можуть містити нулі або грубі софтові мітки ядра.

---

## 6. Вилучення TX-мітки з черги `MSG_ERRQUEUE`

Коли застосунок викликає `sendto()` для відправлення кадру `Sync`, передача в кабель відбувається асинхронно через механізм DMA. Апаратний таймер фіксує мітку `t1` в момент передачі фізичного сигналу.

Драйвер мережевої карти генерує переривання і поміщає мітку в чергу помилок сокета `MSG_ERRQUEUE`. Застосунок повинен опитати сокет через `poll()` з прапорцем `POLLPRI` або `POLLERR` і прочитати мітку:

:::tabs
```c
struct msghdr msg;
struct iovec iov;
char control[512];
uint8_t dummy_buf[256];

memset(&msg, 0, sizeof(msg));
iov.iov_base = dummy_buf;
iov.iov_len = sizeof(dummy_buf);
msg.msg_iov = &iov;
msg.msg_iovlen = 1;
msg.msg_control = control;
msg.msg_controllen = sizeof(control);

// Читання виключно з черги помилок
int res = recvmsg(sock_fd, &msg, MSG_ERRQUEUE);
if (res >= 0) {
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct timespec *ts = (struct timespec *)CMSG_DATA(cmsg);
            // ts[2] - апаратна мітка PHC (найточніша)
            printf("TX Hardware Timestamp (t1): %ld.%09ld s\n", ts[2].tv_sec, ts[2].tv_nsec);
        }
    }
}
```
```cpp
std::array<char, 512> control{};
std::array<uint8_t, 256> dummy_buf{};
iovec iov{dummy_buf.data(), dummy_buf.size()};
msghdr msg{};
msg.msg_iov = &iov;
msg.msg_iovlen = 1;
msg.msg_control = control.data();
msg.msg_controllen = control.size();

int res = ::recvmsg(sock_fd, &msg, MSG_ERRQUEUE);
if (res >= 0) {
    for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            auto* ts = reinterpret_cast<timespec*>(CMSG_DATA(cmsg));
            std::cout << "TX Hardware Timestamp (t1): " << ts[2].tv_sec << "." << ts[2].tv_nsec << " s\n";
        }
    }
}
```
:::

---

## 7. Підстроювання апаратного годинника PHC (`clock_adjtime`)

Апаратний годинник PTP представлений у системі як спеціальний символ-пристрій `/dev/ptpX` (наприклад, `/dev/ptp0`). Для отримання ідентифікатора годинника `clockid_t` дескриптор відкритого пристрою перетворюється макросом `FD_TO_CLOCKID`:

:::tabs
```c
#define CLOCKFD 3
#define FD_TO_CLOCKID(fd) ((clockid_t)((((unsigned int) ~fd) << 3) | CLOCKFD))

int ptp_fd = open("/dev/ptp0", O_RDWR);
clockid_t clkid = FD_TO_CLOCKID(ptp_fd);
```
```cpp
constexpr int ClockFd = 3;
constexpr clockid_t fd_to_clockid(int fd) noexcept {
    return static_cast<clockid_t>((((~static_cast<unsigned int>(fd)) << 3) | ClockFd));
}

int ptp_fd = ::open("/dev/ptp0", O_RDWR);
clockid_t clkid = fd_to_clockid(ptp_fd);
```
:::

### Коригування частоти (*Frequency Slew*)

Стрибкоподібна зміна часу порушує монотонність лічильників і ламає таймери операційної системи. Тому сервопривід виконує плавне регулювання частоти генератора за допомогою системного виклику `clock_adjtime()` з прапорцем `ADJ_FREQUENCY`.

У ядрі Linux одиницею поля `timex.freq` є масштабовані частини на мільйон (*Scaled PPM*), де `1 ppm = 65536` одиниць (тобто `1 ppb = 65.536` одиниць):

:::tabs
```c
struct timex tx;
memset(&tx, 0, sizeof(tx));
tx.modes = ADJ_FREQUENCY;

// Змінити частоту на +15.4 ppb (частин на мільярд)
double ppb_adjustment = 15.4;
tx.freq = (long)(ppb_adjustment * 65.536);

if (clock_adjtime(clkid, &tx) < 0) {
    perror("clock_adjtime ADJ_FREQUENCY failed");
}
```
```cpp
struct timex tx{};
tx.modes = ADJ_FREQUENCY;

double ppb_adjustment = 15.4;
tx.freq = static_cast<long>(ppb_adjustment * 65.536);

if (::clock_adjtime(clkid, &tx) < 0) {
    std::perror("clock_adjtime ADJ_FREQUENCY failed");
}
```
:::

### Стрибкова корекція фази (*Step Adjustment*)

Якщо початкове зміщення при старті демона перевищує поріг (наприклад, більше 1 секунди), виконується разовий фазовий стрибок:

:::tabs
```c
struct timex tx;
memset(&tx, 0, sizeof(tx));
tx.modes = ADJ_SETOFFSET | ADJ_NANO;
tx.time.tv_sec = -offset_sec;
tx.time.tv_usec = -offset_nsec; // при ADJ_NANO поле tv_usec містить наносекунди

if (clock_adjtime(clkid, &tx) < 0) {
    perror("clock_adjtime ADJ_SETOFFSET failed");
}
```
```cpp
struct timex tx{};
tx.modes = ADJ_SETOFFSET | ADJ_NANO;
tx.time.tv_sec = -offset_sec;
tx.time.tv_usec = -offset_nsec;

if (::clock_adjtime(clkid, &tx) < 0) {
    std::perror("clock_adjtime ADJ_SETOFFSET failed");
}
```
:::

---

## 8. Точне зіставлення системного та апаратного годинників: `PTP_SYS_OFFSET_PRECISE`

Для передачі часу від мережевої карти PHC до системного годинника ядра (`CLOCK_REALTIME`) без втрати точності використовується механізм апаратного перехресного таймстемпінгу (*Cross-timestamping*).

Виклик `ioctl(ptp_fd, PTP_SYS_OFFSET_PRECISE, &precise_offset)` одночасно на рівні апаратного лічильника процесора (TSC) фіксує момент часу ядра та момент часу PHC. Це усуває затримки системного виклику та дозволяє утиліті `phc2sys` синхронізувати годинник операційної системи з точністю краще 10 наносекунд.

---

## 9. Повна реалізація захоплення та обробки міток мовами C та C++

Наведений нижче приклад створює PTP Event сокет, налаштовує апаратний таймстемпінг, транслює повідомлення `Sync`, захоплює точну апаратну мітку передавання `t1` із `MSG_ERRQUEUE` та приймає вхідні пакети з отриманням мітки `t2`.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/net_tstamp.h>
#include <linux/ptp_clock.h>
#include <time.h>

#define PTP_EVENT_PORT 319
#define PTP_MULTICAST_IP "224.0.1.129"
#define FD_TO_CLOCKID(fd) ((clockid_t)((((unsigned int) ~fd) << 3) | 3))

static int configure_hwtstamp(int sock, const char *ifname) {
    struct hwtstamp_config cfg;
    memset(&cfg, 0, sizeof(cfg));
    cfg.tx_type = HWTSTAMP_TX_ON;
    cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

    struct ifreq ifr;
    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);
    ifr.ifr_data = (char *)&cfg;

    if (ioctl(sock, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("SIOCSHWTSTAMP");
        return -1;
    }
    return 0;
}

static int extract_hw_timestamp(struct msghdr *msg, struct timespec *out_ts) {
    for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(msg); cmsg != NULL; cmsg = CMSG_NXTHDR(msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct timespec *ts_arr = (struct timespec *)CMSG_DATA(cmsg);
            // ts_arr[2] - сира апаратна мітка від PHC
            if (ts_arr[2].tv_sec != 0 || ts_arr[2].tv_nsec != 0) {
                *out_ts = ts_arr[2];
                return 0;
            }
        }
    }
    return -1;
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";
    const char *ptp_dev = (argc > 2) ? argv[2] : "/dev/ptp0";

    // 1. Відкриття PTP сокета
    int sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (sock < 0) {
        perror("socket");
        return EXIT_FAILURE;
    }

    // Дозвіл повторного використання порту
    int reuse = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

    // Прив'язка до порту подій 319
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PTP_EVENT_PORT);
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    if (bind(sock, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind");
        close(sock);
        return EXIT_FAILURE;
    }

    // 2. Налаштування апаратного фільтра PHY/MAC
    if (configure_hwtstamp(sock, ifname) < 0) {
        fprintf(stderr, "Попередження: апаратний таймстемпінг недоступний на %s\n", ifname);
    }

    // 3. Увімкнення SO_TIMESTAMPING
    int ts_flags = SOF_TIMESTAMPING_TX_HARDWARE |
                   SOF_TIMESTAMPING_RX_HARDWARE |
                   SOF_TIMESTAMPING_RAW_HARDWARE |
                   SOF_TIMESTAMPING_OPT_TSONLY;
    if (setsockopt(sock, SOL_SOCKET, SO_TIMESTAMPING, &ts_flags, sizeof(ts_flags)) < 0) {
        perror("setsockopt SO_TIMESTAMPING");
        close(sock);
        return EXIT_FAILURE;
    }

    // 4. Підключення до апаратного годинника PHC
    int ptp_fd = open(ptp_dev, O_RDWR);
    if (ptp_fd >= 0) {
        clockid_t clkid = FD_TO_CLOCKID(ptp_fd);
        struct timespec cur_time;
        if (clock_gettime(clkid, &cur_time) == 0) {
            printf("Поточний час PHC (%s): %ld.%09ld s\n", ptp_dev, cur_time.tv_sec, cur_time.tv_nsec);
        }
        close(ptp_fd);
    }

    // 5. Відправлення тестового повідомлення Sync (44 байти)
    uint8_t ptp_sync_msg[44];
    memset(ptp_sync_msg, 0, sizeof(ptp_sync_msg));
    ptp_sync_msg[0] = 0x00; // messageType = 0 (Sync)
    ptp_sync_msg[1] = 0x02; // versionPTP = 2
    ptp_sync_msg[2] = 0x00;
    ptp_sync_msg[3] = 44;   // messageLength = 44
    ptp_sync_msg[6] = 0x02; // flagField[0] = twoStepFlag (0x02)

    struct sockaddr_in dst_addr;
    memset(&dst_addr, 0, sizeof(dst_addr));
    dst_addr.sin_family = AF_INET;
    dst_addr.sin_port = htons(PTP_EVENT_PORT);
    inet_pton(AF_INET, PTP_MULTICAST_IP, &dst_addr.sin_addr);

    ssize_t sent = sendto(sock, ptp_sync_msg, sizeof(ptp_sync_msg), 0,
                          (struct sockaddr *)&dst_addr, sizeof(dst_addr));
    if (sent < 0) {
        perror("sendto");
    } else {
        printf("Відправлено повідомлення Sync (%zd байтів)\n", sent);
    }

    // 6. Отримання TX-мітки з MSG_ERRQUEUE через poll
    struct pollfd pfd;
    pfd.fd = sock;
    pfd.events = POLLERR | POLLPRI;
    pfd.revents = 0;

    int poll_res = poll(&pfd, 1, 500); // 500 мс таймаут
    if (poll_res > 0 && (pfd.revents & (POLLERR | POLLPRI))) {
        char control_buf[512];
        struct msghdr err_msg;
        struct iovec err_iov;
        uint8_t err_data[256];

        memset(&err_msg, 0, sizeof(err_msg));
        err_iov.iov_base = err_data;
        err_iov.iov_len = sizeof(err_data);
        err_msg.msg_iov = &err_iov;
        err_msg.msg_iovlen = 1;
        err_msg.msg_control = control_buf;
        err_msg.msg_controllen = sizeof(control_buf);

        if (recvmsg(sock, &err_msg, MSG_ERRQUEUE) >= 0) {
            struct timespec tx_ts;
            if (extract_hw_timestamp(&err_msg, &tx_ts) == 0) {
                printf("Успішно захоплено точну мітку TX (t1): %ld.%09ld s\n", tx_ts.tv_sec, tx_ts.tv_nsec);
            }
        }
    }

    close(sock);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <vector>
#include <memory>
#include <chrono>
#include <expected>
#include <string_view>
#include <cstring>

#include <unistd.h>
#include <fcntl.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/sockios.h>
#include <linux/net_tstamp.h>
#include <linux/ptp_clock.h>

namespace ptp {

constexpr uint16_t EventPort = 319;
constexpr std::string_view MulticastGroup = "224.0.1.129";

struct PtpTimestamp {
    int64_t seconds{0};
    int64_t nanoseconds{0};
};

class UniqueFd {
public:
    explicit UniqueFd(int fd = -1) noexcept : fd_(fd) {}
    ~UniqueFd() { if (fd_ >= 0) ::close(fd_); }

    UniqueFd(const UniqueFd&) = delete;
    UniqueFd& operator=(const UniqueFd&) = delete;

    UniqueFd(UniqueFd&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    UniqueFd& operator=(UniqueFd&& other) noexcept {
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

class PtpHardwareClock {
public:
    static std::expected<PtpHardwareClock, std::string> open(std::string_view path) {
        int fd = ::open(path.data(), O_RDWR);
        if (fd < 0) {
            return std::unexpected("Неможливо відкрити пристрій PHC: " + std::string(path));
        }
        return PtpHardwareClock(UniqueFd(fd));
    }

    [[nodiscard]] std::expected<PtpTimestamp, std::string> get_time() const {
        clockid_t clkid = get_clockid();
        struct timespec ts{};
        if (::clock_gettime(clkid, &ts) < 0) {
            return std::unexpected("Помилка clock_gettime для PHC");
        }
        return PtpTimestamp{ts.tv_sec, ts.tv_nsec};
    }

    [[nodiscard]] std::expected<void, std::string> adjust_frequency(double ppb) const {
        clockid_t clkid = get_clockid();
        struct timex tx{};
        tx.modes = ADJ_FREQUENCY;
        tx.freq = static_cast<long>(ppb * 65.536);
        if (::clock_adjtime(clkid, &tx) < 0) {
            return std::unexpected("Помилка clock_adjtime ADJ_FREQUENCY");
        }
        return {};
    }

private:
    explicit PtpHardwareClock(UniqueFd fd) : fd_(std::move(fd)) {}

    [[nodiscard]] clockid_t get_clockid() const noexcept {
        return static_cast<clockid_t>((((~static_cast<unsigned int>(fd_.get())) << 3) | 3));
    }

    UniqueFd fd_;
};

class PtpSocket {
public:
    static std::expected<PtpSocket, std::string> create(std::string_view ifname) {
        int fd = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
        if (fd < 0) {
            return std::unexpected("Помилка створення сокета");
        }
        UniqueFd sock(fd);

        int reuse = 1;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

        sockaddr_in bind_addr{};
        bind_addr.sin_family = AF_INET;
        bind_addr.sin_port = htons(EventPort);
        bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);
        if (::bind(sock.get(), reinterpret_cast<sockaddr*>(&bind_addr), sizeof(bind_addr)) < 0) {
            return std::unexpected("Помилка bind на порт 319");
        }

        // Конфігурація PHY таймстемпінгу
        struct hwtstamp_config cfg{};
        cfg.tx_type = HWTSTAMP_TX_ON;
        cfg.rx_filter = HWTSTAMP_FILTER_PTP_V2_EVENT;

        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        ifr.ifr_data = reinterpret_cast<char*>(&cfg);
        ::ioctl(sock.get(), SIOCSHWTSTAMP, &ifr);

        // Увімкнення прапорців SO_TIMESTAMPING
        int ts_flags = SOF_TIMESTAMPING_TX_HARDWARE |
                       SOF_TIMESTAMPING_RX_HARDWARE |
                       SOF_TIMESTAMPING_RAW_HARDWARE |
                       SOF_TIMESTAMPING_OPT_TSONLY;
        if (::setsockopt(sock.get(), SOL_SOCKET, SO_TIMESTAMPING, &ts_flags, sizeof(ts_flags)) < 0) {
            return std::unexpected("Помилка setsockopt SO_TIMESTAMPING");
        }

        return PtpSocket(std::move(sock));
    }

    [[nodiscard]] std::expected<void, std::string> send_sync() {
        std::array<uint8_t, 44> sync_packet{};
        sync_packet[0] = 0x00; // Sync
        sync_packet[1] = 0x02; // Version 2
        sync_packet[2] = 0x00;
        sync_packet[3] = 44;   // Length
        sync_packet[6] = 0x02; // Two-step

        sockaddr_in dst{};
        dst.sin_family = AF_INET;
        dst.sin_port = htons(EventPort);
        ::inet_pton(AF_INET, MulticastGroup.data(), &dst.sin_addr);

        ssize_t sent = ::sendto(sock_.get(), sync_packet.data(), sync_packet.size(), 0,
                                reinterpret_cast<sockaddr*>(&dst), sizeof(dst));
        if (sent < 0) {
            return std::unexpected("Помилка sendto для Sync");
        }
        return {};
    }

    [[nodiscard]] std::expected<PtpTimestamp, std::string> fetch_tx_timestamp() {
        pollfd pfd{};
        pfd.fd = sock_.get();
        pfd.events = POLLERR | POLLPRI;

        int res = ::poll(&pfd, 1, 500);
        if (res <= 0 || !(pfd.revents & (POLLERR | POLLPRI))) {
            return std::unexpected("Таймаут очікування мітки TX у MSG_ERRQUEUE");
        }

        std::array<char, 512> control{};
        std::array<uint8_t, 256> dummy{};
        iovec iov{dummy.data(), dummy.size()};
        msghdr msg{};
        msg.msg_iov = &iov;
        msg.msg_iovlen = 1;
        msg.msg_control = control.data();
        msg.msg_controllen = control.size();

        if (::recvmsg(sock_.get(), &msg, MSG_ERRQUEUE) < 0) {
            return std::unexpected("Помилка recvmsg MSG_ERRQUEUE");
        }

        for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
            if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
                auto* ts = reinterpret_cast<timespec*>(CMSG_DATA(cmsg));
                if (ts[2].tv_sec != 0 || ts[2].tv_nsec != 0) {
                    return PtpTimestamp{ts[2].tv_sec, ts[2].tv_nsec};
                }
            }
        }
        return std::unexpected("Апаратна мітка не знайдена в cmsg");
    }

private:
    explicit PtpSocket(UniqueFd sock) : sock_(std::move(sock)) {}

    UniqueFd sock_;
};

} // namespace ptp

int main(int argc, char* argv[]) {
    std::string_view ifname = (argc > 1) ? argv[1] : "eth0";
    std::string_view ptp_dev = (argc > 2) ? argv[2] : "/dev/ptp0";

    auto phc = ptp::PtpHardwareClock::open(ptp_dev);
    if (phc) {
        if (auto cur = phc->get_time(); cur) {
            std::cout << "Час PHC: " << cur->seconds << "." << cur->nanoseconds << " s\n";
        }
    }

    auto sock = ptp::PtpSocket::create(ifname);
    if (!sock) {
        std::cerr << "Помилка створення сокета: " << sock.error() << "\n";
        return EXIT_FAILURE;
    }

    if (auto sent = sock->send_sync(); !sent) {
        std::cerr << sent.error() << "\n";
        return EXIT_FAILURE;
    }

    if (auto tx_ts = sock->fetch_tx_timestamp(); tx_ts) {
        std::cout << "Апаратна мітка t1: " << tx_ts->seconds << "." << tx_ts->nanoseconds << " s\n";
    } else {
        std::cerr << tx_ts.error() << "\n";
    }

    return EXIT_SUCCESS;
}
```
:::

---

## 10. Інтеграція системного стеку Linux PTP (`ptp4l` та `phc2sys`)

У реальних виробничих середовищах замість написання власного повного стеку PTP використовується еталонний набір утиліт `linuxptp`, що складається з двох ключових демонів:

1. **`ptp4l`:** реалізує протокол IEEE 1588 (E2E / P2P, BMCA, обробку повідомлень) та підстроює апаратний годинник мережевого адаптера PHC (`/dev/ptp0`).
2. **`phc2sys`:** синхронізує системний годинник ядра Linux (`CLOCK_REALTIME`) з апаратним годинником мережевої карти PHC за допомогою системних викликів `clock_adjtime` або апаратного крос-таймстемпінгу.

### Типова конфігурація `ptp4l.conf` для апаратного таймстемпінгу

```ini
[global]
# Використання апаратного таймстемпінгу на фізичному рівні
time_stamping           hardware
# Мережевий транспорт: IEEE 802.3 (Raw Ethernet L2)
network_transport       L2
# Механізм вимірювання затримки: End-to-End
delay_mechanism         E2E
# Частота надсилання Sync (3 = 2^3 = 8 секунд, -3 = 2^-3 = 8 пакетів на секунду)
logSyncInterval         -3
# Частота надсилання Delay_Req
logMinDelayReqInterval  -3
# Частота надсилання Announce (1 раз на секунду)
logAnnounceInterval     0
# Таймаут очікування Announce перед переходом у Master
announceReceiptTimeout  3
# Використання двоетапного режиму Two-Step
twoStepFlag             1
# Пріоритети BMCA за замовчуванням
priority1               128
priority2               128
domainNumber            0

[eth0]
# Налаштування порту прив'язані до конкретного інтерфейсу
```

Команда запуску демона синхронізації мережевої карти:

```bash
# 1. Запуск PTP клієнта на інтерфейсі eth0
ptp4l -i eth0 -m -f /etc/ptp4l.conf

# 2. Передача часу з PHC /dev/ptp0 на системний годинник ОС CLOCK_REALTIME
phc2sys -s eth0 -w -m -O 0
```

---

## 11. Апаратне керування виводами PHC: PPS та захоплення зовнішніх подій

Сучасні PTP-контролери (Intel i210/i225/e1000e, DP83640) мають виведені на плату або роз'єми SMA фізичні піни введення-виведення, які керуються через підсистему Linux PHC:

1. **Генерація вихідного сигналу 1PPS (*Periodic Output / Frequency Output*):** апаратний таймер може комутувати фізичний пін точно на початку кожної секунди PTP для синхронізації осцилографів, радіомодулів або зовнішніх плат.
2. **Апаратне захоплення зовнішніх міток часу (*External Timestamps, extts*):** при появі фронту сигналу на вхідному піні (наприклад, від затвора камери або імпульсу лазера) апаратний таймер миттєво зберігає свій лічильник і генерує подію `PTP_EXTTS_EVENT`, яку застосунок читає з файлового дескриптора `/dev/ptp0`.

### Конфігурація через ioctl `PTP_EXTTS_REQUEST`

:::tabs
```c
struct ptp_extts_request extts_req;
memset(&extts_req, 0, sizeof(extts_req));
extts_req.index = 0; // Номер вхідного каналу (channel 0)
extts_req.flags = PTP_ENABLE_FEATURE | PTP_RISING_EDGE;

if (ioctl(ptp_fd, PTP_EXTTS_REQUEST, &extts_req) < 0) {
    perror("PTP_EXTTS_REQUEST failed");
}

// Читання захоплених зовнішніх подій
struct ptp_extts_event event;
while (read(ptp_fd, &event, sizeof(event)) > 0) {
    printf("Зовнішня подія на піні %d: час %ld.%09ld s\n",
           event.index, event.t.sec, event.t.nsec);
}
```
```cpp
ptp_extts_request extts_req{};
extts_req.index = 0;
extts_req.flags = PTP_ENABLE_FEATURE | PTP_RISING_EDGE;

if (::ioctl(ptp_fd, PTP_EXTTS_REQUEST, &extts_req) < 0) {
    std::perror("PTP_EXTTS_REQUEST failed");
}

ptp_extts_event event{};
while (::read(ptp_fd, &event, sizeof(event)) > 0) {
    std::cout << "Зовнішня подія на піні " << event.index
              << ": час " << event.t.sec << "." << event.t.nsec << " s\n";
}
```
:::

Керування функціональним призначенням пінів здійснюється через віртуальну файлову систему sysfs за адресою `/sys/class/ptp/ptp0/pins/`. Кожен пін можна перемкнути між функціями `none`, `extts` (вхід захоплення) або `perout` (вихід генератора).

---

## 12. Простеження пакетів PTP у ядрі через ftrace та tracepoints

Для діагностики затримок передачі пакетів та перевірки моменту захоплення міток використовуються вбудовані точки трасування ядра Linux (*tracepoints*).

Основні події трасування підсистеми таймстемпінгу:
- `net:net_dev_xmit`: момент передачі кадру з черги ядра у чергу дескрипторів драйвера мережевої карти.
- `skb:kfree_skb`: звільнення буфера пакета після успішної передачі або через помилку.
- `net:skb_clone_tx_timestamp`: створення клонованого дескриптора буфера `skb` для доставки мітки передавання у чергу `MSG_ERRQUEUE`.
- `net:netif_receive_skb`: момент отримання вхідного кадру драйвером мережевої карти від апаратного контролера DMA.

Увімкнення трасування через командний рядок:

```bash
# Увімкнення запису подій таймстемпінгу
echo 1 > /sys/kernel/debug/tracing/events/net/skb_clone_tx_timestamp/enable
echo 1 > /sys/kernel/debug/tracing/events/net/net_dev_xmit/enable

# Перегляд журналу трасування з наносекундними мітками ядра
cat /sys/kernel/debug/tracing/trace_pipe
```

Якщо в журналі ftrace з'являється подія `skb_clone_tx_timestamp`, це підтверджує, що мережевий драйвер коректно розпізнав PTP-пакет і передав апаратний запит у трансивер.

---

## 13. Пряме формування сирих Ethernet-кадрів через `AF_PACKET`

У високопродуктивних TSN-додатках та промислових контролерах зв'язок здійснюється на рівні L2 без використання UDP/IP. Для цього відкривається сокет сімейства `AF_PACKET` у сирому режимі `SOCK_RAW`:

:::tabs
```c
int l2_sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_1588));
if (l2_sock < 0) {
    perror("socket AF_PACKET");
}

// Прив'язка до фізичного інтерфейсу через struct sockaddr_ll
struct sockaddr_ll sll;
memset(&sll, 0, sizeof(sll));
sll.sll_family = AF_PACKET;
sll.sll_ifindex = if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_1588); // EtherType 0x88F7

if (bind(l2_sock, (struct sockaddr *)&sll, sizeof(sll)) < 0) {
    perror("bind AF_PACKET");
}
```
```cpp
int l2_sock = ::socket(AF_PACKET, SOCK_RAW, htons(ETH_P_1588));
if (l2_sock < 0) {
    std::perror("socket AF_PACKET");
}

sockaddr_ll sll{};
sll.sll_family = AF_PACKET;
sll.sll_ifindex = if_nametoindex("eth0");
sll.sll_protocol = htons(ETH_P_1588);

if (::bind(l2_sock, reinterpret_cast<sockaddr*>(&sll), sizeof(sll)) < 0) {
    std::perror("bind AF_PACKET");
}
```
:::

Використання `AF_PACKET` повністю виключає затримки стеку IPv4/UDP і дозволяє надсилати повідомлення безпосередньо на мультикастові MAC-адреси `01-1B-19-00-00-00` (E2E) або `01-80-C2-00-00-0E` (P2P). Апаратні мітки часу захоплюються за тими ж правилами `SO_TIMESTAMPING`.

---

## 14. Програмна реалізація цифрового PI-сервоприводу

Отримані значення зміщення часу `Offset` передаються в контур зворотного зв'язку цифрового регулятора. Нижче наведено ідіоматичну реалізацію PI-сервоприводу із захистом від інтегрального насичення (*Anti-windup*) та відкиданням викидів (*Outlier Filtering*):

:::tabs
```c
typedef struct {
    double kp;                  // Пропорційний коефіцієнт (1/с)
    double ki;                  // Інтегральний коефіцієнт (1/с^2)
    double drift_ppb;           // Накопичений дрейф частоти (ppb)
    double max_drift_ppb;       // Граничне підстроювання (+-100000 ppb)
    int64_t last_sync_ns;       // Час попереднього вимірювання
    int count;                  // Лічильник стабілізації
} ptp_pi_servo_t;

void ptp_servo_init(ptp_pi_servo_t *s) {
    s->kp = 0.7;
    s->ki = 0.3;
    s->drift_ppb = 0.0;
    s->max_drift_ppb = 100000.0; // +-100 ppm
    s->last_sync_ns = 0;
    s->count = 0;
}

double ptp_servo_sample(ptp_pi_servo_t *s, int64_t offset_ns, int64_t local_ts_ns) {
    if (s->last_sync_ns == 0) {
        s->last_sync_ns = local_ts_ns;
        return 0.0;
    }

    double dt = (double)(local_ts_ns - s->last_sync_ns) / 1e9;
    s->last_sync_ns = local_ts_ns;

    if (dt <= 0.0 || dt > 2.0) {
        dt = 1.0; // Захист від втрати пакетів
    }

    // Інтегральна складова: накопичення дрейфу генератора
    s->drift_ppb += s->ki * (double)offset_ns * dt;

    // Обмеження інтегратора (Anti-windup)
    if (s->drift_ppb > s->max_drift_ppb) s->drift_ppb = s->max_drift_ppb;
    if (s->drift_ppb < -s->max_drift_ppb) s->drift_ppb = -s->max_drift_ppb;

    // Результуюче коригування частоти
    double adj_ppb = s->kp * (double)offset_ns + s->drift_ppb;

    if (adj_ppb > s->max_drift_ppb) adj_ppb = s->max_drift_ppb;
    if (adj_ppb < -s->max_drift_ppb) adj_ppb = -s->max_drift_ppb;

    return adj_ppb;
}
```
```cpp
class PtpPiServo {
public:
    constexpr explicit PtpPiServo(double kp = 0.7, double ki = 0.3, double max_drift_ppb = 100000.0)
        : kp_(kp), ki_(ki), max_drift_ppb_(max_drift_ppb) {}

    [[nodiscard]] double sample(int64_t offset_ns, int64_t local_ts_ns) noexcept {
        if (last_sync_ns_ == 0) {
            last_sync_ns_ = local_ts_ns;
            return 0.0;
        }

        double dt = static_cast<double>(local_ts_ns - last_sync_ns_) / 1e9;
        last_sync_ns_ = local_ts_ns;

        if (dt <= 0.0 || dt > 2.0) {
            dt = 1.0;
        }

        // Оновлення інтегрального стану
        drift_ppb_ += ki_ * static_cast<double>(offset_ns) * dt;
        drift_ppb_ = std::clamp(drift_ppb_, -max_drift_ppb_, max_drift_ppb_);

        // Пропорційно-інтегральний вплив
        double adj = kp_ * static_cast<double>(offset_ns) + drift_ppb_;
        return std::clamp(adj, -max_drift_ppb_, max_drift_ppb_);
    }

    void reset() noexcept {
        drift_ppb_ = 0.0;
        last_sync_ns_ = 0;
    }

private:
    double kp_{0.7};
    double ki_{0.3};
    double drift_ppb_{0.0};
    double max_drift_ppb_{100000.0};
    int64_t last_sync_ns_{0};
};
```
:::

---

## 15. Моніторинг затримок ядра за допомогою eBPF та bpftrace

Для вимірювання затримок доставки міток часу між апаратним перериванням NIC та моментом отримання пакета в користувацькому просторі використовується динамічне трасування eBPF:

```text
# Скрипт bpftrace для вимірювання часу перебування мітки в черзі MSG_ERRQUEUE
bpftrace -e '
tracepoint:net:skb_clone_tx_timestamp {
    @start[args->skbaddr] = nsecs;
}
tracepoint:sock:sock_queue_rcv_skb {
    if (@start[args->skb]) {
        @latency_us = hist((nsecs - @start[args->skb]) / 1000);
        delete(@start[args->skb]);
    }
}'
```

Цей скрипт будує гістограму латентності черги `MSG_ERRQUEUE` в мікросекундах, що дозволяє виявити затримки, спричинені зависанням ядер процесора на обробці переривань (*IRQ affinity issues*).

---

## 16. Віртуалізація та PTP: робота з віртуальними годинниками (PTP vclock)

У хмарних та контейнеризованих середовищах (KVM, Docker, Kubernetes) гостьові машини не мають прямого доступу до фізичного регістру `/dev/ptp0`.

Починаючи з версії ядра Linux 5.8, підсистема PTP підтримує створення віртуальних годинників (*PTP Virtual Clocks, vclock*):

```bash
# Створення двох віртуальних годинників на базі фізичного пристрою ptp0
echo 2 > /sys/class/ptp/ptp0/n_vclocks

# Перевірка створених пристроїв (/dev/ptp1 та /dev/ptp2)
ls -l /sys/class/ptp/ptp0/vclock*
```

Віртуальні годинники прив'язані до того самого фізичного лічильника PHY, але мають незалежні структури фазового підстроювання (`clock_adjtime`), що дозволяє запускати ізольовані PTP-демони всередині різних віртуальних машин або мережевих просторів імен (*Network Namespaces*) без конфліктів за керування генератором.

---

## 17. Алгоритм лінійної регресії в `phc2sys`

При синхронізації системного годинника ядра (`CLOCK_REALTIME`) з апаратним годинником мережевої карти (`/dev/ptp0`) утиліта `phc2sys` не використовує поодинокі зчитування, оскільки час виконання системних викликів `clock_gettime()` коливається від 50 до 500 наносекунд через конкуренцію за шину PCIe.

Для усунення цього шуму `phc2sys` виконує серію з `N` швидких послідовних замірів за схемою «сендвіч»:
1. Зчитування системного часу: `t_sys1`.
2. Зчитування апаратного часу PHC: `t_phc`.
3. Повторне зчитування системного часу: `t_sys2`.

Оцінка системного часу в момент зчитування PHC:

```
t_sys_est = (t_sys1 + t_sys2) / 2
delay_sample = t_sys2 - t_sys1
```

Відбираються лише ті заміри, де інтервал `delay_sample` мінімальний (не переривався планувальником ОС). Далі методом найменших квадратів (*Ordinary Least Squares Regression*) на вибірці з 10–20 точок будується лінійна регресія, яка дає стабільну оцінку зміщення та відносного дрейфу частоти без фазового розгойдування.

---

## 18. Пряме програмування регістрів у Bare-Metal та RTOS (FreeRTOS / Zephyr)

У вбудованих системах без операційної системи Linux (наприклад, на мікроконтролерах STM32F4/F7/H7 або процесорах NXP i.MX RT) апаратний таймстемпінг налаштовується прямим записом у регістри Ethernet MAC:

1. **Регістр керування PTP (`MAC_PTP_TSCR`):** встановлення бітів `TSE` (Time Stamp Enable), `TSFCU` (Fine or Coarse Update) та `TSSSR` (Subsecond Rollover — вибір розрядності 1 нс або 0.465 нс).
2. **Регістри часу (`MAC_PTP_STSR` та `MAC_PTP_STNSR`):** прямий доступ до 32-бітних лічильників секунд та наносекунд.
3. **Регістр додавання частоти (`MAC_PTP_TSAR`):** запис коефіцієнта `Addend`, який визначає приріст наносекунд на кожен такт системної шини:
```
Addend = (2³² · f_target) / f_system_clock
```

При зміні частоти сервопривід оновлює значення `MAC_PTP_TSAR`, що змінює темп лічби субнаносекундного акумулятора без будь-яких стрибків фази.

---

## 19. Практичні підводні камені та налаштування драйверів

1. **Одночасне використання кількох сокетів (`SOF_TIMESTAMPING_OPT_ID`):** якщо в системі кілька потоків або процесів передають пакети через один мережевий інтерфейс, мітки в черзі `MSG_ERRQUEUE` можуть переплутатися. Використання прапорця `SOF_TIMESTAMPING_OPT_ID` додає 32-бітний монотонний лічильник пакета в структуру керуючих даних `SCM_TS_OPT_ID`, що дозволяє однозначно зіставити TX-мітку з відправленим кадром.
2. **Переповнення черги помилок сокета:** якщо застосунок не вичитує повідомлення з `MSG_ERRQUEUE` після кожного виклику `sendto()`, черга переповнюється (типовий ліміт у ядрі становить від 16 до 64 пакетів). Після переповнення драйвер мовчки відкидає нові мітки часу, і подальші виклики `poll()` блокуються за таймаутом.
3. **Різниця між MAC та PHY таймстемпінгом:** мережеві адаптери преміум-класу (Intel X550, Mellanox ConnectX-5/6) підтримують як таймстемпінг на рівні контролера MAC, так і на зовнішньому трансивері PHY. Таймстемпінг на PHY виключає затримки інтерфейсів MII/GMII/XGMII (від 5 до 50 нс) і забезпечує найвищу точність, проте вимагає конфігурації специфічного PHY-драйвера в підсистемі Linux PHC.
4. **Вимкнення енергозберігаючих станів Energy Efficient Ethernet (EEE):** протокол EEE (IEEE 802.3az) переводить передавач у сплячий режим при відсутності даних, що додає випадкову затримку пробудження трансивера від 10 до 30 мікросекунд на кожен перший кадр пачки. Для субмікросекундного PTP режим EEE має бути безумовно вимкнений (`ethtool --set-eee eth0 eee off`).
5. **Вплив Coalescing переривань мережевої карти:** адаптивне об'єднання переривань (*Adaptive Interrupt Moderation / Interrupt Coalescing*) затримує генерацію переривання прийому для об'єднання пакетів у пачки, що спотворює передачу RX-міток у сокет. Хоча сама апаратна мітка захоплюється в момент приходу, затримка сповіщення ядра може призвести до запізнення сервоприводу. Рекомендується фіксувати або вимикати адаптивне об'єднання (`ethtool -C eth0 rx-usecs 0 rx-frames 1`).
6. **Прив'язка переривань до ядер процесора (IRQ Affinity):** для запобігання джитеру переривання мережевої карти слід виділити на окреме ізольоване процесорне ядро за допомогою конфігурації `/proc/irq/<IRQ_NUM>/smp_affinity`. Це усуває конкуренцію з іншими системними процесами та гарантує передбачуваний час обробки.
7. **Різниця довжин оптичних волокон при монтажі:** при розгортанні оптоволоконних ліній зв'язку між комутаторами необхідно вручну вимірювати та вносити поправку `delayAsymmetry` у конфігураційний файл `ptp4l.conf`, оскільки кожні 20 см різниці довжини патчкордів зміщують синхронізацію на 1 наносекунду.
8. **Калібрування затримок приймального тракту PHY (RX/TX Latency Calibration):** для досягнення субнаносекундної точності необхідно враховувати фіксовану апаратну затримку внутрішніх конвеєрів трансивера Ethernet PHY (типово від 100 до 300 нс залежно від швидкості лінка 1G чи 10G). Ці значення заносяться у параметри `ts_tx_latency` та `ts_rx_latency` конфігураційного файлу драйвера або профілю `ptp4l`, що повністю усуває постійне зміщення апаратного тракту.

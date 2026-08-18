# 📋 Linux SO_TIMESTAMPING та PHC ioctl: програмний та апаратний інтерфейс міток часу

Інтерфейс часових міток ядра Linux та підсистеми апаратних годинників PTP Hardware Clock (PHC) надає розробнику повний набір конфігураційних прапорців, структур даних та системних викликів для фіксування точних моментів надсилання й отримання мережевих пакетів на всіх рівнях операційної системи та апаратного забезпечення. Цей довідник містить вичерпний опис прапорців сокетної опції `SO_TIMESTAMPING`, керування апаратним фільтром мережевого адаптера через команду `SIOCSHWTSTAMP`, вичитування міток із черги помилок сокета `MSG_ERRQUEUE`, пряме керування годинником через символьний пристрій `/dev/ptpX`, механізми нульового копіювання XDP та DPDK, а також системні виклики перехресного зчитування часу `PTP_SYS_OFFSET` та `PTP_SYS_OFFSET_PRECISE`.

---

### 1. Сокетна опція SO_TIMESTAMPING та її життєвий цикл

Налаштування генерації, фільтрації та доставки міток часу здійснюється через виклик `setsockopt()` для рівня `SOL_SOCKET` із параметром `SO_TIMESTAMPING`. Аргументом передається 32-бітне ціле число — бітова маска комбінації прапорців, що поділяються на три функціональні групи: вибір точок генерації (Generation Flags), вибір джерел часу для звіту (Reporting Flags) та модифікатори поведінки доставки (Delivery Modifiers).

#### Архітектура обробки міток у ядрі Linux

Коли користувацька програма викликає системний виклик відправки даних `sendto()` або `sendmsg()` на сокеті з увімкненим прапорцем `SOF_TIMESTAMPING_TX_HARDWARE` або `SOF_TIMESTAMPING_TX_SOFTWARE`, ядро виділяє буферну структуру `sk_buff`. У полі `skb_shared_info(skb)->tx_flags` виставляються відповідні біти запиту мітки часу:

1. **Програмна точка відправки (`dev_queue_xmit`):** Якщо встановлено прапорець `SOF_TIMESTAMPING_TX_SOFTWARE`, функція ядра `__dev_queue_xmit()` безпосередньо перед передачею буфера в чергу планувальника дисципліни обслуговування (qdisc) зчитує системний годинник ядра (`ktime_get_real()`) та створює клон структури `skb` через виклик `skb_clone_tx_timestamp()`.
2. **Точка виходу з планувальника (`qdisc`):** Якщо активовано `SOF_TIMESTAMPING_TX_SCHED`, мітка часу фіксується в момент, коли планувальник черг мережевого інтерфейсу фактично вилучає пакет із черги та передає його дескриптор у кільцевий буфер передавача драйвера (`tx_ring`).
3. **Апаратна точка передавача (MAC/PHY):** Якщо активовано `SOF_TIMESTAMPING_TX_HARDWARE`, драйвер мережевої карти встановлює спеціальний бітовий прапорець в апаратному дескрипторі передачі DMA. Контролер мережевої карти, виявивши цей прапорець, фіксує значення свого внутрішнього апаратного лічильника PHC в момент передачі першого байта Start of Frame Delimiter (SFD) на фізичну лінію. Апаратна мітка записується в окремий регістр захоплення адаптера (Tx Timestamp Register).
4. **Зворотна доставка через переривання:** Після завершення передачі кадру мережева карта генерує апаратне переривання передавача (Tx clean interrupt). Обробник переривання драйвера зчитує значення з апаратного регістру мітки, поміщає його в збережену структуру клонованого `skb` і передає цей буфер у спеціальну чергу помилок сокета (`sk->sk_error_queue`).
5. **Отримання програмою:** Користувацький процес сповіщається про наявність готової мітки через механізм мультиплексування викликів `poll()`, `epoll()` або `select()` за подією `POLLERR` і вичитує дані викликом `recvmsg()` із прапорцем `MSG_ERRQUEUE`.

#### Прапорці вибору точок генерації міток (Timestamp Generation Flags)

| Прапорець | Числове значення | Рівень фіксації та механізм дії |
|:---|:---:|:---|
| `SOF_TIMESTAMPING_TX_HARDWARE` | `(1 << 0)` | Вимагає формування апаратної мітки передавача (Tx) мережевим адаптером (MAC або PHY) при виході кадру на фізичну лінію. |
| `SOF_TIMESTAMPING_TX_SOFTWARE` | `(1 << 1)` | Формує програмну мітку Tx у ядрі в момент передачі пакета з мережевого стека до драйвера пристрою (`dev_queue_xmit()`). |
| `SOF_TIMESTAMPING_RX_HARDWARE` | `(1 << 2)` | Вимагає збереження апаратної мітки приймача (Rx), зафіксованої адаптером при виявленні преамбули вхідного кадру. |
| `SOF_TIMESTAMPING_RX_SOFTWARE` | `(1 << 3)` | Формує програмну мітку Rx у ядрі в момент обробки пакета функцією `__netif_receive_skb()`. |
| `SOF_TIMESTAMPING_TX_SCHED` | `(1 << 8)` | Фіксує програмну мітку Tx у момент виходу пакета з черги планувальника трафіку ядра (qdisc). |
| `SOF_TIMESTAMPING_TX_ACK` | `(1 << 9)` | Генерує мітку Tx у момент отримання підтвердження (ACK) для надісланих даних на рівні TCP (дозволяє оцінити повний RTT). |

#### Прапорці звітування та вибору шкали часу (Reporting Flags)

| Прапорець | Числове значення | Призначення |
|:---|:---:|:---|
| `SOF_TIMESTAMPING_SOFTWARE` | `(1 << 4)` | Вмикає повернення програмних міток ядра у структурі допоміжних даних `SCM_TIMESTAMPING`. |
| `SOF_TIMESTAMPING_SYS_HARDWARE` | `(1 << 5)` | **Застарілий прапорець**. Повертав апаратну мітку, скориговану ядром до системної шкали часу `CLOCK_REALTIME`. |
| `SOF_TIMESTAMPING_RAW_HARDWARE` | `(1 << 6)` | Повертає немодифіковане (сире) значення апаратного лічильника часу PHC мережевого адаптера. |

#### Модифікатори поведінки доставки (Delivery Modifiers)

| Прапорець | Числове значення | Механізм оптимізації |
|:---|:---:|:---|
| `SOF_TIMESTAMPING_OPT_ID` | `(1 << 7)` | Прив'язує до кожного вихідного пакета монотонний 32-бітний числовий лічильник (Sequence ID) для зіставлення мітки з пакетом. |
| `SOF_TIMESTAMPING_OPT_TSONLY` | `(1 << 11)` | Повертає з черги помилок виключно заголовок із міткою часу без копіювання корисного навантаження (економить пам'ять та CPU). |
| `SOF_TIMESTAMPING_OPT_PKTINFO` | `(1 << 13)` | Додає у допоміжне повідомлення структуру `struct scm_ts_pktinfo` з мережевим індексом інтерфейсу, що передав пакет. |
| `SOF_TIMESTAMPING_OPT_TX_SWHW` | `(1 << 14)` | Дозволяє одночасне отримання як програмної, так і апаратної мітки для одного й того самого вихідного пакета. |

---

### 2. Конфігурація апаратного фільтра мережевого адаптера (SIOCSHWTSTAMP)

Перед увімкненням опції `SOF_TIMESTAMPING_TX_HARDWARE` або `SOF_TIMESTAMPING_RX_HARDWARE` на окремому сокеті необхідно виконати глобальне налаштування апаратного фільтра мережевого інтерфейсу на рівні операційної системи за допомогою системного виклику `ioctl()` із командою `SIOCSHWTSTAMP`.

```c
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <net/if.h>

struct hwtstamp_config {
    int flags;          // Резервні прапорці, завжди встановлюються в 0
    int tx_type;        // Режим генерації міток передавача (Tx)
    int rx_filter;      // Тип пакетного фільтра приймача (Rx)
};
```

Драйвер мережевої карти передає цю конфігурацію безпосередньо у внутрішні керуючі регістри контролера (наприклад, регістри `TSYNCTXCTL` та `TSYNCRXCTL` на адаптерах Intel 82576/82580/I350/X540/E810 або через команди прошивки NIC у контролерах Mellanox ConnectX).

#### Режими конфігурації передавача (`tx_type`)

* `HWTSTAMP_TX_OFF` (`0`) — апаратне фіксування міток для вихідних пакетів повністю вимкнено в кремнії адаптера.
* `HWTSTAMP_TX_ON` (`1`) — апаратне фіксування передавача увімкнено. Мережевий адаптер фіксує момент передачі кожного дозволеного сокетом кадру, записує мітку в буферний регістр захоплення та ініціює апаратне переривання для повернення значення ядру.
* `HWTSTAMP_TX_ONESTEP_SYNC` (`2`) — однокроковий режим PTP (One-Step Clock). Контролер мережевої карти самостійно обчислює апаратний час і на льоту перезаписує поле вихідної мітки часу або поле корекції безпосередньо у вихідному кадрі `Sync` протоколу PTP без збереження мітки в регістрі та без генерації зворотного переривання.
* `HWTSTAMP_TX_ONESTEP_P2P` (`3`) — однокроковий апаратний режим для повідомлень вимірювання затримки вузол-вузол (`Pdelay_Resp`).

#### Режими фільтрації приймача (`rx_filter`)

Апаратний парсер мережевого адаптера перевіряє заголовки кожного вхідного кадру на рівні кремнію. Вибір фільтра визначає, які саме пакети підлягають апаратному стробуванню таймера:

* `HWTSTAMP_FILTER_NONE` (`0`) — апаратне фіксування вхідних пакетів вимкнено.
* `HWTSTAMP_FILTER_ALL` (`1`) — контролер фіксує апаратну мітку для **всіх без винятку** вхідних Ethernet-кадрів. Цей режим створює максимальне навантаження на кільцеві буфери дескрипторів RX DMA, оскільки до кожного дескриптора додається 64- або 80-бітне значення часу. На інтерфейсах 10/25/100 Гбіт/с рекомендується використовувати вибіркову фільтрацію для запобігання переповненню апаратного FIFO міток.
* `HWTSTAMP_FILTER_PTP_V1_L4_EVENT` (`4`) — фіксування пакетів подій PTP v1 поверх транспортного протоколу UDP/IPv4.
* `HWTSTAMP_FILTER_PTP_V2_L4_EVENT` (`7`) — апаратне фіксування пакетів подій PTP v2 (IEEE 1588-2008 / IEEE 1588-2019), переданих поверх UDP через порт 319 (повідомлення `Sync`, `Delay_Req`, `Pdelay_Req`, `Pdelay_Resp`).
* `HWTSTAMP_FILTER_PTP_V2_L2_EVENT` (`10`) — фіксування повідомлень подій PTP v2, що інкапсульовані безпосередньо в кадри Ethernet другого рівня (тип EtherType `0x88F7`).
* `HWTSTAMP_FILTER_PTP_V2_EVENT` (`12`) — універсальний фільтр PTP v2, що фіксує повідомлення подій як поверх Layer 2 Ethernet, так і поверх транспортних стеків UDP/IPv4 та UDP/IPv6.
* `HWTSTAMP_FILTER_NTP_ALL` (`15`) — апаратне фіксування всіх вхідних UDP-пакетів мережевого протоколу синхронізації часу NTP (порт призначення 123).

---

### 3. Структури даних допоміжних повідомлень (Control Messages)

Отримання часових міток через сокетний інтерфейс здійснюється через допоміжні керуючі повідомлення (Control Messages, `cmsg`), які упаковуються ядром у виділений службовий буфер `msg_control` структури `struct msghdr` при виконанні системного виклику `recvmsg()`.

#### Структура `struct scm_timestamping64`

Основний контейнер для транспортування часових міток у ядрі Linux (визначений у заголовковому файлі `<linux/net_tstamp.h>`):

```c
struct scm_timestamping64 {
    struct __kernel_timespec ts[3];
};
```

Масив `ts[3]` містить три взаємодоповнюючі часові мітки:
1. `ts[0]` — **Програмна мітка ядра (Software Timestamp)**. Відображає системний час ядра (`CLOCK_REALTIME` або `CLOCK_MONOTONIC`) у точці проходження мережевого стека. Заповнюється, якщо активний прапорець `SOF_TIMESTAMPING_SOFTWARE`.
2. `ts[1]` — **Трансформована мітка (Transformed Hardware Timestamp)**. Застаріле поле, в якому ядро намагалося автоматично транслювати апаратний час PHC у системний час за допомогою лінійної екстраполяції (активувалося прапорцем `SOF_TIMESTAMPING_SYS_HARDWARE`). У сучасному коді не використовується через накопичення систематичної похибки.
3. `ts[2]` — **Сира апаратна мітка (Raw Hardware Timestamp)**. Точний фізичний час лічильника PHC мережевого адаптера в момент фіксації преамбули кадру на межі MAC/PHY трансивера. Заповнюється, якщо встановлено прапорець `SOF_TIMESTAMPING_RAW_HARDWARE`.

#### Структура `struct sock_extended_err`

При зчитуванні міток вихідних пакетів (Tx) через чергу помилок сокета `MSG_ERRQUEUE`, керуюче повідомлення рівня `SOL_IP` або `SOL_IPV6` містить розширену інформаційну структуру:

```c
struct sock_extended_err {
    uint32_t ee_errno;    // Код помилки (для міток часу завжди встановлюється в ENOMSG)
    uint8_t  ee_origin;   // Джерело події (SO_EE_ORIGIN_TIMESTAMPING)
    uint8_t  ee_type;     // Додатковий тип події ядра
    uint8_t  ee_code;     // Додатковий код статусу
    uint8_t  ee_pad;
    uint32_t ee_info;     // Тип зафіксованої мітки часу
    uint32_t ee_data;     // Унікальний Sequence ID пакета (при увімкненому SOF_TIMESTAMPING_OPT_ID)
};
```

Поле `ee_info` однозначно вказує на фазу обробки вихідного кадру:
* `SCM_TSTAMP_SND` — мітка фактичної передачі в лінію зв'язку (апаратна мітка MAC/PHY або програмна мітка відправки).
* `SCM_TSTAMP_SCHED` — мітка моменту виходу з планувальника черг qdisc.
* `SCM_TSTAMP_ACK` — мітка моменту отримання кумулятивного TCP ACK від віддаленої сторони.

Поле `ee_data` містить числовий ідентифікатор, який інкрементується ядром для кожного вихідного пакета окремо на рівні сокета. Це дозволяє прикладній програмі точно зіставити отриману з черги помилок мітку з раніше надісланим пакетом навіть при інтенсивному асинхронному трафіку.

#### Структура `struct scm_ts_pktinfo`

Якщо під час конфігурації сокета було встановлено прапорець `SOF_TIMESTAMPING_OPT_PKTINFO`, разом із міткою часу ядро повертає додаткове службове повідомлення типу `SCM_TIMESTAMPING_PKTINFO`:

```c
struct scm_ts_pktinfo {
    uint32_t if_index; // Системний числовий індекс мережевого інтерфейсу
    uint32_t pkt_length; // Повна довжина пакета в байтах
    uint32_t seq_no; // Порядковий номер пакета
    uint32_t reserved;
};
```

Це критично важливо для додатків синхронізації часу, що працюють на мультиінтерфейсних маршрутизаторах або мостах, де вихідний пакет може бути спрямований ядром через різні фізичні порти залежно від динамічної таблиці комутації.

---

### 4. Інтерфейс системних викликів PHC (PTP Hardware Clock ioctl)

Символьні пристрої `/dev/ptp0`, `/dev/ptp1`, ..., `/dev/ptpN` представляють прямий апаратний інтерфейс до годинників мережевих карт. Зв'язок між мережевим інтерфейсом `eth0` та відповідним символьним пристроєм визначається командою `ethtool -T eth0` або через читання псевдофайлової системи sysfs: `/sys/class/net/eth0/device/ptp/ptp0`.

#### Системні виклики прямого зчитування та підстроювання частоти

Файловий дескриптор відкритого пристрою `/dev/ptpX` може бути перетворений у стандартний системний ідентифікатор `clockid_t` за допомогою макросу `FD_TO_CLOCKID(fd)`:

```c
#include <linux/ptp_clock.h>
#include <time.h>

#define CLOCKFD 3
#define FD_TO_CLOCKID(fd) ((~(clockid_t)(fd) << 3) | CLOCKFD)

// Зчитування поточного апаратного часу:
struct timespec64 ts;
clockid_t clkid = FD_TO_CLOCKID(ptp_fd);
clock_gettime(clkid, (struct timespec *)&ts);
```

Для дисциплінування апаратного годинника використовується системний виклик `clock_adjtime()`:
* **Корекція частоти генератора (Frequency Tuning):** Передається прапорець `ADJ_FREQUENCY` та значення зміщення частоти `freq` у форматі частин на мільярд зі зсувом 16 бітів (Scaled PPM / PPB). Це змінює коефіцієнт ділення апаратного цифрового акумулятора частоти (Phase Accumulator) без стрибків фази.
* **Фазове зміщення (Phase Step):** Передається прапорець `ADJ_SETOFFSET` разом зі структурою зміщення часу `struct timex`, що миттєво додає або віднімає задану кількість секунд та наносекунд від лічильника годинника.

#### Програмне перехресне зчитування (`PTP_SYS_OFFSET`)

Якщо апаратна платформа не підтримує синхронне стробування лічильників у кремнії, для оцінки розсинхрону між системним годинником CPU та годинником PHC мережевої карти застосовується системний виклик `ioctl(fd, PTP_SYS_OFFSET, &sysoff)`:

```c
struct ptp_sys_offset {
    unsigned int n_samples; // Кількість вимірювальних трійок (максимум PTP_MAX_SAMPLES = 25)
    unsigned int rsv[3];    // Резервні поля
    struct ptp_clock_time ts[2 * PTP_MAX_SAMPLES + 1];
};
```

Ядро в циклі з вимкненими локальними перериваннями виконує послідовність вимірювань:
1. `ts[2*i]` — системний час процесора `ktime_get_real()` безпосередньо перед транзакцією читання шини PCIe.
2. `ts[2*i + 1]` — апаратний час PHC, вичитаний через регістр шини PCIe.
3. `ts[2*i + 2]` — системний час процесора `ktime_get_real()` одразу після завершення операції зчитування PCIe.

Оцінка часу процесора в момент фіксації апаратного значення розраховується як середина інтервалу `(ts[2*i] + ts[2*i + 2]) / 2`, а максимальна похибка оцінки дорівнює половині тривалості транзакції PCIe: `(ts[2*i + 2] - ts[2*i]) / 2`. Серед серії вибірок алгоритм вибирає ту, для якої затримка шини виявилася мінімальною.

#### Апаратне перехресне зчитування (`PTP_SYS_OFFSET_PRECISE`)

На сучасних процесорних платформах (Intel Skylake і новіше з таймером Always Running Timer, ART, або ARMv8/v9 з Generic Timer) та серверних мережевих картах з підтримкою розширення шини PCIe Precision Time Measurement (PTM) доступне апаратне стробування:

```c
struct ptp_sys_offset_precise {
    struct ptp_clock_time device;       // Час PHC мережевої карти
    struct ptp_clock_time sys_realtime; // Системний час CLOCK_REALTIME у той самий фізичний такт
    struct ptp_clock_time sys_monoraw;  // Системний час CLOCK_MONOTONIC_RAW у той самий фізичний такт
    unsigned int rsv[4];                // Резерв
};
```

Команда `PTP_SYS_OFFSET_PRECISE` використовує апаратний сигнал стробування або протокольні пакети PCIe PTM TLP для одночасної фіксації стану лічильників процесора та мережевого адаптера на фізичному рівні. Це повністю усуває невизначеність затримок шини PCIe, черг транзакцій та переривань операційної системи, забезпечуючи точність взаємної прив'язки кращу за 10 наносекунд.

---

### 5. Високопродуктивні інтерфейси нульового копіювання (XDP та DPDK)

Для додатків ультранизької затримки (алгоритмічна торгівля, обробка радарних даних, високоточні шлюзи Time-Sensitive Networking) стандартний сокетний стек ядра додає 1–5 мікросекунд накладних витрат на виділення пам'яті `sk_buff` та копіювання даних. У цих сценаріях застосовуються спеціалізовані інтерфейси прямого доступу до дескрипторів.

#### Апаратні мітки в eXpress Data Path (eBPF / XDP)

Починаючи з версії ядра Linux 6.3, підсистема XDP надає стандартизований інтерфейс метаданих `XDP Metadata KFuncs` для зчитування апаратних міток часу безпосередньо в драйвері мережевої карти до створення структури `sk_buff`:

```c
// Виклик усередині програми eBPF XDP:
extern int bpf_xdp_metadata_rx_timestamp(const struct xdp_md *ctx, __u64 *timestamp) __ksym;

SEC("xdp")
int filter_ptp_fast(struct xdp_md *ctx) {
    __u64 hw_timestamp_ns = 0;
    if (bpf_xdp_metadata_rx_timestamp(ctx, &hw_timestamp_ns) == 0) {
        // Доступ до сирої наносекундної мітки з апаратного дескриптора RX
        // Обробка або передача в AF_XDP сокет через кільце UMEM
    }
    return XDP_PASS;
}
```

#### Інтерфейс DPDK (Data Plane Development Kit)

У просторі користувача DPDK керує мережевим адаптером через драйвери режиму опитування (Poll Mode Drivers, PMD) в обхід ядра Linux. Для роботи з часовими мітками IEEE 1588 API DPDK надає набір функцій:

```c
#include <rte_ethdev.h>

// 1. Активація апаратного таймстемпінгу на порту:
rte_eth_timesync_enable(port_id);

// 2. Зчитування апаратної мітки вхідного пакета:
struct timespec rx_ts;
rte_eth_timesync_read_rx_timestamp(port_id, &rx_ts, pkt_flags);

// 3. Зчитування мітки передавача після відправки:
struct timespec tx_ts;
rte_eth_timesync_read_tx_timestamp(port_id, &tx_ts);

// 4. Пряме підстроювання апаратного годинника карти:
rte_eth_timesync_adjust_time(port_id, delta_nanoseconds);
```

---

### 6. Діагностика, простеження та обробка крайових випадків

#### Перевірка апаратних можливостей інтерфейсу через ethtool

Перед розгортанням програмного забезпечення необхідно перевірити апаратні можливості мережевого інтерфейсу та драйвера:

```bash
$ ethtool -T eth0
Time stamping parameters for eth0:
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
    all                   (HWTSTAMP_FILTER_ALL)
    ptpv2-event           (HWTSTAMP_FILTER_PTP_V2_EVENT)
```

#### Типові помилки та системні обмеження

1. **Переповнення черги помилок сокета (`ENOBUFS` / `ENOMSG`):** Якщо користувацька програма надсилає пакети з високою частотою, але не вичитує мітки з черги `MSG_ERRQUEUE`, буфер сокета переповнюється. Ядро починає скидати нові мітки часу. Розмір виділеної службової пам'яті для сокетних допоміжних повідомлень обмежується системним параметром `sysctl net.core.optmem_max` (за замовчуванням 20480 байтів; для високонавантажених PTP-систем рекомендується збільшувати до 2–4 МБ).
2. **Конкуренція за апаратні регістри захоплення Tx:** Багато недорогих мережевих адаптерів мають лише один або два апаратні регістри для збереження Tx-міток. Якщо програма намагається надіслати другий пакет із запитом апаратної мітки до того, як драйвер вичитав попередню мітку через переривання, мережева карта повертає помилку або перезаписує попереднє значення. Для уникнення цього необхідно або обмежувати кількість вихідних синхронізаційних пакетів у польоті, або використовувати прапорець `SOF_TIMESTAMPING_OPT_ID` для суворого контролю черговості.
3. **Віртуальні інтерфейси та агрегація каналів (Bonding/VLAN):** При роботі через віртуальні інтерфейси типу `bond0` або `vlan100` сокетна опція `SO_TIMESTAMPING` має налаштовуватися на рівні сокета, проте конфігурація апаратного фільтра `SIOCSHWTSTAMP` повинна виконуватися безпосередньо над фізичними підпорядкованими інтерфейсами (`eth0`, `eth1`).

---

### 7. Практичні приклади реалізації

Нижче наведено повні промислові реалізації конфігурації апаратних міток сокета, надсилання UDP-пакета, вичитування мітки передавача з черги `MSG_ERRQUEUE`, а також виконання перехресного зчитування часу PHC.

#### Приклад 1: Налаштування сокета та вичитування Tx-мітки часу

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <linux/errqueue.h>
#include <poll.h>

static int enable_hwtstamp(int sock, const char *ifname) {
    struct ifreq ifr;
    struct hwtstamp_config config;

    memset(&ifr, 0, sizeof(ifr));
    strncpy(ifr.ifr_name, ifname, sizeof(ifr.ifr_name) - 1);

    memset(&config, 0, sizeof(config));
    config.tx_type = HWTSTAMP_TX_ON;
    config.rx_filter = HWTSTAMP_FILTER_ALL;
    ifr.ifr_data = (char *)&config;

    if (ioctl(sock, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("ioctl(SIOCSHWTSTAMP)");
        return -1;
    }
    return 0;
}

static int configure_socket_ts(int sock) {
    int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                SOF_TIMESTAMPING_TX_SOFTWARE |
                SOF_TIMESTAMPING_RX_HARDWARE |
                SOF_TIMESTAMPING_RX_SOFTWARE |
                SOF_TIMESTAMPING_RAW_HARDWARE |
                SOF_TIMESTAMPING_SOFTWARE |
                SOF_TIMESTAMPING_OPT_ID |
                SOF_TIMESTAMPING_OPT_TSONLY;

    if (setsockopt(sock, SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
        perror("setsockopt(SO_TIMESTAMPING)");
        return -1;
    }
    return 0;
}

static void read_tx_timestamp(int sock) {
    struct pollfd pfd = { .fd = sock, .events = POLLERR, .revents = 0 };
    int poll_res = poll(&pfd, 1, 500); // Очікування події в черзі помилок до 500 мс

    if (poll_res <= 0) {
        fprintf(stderr, "Таймаут або помилка очікування мітки в MSG_ERRQUEUE\n");
        return;
    }

    char ctrl_buf[512];
    struct msghdr msg;
    memset(&msg, 0, sizeof(msg));
    msg.msg_control = ctrl_buf;
    msg.msg_controllen = sizeof(ctrl_buf);

    int res = recvmsg(sock, &msg, MSG_ERRQUEUE | MSG_DONTWAIT);
    if (res < 0) {
        perror("recvmsg(MSG_ERRQUEUE)");
        return;
    }

    struct cmsghdr *cmsg;
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
            struct scm_timestamping *ts = (struct scm_timestamping *)CMSG_DATA(cmsg);
            printf("Отримано мітку Tx:\n");
            printf("  Програмна (SW):  %ld.%09ld с\n", (long)ts->ts[0].tv_sec, (long)ts->ts[0].tv_nsec);
            printf("  Апаратна (HW raw): %ld.%09ld с\n", (long)ts->ts[2].tv_sec, (long)ts->ts[2].tv_nsec);
        }
    }
}

int main(int argc, char *argv[]) {
    const char *ifname = (argc > 1) ? argv[1] : "eth0";
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    if (enable_hwtstamp(sock, ifname) < 0) {
        fprintf(stderr, "Попередження: Не вдалося активувати апаратне фіксування на %s\n", ifname);
    }

    if (configure_socket_ts(sock) < 0) {
        close(sock);
        return 1;
    }

    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(12345);
    inet_pton(AF_INET, "127.0.0.1", &dest_addr.sin_addr);

    const char payload[] = "Синхронізаційний тестовий пакет";
    ssize_t sent = sendto(sock, payload, sizeof(payload), 0,
                          (struct sockaddr *)&dest_addr, sizeof(dest_addr));
    if (sent < 0) {
        perror("sendto");
    } else {
        printf("Пакет надіслано (%zd байтів). Очікування Tx-мітки...\n", sent);
        read_tx_timestamp(sock);
    }

    close(sock);
    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <linux/errqueue.h>
#include <poll.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() {
        if (fd_ >= 0) {
            ::close(fd_);
        }
    }
    SocketHandle(const SocketHandle&) = delete;
    SocketHandle& operator=(const SocketHandle&) = delete;
    SocketHandle(SocketHandle&& other) noexcept : fd_(other.fd_) { other.fd_ = -1; }
    SocketHandle& operator=(SocketHandle&& other) noexcept {
        if (this != &other) {
            if (fd_ >= 0) ::close(fd_);
            fd_ = other.fd_;
            other.fd_ = -1;
        }
        return *this;
    }
    [[nodiscard]] int get() const noexcept { return fd_; }
    [[nodiscard]] bool is_valid() const noexcept { return fd_ >= 0; }
};

struct TimestampReport {
    timespec software_ts{};
    timespec raw_hardware_ts{};
    uint32_t packet_seq_id{0};
};

class TimestampedSocket {
    SocketHandle sock_;

public:
    static std::expected<TimestampedSocket, std::error_code> create(std::string_view ifname) {
        int fd = ::socket(AF_INET, SOCK_DGRAM, 0);
        if (fd < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        SocketHandle handle(fd);

        // Налаштування апаратного фільтра мережевої карти
        struct ifreq ifr{};
        std::strncpy(ifr.ifr_name, ifname.data(), sizeof(ifr.ifr_name) - 1);
        struct hwtstamp_config config{};
        config.tx_type = HWTSTAMP_TX_ON;
        config.rx_filter = HWTSTAMP_FILTER_ALL;
        ifr.ifr_data = reinterpret_cast<char*>(&config);

        if (::ioctl(handle.get(), SIOCSHWTSTAMP, &ifr) < 0) {
            std::cerr << "Попередження: SIOCSHWTSTAMP не підтримується для " << ifname << "\n";
        }

        // Конфігурація сокетних прапорців SO_TIMESTAMPING
        int flags = SOF_TIMESTAMPING_TX_HARDWARE |
                    SOF_TIMESTAMPING_TX_SOFTWARE |
                    SOF_TIMESTAMPING_RX_HARDWARE |
                    SOF_TIMESTAMPING_RX_SOFTWARE |
                    SOF_TIMESTAMPING_RAW_HARDWARE |
                    SOF_TIMESTAMPING_SOFTWARE |
                    SOF_TIMESTAMPING_OPT_ID |
                    SOF_TIMESTAMPING_OPT_TSONLY;

        if (::setsockopt(handle.get(), SOL_SOCKET, SO_TIMESTAMPING, &flags, sizeof(flags)) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        return TimestampedSocket(std::move(handle));
    }

    explicit TimestampedSocket(SocketHandle sock) : sock_(std::move(sock)) {}

    std::expected<void, std::error_code> send(std::span<const std::byte> data, const sockaddr_in& dest) {
        ssize_t res = ::sendto(sock_.get(), data.data(), data.size(), 0,
                               reinterpret_cast<const sockaddr*>(&dest), sizeof(dest));
        if (res < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        return {};
    }

    std::expected<TimestampReport, std::error_code> receive_tx_timestamp(int timeout_ms = 500) {
        pollfd pfd{.fd = sock_.get(), .events = POLLERR, .revents = 0};
        int poll_res = ::poll(&pfd, 1, timeout_ms);
        if (poll_res <= 0) {
            return std::unexpected(std::make_error_code(std::errc::timed_out));
        }

        std::array<char, 512> ctrl_buf{};
        msghdr msg{};
        msg.msg_control = ctrl_buf.data();
        msg.msg_controllen = ctrl_buf.size();

        if (::recvmsg(sock_.get(), &msg, MSG_ERRQUEUE | MSG_DONTWAIT) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        TimestampReport report{};
        for (auto* cmsg = CMSG_FIRSTHDR(&msg); cmsg != nullptr; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
            if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SCM_TIMESTAMPING) {
                auto* ts = reinterpret_cast<struct scm_timestamping*>(CMSG_DATA(cmsg));
                report.software_ts = ts->ts[0];
                report.raw_hardware_ts = ts->ts[2];
            } else if (cmsg->cmsg_level == SOL_IP && cmsg->cmsg_type == IP_RECVERR) {
                auto* err = reinterpret_cast<struct sock_extended_err*>(CMSG_DATA(cmsg));
                report.packet_seq_id = err->ee_data;
            }
        }
        return report;
    }
};

int main(int argc, char* argv[]) {
    std::string_view ifname = (argc > 1) ? argv[1] : "eth0";

    auto sock_res = TimestampedSocket::create(ifname);
    if (!sock_res) {
        std::cerr << "Помилка ініціалізації сокета: " << sock_res.error().message() << "\n";
        return 1;
    }
    auto& ts_sock = *sock_res;

    sockaddr_in dest{};
    dest.sin_family = AF_INET;
    dest.sin_port = htons(12345);
    ::inet_pton(AF_INET, "127.0.0.1", &dest.sin_addr);

    std::string_view msg = "Тестове повідомлення C++";
    auto data_span = std::as_bytes(std::span(msg.data(), msg.size()));

    if (auto res = ts_sock.send(data_span, dest); !res) {
        std::cerr << "Помилка надсилання: " << res.error().message() << "\n";
        return 1;
    }
    std::cout << "Пакет надіслано. Очікування мітки часу...\n";

    auto ts_res = ts_sock.receive_tx_timestamp();
    if (!ts_res) {
        std::cerr << "Помилка отримання мітки: " << ts_res.error().message() << "\n";
        return 1;
    }

    const auto& rep = *ts_res;
    std::cout << "Успішно отримано мітку часу для пакета ID " << rep.packet_seq_id << ":\n"
              << "  Програмний час (SW): " << rep.software_ts.tv_sec << "." << rep.software_ts.tv_nsec << " с\n"
              << "  Апаратний час (HW):  " << rep.raw_hardware_ts.tv_sec << "." << rep.raw_hardware_ts.tv_nsec << " с\n";
    return 0;
}
```
:::

#### Приклад 2: Зчитування апаратного Cross-timestamping через `/dev/ptpX`

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/ioctl.h>
#include <linux/ptp_clock.h>

int read_precise_cross_timestamp(const char *ptp_device) {
    int fd = open(ptp_device, O_RDONLY);
    if (fd < 0) {
        perror("open(ptp_device)");
        return -1;
    }

    struct ptp_sys_offset_precise offset;
    memset(&offset, 0, sizeof(offset));

    if (ioctl(fd, PTP_SYS_OFFSET_PRECISE, &offset) == 0) {
        printf("Апаратний Cross-Timestamping (PTP_SYS_OFFSET_PRECISE):\n");
        printf("  Апаратний годинник PHC:  %lld.%09u с\n",
               (long long)offset.device.sec, offset.device.nsec);
        printf("  Системний час (Realtime): %lld.%09u с\n",
               (long long)offset.sys_realtime.sec, offset.sys_realtime.nsec);
        printf("  Монотонний сирий (MonoRaw): %lld.%09u с\n",
               (long long)offset.sys_monoraw.sec, offset.sys_monoraw.nsec);

        long long diff_ns = ((long long)offset.sys_realtime.sec - offset.device.sec) * 1000000000LL +
                            ((long long)offset.sys_realtime.nsec - offset.device.nsec);
        printf("  Миттєвий розсинхрон (Offset): %lld нс\n", diff_ns);
    } else {
        printf("PTP_SYS_OFFSET_PRECISE не підтримується обладнанням. Використання PTP_SYS_OFFSET...\n");
        
        struct ptp_sys_offset sysoff;
        memset(&sysoff, 0, sizeof(sysoff));
        sysoff.n_samples = 5;

        if (ioctl(fd, PTP_SYS_OFFSET, &sysoff) < 0) {
            perror("ioctl(PTP_SYS_OFFSET)");
            close(fd);
            return -1;
        }

        printf("Результати програмного сендвіча PTP_SYS_OFFSET (%u вибірок):\n", sysoff.n_samples);
        for (unsigned int i = 0; i < sysoff.n_samples; i++) {
            long long t_cpu1 = (long long)sysoff.ts[2 * i].sec * 1000000000LL + sysoff.ts[2 * i].nsec;
            long long t_phc  = (long long)sysoff.ts[2 * i + 1].sec * 1000000000LL + sysoff.ts[2 * i + 1].nsec;
            long long t_cpu2 = (long long)sysoff.ts[2 * i + 2].sec * 1000000000LL + sysoff.ts[2 * i + 2].nsec;

            long long cpu_mid = (t_cpu1 + t_cpu2) / 2;
            long long delay = t_cpu2 - t_cpu1;
            long long offset_ns = cpu_mid - t_phc;

            printf("  Зріз %u: PHC=%lld нс, CPU_mid=%lld нс, Затримка PCIe=%lld нс, Зсув=%lld нс\n",
                   i, t_phc, cpu_mid, delay, offset_ns);
        }
    }

    close(fd);
    return 0;
}

int main(int argc, char *argv[]) {
    const char *dev = (argc > 1) ? argv[1] : "/dev/ptp0";
    return read_precise_cross_timestamp(dev);
}
```
```cpp
#include <iostream>
#include <string_view>
#include <expected>
#include <system_error>
#include <vector>
#include <cstring>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>
#include <linux/ptp_clock.h>

class PtpDevice {
    int fd_{-1};
public:
    explicit PtpDevice(std::string_view path) {
        fd_ = ::open(path.data(), O_RDONLY);
    }
    ~PtpDevice() {
        if (fd_ >= 0) ::close(fd_);
    }
    [[nodiscard]] bool is_open() const noexcept { return fd_ >= 0; }
    [[nodiscard]] int get() const noexcept { return fd_; }
};

struct PreciseTimestampPair {
    int64_t phc_time_ns{0};
    int64_t sys_realtime_ns{0};
    int64_t sys_monoraw_ns{0};
    int64_t offset_ns{0};
};

struct SampledOffset {
    int64_t phc_time_ns{0};
    int64_t sys_midpoint_ns{0};
    int64_t bus_delay_ns{0};
    int64_t offset_ns{0};
};

class CrossTimestampReader {
    PtpDevice dev_;

public:
    explicit CrossTimestampReader(std::string_view path) : dev_(path) {}

    [[nodiscard]] bool is_valid() const noexcept { return dev_.is_open(); }

    std::expected<PreciseTimestampPair, std::error_code> read_precise() {
        if (!dev_.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        struct ptp_sys_offset_precise offset{};
        if (::ioctl(dev_.get(), PTP_SYS_OFFSET_PRECISE, &offset) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        PreciseTimestampPair pair{};
        pair.phc_time_ns = static_cast<int64_t>(offset.device.sec) * 1'000'000'000LL + offset.device.nsec;
        pair.sys_realtime_ns = static_cast<int64_t>(offset.sys_realtime.sec) * 1'000'000'000LL + offset.sys_realtime.nsec;
        pair.sys_monoraw_ns = static_cast<int64_t>(offset.sys_monoraw.sec) * 1'000'000'000LL + offset.sys_monoraw.nsec;
        pair.offset_ns = pair.sys_realtime_ns - pair.phc_time_ns;

        return pair;
    }

    std::expected<std::vector<SampledOffset>, std::error_code> read_software_sandwich(unsigned int samples = 5) {
        if (!dev_.is_open()) {
            return std::unexpected(std::make_error_code(std::errc::bad_file_descriptor));
        }

        struct ptp_sys_offset sysoff{};
        sysoff.n_samples = samples;

        if (::ioctl(dev_.get(), PTP_SYS_OFFSET, &sysoff) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }

        std::vector<SampledOffset> results;
        results.reserve(samples);

        for (unsigned int i = 0; i < sysoff.n_samples; ++i) {
            int64_t t_cpu1 = static_cast<int64_t>(sysoff.ts[2 * i].sec) * 1'000'000'000LL + sysoff.ts[2 * i].nsec;
            int64_t t_phc  = static_cast<int64_t>(sysoff.ts[2 * i + 1].sec) * 1'000'000'000LL + sysoff.ts[2 * i + 1].nsec;
            int64_t t_cpu2 = static_cast<int64_t>(sysoff.ts[2 * i + 2].sec) * 1'000'000'000LL + sysoff.ts[2 * i + 2].nsec;

            int64_t cpu_mid = (t_cpu1 + t_cpu2) / 2;
            int64_t delay = t_cpu2 - t_cpu1;
            int64_t offset = cpu_mid - t_phc;

            results.push_back(SampledOffset{
                .phc_time_ns = t_phc,
                .sys_midpoint_ns = cpu_mid,
                .bus_delay_ns = delay,
                .offset_ns = offset
            });
        }
        return results;
    }
};

int main(int argc, char* argv[]) {
    std::string_view ptp_path = (argc > 1) ? argv[1] : "/dev/ptp0";
    CrossTimestampReader reader(ptp_path);

    if (!reader.is_valid()) {
        std::cerr << "Не вдалося відкрити пристрій " << ptp_path << "\n";
        return 1;
    }

    if (auto precise_res = reader.read_precise(); precise_res) {
        const auto& p = *precise_res;
        std::cout << "Апаратний Cross-Timestamping (PTP_SYS_OFFSET_PRECISE):\n"
                  << "  Час PHC:      " << p.phc_time_ns << " нс\n"
                  << "  Час Realtime: " << p.sys_realtime_ns << " нс\n"
                  << "  Зсув (Offset):" << p.offset_ns << " нс\n";
    } else {
        std::cout << "PTP_SYS_OFFSET_PRECISE недоступний (" << precise_res.error().message()
                  << "). Спроба програмного вимірювання PTP_SYS_OFFSET...\n";

        auto sw_res = reader.read_software_sandwich(5);
        if (!sw_res) {
            std::cerr << "Помилка PTP_SYS_OFFSET: " << sw_res.error().message() << "\n";
            return 1;
        }

        std::cout << "Результати програмного опитування:\n";
        for (size_t i = 0; i < sw_res->size(); ++i) {
            const auto& s = (*sw_res)[i];
            std::cout << "  Вибірка " << i << ": PHC=" << s.phc_time_ns
                      << " нс, CPU_mid=" << s.sys_midpoint_ns
                      << " нс, Затримка шини=" << s.bus_delay_ns
                      << " нс, Зсув=" << s.offset_ns << " нс\n";
        }
    }
    return 0;
}
```
:::

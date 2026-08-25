# ⚙️ Реалізація клієнта SNTP з корекцією зміщення та плавною дисципліною часу

Протокол SNTP (англ. *Simple Network Time Protocol*, RFC 4330) є спрощеним профілем повнофункціонального стека NTPv4. Він використовує ідентичний 48-байтний двійковий формат датаграм UDP на порті 123 та однаковий чотириточковий алгоритм фіксації міток часу `T1..T4`, але навмисно виключає складні механізми перехресного пірингу, матричну фільтрацію Марзулло та безперервне калібрування дрейфу кварцового резонатора.

Це робить SNTP основним вибором для мікроконтролерів (ESP32, STM32), системних утиліт одноразової синхронізації (наприклад, `sntp`, `rdate`), контейнерів і системних служб ініціалізації (`systemd-timesyncd`).

Нижче наведено повну архітектуру та реалізацію промислового клієнта SNTP мовами C та C++, здатного надійно працювати в ненадійних мережах, виявляти спроби підміни пакетів, обробляти коди відмови Kiss-o'-Death та безпечно керувати системним годинником ядра через плавне підведення ходу (`slew`) або разовий стрибок (`step`).

### Повна архітектура клієнтського процесу

Процес синхронізації клієнта розбивається на п'ять строго послідовних етапів:

```
[1. Підготовка сокета] → [2. Запит T1] → [3. Мережевий обмін UDP] → [4. Прийом T4 та валідація] → [5. Дисципліна ядра]
```

#### Етап 1: Конфігурація мережевого сокета
Клієнт створює датаграмний сокет UDP (`AF_INET`, `SOCK_DGRAM`). Оскільки протокол UDP не гарантує доставки пакетів, мережевий збій або перезавантаження сервера призведуть до вічного блокування виклику `recvfrom()`.
Щоб запобігти цьому, на сокеті налаштовується тайм-аут прийому через опцію сокета `SO_RCVTIMEO` (зазвичай від 2 до 5 секунд). У багатопотокових або подійно-орієнтованих архітектурах застосовується неблокуючий режим із моніторингом дескриптора через `poll()` або `epoll()`.

Для прецизійних задач промислової автоматизації та фінансового трейдингу операційна система Linux дозволяє вмикати апаратне маркування пакетів через прапорець `SO_TIMESTAMPING`. При цьому мережева карта фіксує моменти прийому та передачі на фізичному рівні PHY або MAC, виключаючи затримки обробки переривань процесором та планувальника задач ядра.

#### Етап 2: Генерація запиту та фіксація мітки T1
Клієнт ініціалізує 48-байтний буфер пакета:
* Перший байт `li_vn_mode` встановлюється у значення `0x23` (двійкове `00 100 011`₂: `LI = 0` — без попередження, `VN = 4` — версія NTPv4, `Mode = 3` — клієнт).
* Усі інші поля (Stratum, Poll, Precision, Root Delay, Root Dispersion) заповнюються нулями.
* Безпосередньо перед системним викликом `sendto()` зчитується системний час хоста `T1` через `clock_gettime(CLOCK_REALTIME)`. Мітка конвертується у 64-бітний формат NTP і записується в поле `Transmit Timestamp` запиту.

> 🔧 **Навіщо це.** Запис унікального поточного часу `T1` у поле відправки виконує роль криптографічного одноразового числа (англ. *nonce*). Сервер за стандартом зобов'язаний скопіювати це число у поле `Origin Timestamp` своєї відповіді. Перевірка збігу `Origin Timestamp == T1` на клієнті надійно захищає від атак повторення (англ. *replay attack*) та від прийому запізнілих відповідей від попередніх сесій.

#### Етап 3: Мережевий транспорт та фіксація міток на сервері
Пакет рухається мережею крізь комутатори та маршрутизатори протягом часу `d_req`. Сервер фіксує момент отримання `T2` (Receive Timestamp) за власним годинником, формує відповідь, встановлює час відправки `T3` (Transmit Timestamp), копіює `T1` в `Origin Timestamp` і надсилає UDP-датаграму назад клієнту.

#### Етап 4: Прийом відповіді, фіксація мітки T4 та фільтрація
Одразу після повернення виклику `recvfrom()` клієнт миттєво фіксує локальний час прибуття `T4`.
Перш ніж виконувати математичні розрахунки, клієнт проводить комплекс перевірок коректності (англ. *sanity checks*):
1. **Перевірка довжини:** отриманий буфер мусить містити щонайменше 48 байтів.
2. **Перевірка режиму:** поле `Mode` відповіді сервера мусить дорівнювати `4` (Server) або `5` (Broadcast).
3. **Перевірка цілісності сесії:** значення `Origin Timestamp` у відповіді мусить точно збігатися з відправленим `T1`.
4. **Обробка коду Kiss-o'-Death:** якщо `Stratum == 0`, клієнт перевіряє 4 байти поля `Reference ID`. При отриманні коду `RATE` клієнт експоненційно збільшує паузу між опитуваннями, а при `DENY`/`RSTR` припиняє роботу із сервером.
5. **Перевірка валідності джерела:** якщо `LI == 3` (Alarm / Clock Unsynchronized) або `Stratum >= 16`, сервер вважається розсинхронізованим, і його дані відкидаються.
6. **Перевірка фізичної причинності:** кругова затримка `δ = (T4 − T1) − (T3 − T2)` не може бути від'ємною. Від'ємна затримка свідчить про стрибок системного годинника під час вимірювання; такий відлік анулюється.

#### Етап 5: Розрахунок метрик та дисципліна системного годинника ядра
Клієнт обчислює зміщення `θ = ((T2 − T1) + (T3 − T4)) / 2`.
Для внесення поправки у системний годинник застосовується дворівнева логіка:
* **Плавне регулювання ходу (Clock Slew):** якщо `|θ| < 128 мс`, викликається функція `adjtime()` (або низькорівневий системний виклик `adjtimex()` / `clock_adjtime()` у Linux). Ядро операційної системи тимчасово сповільнює або прискорює системний таймер на фіксовану величину (до ±500 ppm, тобто ±0.5 мс за секунду), плавно зводячи похибку до нуля. При цьому системний час залишається строго монотонним, що критично для баз даних та таймерів.
* **Разовий стрибок часу (Clock Step):** якщо `128 мс ≤ |θ| < 1000 с`, накопичена похибка надто велика, щоб усувати її плавним підведенням (підведення 10 секунд зі швидкістю 500 ppm зайняло б понад 5.5 годин). У цьому разі виконується разовий виклик `clock_settime(CLOCK_REALTIME)`, який миттєво виставляє точний час.
* **Аварійна зупинка (Panic Threshold):** якщо `|θ| ≥ 1000 с` (~16.6 хвилин), клієнт відмовляється автоматично змінювати час, фіксує аварійний стан у системному журналі та завершує роботу для запобігання пошкодженню даних у разі атаки чи масштабної системної аварії.

### Багатосерверна стратегія та відмовостійкість пулу

У реальних виробничих середовищах клієнт ніколи не прив'язується до єдиної статичної IP-адреси. Якщо сервер виходить з ладу або зазнає перевантаження, клієнт застосовує алгоритм ротації пулу (англ. *Server Pool Failover*):

1. **Резолвінг доменного імені пулу:** клієнт звертається до DNS за адресою пулу (наприклад, `pool.ntp.org`). DNS-сервер повертає масив із кількох випадкових IPv4 та IPv6 адрес (Round-Robin DNS).
2. **Послідовне опитування зі зміщенням:** клієнт опитує першу отриману адресу. Якщо протягом встановленого тайм-ауту (наприклад, 3 секунди) відповідь не надходить, клієнт негайно надсилає новий запит до наступної адреси зі списку.
3. **Експоненційне сповільнення (Exponential Backoff):** якщо всі сервери пулу тимчасово недоступні або повертають код відмови `RATE`, клієнт подвоює інтервал між спробами опитування (`64 с → 128 с → 256 с`), запобігаючи перевантаженню мережі під час системних збоїв.

### Внутрішній устрій коригування часу в ядрі Linux

Коли застосунок викликає функцію `adjtime(&adj, NULL)`, операційна система Linux не змінює покази лічильника часу миттєво. Усередині структури керування часом ядра (`struct timekeeper`) зберігається накопичена похибка `time_offset`.

Під час кожного спрацьовування апаратного таймера (переривання `tick`, що генерується кожні 1–4 мілісекунди залежно від параметра конфігурації ядра `CONFIG_HZ`), функція `update_wall_time()` додає до системного часу значення:

```
delta_tick = nominal_tick_ns + slew_correction_ns
```

Величина `slew_correction_ns` суворо обмежена значенням 500 ppm (тобто не більше 0.5 наносекунди на кожну мікросекунду ходу часу). Завдяки цьому жоден системний виклик `clock_gettime(CLOCK_REALTIME)` або `gettimeofday()` ніколи не поверне однакове або менше значення порівняно з попереднім викликом.

#### Низькорівневий інтерфейс ядра `adjtimex` та структура `struct timex`
Для прецизійного керування ядро Linux надає системний виклик `adjtimex(struct timex *tx)` (або `clock_adjtime` у POSIX):

| Поле структури `timex` | Призначення та одиниці виміру |
| :--- | :--- |
| `modes` | Бітова маска параметрів, що змінюються (`ADJ_OFFSET`, `ADJ_FREQUENCY`, `ADJ_STATUS`, `ADJ_TICK`) |
| `offset` | Фазове зміщення часу (мікросекунди або наносекунди при прапорці `STA_NANO`) |
| `freq` | Поправка частоти апаратного генератора у форматі з фіксованою комою `s16.16` ppm (масштаб `2⁻¹⁶` ppm) |
| `maxerror` / `esterror` | Максимальна та оцінена дисперсія похибки синхронізації |
| `status` | Прапорці контуру керування (`STA_PLL` — фазовий контур, `STA_FLL` — частотний контур, `STA_UNSYNC` — стан розсинхронізації) |
| `constant` | Постійна часу фільтра другого порядку (відповідає поточному інтервалу опитування `Poll`) |
| `tick` | Базова тривалість системного тику (номінал 10000 мкс для `HZ=100` або 1000 мкс для `HZ=1000`) |

### Апаратна дисципліна 1 PPS (Pulse Per Second)

Для досягнення субмікросекундної точності серверні вузли поєднують клієнт SNTP з апаратним приймачем GPS/GNSS, що генерує фізичний імпульс **1 PPS** (один імпульс на секунду).
* Імпульс 1 PPS має надзвичайно крутий фронт нарастання (тривалість переходу менше 20 наносекунд) і прив'язаний до початку кожної секунди шкали UTC з похибкою менше 50 наносекунд.
* Сигнал заводиться на контакт переривання процесора (DCD послідовного порту UART або вивід GPIO на одноплатних комп'ютерах).
* Підсистема ядра Linux `pps-gpio` та модуль `pps_core` реєструють символьний пристрій `/dev/pps0`.
* Клієнт SNTP/NTP виконує грубу прив'язку до абсолютної секунди епохи Unix (визначає, яка саме це секунда: наприклад, `1718020800`), а підсистема PPS фіксує точний нульовий момент настання цієї секунди на апаратному лічильнику процесора.

### Температурна компенсація та збереження дрейфу генератора

Кварцові генератори материнських плат зазнають значного дрейфу частоти під впливом зміни температури корпусу процесора. Для стандартного нетермокомпенсованого кристала (XO) температурна характеристика описується параболою з коефіцієнтом приблизно `-0.035 ppm/°C²`. Зміна температури всередині сервера на 15°C викликає дрейф частоти до 8–10 ppm (що дає похибку понад 800 мілісекунд на добу без мережевої синхронізації).

Промисловий клієнт SNTP між послідовними циклами синхронізації обчислює накопичений коефіцієнт дрейфу:

```
drift_ppm = ((offset_k - offset_0) / delta_t_seconds) · 10^6
```

Обчислене значення зберігається у системному файлі (наприклад, `/var/lib/sntp/sntp.drift`). Під час перезавантаження операційної системи клієнт одразу передає це значення в ядро через параметр `tx.modes = ADJ_FREQUENCY`, завдяки чому годинник іде з правильною швидкістю ще до отримання першого мережевого пакета.

### Захист журналювання та безпека від часових атак

Маніпуляція системним годинником є поширеним вектором атак у розподілених інфраструктурах:
* **Анулювання криптографічних сертифікатів:** штучне переведення годинника вперед або назад дозволяє зловмисникам обходити перевірку дійсності TLS-сертифікатів чи продовжувати життя прострочених токенів автентифікації (JWT, Kerberos tickets).
* **Порушення монотонності аудиту:** відкат системного часу назад створює часові колізії в системних журналах `auditd` та `journald`, що ускладнює розслідування інцидентів інформаційної безпеки.
* **Захист через плавне підведення (Slew-Only Policy):** у критичних виробничих контурах параметри клієнта налаштовують на повну заборону операцій `step` після завершення початкового завантаження, гарантуючи виключно плавний хід часу.

### Покроковий архітектурний розбір коду C та C++

У наведених нижче реалізаціях мовами C та C++ реалізовано повний життєвий цикл клієнта:
1. **Ініціалізація та керування сокетом (RAII):** у коді на C++ використовується клас `SocketHandle`, що гарантує закриття дескриптора файлу при будь-якому виході з функції або поверненні помилки. У C застосовано виклик `close(fd)` у всіх гілках повернення статусів.
2. **Типобезпечна обробка результатів:** у C++23 функція `query()` повертає `std::expected<NtpMeasurement, std::string>`, що усуває потребу у глобальній змінній `errno` та надає читабельний опис причини відмови.
3. **Обробка порядку байтів:** для всіх 32-бітних полів виконується перетворення `ntohl()` та `htonl()` (або `std::byteswap()` у C++), що гарантує кросплатформну сумісність на архітектурах Little-Endian (x86_64, ARM64) та Big-Endian.

### Програмна реалізація клієнта SNTP

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <errno.h>
#include <math.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>

#define NTP_PORT 123
#define NTP_UNIX_OFFSET 2208988800ULL
#define NTP_FRAC_SCALE 4294967296.0

#define NTP_STEP_THRESHOLD 0.128   /* 128 мс: поріг перемикання між slew та step */
#define NTP_PANIC_THRESHOLD 1000.0 /* 1000 с: поріг аварійної панічної зупинки */

#pragma pack(push, 1)

/* 48-байтний заголовок пакета SNTPv4 (RFC 4330) */
typedef struct {
    uint8_t  li_vn_mode;       /* LI (2 біти), VN (3 біти), Mode (3 біти) */
    uint8_t  stratum;          /* Шар еталона (0..16) */
    int8_t   poll;             /* log2 інтервалу опитування */
    int8_t   precision;        /* log2 точності генератора */
    uint32_t root_delay;       /* s16.16 затримка до первинного еталона */
    uint32_t root_dispersion;  /* u16.16 сумарна дисперсія еталона */
    uint32_t ref_id;           /* 4 ASCII або IPv4 адреса джерела */
    uint32_t ref_ts_sec;       /* Час останнього оновлення (секунди) */
    uint32_t ref_ts_frac;      /* Час останнього оновлення (дріб) */
    uint32_t orig_ts_sec;      /* T1: час відправки клієнтом (секунди) */
    uint32_t orig_ts_frac;     /* T1: час відправки клієнтом (дріб) */
    uint32_t rx_ts_sec;        /* T2: час прийому сервером (секунди) */
    uint32_t rx_ts_frac;       /* T2: час прийому сервером (дріб) */
    uint32_t tx_ts_sec;        /* T3: час відправки сервером (секунди) */
    uint32_t tx_ts_frac;       /* T3: час відправки сервером (дріб) */
} sntp_packet_t;

#pragma pack(pop)

/* Конвертація struct timespec у секунди формату double */
static inline double timespec_to_seconds(const struct timespec *ts) {
    return (double)ts->tv_sec + ((double)ts->tv_nsec / 1e9);
}

/* Конвертація 64-бітного NTP Timestamp у секунди епохи Unix */
static inline double ntp_to_unix_seconds(uint32_t sec_be, uint32_t frac_be) {
    uint32_t s = ntohl(sec_be);
    uint32_t f = ntohl(frac_be);
    if (s == 0 && f == 0) return 0.0;
    return ((double)(s - NTP_UNIX_OFFSET)) + ((double)f / NTP_FRAC_SCALE);
}

/* Конвертація секунд епохи Unix у 64-бітний NTP Timestamp */
static inline void unix_seconds_to_ntp(double unix_sec, uint32_t *out_sec_be, uint32_t *out_frac_be) {
    double int_part;
    double frac_part = modf(unix_sec, &int_part);
    *out_sec_be = htonl((uint32_t)(int_part + NTP_UNIX_OFFSET));
    *out_frac_be = htonl((uint32_t)(frac_part * NTP_FRAC_SCALE));
}

/* Дисципліна системного годинника ядра: Slew проти Step */
static int apply_clock_discipline(double offset) {
    double abs_offset = fabs(offset);

    if (abs_offset >= NTP_PANIC_THRESHOLD) {
        fprintf(stderr, "Критична помилка: зміщення %.3f с перевищує ліміт паніки (1000 с)!\n", offset);
        return -1;
    }

    if (abs_offset < NTP_STEP_THRESHOLD) {
        /* Плавне регулювання частоти кварцового генератора (Clock Slew) */
        struct timeval adj;
        adj.tv_sec = (time_t)offset;
        adj.tv_usec = (suseconds_t)((offset - (double)adj.tv_sec) * 1e6);
        
        if (adjtime(&adj, NULL) != 0) {
            perror("Помилка системного виклику adjtime");
            return -1;
        }
        printf("Дисципліна: виконано плавне коригування (slew) на %.6f с (монотонно)\n", offset);
    } else {
        /* Разовий стрибок системного часу (Clock Step) */
        struct timespec now;
        if (clock_gettime(CLOCK_REALTIME, &now) != 0) {
            perror("Помилка clock_gettime");
            return -1;
        }
        double target_sec = timespec_to_seconds(&now) + offset;
        struct timespec target;
        target.tv_sec = (time_t)target_sec;
        target.tv_nsec = (long)((target_sec - (double)target.tv_sec) * 1e9);

        if (clock_settime(CLOCK_REALTIME, &target) != 0) {
            perror("Помилка clock_settime (потрібні привілеї суперкористувача root)");
            return -1;
        }
        printf("Дисципліна: виконано разовий стрибок часу (step) на %.6f с\n", offset);
    }
    return 0;
}

/* Виконання мережевого запиту до сервера SNTP */
int query_sntp_server(const char *hostname, double *out_offset, double *out_delay) {
    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_DGRAM;

    char port_str[6];
    snprintf(port_str, sizeof(port_str), "%d", NTP_PORT);

    int rc = getaddrinfo(hostname, port_str, &hints, &res);
    if (rc != 0) {
        fprintf(stderr, "Помилка резолвінгу хоста %s: %s\n", hostname, gai_strerror(rc));
        return -1;
    }

    int fd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    if (fd < 0) {
        perror("Помилка створення сокета UDP");
        freeaddrinfo(res);
        return -1;
    }

    /* Налаштування тайм-ауту 3 секунди на очікування відповіді */
    struct timeval tv = {.tv_sec = 3, .tv_usec = 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

    sntp_packet_t req;
    memset(&req, 0, sizeof(req));
    /* Формування першого байта: LI=0 (no warning), VN=4 (NTPv4), Mode=3 (Client) */
    req.li_vn_mode = (0 << 6) | (4 << 3) | 3;

    /* Фіксація локального часу відправки клієнта T1 */
    struct timespec ts_t1;
    clock_gettime(CLOCK_REALTIME, &ts_t1);
    double t1 = timespec_to_seconds(&ts_t1);
    unix_seconds_to_ntp(t1, &req.tx_ts_sec, &req.tx_ts_frac);

    if (sendto(fd, &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
        perror("Помилка відправки запиту sendto");
        close(fd);
        freeaddrinfo(res);
        return -1;
    }

    sntp_packet_t resp;
    struct sockaddr_storage from_addr;
    socklen_t from_len = sizeof(from_addr);

    ssize_t n = recvfrom(fd, &resp, sizeof(resp), 0, (struct sockaddr *)&from_addr, &from_len);
    
    /* Фіксація локального часу прийому клієнта T4 */
    struct timespec ts_t4;
    clock_gettime(CLOCK_REALTIME, &ts_t4);
    double t4 = timespec_to_seconds(&ts_t4);

    close(fd);
    freeaddrinfo(res);

    if (n < (ssize_t)sizeof(sntp_packet_t)) {
        fprintf(stderr, "Помилка прийому: отримано %zd байтів замість очікуваних 48\n", n);
        return -1;
    }

    /* Валідація полів заголовка */
    uint8_t li = (resp.li_vn_mode >> 6) & 0x03;
    uint8_t mode = resp.li_vn_mode & 0x07;
    uint8_t stratum = resp.stratum;

    if (mode != 4 && mode != 5) {
        fprintf(stderr, "Помилка: некоректний режим відповіді Mode=%d (очікувався Server=4)\n", mode);
        return -1;
    }

    /* Перевірка коду відмови Kiss-o'-Death */
    if (stratum == 0) {
        char kod[5] = {0};
        memcpy(kod, &resp.ref_id, 4);
        fprintf(stderr, "Сервер надіслав код відмови Kiss-o'-Death (Stratum 0): [%s]\n", kod);
        return -2;
    }

    /* Перевірка на розсинхронізований стан сервера */
    if (li == 3 || stratum >= 16) {
        fprintf(stderr, "Помилка: сервер розсинхронізований (LI=%d, Stratum=%d)\n", li, stratum);
        return -1;
    }

    /* Перевірка захисту від атак повторення: Origin Timestamp мусить дорівнювати T1 */
    if (resp.orig_ts_sec != req.tx_ts_sec || resp.orig_ts_frac != req.tx_ts_frac) {
        fprintf(stderr, "Помилка безпеки: Origin Timestamp не збігається з міткою запиту T1!\n");
        return -1;
    }

    double t2 = ntp_to_unix_seconds(resp.rx_ts_sec, resp.rx_ts_frac);
    double t3 = ntp_to_unix_seconds(resp.tx_ts_sec, resp.tx_ts_frac);

    /* Розрахунок затримки та зміщення за стандартом RFC 5905 */
    double delay = (t4 - t1) - (t3 - t2);
    double offset = ((t2 - t1) + (t3 - t4)) / 2.0;

    if (delay < 0.0) {
        fprintf(stderr, "Попередження: кругова затримка від'ємна (%.6f с), відкидаємо вибірку\n", delay);
        return -1;
    }

    *out_offset = offset;
    *out_delay = delay;

    printf("Успішний обмін: Stratum=%d, T1=%.6f, T2=%.6f, T3=%.6f, T4=%.6f\n", stratum, t1, t2, t3, t4);
    printf("Метрики зв'язку: Round-Trip Delay = %.6f с, Clock Offset = %.6f с\n", delay, offset);

    return 0;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <chrono>
#include <expected>
#include <system_error>
#include <array>
#include <cmath>
#include <cstring>
#include <netdb.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/time.h>

class SocketHandle {
    int fd_{-1};
public:
    explicit SocketHandle(int fd) noexcept : fd_(fd) {}
    ~SocketHandle() noexcept {
        if (fd_ >= 0) ::close(fd_);
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
    [[nodiscard]] bool valid() const noexcept { return fd_ >= 0; }
};

struct NtpMeasurement {
    double offset_seconds{0.0};
    double delay_seconds{0.0};
    uint8_t stratum{0};
    uint8_t leap_indicator{0};
};

class SntpClient {
public:
    static constexpr uint16_t DefaultPort = 123;
    static constexpr uint32_t NtpEpochDelta = 2208988800ULL;
    static constexpr double NtpFracDivisor = 4294967296.0;

    static constexpr double StepThreshold = 0.128;   // 128 мс
    static constexpr double PanicThreshold = 1000.0; // 1000 с

#pragma pack(push, 1)
    struct Packet {
        uint8_t  li_vn_mode{0};
        uint8_t  stratum{0};
        int8_t   poll{0};
        int8_t   precision{0};
        uint32_t root_delay{0};
        uint32_t root_dispersion{0};
        uint32_t ref_id{0};
        uint32_t ref_sec{0};
        uint32_t ref_frac{0};
        uint32_t orig_sec{0};
        uint32_t orig_frac{0};
        uint32_t rx_sec{0};
        uint32_t rx_frac{0};
        uint32_t tx_sec{0};
        uint32_t tx_frac{0};
    };
#pragma pack(pop)

    static double to_unix_seconds(uint32_t be_sec, uint32_t be_frac) noexcept {
        const uint32_t s = ntohl(be_sec);
        const uint32_t f = ntohl(be_frac);
        if (s == 0 && f == 0) return 0.0;
        return static_cast<double>(s - NtpEpochDelta) + (static_cast<double>(f) / NtpFracDivisor);
    }

    static void to_ntp_timestamp(double unix_sec, uint32_t& out_sec, uint32_t& out_frac) noexcept {
        double int_part{0.0};
        const double frac_part = std::modf(unix_sec, &int_part);
        out_sec = htonl(static_cast<uint32_t>(int_part + NtpEpochDelta));
        out_frac = htonl(static_cast<uint32_t>(frac_part * NtpFracDivisor));
    }

    static double current_realtime_seconds() noexcept {
        struct timespec ts{};
        ::clock_gettime(CLOCK_REALTIME, &ts);
        return static_cast<double>(ts.tv_sec) + (static_cast<double>(ts.tv_nsec) / 1e9);
    }

    static std::expected<NtpMeasurement, std::string> query(std::string_view host, std::chrono::seconds timeout = std::chrono::seconds{3}) {
        struct addrinfo hints{};
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_DGRAM;

        struct addrinfo* res{nullptr};
        if (const int rc = ::getaddrinfo(host.data(), "123", &hints, &res); rc != 0) {
            return std::unexpected(std::string("getaddrinfo failed: ") + ::gai_strerror(rc));
        }

        SocketHandle sock(::socket(res->ai_family, res->ai_socktype, res->ai_protocol));
        if (!sock.valid()) {
            ::freeaddrinfo(res);
            return std::unexpected("Failed to create UDP socket");
        }

        struct timeval tv{};
        tv.tv_sec = timeout.count();
        tv.tv_usec = 0;
        ::setsockopt(sock.get(), SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));

        Packet req{};
        req.li_vn_mode = (0 << 6) | (4 << 3) | 3; // LI=0, VN=4, Mode=3 (Client)

        const double t1 = current_realtime_seconds();
        to_ntp_timestamp(t1, req.tx_sec, req.tx_frac);

        if (::sendto(sock.get(), &req, sizeof(req), 0, res->ai_addr, res->ai_addrlen) < 0) {
            ::freeaddrinfo(res);
            return std::unexpected("sendto failed: " + std::string(std::strerror(errno)));
        }

        Packet resp{};
        struct sockaddr_storage src_addr{};
        socklen_t src_len = sizeof(src_addr);

        const ssize_t bytes = ::recvfrom(sock.get(), &resp, sizeof(resp), 0,
                                        reinterpret_cast<struct sockaddr*>(&src_addr), &src_len);
        const double t4 = current_realtime_seconds();

        ::freeaddrinfo(res);

        if (bytes < static_cast<ssize_t>(sizeof(Packet))) {
            return std::unexpected("Invalid packet size or timeout occurred");
        }

        const uint8_t li = (resp.li_vn_mode >> 6) & 0x03;
        const uint8_t mode = resp.li_vn_mode & 0x07;
        const uint8_t stratum = resp.stratum;

        if (mode != 4 && mode != 5) {
            return std::unexpected("Invalid server mode: " + std::to_string(mode));
        }

        if (stratum == 0) {
            char kod[5] = {0};
            std::memcpy(kod, &resp.ref_id, 4);
            return std::unexpected("Received Kiss-o'-Death code: [" + std::string(kod) + "]");
        }

        if (li == 3 || stratum >= 16) {
            return std::unexpected("Server is unsynchronized");
        }

        if (resp.orig_sec != req.tx_sec || resp.orig_frac != req.tx_frac) {
            return std::unexpected("Origin timestamp mismatch (possible replay attack)");
        }

        const double t2 = to_unix_seconds(resp.rx_sec, resp.rx_frac);
        const double t3 = to_unix_seconds(resp.tx_sec, resp.tx_frac);

        const double delay = (t4 - t1) - (t3 - t2);
        const double offset = ((t2 - t1) + (t3 - t4)) / 2.0;

        if (delay < 0.0) {
            return std::unexpected("Negative round-trip delay detected");
        }

        return NtpMeasurement{
            .offset_seconds = offset,
            .delay_seconds = delay,
            .stratum = stratum,
            .leap_indicator = li
        };
    }

    static std::expected<void, std::string> adjust_clock(double offset) noexcept {
        const double abs_offset = std::abs(offset);

        if (abs_offset >= PanicThreshold) {
            return std::unexpected("Offset exceeds panic threshold (1000s)");
        }

        if (abs_offset < StepThreshold) {
            struct timeval adj{};
            adj.tv_sec = static_cast<time_t>(offset);
            adj.tv_usec = static_cast<suseconds_t>((offset - static_cast<double>(adj.tv_sec)) * 1e6);

            if (::adjtime(&adj, nullptr) != 0) {
                return std::unexpected(std::string("adjtime failed: ") + std::strerror(errno));
            }
            std::cout << "Discipline: Applied clock slew: " << offset << " s (monotonic)\n";
        } else {
            struct timespec now{};
            ::clock_gettime(CLOCK_REALTIME, &now);
            const double target_sec = (static_cast<double>(now.tv_sec) + (static_cast<double>(now.tv_nsec) / 1e9)) + offset;

            struct timespec target{};
            target.tv_sec = static_cast<time_t>(target_sec);
            target.tv_nsec = static_cast<long>((target_sec - static_cast<double>(target.tv_sec)) * 1e9);

            if (::clock_settime(CLOCK_REALTIME, &target) != 0) {
                return std::unexpected(std::string("clock_settime failed: ") + std::strerror(errno));
            }
            std::cout << "Discipline: Applied clock step: " << offset << " s\n";
        }
        return {};
    }
};
```
:::

### Діагностика та аналіз трафіку SNTP утилітою tcpdump

Для низькорівневої перевірки правильності обміну та налагодження клієнтів застосовують утиліту `tcpdump`:

```
$ sudo tcpdump -nvvXX -i eth0 port 123
```

Зразок отриманого двійкового дампу відповіді сервера:
```
12:00:00.153000 IP (tos 0xb8, ttl 56, id 41223, offset 0, flags [DF], proto UDP (17), length 76)
    192.0.2.1.123 > 198.51.100.5.54321: [udp sum ok] NTPv4, length 48
	Server, Leap none, Stratum 2 (secondary reference), poll 6 (64s), precision -20
	Root Delay: 0.012542, Root Dispersion: 0.000412, Reference-ID: 198.18.0.1
	  Reference Timestamp:  3924854380.501234000 (2026-06-10 11:59:40 UTC)
	  Originator Timestamp: 3924854400.100000000 (2026-06-10 12:00:00 UTC) [T1]
	  Receive Timestamp:    3924854400.125000000 (2026-06-10 12:00:00 UTC) [T2]
	  Transmit Timestamp:   3924854400.126000000 (2026-06-10 12:00:00 UTC) [T3]
	    Originator - Receive Timestamp:  +0.025000000
	    Originator - Transmit Timestamp: +0.026000000
```

Утиліта підтверджує:
1. Заголовок має довжину рівно 48 байтів;
2. Поле `Originator Timestamp` збігається з часом відправки запиту клієнтом `T1`;
3. Поле `Receive Timestamp` містить час надходження на сервер `T2`;
4. Поле `Transmit Timestamp` фіксує відправку сервером `T3`.

Клієнт після зчитування `T4 = 12:00:00.153` обчислює `δ = 52 мс` та зміщення `θ = -1.0 мс`, успішно завершуючи ітерацію синхронізації.

### Діагностика синхронізації в Linux через timedatectl

У сучасних дистрибутивах Linux стан підсистеми синхронізації перевіряється вбудованою службою `systemd-timesyncd`:

```
$ timedatectl timesync-status
```

Команда повертає деталізований звіт про якість поточного з'єднання:
```
       Server: 192.0.2.1 (time.cloudflare.com)
Poll interval: 4min 16s (min: 32s; max 34min 8s)
         Leap: normal
      Version: 4
      Stratum: 3
    Reference: C0000201
       Offset: -214.321us
        Delay: 12.451ms
       Jitter: 48.120us
 Packet count: 18
  Jitter (sys): 52.301us
```

Параметри `Offset`, `Delay` та `Jitter` відображають статистичну стабільність каналу: низький джиттер свідчить про відсутність асиметричних черг, а від'ємне зміщення вказує на незначне відставання системного кварцового генератора хоста відносно первинного еталона.

### Інтеграція клієнта як системної служби systemd

Для періодичного автономного виконання синхронізації на Linux-серверах клієнт оформлюють як системну службу та таймер `systemd`:

1. **Файл служби `/etc/systemd/system/sntp-sync.service`:**
   ```ini
   [Unit]
   Description=SNTP One-Shot Network Time Synchronization
   After=network-online.target
   Wants=network-online.target

   [Service]
   Type=oneshot
   ExecStart=/usr/local/bin/sntp-client time.cloudflare.com
   CapabilityBoundingSet=CAP_SYS_TIME
   AmbientCapabilities=CAP_SYS_TIME
   ProtectSystem=strict
   ProtectHome=true
   PrivateTmp=true
   NoNewPrivileges=true
   ```

2. **Файл періодичного таймера `/etc/systemd/system/sntp-sync.timer`:**
   ```ini
   [Unit]
   Description=Run SNTP Synchronization Periodically

   [Timer]
   OnBootSec=15s
   OnUnitActiveSec=15min
   RandomizedDelaySec=30s
   Persistent=true

   [Install]
   WantedBy=timers.target
   ```

Параметр `RandomizedDelaySec=30s` розподіляє моменти звернення тисяч хостів до публічних пулів NTP, усуваючи синхронні сплески трафіку (англ. *Thundering Herd problem*).

### Експорт метрик синхронізації в системи спостережуваності

Для безперервного контролю розбіжності часу в кластерних середовищах клієнт експортує метрики у форматі OpenMetrics/Prometheus:
* `sntp_offset_seconds` — поточне зміщення системного годинника відносно віддаленого сервера;
* `sntp_round_trip_delay_seconds` — мережева кругова затримка датаграми;
* `sntp_server_stratum` — шар ієрархії опитаного сервера;
* `sntp_last_sync_timestamp` — час Unix останнього успішного оновлення;
* `sntp_sync_errors_total` — лічильник виявлених помилок (тайм-аути, розрив валідації `T1`, пакети Kiss-o'-Death).

Системи алертінгу (Alertmanager) налаштовують на спрацьовування сповіщень при перевищенні порогу `abs(sntp_offset_seconds) > 0.05` (50 мс) або за відсутності оновлень понад 1 годину.

### Порівняльний аналіз: SNTP проти повнофункціонального NTPd та Chrony

| Критерій | Легковаговий клієнт SNTP | Класичний демон NTPd | Сучасний демон Chrony |
| :--- | :--- | :--- | :--- |
| **Архітектурна складність** | Мінімальна (~300 рядків коду) | Висока (~150 000 рядків коду) | Середня (~60 000 рядків коду) |
| **Використання пам'яті (RAM)** | < 1 МБ (вивантажується після відліку) | 10–25 МБ (постійний процес) | 3–8 МБ (постійний процес) |
| **Матрична фільтрація пірів** | Відсутня (одночасне або послідовне опитування) | Алгоритм перетину Марзулло + кластеризація | Алгоритм перетину + статистична регресія затримок |
| **Калібрування дрейфу кристала** | Відсутнє (залежить від стабільності ОС) | Безперервний контур PLL/FLL (`driftfile`) | Оцінка нахилу частоти за методом найменших квадратів |
| **Швидкість початкового сходу** | Миттєва (разовий Step/Slew) | Повільна (10–30 хвилин через PLL) | Дуже швидка (режим `makestep 1.0 3`) |
| **Підтримка NTS (RFC 8915)** | Потребує зовнішньої бібліотеки TLS | Доступна в ntpsec | Повна нативна підтримка |
| **Типові сценарії застосування** | Мікроконтролери, IoT, CLI-утиліти, контейнери | Опорні сервери телекомунікацій | Хмарні інстанси, бази даних, робочі станції |

### Типові пастки та крайові випадки при розробці клієнтів SNTP

1. **Ігнорування мережевого порядку байтів (Endianness):**
   Поля `seconds` та `fraction` передаються як 32-бітні цілі числа у форматі Big-Endian. На апаратних платформах x86 та ARM (Little-Endian) пряме читання `uint32_t` без функції `ntohl()` перетворює секунди на безладні числа, зміщуючи шкалу часу на сотні років у майбутнє або минуле.

2. **Втрата точності при використанні чисел із плаваючою комою:**
   Дробова частина часу NTP має 32 біти двійкової роздільності (~232 пікосекунди). Стандартний 64-бітний тип `double` (стандарт IEEE 754) має лише 53 біти мантиси. Для повної кількості секунд від 1900 року (`~4 · 10⁹` секунд, що займає 32 біти), на дробову частину в `double` залишається лише 21 біт роздільності (~0.47 мікросекунди). Для наносекундних розрахунків арифметику виконують у 64-бітних цілих числах наносекунд через `struct timespec`.

3. **Спуфінг та атака повторення (Replay Attack):**
   Якщо клієнт залишає поле `Transmit Timestamp` у запиті нульовим, зловмисник у локальній мережі може надіслати підроблену або записану раніше відповідь від легітимного сервера. Запис локального часу `T1` у поле `Tx Timestamp` запиту та сувора перевірка його наявності в полі `Origin Timestamp` відповіді унеможливлює підміну пакетів без знання точного моменту генерації запиту.

4. **Розрив монотонності при одночасному виконанні таймерів:**
   Якщо клієнт виконує `clock_settime()` (Clock Step) назад, таймери ядра POSIX `timerfd_create()` з прапорцем `CLOCK_REALTIME` можуть заблокуватися або ніколи не спрацювати. Для надійних інтервальних таймерів у системному програмуванні завжди застосовують монотонний таймер `CLOCK_MONOTONIC`, хід якого не зазнає розривів навіть під час стрибків абсолютного часу `CLOCK_REALTIME`.

5. **Стохастичний джиттер черг (Bufferbloat):**
   Якщо мережевий канал зазнає перевантаження іншим трафіком, датаграма NTP може затриматися в буфері на сотні мілісекунд. Простий клієнт SNTP без накопичення ковзного вікна вибірок сприйме цю затримку як симетричну, внісши спотворення у системний годинник. Для критичних вузлів налаштовують пріоритет трафіку QoS (DSCP `0x2E` / Expedited Forwarding) на порті UDP 123.

6. **Вимоги розподілених баз даних (Max Offset Guard):**
   Сучасні розподілені сховища (CockroachDB, YugabyteDB) перевіряють похибку синхронізації через `maxerror` виклику `adjtimex()`. Якщо локальний годинник відхиляється від кворуму більше ніж на встановлений ліміт (зазвичай 250–500 мс), вузол самостійно вимикається для усунення ризику порушення лінеаризовності транзакцій (англ. *Linearizability violation*).

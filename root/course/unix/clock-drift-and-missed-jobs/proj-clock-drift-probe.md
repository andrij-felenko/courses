# Практичний зонд дрейфу часу: вимірювання розбіжності та монітор фазового стану ядра

Стандартні утиліти моніторингу зазвичай показують усереднені значення зміщення, приховуючи фізичну поведінку окремих системних годинників та прямий стан контуру автопідстроювання ядра. Щоб діагностувати апаратний дрейф кварцового генератора, перевірити, чи не заблокована синхронізація з RTC через прапорець `STA_UNSYNC`, та виміряти розходження між різними шкалами часу (`CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_MONOTONIC_RAW`), потрібен спеціалізований діагностичний інструмент.

Цей проєкт реалізує низькорівневий інженерний зонд, який вирішує чотири прикладні задачі:
1. Зчитує структуру ядра `timex` через системний виклик `adjtimex(2)` без модифікації системного стану (`modes = 0`), що дозволяє запускати утиліту від імені будь-якого непривілейованого користувача;
2. Декодує активні бітові прапорці стану (`STA_*`), перевіряє статус синхронізації та виявляє загрозу блокування автоматичного оновлення апаратного годинника RTC;
3. Здійснює синхронний замір чотирьох годинників ядра (`REALTIME`, `MONOTONIC`, `MONOTONIC_RAW`, `BOOTTIME`) і фіксує накопичене розходження між апаратним часом та часом контуру NTP;
4. Проводить контрольне вимірювання власного апаратного дрейфу частоти за заданий інтервал часу з обчисленням відхилення у частках на мільйон (ppm).

## Реалізація зонда

:::tabs
@tab C
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <errno.h>
#include <sys/timex.h>

static int64_t ts_to_ns(const struct timespec *ts) {
    return (int64_t)ts->tv_sec * 1000000000LL + ts->tv_nsec;
}

static void print_status_flags(int status) {
    printf("  Прапорці стану (status=0x%04X):\n", status);
    if (status & STA_PLL)       printf("    [+] STA_PLL       (контур фазового автопідстроювання активний)\n");
    if (status & STA_FLL)       printf("    [+] STA_FLL       (контур частотного автопідстроювання активний)\n");
    if (status & STA_UNSYNC)    printf("    [!] STA_UNSYNC    (ГОДИННИК НЕ СИНХРОНІЗОВАНО! Запис у RTC вимкнено)\n");
    if (status & STA_PPSSIGNAL) printf("    [+] STA_PPSSIGNAL (сигнал точного часу PPS виявлено)\n");
    if (status & STA_NANO)      printf("    [+] STA_NANO      (роздільність зсуву в наносекундах)\n");
    if (status & STA_INS)       printf("    [!] STA_INS       (заплановано додавання секунди координації)\n");
    if (status & STA_DEL)       printf("    [!] STA_DEL       (заплановано віднімання секунди координації)\n");
}

static void decode_adjtimex_state(void) {
    struct timex tx;
    memset(&tx, 0, sizeof(tx));
    tx.modes = 0; // Режим лише для зчитування

    int state = adjtimex(&tx);
    if (state == -1) {
        perror("adjtimex");
        return;
    }

    printf("=== СТАН ЯДЕРНОГО СИНХРОНІЗАТОРА TIMEKEEPING ===\n");
    printf("  Код повернення Leap State : %d ", state);
    switch (state) {
        case TIME_OK:    printf("(TIME_OK: час синхронізовано)\n"); break;
        case TIME_INS:   printf("(TIME_INS: вставка leap second)\n"); break;
        case TIME_DEL:   printf("(TIME_DEL: видалення leap second)\n"); break;
        case TIME_OOP:   printf("(TIME_OOP: leap second у процесі)\n"); break;
        case TIME_WAIT:  printf("(TIME_WAIT: leap second завершено)\n"); break;
        case TIME_ERROR: printf("(TIME_ERROR: помилка синхронізації / STA_UNSYNC)\n"); break;
        default:         printf("(невідомий стан)\n"); break;
    }

    // tx.freq зберігається у масштабі 2^16 = 65536 на 1 ppm
    double freq_ppm = (double)tx.freq / 65536.0;
    double max_err_ms = (double)tx.maxerror / 1000.0;
    double est_err_ms = (double)tx.esterror / 1000.0;

    printf("  Частотна корекція (freq)  : %.4f ppm (сире значення: %ld)\n", freq_ppm, tx.freq);
    printf("  Фазовий зсув (offset)     : %ld %s\n", tx.offset, (tx.status & STA_NANO) ? "нс" : "мкс");
    printf("  Максимальна похибка       : %.3f мс\n", max_err_ms);
    printf("  Оцінена похибка           : %.3f мс\n", est_err_ms);
    printf("  Постійна часу контуру PLL : %ld\n", tx.constant);
    printf("  Тривалість тика ядра      : %ld мкс\n", tx.tick);

    print_status_flags(tx.status);
}

static void sample_clock_divergence(void) {
    struct timespec ts_real, ts_mono, ts_raw, ts_boot;

    clock_gettime(CLOCK_REALTIME, &ts_real);
    clock_gettime(CLOCK_MONOTONIC, &ts_mono);
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts_raw);
    clock_gettime(CLOCK_BOOTTIME, &ts_boot);

    int64_t ns_real = ts_to_ns(&ts_real);
    int64_t ns_mono = ts_to_ns(&ts_mono);
    int64_t ns_raw  = ts_to_ns(&ts_raw);
    int64_t ns_boot = ts_to_ns(&ts_boot);

    printf("\n=== ЗРІЗ СИСТЕМНИХ ГОДИННИКІВ ===\n");
    printf("  CLOCK_REALTIME      : %lld.%09ld с\n", (long long)ts_real.tv_sec, ts_real.tv_nsec);
    printf("  CLOCK_MONOTONIC     : %lld.%09ld с\n", (long long)ts_mono.tv_sec, ts_mono.tv_nsec);
    printf("  CLOCK_MONOTONIC_RAW : %lld.%09ld с\n", (long long)ts_raw.tv_sec, ts_raw.tv_nsec);
    printf("  CLOCK_BOOTTIME      : %lld.%09ld с\n", (long long)ts_boot.tv_sec, ts_boot.tv_nsec);

    int64_t raw_vs_mono = ns_mono - ns_raw;
    int64_t boot_vs_mono = ns_boot - ns_mono;

    printf("  Різниця NTP Slew (MONO - RAW)     : %+lld нс (%+.3f мс)\n",
           (long long)raw_vs_mono, (double)raw_vs_mono / 1000000.0);
    printf("  Час у сні/гібернації (BOOT - MONO): %+lld нс (%+.3f с)\n",
           (long long)boot_vs_mono, (double)boot_vs_mono / 1000000000.0);
}

int main(int argc, char **argv) {
    int duration_sec = 2;
    if (argc > 1) {
        duration_sec = atoi(argv[1]);
        if (duration_sec < 1) duration_sec = 1;
    }

    decode_adjtimex_state();
    sample_clock_divergence();

    printf("\n=== ВИМІРЮВАННЯ ВЛАСНОГО АПАРАТНОГО ДРЕЙФУ (%d с) ===\n", duration_sec);
    struct timespec mono_start, raw_start;
    clock_gettime(CLOCK_MONOTONIC, &mono_start);
    clock_gettime(CLOCK_MONOTONIC_RAW, &raw_start);

    sleep((unsigned int)duration_sec);

    struct timespec mono_end, raw_end;
    clock_gettime(CLOCK_MONOTONIC, &mono_end);
    clock_gettime(CLOCK_MONOTONIC_RAW, &raw_end);

    int64_t d_mono = ts_to_ns(&mono_end) - ts_to_ns(&mono_start);
    int64_t d_raw  = ts_to_ns(&raw_end) - ts_to_ns(&raw_start);

    int64_t drift_ns = d_mono - d_raw;
    double drift_ppm = ((double)drift_ns / (double)d_raw) * 1e6;

    printf("  Тривалість за CLOCK_MONOTONIC     : %.6f с\n", (double)d_mono / 1e9);
    printf("  Тривалість за CLOCK_MONOTONIC_RAW : %.6f с\n", (double)d_raw / 1e9);
    printf("  Накопичений зсув контуру NTP      : %+lld нс\n", (long long)drift_ns);
    printf("  Миттєва швидкість компенсації     : %+.4f ppm\n", drift_ppm);

    return 0;
}
```
@tab C++
```cpp
#include <iostream>
#include <iomanip>
#include <chrono>
#include <string_view>
#include <system_error>
#include <thread>
#include <cstdint>
#include <cstring>
#include <sys/timex.h>
#include <unistd.h>

namespace timeprobe {

using nanoseconds = std::chrono::nanoseconds;

struct ClockSnapshot {
    std::chrono::system_clock::time_point realtime;
    std::chrono::steady_clock::time_point monotonic;
    nanoseconds monotonic_raw{0};
    nanoseconds boottime{0};
};

class KernelTimeInspector {
public:
    static void print_diagnostics() {
        timex tx{};
        tx.modes = 0; // Суто читання

        int state = ::adjtimex(&tx);
        if (state == -1) {
            throw std::system_error(errno, std::generic_category(), "Помилка виклику adjtimex");
        }

        std::cout << "=== СТАН ЯДЕРНОГО СИНХРОНІЗАТОРА TIMEKEEPING ===\n";
        std::cout << "  Код повернення Leap State : " << state << " " << decode_leap_state(state) << "\n";

        double freq_ppm = static_cast<double>(tx.freq) / 65536.0;
        double max_err_ms = static_cast<double>(tx.maxerror) / 1000.0;
        double est_err_ms = static_cast<double>(tx.esterror) / 1000.0;

        std::cout << std::fixed << std::setprecision(4);
        std::cout << "  Частотна корекція (freq)  : " << freq_ppm << " ppm (сире: " << tx.freq << ")\n";
        std::cout << "  Фазовий зсув (offset)     : " << tx.offset << " " << ((tx.status & STA_NANO) ? "нс" : "мкс") << "\n";
        std::cout << std::setprecision(3);
        std::cout << "  Максимальна похибка       : " << max_err_ms << " мс\n";
        std::cout << "  Оцінена похибка           : " << est_err_ms << " мс\n";
        std::cout << "  Постійна часу контуру PLL : " << tx.constant << "\n";
        std::cout << "  Тривалість тика ядра      : " << tx.tick << " мкс\n";

        print_flags(tx.status);
    }

    static ClockSnapshot capture_snapshot() {
        timespec ts_real{}, ts_mono{}, ts_raw{}, ts_boot{};
        ::clock_gettime(CLOCK_REALTIME, &ts_real);
        ::clock_gettime(CLOCK_MONOTONIC, &ts_mono);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &ts_raw);
        ::clock_gettime(CLOCK_BOOTTIME, &ts_boot);

        ClockSnapshot snap{};
        snap.realtime = std::chrono::system_clock::time_point(
            std::chrono::seconds(ts_real.tv_sec) + std::chrono::nanoseconds(ts_real.tv_nsec));
        snap.monotonic = std::chrono::steady_clock::time_point(
            std::chrono::seconds(ts_mono.tv_sec) + std::chrono::nanoseconds(ts_mono.tv_nsec));
        snap.monotonic_raw = std::chrono::seconds(ts_raw.tv_sec) + std::chrono::nanoseconds(ts_raw.tv_nsec);
        snap.boottime = std::chrono::seconds(ts_boot.tv_sec) + std::chrono::nanoseconds(ts_boot.tv_nsec);
        return snap;
    }

private:
    static std::string_view decode_leap_state(int state) noexcept {
        switch (state) {
            case TIME_OK:    return "(TIME_OK: час синхронізовано)";
            case TIME_INS:   return "(TIME_INS: вставка leap second)";
            case TIME_DEL:   return "(TIME_DEL: видалення leap second)";
            case TIME_OOP:   return "(TIME_OOP: leap second у процесі)";
            case TIME_WAIT:  return "(TIME_WAIT: leap second завершено)";
            case TIME_ERROR: return "(TIME_ERROR: помилка синхронізації / STA_UNSYNC)";
            default:         return "(невідомий стан)";
        }
    }

    static void print_flags(int status) {
        std::cout << "  Прапорці стану (status=0x" << std::hex << std::uppercase
                  << std::setw(4) << std::setfill('0') << status << std::dec << std::setfill(' ') << "):\n";
        if (status & STA_PLL)       std::cout << "    [+] STA_PLL       (контур фазового автопідстроювання активний)\n";
        if (status & STA_FLL)       std::cout << "    [+] STA_FLL       (контур частотного автопідстроювання активний)\n";
        if (status & STA_UNSYNC)    std::cout << "    [!] STA_UNSYNC    (ГОДИННИК НЕ СИНХРОНІЗОВАНО! Запис у RTC вимкнено)\n";
        if (status & STA_PPSSIGNAL) std::cout << "    [+] STA_PPSSIGNAL (сигнал точного часу PPS виявлено)\n";
        if (status & STA_NANO)      std::cout << "    [+] STA_NANO      (роздільність зсуву в наносекундах)\n";
        if (status & STA_INS)       std::cout << "    [!] STA_INS       (заплановано додавання секунди координації)\n";
        if (status & STA_DEL)       std::cout << "    [!] STA_DEL       (заплановано віднімання секунди координації)\n";
    }
};

} // namespace timeprobe

int main(int argc, char **argv) {
    try {
        int duration_sec = 2;
        if (argc > 1) {
            duration_sec = std::max(1, std::atoi(argv[1]));
        }

        timeprobe::KernelTimeInspector::print_diagnostics();

        auto snap = timeprobe::KernelTimeInspector::capture_snapshot();
        auto mono_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(snap.monotonic.time_since_epoch()).count();
        auto raw_ns = snap.monotonic_raw.count();
        auto boot_ns = snap.boottime.count();

        std::cout << "\n=== ЗРІЗ СИСТЕМНИХ ГОДИННИКІВ ===\n";
        std::cout << "  CLOCK_MONOTONIC     : " << mono_ns << " нс\n";
        std::cout << "  CLOCK_MONOTONIC_RAW : " << raw_ns << " нс\n";
        std::cout << "  CLOCK_BOOTTIME      : " << boot_ns << " нс\n";

        auto raw_vs_mono = mono_ns - raw_ns;
        auto boot_vs_mono = boot_ns - mono_ns;

        std::cout << std::fixed << std::setprecision(3);
        std::cout << "  Різниця NTP Slew (MONO - RAW)     : " << raw_vs_mono << " нс ("
                  << (static_cast<double>(raw_vs_mono) / 1e6) << " мс)\n";
        std::cout << "  Час у сні/гібернації (BOOT - MONO): " << boot_vs_mono << " нс ("
                  << (static_cast<double>(boot_vs_mono) / 1e9) << " с)\n";

        std::cout << "\n=== ВИМІРЮВАННЯ ВЛАСНОГО АПАРАТНОГО ДРЕЙФУ (" << duration_sec << " с) ===\n";
        timespec m_start{}, r_start{};
        ::clock_gettime(CLOCK_MONOTONIC, &m_start);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &r_start);

        std::this_thread::sleep_for(std::chrono::seconds(duration_sec));

        timespec m_end{}, r_end{};
        ::clock_gettime(CLOCK_MONOTONIC, &m_end);
        ::clock_gettime(CLOCK_MONOTONIC_RAW, &r_end);

        int64_t d_mono = (static_cast<int64_t>(m_end.tv_sec - m_start.tv_sec) * 1000000000LL) + (m_end.tv_nsec - m_start.tv_nsec);
        int64_t d_raw  = (static_cast<int64_t>(r_end.tv_sec - r_start.tv_sec) * 1000000000LL) + (r_end.tv_nsec - r_start.tv_nsec);

        int64_t drift_ns = d_mono - d_raw;
        double drift_ppm = (static_cast<double>(drift_ns) / static_cast<double>(d_raw)) * 1e6;

        std::cout << "  Тривалість за CLOCK_MONOTONIC     : " << (static_cast<double>(d_mono) / 1e9) << " с\n";
        std::cout << "  Тривалість за CLOCK_MONOTONIC_RAW : " << (static_cast<double>(d_raw) / 1e9) << " с\n";
        std::cout << "  Накопичений зсув контуру NTP      : " << drift_ns << " нс\n";
        std::cout << std::setprecision(4);
        std::cout << "  Миттєва швидкість компенсації     : " << drift_ppm << " ppm\n";

    } catch (const std::exception &ex) {
        std::cerr << "Помилка: " << ex.what() << "\n";
        return 1;
    }
    return 0;
}
```
:::

## Збирання та запуск

Для компіляції програми використовують стандартні компілятори GNU або Clang:

```bash
# Компіляція версії C (POSIX/Linux API)
gcc -O2 -Wall -Wextra timeprobe.c -o timeprobe_c

# Компіляція версії C++ (C++20, STL chrono)
g++ -O2 -Wall -Wextra -std=c++20 timeprobe.cpp -o timeprobe_cpp

# Запуск із вимірювальним вікном у 5 секунд
./timeprobe_c 5
```

## Аналіз діагностичного виводу

Запуск скомпільованого бінарника на стабільно синхронізованій системі демонструє злагоджену роботу підсистеми керування часом:

```text
=== СТАН ЯДЕРНОГО СИНХРОНІЗАТОРА TIMEKEEPING ===
  Код повернення Leap State : 0 (TIME_OK: час синхронізовано)
  Частотна корекція (freq)  : -18.4120 ppm (сире значення: -1206648)
  Фазовий зсув (offset)     : -412 нс
  Максимальна похибка       : 24.120 мс
  Оцінена похибка           : 0.082 мс
  Постійна часу контуру PLL : 6
  Тривалість тика ядра      : 10000 мкс
  Прапорці стану (status=0x2001):
    [+] STA_PLL       (контур фазового автопідстроювання активний)
    [+] STA_NANO      (роздільність зсуву в наносекундах)

=== ЗРІЗ СИСТЕМНИХ ГОДИННИКІВ ===
  CLOCK_REALTIME      : 1771963215.845120300 с
  CLOCK_MONOTONIC     : 481230.142050110 с
  CLOCK_MONOTONIC_RAW : 481221.285012400 с
  CLOCK_BOOTTIME      : 481230.142050110 с
  Різниця NTP Slew (MONO - RAW)     : +8857037710 нс (+8857.038 мс)
  Час у сні/гібернації (BOOT - MONO): +0 нс (+0.000 с)

=== ВИМІРЮВАННЯ ВЛАСНОГО АПАРАТНОГО ДРЕЙФУ (2 с) ===
  Тривалість за CLOCK_MONOTONIC     : 2.000142 с
  Тривалість за CLOCK_MONOTONIC_RAW : 2.000179 с
  Накопичений зсув контуру NTP      : -37000 нс
  Миттєва швидкість компенсації     : -18.4984 ppm
```

### Інженерна інтерпретація метрик

При аналізі результатів зондування системний інженер звертає увагу на чотири критичні аспекти:

1. **Коливання між `MONOTONIC` та `MONOTONIC_RAW`:** 
   Годинник `CLOCK_MONOTONIC_RAW` підраховує виключно апаратні такти лічильника TSC/HPET без будь-якого впливу контурів NTP або adjtimex. Поступове накопичення різниці між керованим `CLOCK_MONOTONIC` та апаратним `CLOCK_MONOTONIC_RAW` показує інтегральну роботу демона синхронізації з моменту старту ядра. У наведеному вище прикладі контур плавного регулювання уповільнив системний монотонний годинник сумарно на 8.85 с, компенсуючи фізичне поспішання локального кварцового резонатора.

2. **Діагностика прапорця `STA_UNSYNC`:** 
   Якщо в блоці прапорців виводиться повідомлення `[!] STA_UNSYNC`, це означає, що системний демон NTP або не запущений, або втратив зв'язок з усіма довіреними джерелами часу понад допустимий інтервал. У цьому стані ядро блокує періодичний 11-хвилинний запис у мікросхему RTC. Якщо сервер буде перезавантажено в такому стані, він запуститься з застарілим часом, що призведе до збою розкладу завдань `cron` та відмови сертифікатів безпеки.

3. **Аналіз поля `freq` у ppm:** 
   Якщо значення `freq` наближається до апаратного ліміту ядра ±500 ppm (сире значення ±32768000), це свідчить про серйозний дефект кварцового генератора материнської плати або про некоректне калібрування тактової частоти віртуального процесора (vCPU) у конфігурації гіпервізора.

4. **Час перебування у сні (`BOOTTIME - MONOTONIC`):** 
   Різниця між `CLOCK_BOOTTIME` та `CLOCK_MONOTONIC` показує точний сумарний час, який система провела у стані глибокого сну (suspend/hibernate). Якщо ця різниця не дорівнює нулю на сервері безперервної роботи, це свідчить про незаплановані переходи в енергозберігаючі стани ACPI.

## Продуктивність зчитування часу: магія vDSO проти справжнього системного виклику

У високонавантажених системах виклики вимірювання часу здійснюються мільйони разів на секунду (наприклад, у профайлерах, трасувальниках запитів та логерах).

В операційній системі Linux існує принципова різниця у вартості викликів `clock_gettime()` та `adjtimex()`:

1. **Прискорення через vDSO (Virtual Dynamic Shared Object):**
   Виклики `clock_gettime(CLOCK_REALTIME)` та `clock_gettime(CLOCK_MONOTONIC)` не здійснюють перемикання контексту процесора у простір ядра (ring 0). Ядро мапить сторінку пам'яті `vvar` у простір користувача, де зберігаються поточні базові значення лічильника TSC та множники переведення. Код утиліти у просторі користувача зчитує регістр процесора `rdtsc` або `rdtscp` і самостійно розраховує час за 15–25 наносекунд.

2. **Повноцінний системний виклик `adjtimex`:**
   На відміну від зчитування часу, виклик `adjtimex()` завжди призводить до повноцінного апаратного переривання та перемикання контексту у простір ядра. Його виконання займає від 500 до 1500 наносекунд. Тому діагностичні виклики `adjtimex()` не слід викликати на гарячих шляхах обробки мережевих пакетів.

## Пастки програмування таймерів: чому не можна спати за REALTIME

При розробці високонавантажених сервісів та планувальників завдань вибір годинника для таймерів визначає стійкість застосунку до коригувань часу.

Системні виклики очікування (`nanosleep`, `clock_nanosleep`, `select`, `poll`, `epoll_wait`, `timerfd_settime`) поводяться принципово по-різному залежно від типу годинника:

* **Відносний сон (Relative Sleep):** виклик `sleep(10)` або `nanosleep(&req, NULL)` вимірює інтервал за монотонним таймером ядра. Навіть якщо під час сну системний календарний час стрибне на 5 років назад або вперед, потік прокинеться рівно через 10 фізичних секунд.
* **Абсолютний сон за REALTIME (Absolute Sleep):** якщо програма використовує прапорець `TIMER_ABSTIME` з годинником `CLOCK_REALTIME` (наприклад, `clock_nanosleep(CLOCK_REALTIME, TIMER_ABSTIME, &target_time, NULL)`):
  - Якщо час стрибає **вперед**, цільова абсолютна мить настає раніше — таймер спрацьовує миттєво, не дочекавшись реального інтервалу;
  - Якщо час стрибає **назад**, цільова мить віддаляється — потік засинає на додатковий час стрибка (наприклад, замість 5 секунд потік спить 15 хвилин).
* **Спеціальний прапорець `TFD_TIMER_CANCEL_ON_SET`:** для файлових дескрипторів `timerfd`, прив'язаних до `CLOCK_REALTIME`, рекомендується передавати прапорець `TFD_TIMER_CANCEL_ON_SET`. У такому разі будь-який ступінчастий стрибок системного часу негайно скасовує таймер і повертає помилку `ECANCELED`, дозволяючи застосунку перерахувати інтервал замість нескінченного зависання.

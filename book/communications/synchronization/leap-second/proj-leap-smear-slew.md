# ⚙️ Програмне коригування годинника та емуляція розмазування секунди в Linux

Програмне керування частотою системного годинника в операційних системах сімейства Linux здійснюється через системні виклики `adjtimex()` та `ntp_adjtime()`. Ця вставка містить архітектурний розбір алгоритму розмазування високосної секунди (Leap Smearing), спосіб перерахунку фізичних одиниць частоти у внутрішній 64-бітний масштаб ядра Linux, інженерні методи усунення накопиченого дрейфу в циклах регулювання, роботу з новими типами годинників у C++20 (`std::chrono::utc_clock`, `std::chrono::tai_clock`), а також завершену реалізацію демона розмазування на мовах C та ідіоматичному C++20.

---

### Архітектура керування частотою в ядрі Linux

Ядро Linux моделює системний годинник `CLOCK_REALTIME` як неперервний інтегратор фази, що живиться від апаратного лічильника процесора (TSC, HPET або ACPI PM Timer). Частота інкременту системного часу контролюється алгоритмом фазового автопідстроювання частоти (Phase-Locked Loop, PLL), описаним у стандарті RFC 5905 та роботах Девіда Міллса (англ. *David L. Mills*).

Керування підсистемою часу з простору користувача виконується за допомогою системної структури `struct timex` (заголовний файл `<sys/timex.h>`).

Коли користувацький процес або демон синхронізації викликає `adjtimex()` із маскою `modes = ADJ_FREQUENCY`, ядро не змінює поточні покази секунд або мікросекунд, а модифікує коефіцієнт масштабування апаратного лічильника. Під час кожного апаратного переривання або звернення до годинника функція `timekeeping_advance()` додає до системного часу кількість наносекунд, скориговану на величину встановленого відхилення частоти.

#### Шкала представлення частоти `tx.freq`
Ядро Linux вимірює відносне відхилення частоти у спеціальному масштабованому форматі з фіксованою комою: одиниця відповідає `1 / 65 536` частці на мільйон (`2⁻¹⁶ ppm`). 

Такий вибір формату зумовлений прагненням розробників ядра уникнути використання операцій з плаваючою комою (floating-point arithmetic) у просторі ядра. Всі розрахунки фази виконуються за допомогою 64-бітних цілочисельних операцій множення та бітового зсуву.

Формула прямого перетворення відносного відхилення частоти `y` (у ppm) у цілочисельне значення для ядра `tx.freq`:

```
tx.freq = (long)(y_ppm · 65536.0)      [масштабування у формат 16 бітів дробу]
```

*Приклади перерахунку величин:*
* Відхилення `+1.0 ppm` відповідає значенню `tx.freq = 65536`.
* Відхилення `-11.574074 ppm` (середнє уповільнення при 24-годинному лінійному розмазуванні) відповідає значенню `tx.freq = -758514`.
* Пікове відхилення `-23.148148 ppm` (опівнічний максимум косинусного розмазування) відповідає значенню `tx.freq = -1517028`.
* Максимально допустиме коригування частоти в ядрі Linux становить `±500 ppm`, що обмежує поле `tx.freq` діапазоном `[-32 768 000, +32 768 000]`.

---

### Принцип побудови циклу регулювання демона розмазування

Для реалізації процесу розмазування користувацький демон повинен забезпечити виконання замкненого циклу керування (Control Loop):

1. **Вибір опорного годинника для внутрішнього таймінгу:**
   Демон розмазування в жодному разі не повинен використовувати `CLOCK_REALTIME` для вимірювання власного прогресу, оскільки зміна частоти `CLOCK_REALTIME` спотворювала б розрахунок пройденого часу. Замість цього демон використовує монотонний годинник `CLOCK_MONOTONIC` (або `std::chrono::steady_clock` у C++), чий темп не залежить від коригувань цивільного часу.

2. **Запобігання накопиченню похибки сну (Loop Drift Prevention):**
   Використання відносних функцій затримки (таких як `usleep()` або `sleep_for()`) є неприпустимим у високоточних системах керування. Якщо на виконання обчислень та системного виклику витрачається `100 мкс`, а пауза становить `500 мс`, фактичний період ітерації становитиме `500.1 мс`. За добу роботи накопичена похибка перевищить кілька секунд.
   
   Для усунення цього ефекту застосовується абсолютний сон через виклик `clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_wakeup, NULL)`. Демон на кожному кроці додає `500 мс` до цільового абсолютного часу пробудження, що повністю виключає накопичення дрейфу.

3. **Періодичний розрахунок поточної поправки частоти:**
   Демон розбиває загальне 24-годинне вікно розмазування на дискретні інтервали (наприклад, по 500 мілісекунд). На кожній ітерації обчислюється час, що минув від початку вікна `t'`, після чого за аналітичною формулою (лінійною або косинусною) розраховується миттєве значення необхідної поправки `y(t')`.

4. **Атомарне оновлення частоти ядра:**
   Отримане значення `y(t')` перераховується у формат `2⁻¹⁶ ppm` і передається в ядро через виклик `adjtimex(&tx)` із маскою `ADJ_FREQUENCY`.

5. **Гарантоване відновлення номінальної частоти при зупинці:**
   Якщо процес демона буде аварійно перервано користувачем (сигнал `SIGINT` / `Ctrl+C`) або системною службою (`SIGTERM`), ядро залишить генератор у стані уповільненого ходу. Щоб запобігти хронічному відставанню годинника, демон обов'язково повинен містити обробник завершення або RAII-клас, який повертає зміщення частоти `tx.freq` у нульове значення `0`.

---

### Підтримка часових шкал у C++20 (`std::chrono`)

Стандарт C++20 суттєво розширив бібліотеку `<chrono>`, додавши пряму підтримку різних метрологічних шкал часу:

* `std::chrono::system_clock`: системний цивільний час Unix (`sys_time`), що вимірює тривалість без високосних секунд (стандарт POSIX).
* `std::chrono::utc_clock`: офіційна шкала `utc_time`, яка враховує високосні секунди за допомогою вбудованої бази даних IERS (`std::chrono::get_leap_second_info`).
* `std::chrono::tai_clock`: неперервний атомний час `tai_time`, зсунутий відносно UTC на поточну кількість високосних секунд (+37 с).
* `std::chrono::gps_clock`: час супутникової системи GPS `gps_time` (+18 с відносно UTC).

Стандартна бібліотека C++20 надає функцію `std::chrono::clock_cast`, яка виконує коректне перетворення міток часу між цими шкалами:

```cpp
auto utc_now = std::chrono::utc_clock::now();
auto sys_now = std::chrono::clock_cast<std::chrono::system_clock>(utc_now);
auto tai_now = std::chrono::clock_cast<std::chrono::tai_clock>(utc_now);
```

Під час настання секунди `23:59:60 UTC` годинник `std::chrono::utc_clock` повертає коректний час 61-ї секунди, тоді як `std::chrono::system_clock` відтворює повтор таймштампу відповідно до стандарту POSIX.

---

### Реалізація розмазування: C та C++20

Нижче наведено повністю робочий програмний комплекс, який демонструє реалізацію демона розмазування двома мовами програмування з використанням абсолютної монотонної дискретизації.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <sys/timex.h>

#define SECONDS_PER_DAY 86400.0
#define PI 3.14159265358979323846
#define LOOP_INTERVAL_NS 500000000L // 500 мілісекунд

static volatile sig_atomic_t g_running = 1;

// Обробник сигналів завершення для безпечного виходу
static void handle_signal(int sig) {
    (void)sig;
    g_running = 0;
}

// Повернення зміщення частоти ядра в 0
static void reset_frequency(void) {
    struct timex tx;
    memset(&tx, 0, sizeof(tx));
    tx.modes = ADJ_FREQUENCY;
    tx.freq = 0;
    if (adjtimex(&tx) < 0) {
        perror("Помилка скидання частоти в adjtimex");
    } else {
        printf("\n[Система] Частоту годинника успішно відновлено до номіналу.\n");
    }
}

// Розрахунок поточної поправки частоти в ppm
static double compute_smear_ppm(double elapsed_sec, double total_window_sec, 
                                double leap_sec, bool use_cosine) {
    if (elapsed_sec < 0.0 || elapsed_sec >= total_window_sec) {
        return 0.0;
    }
    if (!use_cosine) {
        // Лінійний профіль: y = - ΔΦ / T
        return - (leap_sec / total_window_sec) * 1e6;
    } else {
        // Косинусний профіль: y = - (ΔΦ / T) * (1 - cos(2*pi*t / T))
        double factor = 1.0 - cos(2.0 * PI * elapsed_sec / total_window_sec);
        return - (leap_sec / total_window_sec) * factor * 1e6;
    }
}

int main(int argc, char **argv) {
    bool use_cosine = true;
    double duration_sec = 86400.0; // 24 години
    double leap_sec = 1.0;         // +1 секунда

    if (argc > 1 && strcmp(argv[1], "--linear") == 0) {
        use_cosine = false;
    }

    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = handle_signal;
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);

    printf("=== Демон розмазування високосної секунди (Linux C) ===\n");
    printf("Профіль: %s\n", use_cosine ? "Гладкий піднесений косинус (Google Smooth)" : "Лінійний (Linear)");
    printf("Тривалість вікна: %.0f секунд (24 год)\n", duration_sec);
    printf("Величина корекції: %+.1f с\n\n", leap_sec);

    struct timespec start_ts, next_wakeup;
    clock_gettime(CLOCK_MONOTONIC, &start_ts);
    next_wakeup = start_ts;

    while (g_running) {
        struct timespec now_ts;
        clock_gettime(CLOCK_MONOTONIC, &now_ts);

        double elapsed = (double)(now_ts.tv_sec - start_ts.tv_sec) +
                         (double)(now_ts.tv_nsec - start_ts.tv_nsec) * 1e-9;

        if (elapsed >= duration_sec) {
            printf("\nВікно розмазування повністю вичерпано.\n");
            break;
        }

        double ppm = compute_smear_ppm(elapsed, duration_sec, leap_sec, use_cosine);
        long raw_freq = (long)(ppm * 65536.0);

        struct timex tx;
        memset(&tx, 0, sizeof(tx));
        tx.modes = ADJ_FREQUENCY;
        tx.freq = raw_freq;

        if (adjtimex(&tx) < 0) {
            if (errno == EPERM) {
                fprintf(stderr, "Помилка: потрібні права CAP_SYS_TIME (sudo) для керування частотою ядра!\n");
                return EXIT_FAILURE;
            }
            perror("Помилка виклику adjtimex");
            break;
        }

        printf("\rЧас: %6.1f с / %6.0f с | Поправка: %8.4f ppm (raw: %10ld) | Статус: 0x%04x",
               elapsed, duration_sec, ppm, raw_freq, tx.status);
        fflush(stdout);

        // Розраховуємо абсолютний час наступного пробудження без дрейфу
        next_wakeup.tv_nsec += LOOP_INTERVAL_NS;
        if (next_wakeup.tv_nsec >= 1000000000L) {
            next_wakeup.tv_sec += 1;
            next_wakeup.tv_nsec -= 1000000000L;
        }
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_wakeup, NULL);
    }

    reset_frequency();
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <chrono>
#include <cmath>
#include <numbers>
#include <memory>
#include <expected>
#include <string_view>
#include <thread>
#include <csignal>
#include <cstring>
#include <sys/timex.h>

namespace time_sync {

using namespace std::chrono_literals;

enum class SmearProfile {
    Linear,
    Cosine
};

// RAII-клас керування дисципліною годинника ядра
class ClockDiscipliner {
public:
    ClockDiscipliner() = default;
    
    // Деструктор гарантовано відновлює номінальну частоту при будь-якому виході
    ~ClockDiscipliner() {
        (void)restore_nominal_frequency();
    }

    // Заборона копіювання для збереження інваріанту єдиного керування генератором
    ClockDiscipliner(const ClockDiscipliner&) = delete;
    ClockDiscipliner& operator=(const ClockDiscipliner&) = delete;
    ClockDiscipliner(ClockDiscipliner&&) noexcept = default;
    ClockDiscipliner& operator=(ClockDiscipliner&&) noexcept = default;

    [[nodiscard]] std::expected<void, std::string_view> set_frequency_ppm(double ppm) const noexcept {
        struct timex tx{};
        tx.modes = ADJ_FREQUENCY;
        // Масштабування ppm у внутрішній 16-бітний дріб ядра Linux (1/65536 ppm)
        tx.freq = static_cast<long>(ppm * 65536.0);

        if (::adjtimex(&tx) < 0) {
            if (errno == EPERM) {
                return std::unexpected("Недостатньо привілеїв процесу (потрібен CAP_SYS_TIME)");
            }
            return std::unexpected("Системний збій виклику adjtimex");
        }
        return {};
    }

    [[nodiscard]] std::expected<void, std::string_view> restore_nominal_frequency() const noexcept {
        return set_frequency_ppm(0.0);
    }
};

// Обчислювач поправок розмазування
class LeapSmearEngine {
public:
    LeapSmearEngine(std::chrono::seconds window_duration, 
                    std::chrono::seconds leap_offset,
                    SmearProfile profile) noexcept
        : window_duration_{window_duration},
          leap_offset_{leap_offset},
          profile_{profile} {}

    [[nodiscard]] double calculate_offset_ppm(std::chrono::duration<double> elapsed) const noexcept {
        const double t = elapsed.count();
        const double total = static_cast<double>(window_duration_.count());
        const double delta = static_cast<double>(leap_offset_.count());

        if (t < 0.0 || t >= total) {
            return 0.0;
        }

        if (profile_ == SmearProfile::Linear) {
            // Постійне зміщення: - ΔΦ / T * 1e6
            return -(delta / total) * 1e6;
        } else {
            // Косинусний піднесений профіль: - (ΔΦ / T) * (1 - cos(2*pi*t / T)) * 1e6
            const double factor = 1.0 - std::cos(2.0 * std::numbers::pi * t / total);
            return -(delta / total) * factor * 1e6;
        }
    }

private:
    std::chrono::seconds window_duration_;
    std::chrono::seconds leap_offset_;
    SmearProfile profile_;
};

} // namespace time_sync

static volatile std::sig_atomic_t g_stop_signal = 0;

int main(int argc, char** argv) {
    std::signal(SIGINT, [](int) { g_stop_signal = 1; });
    std::signal(SIGTERM, [](int) { g_stop_signal = 1; });

    const auto profile = (argc > 1 && std::string_view(argv[1]) == "--linear")
                         ? time_sync::SmearProfile::Linear
                         : time_sync::SmearProfile::Cosine;

    std::cout << "=== Демон розмазування високосної секунди (Linux C++20) ===\n"
              << "Профіль: " << (profile == time_sync::SmearProfile::Cosine ? "Smooth Cosine" : "Linear") << "\n"
              << "Ініціалізація RAII-керування частотою ядра...\n";

    time_sync::ClockDiscipliner discipliner;
    time_sync::LeapSmearEngine engine(24h, 1s, profile);

    const auto start_time = std::chrono::steady_clock::now();
    const auto total_window = 24h;
    auto next_wakeup = start_time;

    while (!g_stop_signal) {
        const auto now = std::chrono::steady_clock::now();
        const std::chrono::duration<double> elapsed = now - start_time;

        if (elapsed >= total_window) {
            std::cout << "\nВікно розмазування успішно завершено.\n";
            break;
        }

        const double current_ppm = engine.calculate_offset_ppm(elapsed);
        auto result = discipliner.set_frequency_ppm(current_ppm);

        if (!result) {
            std::cerr << "\nПомилка: " << result.error() << "\n";
            return EXIT_FAILURE;
        }

        std::cout << "\rПрогрес: " << std::fixed << std::chrono::duration_cast<std::chrono::seconds>(elapsed).count()
                  << " с | Поправка: " << current_ppm << " ppm" << std::flush;

        next_wakeup += 500ms;
        std::this_thread::sleep_until(next_wakeup);
    }

    std::cout << "\nЗупинка демона. Автоматичне відновлення частоти через деструктор...\n";
    return EXIT_SUCCESS;
}
```
:::

---

### Практичні аспекти експлуатації та підводні камені

Під час розгортання та тестування систем програмного дисциплінування годинника в промислових серверах Linux необхідно враховувати низку важливих факторів:

1. **Конфлікти з системними службами часу (`chronyd`, `systemd-timesyncd`, `ntpd`):**
   Стандартні системні демони часу постійно виконують власний цикл фільтрації фази та частоти. Якщо в системі одночасно працює `chronyd` та сторонній скрипт керування частотою, вони будуть перетирати значення `tx.freq` один одного під час кожного тіка, що призведе до хаотичних стрибків частоти та повної втрати синхронізації. Перед запуском прямого керування частотою системні служби повинні бути зупинені (`systemctl stop chronyd`), або демон Chrony має бути налаштований на отримання розмазаного часу від зовнішнього сервера з опцією `leapsecmode slew`.

2. **Привілеї процесу та права POSIX Capabilities:**
   Системний виклик `adjtimex` із ненульовим полем `modes` дозволено виконувати лише процесам, що мають системні привілеї суперкористувача (`root`) або спеціальний біт привілеїв `CAP_SYS_TIME`. Запуск від непривілейованого користувача негайно повертає помилку `-1` із кодом `errno = EPERM` (Operation not permitted). Для надання бінарному файлу необхідних прав без запуску з-під root використовується команда:
   ```bash
   sudo setcap cap_sys_time+ep ./leap_smear_daemon
   ```

3. **Вплив віртуалізації (KVM, Hyper-V, AWS Nitro):**
   У віртуалізованих середовищах годинник гостьової операційної системи часто прив'язаний до гіпервізора через паравіртуальні драйвери (`kvm-clock` або `xen-clocksource`). Зміна частоти гостьового ядра через `adjtimex` може частково компенсуватися механізмами корекції гіпервізора. У хмарних інфраструктурах надійніше використовувати вбудовані джерела часу провайдера (наприклад, AWS Time Sync Service `169.254.169.123`), які виконують розмазування безпосередньо на апаратному рівні шасі або DPU-контролера (Nitro/SmartNIC).

4. **Емуляція та тестування профілів:**
   Для перевірки реакції прикладних додатків на високосну секунду в лабораторних умовах не обов'язково чекати 24 години реального часу. Програму можна запустити з параметром тривалості вікна `duration_sec = 60.0`, що дозволяє простежити повний цикл зміни частоти від `0` до `-23.15 ppm` і назад до `0` всього за одну хвилину, контролюючи монотонність міток часу в логах сервісів.

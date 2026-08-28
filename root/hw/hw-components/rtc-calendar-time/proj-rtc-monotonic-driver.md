# ⚙️ Драйвер конфігурації RTC, цифрового калібрування та монотонного часу

Надійний облік часу у вбудованих системах вимагає одночасного розв'язання двох протилежних завдань: прецизійного перетворення апаратних двійково-десяткових регістрів (BCD) у 64-бітні епохальні мітки UNIX, розрахунку регістрів плавного цифрового калібрування (Smooth Digital Calibration) та синтезу гарантовано монотонного годинника для захисту від стрибків часу назад при зовнішній синхронізації через NTP або GNSS.

---

### Архітектурні виклики та системні вимоги

Вбудована система, що працює у розподіленій мережі промислової автоматизації, IoT або медичного моніторингу, одночасно вирішує два фундаментально різні хронометричні завдання:

1. **Календарний астрономічний час (Wall-Clock / Realtime):**
   Абсолютна прив'язка до всесвітньої шкали координованого часу UTC (рік, місяць, число, години, хвилини, секунди, мікросекунди). Цей час використовується виключно для людино-машинного інтерфейсу, формування криптографічних сертифікатів, запису подій у локальні журнали та маркування телеметричних пакетів для хмарних баз даних. Календарний час може стрибати вперед або назад у результаті синхронізації з NTP-сервером чи супутниковим GNSS-приймачем, а також коригуватися при зміні часових поясів.

2. **Монотонний інтервальний час (Monotonic Clock):**
   Строго неспадна, безперервна фізична шкала відліку тривалості (де завжди Δt ≥ 0). Будь-який внутрішній алгоритм — періодичне опитування сенсорів, розрахунок похідних та інтегралів у ПІД-регуляторах приводів, відліки мережевих тайм-аутів і дедлайнів RTOS — повинен опиратися лише на монотонний годинник. Якщо цикл керування розрахує крок дискретизації за різницею календарного часу, що раптово стрибнув назад на 5 секунд через NTP-корекцію, різниця Δt виявиться від'ємною або спричинить переповнення беззнакового 64-бітного цілого (uint64_t underflow) у гігантське число 18.4 квінтильйона мікросекунд. Це призведе до миттєвого зависання таймерів, зриву контуру стабілізації та аварійного відключення системи.

Для подолання цього протиріччя драйвер розділено на три функціональні рівні:
- Рівень апаратного доступу до RTC: атомарне зчитування BCD-регістрів та субсекундного лічильника згладжування (`SSR`);
- Рівень цифрового калібрування: синтез конфігураційних бітів `CALP` та `CALM` за виміряним температурним або статичним зміщенням частоти;
- Рівень диспетчера подвійного часу (Dual-Time Manager): формування неспадної монотонної шкали та динамічного зміщення календаря (`wall_offset`).

---

### Послідовність ініціалізації та розблокування захисту RTC

Вбудовані апаратні модулі RTC захищені від випадкової модифікації регістрів у разі збоїв пам'яті чи зависання вказівників програми спеціальними послідовностями розблокування (Write Protection Keys):
1. **Зняття захисту від запису:** запис фіксованої послідовності байтів (наприклад, ключі `0xCA` та `0x53` у регістр захисту `RTC_WPR`).
2. **Вхід у режим ініціалізації:** встановлення біта `INIT` у регістрі `RTC_ISR` та очікування апаратного прапорця готовності `INITF = 1`. У цьому режимі тактування лічильників календаря зупиняється для безпечного запису коефіцієнтів дільників.
3. **Налаштування прескалерів:** запис коефіцієнтів дільників у регістр `RTC_PRER`. Спочатку налаштовується 7-бітний асинхронний дільник `PREDIV_A = 127` (коефіцієнт ділення 128), який знижує частоту з 32768 Гц до 256 Гц для мінімізації динамічного споживання. Потім налаштовується 15-бітний синхронний дільник `PREDIV_S = 255` (коефіцієнт ділення 256), що виробляє фінальний строб 1.000000 Гц.
4. **Вихід із режиму ініціалізації:** скидання біта `INIT` та відновлення захисту від запису для переходу лічильників у робочий режим.

---

### Реалізація драйвера на мовах C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Структура представлення календарної дати та часу */
typedef struct {
    uint16_t year;                  /* 1970..2099 */
    uint8_t  month;                 /* 1..12 */
    uint8_t  day;                   /* 1..31 */
    uint8_t  hours;                 /* 0..23 */
    uint8_t  minutes;               /* 0..59 */
    uint8_t  seconds;               /* 0..59 */
    uint32_t subseconds_raw;        /* Поточне значення SSR лічильника (наприклад, 255..0) */
    uint32_t prediv_s_value;        /* Встановлений коефіцієнт PREDIV_S (наприклад, 255) */
    uint32_t subsecond_fraction_us; /* Розрахована частка секунди в мікросекундах (0..999999) */
} rtc_datetime_t;

/* Структура результату розрахунку плавного калібрування */
typedef struct {
    bool     calp;                  /* true = додати +512 тактів (+488.28 ppm) */
    uint16_t calm;                  /* маскування 0..511 тактів (0.9537 ppm на крок) */
    float    residual_ppm;          /* залишкове нескомпенсоване відхилення */
} rtc_calibration_t;

/* Стан монотонного диспетчера часу */
typedef struct {
    uint64_t last_monotonic_us;     /* Останнє видане монотонне значення */
    int64_t  wall_clock_offset_us;  /* Зсув календаря відносно монотонної шкали */
    bool     initialized;
} monotonic_time_manager_t;

/* Швидкі побітові перетворення двійково-десяткового коду (BCD) */
static inline uint8_t bcd_to_bin(uint8_t bcd) {
    return (uint8_t)(((bcd >> 4) * 10) + (bcd & 0x0F));
}

static inline uint8_t bin_to_bcd(uint8_t bin) {
    return (uint8_t)(((bin / 10) << 4) | (bin % 10));
}

/* Перевірка високосного року */
static inline bool is_leap_year(uint16_t year) {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

/* Кількість днів від початку року до початку кожного місяця */
static const uint16_t days_before_month[13] = {
    0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* Розрахунок субсекундної мікросекундної частки з регістра SSR.
 * Оскільки лічильник SSR рахує вниз від PREDIV_S до 0, минула частка секунди
 * обчислюється як: (PREDIV_S - SSR) / (PREDIV_S + 1)
 */
uint32_t rtc_calculate_subsecond_us(uint32_t ssr_raw, uint32_t prediv_s) {
    if (prediv_s == 0) return 0;
    if (ssr_raw > prediv_s) ssr_raw = prediv_s;
    
    uint64_t elapsed_ticks = (uint64_t)(prediv_s - ssr_raw);
    uint64_t fraction_us = (elapsed_ticks * 1000000ULL) / (uint64_t)(prediv_s + 1);
    return (uint32_t)fraction_us;
}

/* Розрахунок параметрів плавного калібрування (Smooth Calibration)
 * measured_ppm: виміряне відхилення (+ якщо кварц поспішає, - якщо відстає)
 */
bool rtc_calculate_smooth_calibration(float measured_ppm, rtc_calibration_t *out_cal) {
    if (!out_cal) return false;

    const float STEP_PPM = 0.953674316f; /* 1 / 2^20 */
    const float CALP_PPM = 488.28125f;   /* +512 тактів */

    if (measured_ppm > 487.32f || measured_ppm < -488.28f) {
        return false; /* Поза апаратним діапазоном калібрування */
    }

    if (measured_ppm >= 0.0f) {
        /* Кварц поспішає: вилучаємо імпульси через CALM */
        out_cal->calp = false;
        int32_t calm_val = (int32_t)((measured_ppm / STEP_PPM) + 0.5f);
        if (calm_val > 511) calm_val = 511;
        out_cal->calm = (uint16_t)calm_val;
        out_cal->residual_ppm = measured_ppm - ((float)calm_val * STEP_PPM);
    } else {
        /* Кварц відстає: вмикаємо CALP (+488.28 ppm) та коригуємо CALM */
        out_cal->calp = true;
        float target_reduction = CALP_PPM - (-measured_ppm);
        int32_t calm_val = (int32_t)((target_reduction / STEP_PPM) + 0.5f);
        if (calm_val < 0) calm_val = 0;
        if (calm_val > 511) calm_val = 511;
        out_cal->calm = (uint16_t)calm_val;
        out_cal->residual_ppm = measured_ppm - (CALP_PPM - ((float)calm_val * STEP_PPM));
    }

    return true;
}

/* Перетворення календарної структури у 64-бітну епоху UNIX (мікросекунди) */
uint64_t rtc_datetime_to_unix_us(const rtc_datetime_t *dt) {
    if (!dt || dt->year < 1970 || dt->month < 1 || dt->month > 12) {
        return 0;
    }

    /* 1. Кількість повних днів від 1 січня 1970 року */
    uint32_t days = 0;
    for (uint16_t y = 1970; y < dt->year; y++) {
        days += is_leap_year(y) ? 366 : 365;
    }

    days += days_before_month[dt->month];
    if (dt->month > 2 && is_leap_year(dt->year)) {
        days += 1;
    }
    days += (dt->day - 1);

    /* 2. Загальна кількість секунд */
    uint64_t total_seconds = ((uint64_t)days * 86400ULL) +
                             ((uint64_t)dt->hours * 3600ULL) +
                             ((uint64_t)dt->minutes * 60ULL) +
                             (uint64_t)dt->seconds;

    /* 3. Додавання субсекундної частки */
    return (total_seconds * 1000000ULL) + (uint64_t)dt->subsecond_fraction_us;
}

/* Ініціалізація диспетчера монотонного часу */
void monotonic_manager_init(monotonic_time_manager_t *mgr, uint64_t initial_wall_us, uint64_t initial_hw_ticks_us) {
    if (!mgr) return;
    mgr->last_monotonic_us = initial_hw_ticks_us;
    mgr->wall_clock_offset_us = (int64_t)initial_wall_us - (int64_t)initial_hw_ticks_us;
    mgr->initialized = true;
}

/* Отримання гарантовано монотонного часу (неспадна шкала) */
uint64_t monotonic_get_time_us(monotonic_time_manager_t *mgr, uint64_t raw_hw_ticks_us) {
    if (!mgr || !mgr->initialized) return 0;

    /* Якщо апаратний таймер переповнився або дав збій, фіксуємо останнє значення */
    if (raw_hw_ticks_us > mgr->last_monotonic_us) {
        mgr->last_monotonic_us = raw_hw_ticks_us;
    }
    return mgr->last_monotonic_us;
}

/* Отримання календарного часу */
uint64_t wall_clock_get_time_us(monotonic_time_manager_t *mgr, uint64_t raw_hw_ticks_us) {
    uint64_t mono = monotonic_get_time_us(mgr, raw_hw_ticks_us);
    int64_t wall = (int64_t)mono + mgr->wall_clock_offset_us;
    return wall > 0 ? (uint64_t)wall : 0;
}

/* Синхронізація часу через NTP/GNSS (оновлює зміщення без зламу монотонності) */
void wall_clock_synchronize_ntp(monotonic_time_manager_t *mgr, uint64_t raw_hw_ticks_us, uint64_t ntp_wall_us) {
    if (!mgr) return;
    uint64_t mono = monotonic_get_time_us(mgr, raw_hw_ticks_us);
    /* Оновлюємо offset: монотонна шкала не зазнає стрибка */
    mgr->wall_clock_offset_us = (int64_t)ntp_wall_us - (int64_t)mono;
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <expected>
#include <array>
#include <cmath>

namespace rtc {

using namespace std::chrono_literals;

/* Типізована структура календарного часу */
struct DateTime {
    uint16_t year{2026};        // 1970..2099
    uint8_t  month{1};          // 1..12
    uint8_t  day{1};            // 1..31
    uint8_t  hours{0};          // 0..23
    uint8_t  minutes{0};        // 0..59
    uint8_t  seconds{0};        // 0..59
    uint32_t subsecond_us{0};   // 0..999999

    [[nodiscard]] constexpr bool is_valid() const noexcept {
        if (year < 1970 || month < 1 || month > 12 || day < 1 || day > 31) return false;
        if (hours > 23 || minutes > 59 || seconds > 59 || subsecond_us >= 1'000'000) return false;
        return true;
    }
};

/* Параметри цифрового згладжувального калібрування */
struct CalibrationParams {
    bool     calp{false};       // true = вставка +512 тактів
    uint16_t calm{0};           // маскування 0..511 тактів
    float    residual_ppm{0.0f};// залишкова похибка
};

enum class CalibrationError {
    OutOfRange,
    InvalidInput
};

/* Функції перетворення BCD */
[[nodiscard]] constexpr uint8_t bcd_to_bin(uint8_t bcd) noexcept {
    return static_cast<uint8_t>(((bcd >> 4) * 10) + (bcd & 0x0F));
}

[[nodiscard]] constexpr uint8_t bin_to_bcd(uint8_t bin) noexcept {
    return static_cast<uint8_t>(((bin / 10) << 4) | (bin % 10));
}

[[nodiscard]] constexpr bool is_leap_year(uint16_t year) noexcept {
    return ((year % 4 == 0) && (year % 100 != 0)) || (year % 400 == 0);
}

constexpr std::array<uint16_t, 13> days_before_month = {
    0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334
};

/* Розрахунок субсекундної частки в мікросекундах */
[[nodiscard]] constexpr uint32_t calculate_subsecond_us(uint32_t ssr_raw, uint32_t prediv_s) noexcept {
    if (prediv_s == 0) return 0;
    if (ssr_raw > prediv_s) ssr_raw = prediv_s;
    const uint64_t elapsed_ticks = prediv_s - ssr_raw;
    return static_cast<uint32_t>((elapsed_ticks * 1'000'000ULL) / (prediv_s + 1));
}

/* Розрахунок параметрів плавного калібрування */
[[nodiscard]] constexpr std::expected<CalibrationParams, CalibrationError>
calculate_smooth_calibration(float measured_ppm) noexcept {
    constexpr float STEP_PPM = 0.953674316f;
    constexpr float CALP_PPM = 488.28125f;

    if (measured_ppm > 487.32f || measured_ppm < -488.28f) {
        return std::unexpected(CalibrationError::OutOfRange);
    }

    CalibrationParams params{};
    if (measured_ppm >= 0.0f) {
        params.calp = false;
        auto calm_val = static_cast<int32_t>((measured_ppm / STEP_PPM) + 0.5f);
        if (calm_val > 511) calm_val = 511;
        params.calm = static_cast<uint16_t>(calm_val);
        params.residual_ppm = measured_ppm - (static_cast<float>(calm_val) * STEP_PPM);
    } else {
        params.calp = true;
        float target_reduction = CALP_PPM - (-measured_ppm);
        auto calm_val = static_cast<int32_t>((target_reduction / STEP_PPM) + 0.5f);
        if (calm_val < 0) calm_val = 0;
        if (calm_val > 511) calm_val = 511;
        params.calm = static_cast<uint16_t>(calm_val);
        params.residual_ppm = measured_ppm - (CALP_PPM - (static_cast<float>(calm_val) * STEP_PPM));
    }

    return params;
}

/* Конвертація DateTime у std::chrono::microseconds (UNIX epoch) */
[[nodiscard]] constexpr std::chrono::microseconds to_unix_epoch(const DateTime& dt) noexcept {
    if (!dt.is_valid()) return 0us;

    uint32_t days = 0;
    for (uint16_t y = 1970; y < dt.year; ++y) {
        days += is_leap_year(y) ? 366 : 365;
    }

    days += days_before_month[dt.month];
    if (dt.month > 2 && is_leap_year(dt.year)) {
        days += 1;
    }
    days += (dt.day - 1);

    auto total_sec = std::chrono::seconds(
        (static_cast<uint64_t>(days) * 86400ULL) +
        (static_cast<uint64_t>(dt.hours) * 3600ULL) +
        (static_cast<uint64_t>(dt.minutes) * 60ULL) +
        static_cast<uint64_t>(dt.seconds)
    );

    return std::chrono::duration_cast<std::chrono::microseconds>(total_sec) +
           std::chrono::microseconds(dt.subsecond_us);
}

/* Безпечний диспетчер подвійного часу (Монотонний + Календарний) */
class DualTimeManager {
public:
    constexpr DualTimeManager(std::chrono::microseconds initial_wall,
                              std::chrono::microseconds initial_hw_ticks) noexcept
        : last_monotonic_(initial_hw_ticks),
          wall_offset_(initial_wall - initial_hw_ticks) {}

    /* Отримання гарантовано монотонного часу (ніколи не повертається назад) */
    [[nodiscard]] std::chrono::microseconds get_monotonic(std::chrono::microseconds raw_hw_ticks) noexcept {
        if (raw_hw_ticks > last_monotonic_) {
            last_monotonic_ = raw_hw_ticks;
        }
        return last_monotonic_;
    }

    /* Отримання календарного часу */
    [[nodiscard]] std::chrono::microseconds get_wall_time(std::chrono::microseconds raw_hw_ticks) noexcept {
        const auto mono = get_monotonic(raw_hw_ticks);
        const auto wall = mono + wall_offset_;
        return wall.count() > 0 ? wall : 0us;
    }

    /* Оновлення часу від NTP без збоїв інтервального вимірювання */
    void synchronize_ntp(std::chrono::microseconds raw_hw_ticks,
                         std::chrono::microseconds ntp_wall) noexcept {
        const auto mono = get_monotonic(raw_hw_ticks);
        wall_offset_ = ntp_wall - mono;
    }

private:
    std::chrono::microseconds last_monotonic_{0us};
    std::chrono::microseconds wall_offset_{0us};
};

} // namespace rtc
```
:::

---

### Детальний аналіз крайових випадків та перегонів даних

#### 1. Атомарне зчитування субсекундних регістрів (SSR) та календаря
У мікроконтролерах лічильник субсекунд `SSR` рахує назад від значення `PREDIV_S` (наприклад, 255) до 0 на частоті 256 Гц, а регістр секунд перемикається по переповненню `SSR` на частоті 1 Гц. Якщо процесор зчитує регістр календаря `RTC_TR`, а наступною інструкцією — регістр субсекунд `RTC_SSR`, існує ймовірність, що перехід секунди відбувся саме між цими двома командами. У такому випадку програма отримає секунди з попередньої секунди (наприклад, `12:00:00`), а субсекунди — з нової секунди (`SSR = 255`, що відповідає `0.000` с). У результаті розрахований час стрибне майже на цілу секунду вперед, а при наступному опитуванні — повернеться назад.

**Стратегія захисту:**
- Використання подвійного зчитування: зчитати `SSR1`, потім `RTC_TR`, потім `SSR2`. Якщо `SSR1 < SSR2`, стався перехід секунди, і читання слід повторити;
- Або використання апаратного біта синхронізації `RSF` (Registers Synchronization Flag), який сигналізує про завершення копіювання лічильників у тіньові регістри.

#### 2. Плавне підтягування часу (Slewing) проти миттєвого стрибка (Stepping)
Коли зовнішня служба часу (NTP або GPS) повідомляє про розбіжність годинника:
- **Якщо похибка мала (|Δt| < 128 мс):** застосовується алгоритм плавного підтягування (Slewing). Замість миттєвої зміни лічильника програма тимчасово модифікує регістр калібрування RTC на ±500 ppm, прискорюючи або сповільнюючи хід годинника на 0.5 мілісекунди щосекунди до повного вирівнювання фази. Календарний час плавно наближається до еталону без жодних стрибків і розривів похідних.
- **Якщо похибка велика (|Δt| ≥ 128 мс):** застосовується ступінчаста корекція (Step Adjustment). Диспетчер часу миттєво оновлює `wall_clock_offset_us`, не торкаючись значення монотонного лічильника. Усі активні таймери та розрахунки тривалостей продовжують коректно функціонувати без збоїв.

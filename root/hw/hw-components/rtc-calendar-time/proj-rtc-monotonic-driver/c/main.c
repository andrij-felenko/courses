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

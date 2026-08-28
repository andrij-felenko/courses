/* ============================================================================
 * recurrence_engine.h / recurrence_engine.c (C99)
 * Високопродуктивний рушій обчислення рекурентності без виділення купи.
 * ========================================================================== */
#include <stdint.h>
#include <stdbool.h>
#include <time.h>

#if defined(_MSC_VER)
#  include <intrin.h>
   static inline int ctz64(uint64_t mask) {
       unsigned long idx;
       _BitScanForward64(&idx, mask);
       return (int)idx;
   }
#else
   static inline int ctz64(uint64_t mask) {
       return __builtin_ctzll(mask);
   }
#endif

/* Структура бітового розбору CRON */
typedef struct {
    uint64_t sec_mask;   /* Біти 0..59 */
    uint64_t min_mask;   /* Біти 0..59 */
    uint32_t hour_mask;  /* Біти 0..23 */
    uint32_t dom_mask;   /* Біти 1..31 (біт 0 не використовується) */
    uint16_t mon_mask;   /* Біти 1..12 (біт 0 не використовується) */
    uint8_t  dow_mask;   /* Біти 0..6 (0 = Неділя, 1 = Понеділок... 6 = Субота) */
    bool     dom_is_star;
    bool     dow_is_star;
} cron_schedule_t;

/* Календарна дата */
typedef struct {
    int32_t year;
    int8_t  month;   /* 1..12 */
    int8_t  day;     /* 1..31 */
    int8_t  hour;    /* 0..23 */
    int8_t  minute;  /* 0..59 */
    int8_t  second;  /* 0..59 */
} civil_datetime_t;

/* Чи є рік високосним за григоріанським календарем */
static inline bool is_leap_year(int32_t y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

/* Кількість днів у місяці */
static inline int days_in_month(int32_t y, int m) {
    static const int8_t kDays[13] = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2 && is_leap_year(y)) return 29;
    return kDays[m];
}

/* Переведення (Y, M, D) у кількість днів від 1970-01-01 (Алгоритм Говарда Хіннанта) */
static inline int64_t days_from_civil(int32_t y, int m, int d) {
    y -= (m <= 2) ? 1 : 0;
    const int64_t era = (y >= 0 ? y : y - 399) / 400;
    const uint32_t yoe = (uint32_t)(y - era * 400);
    const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + (uint32_t)(d - 1);
    const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (int64_t)doe - 719468;
}

/* Переведення кількості днів від 1970-01-01 у (Y, M, D) */
static inline void civil_from_days(int64_t z, int32_t *out_y, int8_t *out_m, int8_t *out_d) {
    z += 719468;
    const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const uint32_t doe = (uint32_t)(z - era * 146097);
    const uint32_t yoe = (doe - doe / 1020 + doe / 1460 - doe / 146096) / 365;
    const int32_t y = (int32_t)yoe + (int32_t)(era * 400);
    const uint32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const uint32_t mp = (5 * doy + 2) / 153;
    const uint32_t d = doy - (153 * mp + 2) / 5 + 1;
    const uint32_t m = mp < 10 ? mp + 3 : mp - 9;
    *out_y = y + (m <= 2 ? 1 : 0);
    *out_m = (int8_t)m;
    *out_d = (int8_t)d;
}

/* День тижня: 0 = Неділя, 1 = Понеділок... 6 = Субота */
static inline int day_of_week(int64_t days_since_epoch) {
    int dow = (int)((days_since_epoch + 4) % 7);
    return dow < 0 ? dow + 7 : dow;
}

/* Обчислення наступного входження CRON */
bool cron_next(const cron_schedule_t *cron, civil_datetime_t *dt) {
    /* Починаємо пошук із наступної секунди */
    dt->second++;
    
    int loop_guard = 0;
    while (loop_guard++ < 5000) {
        /* 1. Перевірка місяця */
        if (!((cron->mon_mask >> dt->month) & 1)) {
            uint64_t mask = cron->mon_mask & ~((1ULL << dt->month) - 1);
            if (mask == 0) {
                dt->year++;
                dt->month = (int8_t)ctz64(cron->mon_mask);
            } else {
                dt->month = (int8_t)ctz64(mask);
            }
            dt->day = 1;
            dt->hour = 0;
            dt->minute = 0;
            dt->second = 0;
            continue;
        }

        /* 2. Перевірка дня місяця та дня тижня */
        int max_d = days_in_month(dt->year, dt->month);
        if (dt->day > max_d) {
            dt->month++;
            if (dt->month > 12) {
                dt->month = 1;
                dt->year++;
            }
            dt->day = 1;
            dt->hour = 0;
            dt->minute = 0;
            dt->second = 0;
            continue;
        }

        int64_t days_epoch = days_from_civil(dt->year, dt->month, dt->day);
        int dow = day_of_week(days_epoch);

        bool dom_match = (cron->dom_mask >> dt->day) & 1;
        bool dow_match = (cron->dow_mask >> dow) & 1;
        bool day_valid;

        if (!cron->dom_is_star && !cron->dow_is_star) {
            day_valid = dom_match || dow_match; /* POSIX OR семантика */
        } else if (!cron->dom_is_star) {
            day_valid = dom_match;
        } else if (!cron->dow_is_star) {
            day_valid = dow_match;
        } else {
            day_valid = true;
        }

        if (!day_valid) {
            dt->day++;
            dt->hour = 0;
            dt->minute = 0;
            dt->second = 0;
            continue;
        }

        /* 3. Перевірка години */
        if (!((cron->hour_mask >> dt->hour) & 1)) {
            uint64_t mask = cron->hour_mask & ~((1ULL << dt->hour) - 1);
            if (mask == 0) {
                dt->day++;
                dt->hour = (int8_t)ctz64(cron->hour_mask);
            } else {
                dt->hour = (int8_t)ctz64(mask);
            }
            dt->minute = 0;
            dt->second = 0;
            continue;
        }

        /* 4. Перевірка хвилини */
        if (!((cron->min_mask >> dt->minute) & 1)) {
            uint64_t mask = cron->min_mask & ~((1ULL << dt->minute) - 1);
            if (mask == 0) {
                dt->hour++;
                dt->minute = (int8_t)ctz64(cron->min_mask);
                if (dt->hour > 23) {
                    dt->hour = 0;
                    dt->day++;
                }
            } else {
                dt->minute = (int8_t)ctz64(mask);
            }
            dt->second = 0;
            continue;
        }

        /* 5. Перевірка секунди */
        if (!((cron->sec_mask >> dt->second) & 1)) {
            uint64_t mask = cron->sec_mask & ~((1ULL << dt->second) - 1);
            if (mask == 0) {
                dt->minute++;
                dt->second = (int8_t)ctz64(cron->sec_mask);
                if (dt->minute > 59) {
                    dt->minute = 0;
                    dt->hour++;
                    if (dt->hour > 23) {
                        dt->hour = 0;
                        dt->day++;
                    }
                }
            } else {
                dt->second = (int8_t)ctz64(mask);
            }
            continue;
        }

        /* Усі поля валідні — знайдено точну дату */
        return true;
    }
    return false;
}

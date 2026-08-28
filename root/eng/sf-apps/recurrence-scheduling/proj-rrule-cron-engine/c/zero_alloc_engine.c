/* ============================================================================
 * zero_alloc_engine.h / zero_alloc_engine.c (C99)
 * Повна реалізація рушія рекурентності без купової пам'яті.
 * ========================================================================== */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#if defined(_MSC_VER)
#  include <intrin.h>
   static inline int ctz64_impl(uint64_t mask) {
       unsigned long idx;
       _BitScanForward64(&idx, mask);
       return (int)idx;
   }
#else
   static inline int ctz64_impl(uint64_t mask) {
       return __builtin_ctzll(mask);
   }
#endif

/* Типи частоти RRULE */
typedef enum {
    FREQ_NONE = 0,
    FREQ_SECONDLY,
    FREQ_MINUTELY,
    FREQ_HOURLY,
    FREQ_DAILY,
    FREQ_WEEKLY,
    FREQ_MONTHLY,
    FREQ_YEARLY
} rrule_freq_t;

/* День тижня з номером входження */
typedef struct {
    int8_t ord;  /* -5..+5, де 0 означає будь-який такий день тижня */
    int8_t day;  /* 0 = SU, 1 = MO, 2 = TU, 3 = WE, 4 = TH, 5 = FR, 6 = SA */
} rrule_wday_t;

/* Структура правила RRULE */
typedef struct {
    rrule_freq_t freq;
    uint32_t interval;
    uint32_t count;
    int64_t  until_utc;
    uint16_t by_month_mask;      /* Біти 1..12 */
    uint32_t by_monthday_mask;   /* Біти 1..31 для додатних чисел */
    uint32_t by_neg_monthday;    /* Біти 1..31 для від'ємних чисел (-1..-31) */
    rrule_wday_t by_day[8];
    uint8_t  by_day_count;
    int8_t   by_setpos[8];
    uint8_t  by_setpos_count;
    uint8_t  wkst;
    bool     has_count;
    bool     has_until;
} rrule_t;

/* Структура розкладу CRON */
typedef struct {
    uint64_t sec_mask;
    uint64_t min_mask;
    uint32_t hour_mask;
    uint32_t dom_mask;
    uint16_t mon_mask;
    uint8_t  dow_mask;
    bool     dom_is_star;
    bool     dow_is_star;
} cron_t;

/* Календарний час */
typedef struct {
    int32_t year;
    int8_t  month;
    int8_t  day;
    int8_t  hour;
    int8_t  minute;
    int8_t  second;
} civil_time_t;

/* Допоміжні календарні функції */
static inline bool is_leap(int32_t y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

static inline int days_in_mon(int32_t y, int m) {
    static const int8_t kDays[13] = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2 && is_leap(y)) return 29;
    return kDays[m];
}

static inline int64_t civil_to_days(int32_t y, int m, int d) {
    y -= (m <= 2) ? 1 : 0;
    const int64_t era = (y >= 0 ? y : y - 399) / 400;
    const uint32_t yoe = (uint32_t)(y - era * 400);
    const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + (uint32_t)(d - 1);
    const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (int64_t)doe - 719468;
}

static inline void days_to_civil(int64_t z, int32_t *out_y, int8_t *out_m, int8_t *out_d) {
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

static inline int calc_dow(int64_t days_epoch) {
    int dow = (int)((days_epoch + 4) % 7);
    return dow < 0 ? dow + 7 : dow;
}

/* Швидкий парсер цілого числа */
static const char* parse_uint(const char *p, uint32_t *out) {
    uint32_t v = 0;
    if (*p < '0' || *p > '9') return NULL;
    while (*p >= '0' && *p <= '9') {
        v = v * 10 + (uint32_t)(*p - '0');
        p++;
    }
    *out = v;
    return p;
}

/* Парсер окремого поля CRON у 64-бітну маску */
static const char* parse_cron_field(const char *p, int min_val, int max_val, uint64_t *out_mask, bool *is_star) {
    *out_mask = 0;
    *is_star = false;

    if (*p == '*') {
        *is_star = true;
        p++;
        if (*p == '/') {
            p++;
            uint32_t step = 1;
            p = parse_uint(p, &step);
            if (!p || step == 0) return NULL;
            for (int i = min_val; i <= max_val; i += (int)step) {
                *out_mask |= (1ULL << i);
            }
            *is_star = false;
        } else {
            for (int i = min_val; i <= max_val; i++) {
                *out_mask |= (1ULL << i);
            }
        }
        return p;
    }

    while (*p && *p != ' ' && *p != '\t') {
        uint32_t start = 0;
        p = parse_uint(p, &start);
        if (!p || (int)start < min_val || (int)start > max_val) return NULL;

        uint32_t stop = start;
        uint32_t step = 1;

        if (*p == '-') {
            p++;
            p = parse_uint(p, &stop);
            if (!p || (int)stop < (int)start || (int)stop > max_val) return NULL;
        }

        if (*p == '/') {
            p++;
            p = parse_uint(p, &step);
            if (!p || step == 0) return NULL;
        }

        for (uint32_t i = start; i <= stop; i += step) {
            *out_mask |= (1ULL << i);
        }

        if (*p == ',') {
            p++;
        } else {
            break;
        }
    }
    return p;
}

/* Парсинг рядка CRON (5 полів) */
bool cron_parse(const char *str, cron_t *out) {
    memset(out, 0, sizeof(*out));
    out->sec_mask = 1ULL; /* 0-ва секунда за замовчуванням */

    const char *p = str;
    while (*p == ' ') p++;

    uint64_t mask;
    /* Хвилини */
    p = parse_cron_field(p, 0, 59, &out->min_mask, &(bool){0});
    if (!p) return false;
    while (*p == ' ') p++;

    /* Години */
    p = parse_cron_field(p, 0, 23, &mask, &(bool){0});
    if (!p) return false;
    out->hour_mask = (uint32_t)mask;
    while (*p == ' ') p++;

    /* День місяця */
    p = parse_cron_field(p, 1, 31, &mask, &out->dom_is_star);
    if (!p) return false;
    out->dom_mask = (uint32_t)mask;
    while (*p == ' ') p++;

    /* Місяць */
    p = parse_cron_field(p, 1, 12, &mask, &(bool){0});
    if (!p) return false;
    out->mon_mask = (uint16_t)mask;
    while (*p == ' ') p++;

    /* День тижня */
    p = parse_cron_field(p, 0, 7, &mask, &out->dow_is_star);
    if (!p) return false;
    /* 7 за стандартом транслюється в 0 (неділя) */
    if (mask & (1ULL << 7)) {
        mask |= 1ULL;
        mask &= ~(1ULL << 7);
    }
    out->dow_mask = (uint8_t)mask;

    return true;
}

/* Обчислення наступного входження CRON */
bool cron_evaluate_next(const cron_t *cron, civil_time_t *dt) {
    dt->second++;
    int guard = 0;
    while (guard++ < 5000) {
        if (!((cron->mon_mask >> dt->month) & 1)) {
            uint64_t mask = cron->mon_mask & ~((1ULL << dt->month) - 1);
            if (mask == 0) {
                dt->year++;
                dt->month = (int8_t)ctz64_impl(cron->mon_mask);
            } else {
                dt->month = (int8_t)ctz64_impl(mask);
            }
            dt->day = 1; dt->hour = 0; dt->minute = 0; dt->second = 0;
            continue;
        }

        int max_d = days_in_mon(dt->year, dt->month);
        if (dt->day > max_d) {
            dt->month++;
            if (dt->month > 12) { dt->month = 1; dt->year++; }
            dt->day = 1; dt->hour = 0; dt->minute = 0; dt->second = 0;
            continue;
        }

        int64_t days_epoch = civil_to_days(dt->year, dt->month, dt->day);
        int dow = calc_dow(days_epoch);

        bool dom_match = (cron->dom_mask >> dt->day) & 1;
        bool dow_match = (cron->dow_mask >> dow) & 1;
        bool day_valid = (!cron->dom_is_star && !cron->dow_is_star)
            ? (dom_match || dow_match)
            : (!cron->dom_is_star ? dom_match : (!cron->dow_is_star ? dow_match : true));

        if (!day_valid) {
            dt->day++;
            dt->hour = 0; dt->minute = 0; dt->second = 0;
            continue;
        }

        if (!((cron->hour_mask >> dt->hour) & 1)) {
            uint64_t mask = cron->hour_mask & ~((1ULL << dt->hour) - 1);
            if (mask == 0) {
                dt->day++;
                dt->hour = (int8_t)ctz64_impl(cron->hour_mask);
            } else {
                dt->hour = (int8_t)ctz64_impl(mask);
            }
            dt->minute = 0; dt->second = 0;
            continue;
        }

        if (!((cron->min_mask >> dt->minute) & 1)) {
            uint64_t mask = cron->min_mask & ~((1ULL << dt->minute) - 1);
            if (mask == 0) {
                dt->hour++;
                dt->minute = (int8_t)ctz64_impl(cron->min_mask);
                if (dt->hour > 23) { dt->hour = 0; dt->day++; }
            } else {
                dt->minute = (int8_t)ctz64_impl(mask);
            }
            dt->second = 0;
            continue;
        }

        if (!((cron->sec_mask >> dt->second) & 1)) {
            uint64_t mask = cron->sec_mask & ~((1ULL << dt->second) - 1);
            if (mask == 0) {
                dt->minute++;
                dt->second = (int8_t)ctz64_impl(cron->sec_mask);
                if (dt->minute > 59) {
                    dt->minute = 0; dt->hour++;
                    if (dt->hour > 23) { dt->hour = 0; dt->day++; }
                }
            } else {
                dt->second = (int8_t)ctz64_impl(mask);
            }
            continue;
        }

        return true;
    }
    return false;
}

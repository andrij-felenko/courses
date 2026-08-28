#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    int64_t timestamp_seconds;
    int32_t nanoseconds;
    int16_t offset_minutes;
    bool has_leap_second;
} iso_datetime_t;

/* Обчислення кількості днів від 1970-01-01 (алгоритм Гіннанта) */
static inline int64_t days_from_civil(int32_t y, uint32_t m, uint32_t d) {
    y -= (m <= 2);
    const int32_t era = (y >= 0 ? y : y - 399) / 400;
    const uint32_t yoe = (uint32_t)(y - era * 400);
    const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
    const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return (int64_t)era * 146097 + (int64_t)doe - 719468;
}

/* Перевірка кількості днів у місяці з урахуванням високосного року */
static inline bool is_valid_date(int32_t year, uint32_t month, uint32_t day) {
    if (month < 1 || month > 12 || day < 1 || day > 31) return false;
    if (month == 2) {
        const bool leap = (year % 4 == 0 && (year % 100 != 0 || year % 400 == 0));
        return day <= (leap ? 29u : 28u);
    }
    if (month == 4 || month == 6 || month == 9 || month == 11) {
        return day <= 30u;
    }
    return true;
}

/* Швидкий розбір 2-значного та 4-значного числа */
static inline uint32_t parse_digits2(const char* s) {
    return (uint32_t)(s[0] * 10 + s[1] - 528);
}

static inline uint32_t parse_digits4(const char* s) {
    return (uint32_t)(s[0] * 1000 + s[1] * 100 + s[2] * 10 + s[3] - 53328);
}

bool parse_iso8601_fast(const char* str, size_t len, iso_datetime_t* out) {
    if (len < 20 || !str || !out) return false;

    /* Базова перевірка розділювачів розширеного формату */
    if (str[4] != '-' || str[7] != '-' || (str[10] != 'T' && str[10] != ' ') ||
        str[13] != ':' || str[16] != ':') {
        return false;
    }

    const int32_t year   = (int32_t)parse_digits4(str);
    const uint32_t month = parse_digits2(str + 5);
    const uint32_t day   = parse_digits2(str + 8);
    const uint32_t hour  = parse_digits2(str + 11);
    const uint32_t min   = parse_digits2(str + 14);
    const uint32_t sec   = parse_digits2(str + 17);

    if (!is_valid_date(year, month, day)) return false;
    if (hour > 23 || min > 59 || sec > 60) return false;

    out->has_leap_second = (sec == 60);
    const uint32_t effective_sec = (sec == 60) ? 59 : sec;

    size_t idx = 19;
    int32_t nanos = 0;

    /* Розбір часток секунди (якщо присутні) */
    if (idx < len && (str[idx] == '.' || str[idx] == ',')) {
        idx++;
        int32_t frac = 0;
        int32_t mult = 100000000;
        while (idx < len && str[idx] >= '0' && str[idx] <= '9') {
            if (mult > 0) {
                frac += (str[idx] - '0') * mult;
                mult /= 10;
            }
            idx++;
        }
        nanos = frac;
    }

    /* Розбір зміщення часового поясу */
    int16_t offset_mins = 0;
    if (idx < len) {
        if (str[idx] == 'Z' || str[idx] == 'z') {
            offset_mins = 0;
            idx++;
        } else if ((str[idx] == '+' || str[idx] == '-') && (len - idx >= 6)) {
            const char sign = str[idx];
            if (str[idx + 3] != ':') return false;
            const uint32_t off_h = parse_digits2(str + idx + 1);
            const uint32_t off_m = parse_digits2(str + idx + 4);
            if (off_h > 23 || off_m > 59) return false;
            offset_mins = (int16_t)(off_h * 60 + off_m);
            if (sign == '-') offset_mins = -offset_mins;
            idx += 6;
        } else {
            return false;
        }
    }

    const int64_t days = days_from_civil(year, month, day);
    const int64_t local_secs = days * 86400 + (int64_t)hour * 3600 + (int64_t)min * 60 + effective_sec;
    out->timestamp_seconds = local_secs - (int64_t)offset_mins * 60;
    out->nanoseconds = nanos;
    out->offset_minutes = offset_mins;

    return true;
}

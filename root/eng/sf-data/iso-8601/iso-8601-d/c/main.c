#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct {
    int64_t unix_seconds;
    int16_t offset_minutes;
    bool valid;
} fast_time_t;

/* Алгоритм Говарда Гіннанта: цивільна дата -> дні від 1970-01-01 */
static inline int64_t civil_to_days(int32_t y, uint32_t m, uint32_t d) {
    y -= (m <= 2);
    const int32_t era = (y >= 0 ? y : y - 399) / 400;
    const uint32_t yoe = (uint32_t)(y - era * 400);
    const uint32_t doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
    const uint32_t doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return (int64_t)era * 146097 + (int64_t)doe - 719468;
}

fast_time_t parse_iso8601(const char* s, size_t len) {
    fast_time_t res = {0, 0, false};
    if (len < 20 || s[4] != '-' || s[7] != '-' || (s[10] != 'T' && s[10] != ' ') ||
        s[13] != ':' || s[16] != ':') {
        return res;
    }

    const int32_t year = (int32_t)(s[0]*1000 + s[1]*100 + s[2]*10 + s[3] - 53328);
    const uint32_t mon = (uint32_t)(s[5]*10 + s[6] - 528);
    const uint32_t day = (uint32_t)(s[8]*10 + s[9] - 528);
    const uint32_t h   = (uint32_t)(s[11]*10 + s[12] - 528);
    const uint32_t min = (uint32_t)(s[14]*10 + s[15] - 528);
    uint32_t sec       = (uint32_t)(s[17]*10 + s[18] - 528);

    if (mon < 1 || mon > 12 || day < 1 || day > 31 || h > 23 || min > 59 || sec > 60) {
        return res;
    }
    if (sec == 60) sec = 59; // врахування високосної секунди

    int16_t off = 0;
    if (s[19] == 'Z' || s[19] == 'z') {
        off = 0;
    } else if ((s[19] == '+' || s[19] == '-') && len >= 25 && s[22] == ':') {
        const uint32_t oh = (uint32_t)(s[20]*10 + s[21] - 528);
        const uint32_t om = (uint32_t)(s[23]*10 + s[24] - 528);
        if (oh > 23 || om > 59) return res;
        off = (int16_t)(oh * 60 + om);
        if (s[19] == '-') off = -off;
    } else {
        return res;
    }

    const int64_t days = civil_to_days(year, mon, day);
    res.unix_seconds = days * 86400 + (int64_t)h * 3600 + (int64_t)min * 60 + sec - (int64_t)off * 60;
    res.offset_minutes = off;
    res.valid = true;
    return res;
}

#include <stdint.h>
#include <stddef.h>

static const char DIGITS_LUT[200] =
    "0001020304050607080910111213141516171819"
    "2021222324252627282930313233343536373839"
    "4041424344454647484950515253545556575859"
    "6061626364656667686970717273747576777879"
    "8081828384858687888990919293949596979899";

static inline void write_two_digits(char* dest, uint32_t val) {
    const uint32_t idx = val * 2;
    dest[0] = DIGITS_LUT[idx];
    dest[1] = DIGITS_LUT[idx + 1];
}

size_t format_iso8601_utc(int64_t unix_secs, char* buf, size_t cap) {
    if (cap < 21) return 0;

    int64_t days = unix_secs / 86400;
    int32_t rem  = (int32_t)(unix_secs % 86400);
    if (rem < 0) {
        rem += 86400;
        days -= 1;
    }

    const uint32_t hour = (uint32_t)(rem / 3600);
    rem %= 3600;
    const uint32_t min  = (uint32_t)(rem / 60);
    const uint32_t sec  = (uint32_t)(rem % 60);

    /* Алгоритм зворотного обчислення дати з днів (Гіннант) */
    days += 719468;
    const int64_t era = (days >= 0 ? days : days - 146096) / 146097;
    const uint32_t doe = (uint32_t)(days - era * 146097);
    const uint32_t yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    int32_t y = (int32_t)yoe + (int32_t)era * 400;
    const uint32_t doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const uint32_t mp = (5 * doy + 2) / 153;
    const uint32_t d = doy - (153 * mp + 2) / 5 + 1;
    const uint32_t m = mp < 10 ? mp + 3 : mp - 9;
    if (m <= 2) y += 1;

    /* Запис 20 байтів YYYY-MM-DDThh:mm:ssZ */
    write_two_digits(buf, (uint32_t)(y / 100));
    write_two_digits(buf + 2, (uint32_t)(y % 100));
    buf[4] = '-';
    write_two_digits(buf + 5, m);
    buf[7] = '-';
    write_two_digits(buf + 8, d);
    buf[10] = 'T';
    write_two_digits(buf + 11, hour);
    buf[13] = ':';
    write_two_digits(buf + 14, min);
    buf[16] = ':';
    write_two_digits(buf + 17, sec);
    buf[19] = 'Z';
    buf[20] = '\0';

    return 20;
}

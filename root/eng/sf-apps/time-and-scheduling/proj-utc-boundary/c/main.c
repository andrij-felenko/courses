/* Межа: настінний час ↔ мить, ISO-8601 та високосні секунди на C99. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

enum resolve_kind {
    RESOLVE_EXACT,
    RESOLVE_GAP,
    RESOLVE_AMBIGUOUS
};

struct wall_time {
    int year;
    int month;   /* 1..12 */
    int day;     /* 1..31 */
    int hour;    /* 0..23 */
    int minute;  /* 0..59 */
    int second;  /* 0..60 (60 = високосна секунда) */
    int ms;      /* 0..999 */
    bool is_leap_second;
};

struct resolved_time {
    int64_t instant_epoch_ms;
    enum resolve_kind kind;
};

struct iso8601_parsed {
    struct wall_time wall;
    int offset_minutes;
    bool has_offset;
    bool is_utc;
    bool valid;
};

/* Алгоритм перетворення календарних днів у мить від епохи 1970-01-01 */
static inline int64_t days_from_civil(int y, unsigned m, unsigned d) {
    y -= m <= 2;
    const int64_t era = (y >= 0 ? y : y - 399) / 400;
    const unsigned yoe = (unsigned)(y - era * 400);
    const unsigned doy = (153 * (m > 2 ? m - 3 : m + 9) + 2) / 5 + d - 1;
    const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    return era * 146097 + (int64_t)doe - 719468;
}

static inline void civil_from_days(int64_t z, int *y, unsigned *m, unsigned *d) {
    z += 719468;
    const int64_t era = (z >= 0 ? z : z - 146096) / 146097;
    const unsigned doe = (unsigned)(z - era * 146097);
    const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    const int y_candidate = (int)yoe + (int)era * 400;
    const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    const unsigned mp = (5 * doy + 2) / 153;
    *d = doy - (153 * mp + 2) / 5 + 1;
    *m = mp < 10 ? mp + 3 : mp - 9;
    *y = y_candidate + (*m <= 2);
}

static inline bool is_leap_year(int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
}

static inline int days_in_month(int y, int m) {
    static const int d[12] = { 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };
    if (m == 2 && is_leap_year(y)) return 29;
    return (m >= 1 && m <= 12) ? d[m - 1] : 0;
}

/* Імітація читання таблиці переходів зони для миті UTC */
static int64_t zone_offset_ms(int64_t instant_ms, const char *zone) {
    if (strcmp(zone, "Europe/Kyiv") == 0) {
        /* Межі літнього часу 2026: 29 березня 01:00Z .. 25 жовтня 01:00Z */
        int64_t march_trans = days_from_civil(2026, 3, 29) * 86400000LL + 3600000LL;
        int64_t oct_trans   = days_from_civil(2026, 10, 25) * 86400000LL + 3600000LL;
        if (instant_ms >= march_trans && instant_ms < oct_trans) {
            return 3 * 3600000LL; /* UTC+3 */
        }
        return 2 * 3600000LL;     /* UTC+2 */
    }
    if (strcmp(zone, "Asia/Tokyo") == 0) {
        return 9 * 3600000LL;     /* UTC+9 */
    }
    return 0;
}

/* Парсер рядка ISO-8601 з перевіркою коректності та підтримкою 60-ї секунди */
struct iso8601_parsed parse_iso8601(const char *str) {
    struct iso8601_parsed res;
    memset(&res, 0, sizeof(res));
    if (!str) return res;

    int y = 0, mo = 0, d = 0, h = 0, mi = 0, s = 0;
    int off_h = 0, off_mi = 0;
    char tz_sign = '\0';

    int matched = sscanf(str, "%4d-%2d-%2dT%2d:%2d:%2d", &y, &mo, &d, &h, &mi, &s);
    if (matched < 5) return res;

    if (mo < 1 || mo > 12 || d < 1 || d > days_in_month(y, mo)) return res;
    if (h < 0 || h > 23 || mi < 0 || mi > 59) return res;
    if (s < 0 || s > 60) return res;

    res.wall.year = y;
    res.wall.month = mo;
    res.wall.day = d;
    res.wall.hour = h;
    res.wall.minute = mi;
    res.wall.second = (s == 60) ? 59 : s;
    res.wall.ms = 0;
    res.wall.is_leap_second = (s == 60);

    const char *tz_ptr = strchr(str, 'Z');
    if (tz_ptr) {
        res.is_utc = true;
        res.has_offset = true;
        res.offset_minutes = 0;
    } else if ((tz_ptr = strchr(str, '+')) || (tz_ptr = strrchr(str, '-'))) {
        if (sscanf(tz_ptr, "%c%2d:%2d", &tz_sign, &off_h, &off_mi) >= 2) {
            res.has_offset = true;
            res.offset_minutes = (off_h * 60 + off_mi) * (tz_sign == '-' ? -1 : 1);
        }
    }
    res.valid = true;
    return res;
}

/* Настінний час + назва зони → мить і тип розв'язку */
struct resolved_time resolve_local(struct wall_time w, const char *zone) {
    int64_t days = days_from_civil(w.year, (unsigned)w.month, (unsigned)w.day);
    int64_t as_if_utc = days * 86400000LL + (int64_t)w.hour * 3600000LL 
                        + (int64_t)w.minute * 60000LL + (int64_t)w.second * 1000LL + w.ms;
    const int64_t day_ms = 86400000LL;

    int64_t before = zone_offset_ms(as_if_utc - day_ms, zone);
    int64_t after  = zone_offset_ms(as_if_utc + day_ms, zone);

    int64_t valid_instants[2];
    int valid_count = 0;

    int64_t candidate1 = as_if_utc - before;
    if (zone_offset_ms(candidate1, zone) == before) {
        valid_instants[valid_count++] = candidate1;
    }

    if (before != after) {
        int64_t candidate2 = as_if_utc - after;
        if (zone_offset_ms(candidate2, zone) == after) {
            valid_instants[valid_count++] = candidate2;
        }
    }

    struct resolved_time res;
    if (valid_count == 1) {
        res.instant_epoch_ms = valid_instants[0];
        res.kind = RESOLVE_EXACT;
    } else if (valid_count == 2) {
        res.instant_epoch_ms = (valid_instants[0] < valid_instants[1]) ? valid_instants[0] : valid_instants[1];
        res.kind = RESOLVE_AMBIGUOUS;
    } else {
        int64_t min_off = (before < after) ? before : after;
        res.instant_epoch_ms = as_if_utc - min_off;
        res.kind = RESOLVE_GAP;
    }
    return res;
}

/* Форматування миті в настінний напис читача */
void format_in_zone(int64_t instant_ms, const char *zone, char *buf, size_t buf_size) {
    int64_t off = zone_offset_ms(instant_ms, zone);
    int64_t local_ms = instant_ms + off;
    int64_t days = local_ms / 86400000LL;
    int64_t time_ms = local_ms % 86400000LL;
    if (time_ms < 0) { days--; time_ms += 86400000LL; }

    int y; unsigned m, d;
    civil_from_days(days, &y, &m, &d);
    int h = (int)(time_ms / 3600000LL);
    int mi = (int)((time_ms % 3600000LL) / 60000LL);
    int s = (int)((time_ms % 60000LL) / 1000LL);

    int off_min = (int)(off / 60000LL);
    char sign = (off_min >= 0) ? '+' : '-';
    if (off_min < 0) off_min = -off_min;

    snprintf(buf, buf_size, "%04d-%02u-%02u %02d:%02d:%02d %c%02d:%02d",
             y, m, d, h, mi, s, sign, off_min / 60, off_min % 60);
}

/* Обчислення меж календарної доби користувача на осі митей */
void day_bounds(int y, int mo, int d, const char *zone, int64_t *out_start, int64_t *out_end) {
    struct wall_time w_start = { .year = y, .month = mo, .day = d, .hour = 0, .minute = 0, .second = 0, .ms = 0, .is_leap_second = false };
    int64_t next_days = days_from_civil(y, (unsigned)mo, (unsigned)d) + 1;
    int ny; unsigned nm, nd;
    civil_from_days(next_days, &ny, &nm, &nd);
    struct wall_time w_end = { .year = ny, .month = (int)nm, .day = (int)nd, .hour = 0, .minute = 0, .second = 0, .ms = 0, .is_leap_second = false };

    *out_start = resolve_local(w_start, zone).instant_epoch_ms;
    *out_end   = resolve_local(w_end, zone).instant_epoch_ms;
}

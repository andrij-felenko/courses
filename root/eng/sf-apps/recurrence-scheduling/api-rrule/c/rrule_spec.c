/* ============================================================================
 * rrule_spec.h & rrule_spec.c — еталонний C99 парсер, валідатор та генератор
 * ========================================================================== */
#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <ctype.h>

typedef enum {
    RRULE_OK = 0,
    RRULE_ERR_EMPTY_INPUT,
    RRULE_ERR_INVALID_SYNTAX,
    RRULE_ERR_MISSING_FREQ,
    RRULE_ERR_FREQ_NOT_FIRST,
    RRULE_ERR_DUPLICATE_PART,
    RRULE_ERR_MUTUAL_UNTIL_COUNT,
    RRULE_ERR_INVALID_INTERVAL,
    RRULE_ERR_INVALID_COUNT,
    RRULE_ERR_INVALID_UNTIL,
    RRULE_ERR_INVALID_BYMONTH,
    RRULE_ERR_INVALID_BYMONTHDAY,
    RRULE_ERR_INVALID_BYDAY,
    RRULE_ERR_INVALID_BYSETPOS,
    RRULE_ERR_INVALID_WKST,
    RRULE_ERR_BYSETPOS_WITHOUT_BY,
    RRULE_ERR_BYMONTHDAY_ON_WEEKLY,
    RRULE_ERR_ORDINAL_BYDAY_INVALID,
    RRULE_ERR_BUFFER_TOO_SMALL
} rrule_status_t;

typedef enum {
    FREQ_UNSET = 0,
    FREQ_SECONDLY,
    FREQ_MINUTELY,
    FREQ_HOURLY,
    FREQ_DAILY,
    FREQ_WEEKLY,
    FREQ_MONTHLY,
    FREQ_YEARLY
} rrule_freq_t;

typedef struct {
    int8_t ord;   /* 0 = будь-який, +1..+53, -53..-1 */
    uint8_t wday; /* 0 = SU, 1 = MO, 2 = TU, 3 = WE, 4 = TH, 5 = FR, 6 = SA */
} rrule_wday_spec_t;

typedef struct {
    rrule_freq_t freq;
    uint32_t interval;
    uint32_t count;
    bool has_count;
    char until_str[32];
    bool has_until;
    uint16_t bymonth_mask;        /* Біти 1..12 */
    uint32_t bymonthday_pos_mask; /* Біти 1..31 */
    uint32_t bymonthday_neg_mask; /* Біти 1..31 для -1..-31 */
    rrule_wday_spec_t byday[16];
    uint8_t byday_count;
    int16_t bysetpos[16];
    uint8_t bysetpos_count;
    uint8_t wkst;                 /* 0 = SU..6 = SA, усталено 1 (MO) */
} rrule_spec_t;

static const char* kFreqNames[] = {
    "", "SECONDLY", "MINUTELY", "HOURLY", "DAILY", "WEEKLY", "MONTHLY", "YEARLY"
};

static const char* kWdayNames[] = {
    "SU", "MO", "TU", "WE", "TH", "FR", "SA"
};

static inline int parse_wday_code(const char *s, size_t len) {
    if (len < 2) return -1;
    for (int i = 0; i < 7; i++) {
        if (strncmp(s, kWdayNames[i], 2) == 0) return i;
    }
    return -1;
}

static rrule_status_t parse_integer(const char *s, const char *end, int32_t *out) {
    if (s >= end) return RRULE_ERR_INVALID_SYNTAX;
    bool neg = false;
    if (*s == '-') { neg = true; s++; }
    else if (*s == '+') { s++; }
    if (s >= end || !isdigit((unsigned char)*s)) return RRULE_ERR_INVALID_SYNTAX;
    int64_t v = 0;
    while (s < end && isdigit((unsigned char)*s)) {
        v = v * 10 + (*s - '0');
        if (v > 1000000) return RRULE_ERR_INVALID_SYNTAX;
        s++;
    }
    if (s != end) return RRULE_ERR_INVALID_SYNTAX;
    *out = (int32_t)(neg ? -v : v);
    return RRULE_OK;
}

rrule_status_t rrule_spec_validate(const rrule_spec_t *spec) {
    if (spec->freq == FREQ_UNSET) return RRULE_ERR_MISSING_FREQ;
    if (spec->has_count && spec->has_until) return RRULE_ERR_MUTUAL_UNTIL_COUNT;
    if (spec->interval == 0) return RRULE_ERR_INVALID_INTERVAL;
    if (spec->has_count && spec->count == 0) return RRULE_ERR_INVALID_COUNT;

    if (spec->has_until) {
        size_t ulen = strlen(spec->until_str);
        if (ulen < 8) return RRULE_ERR_INVALID_UNTIL;
        if (ulen > 8 && spec->until_str[ulen - 1] != 'Z') {
            return RRULE_ERR_INVALID_UNTIL; /* UTC дата-час мусить мати Z */
        }
    }

    if (spec->freq == FREQ_WEEKLY && (spec->bymonthday_pos_mask || spec->bymonthday_neg_mask)) {
        return RRULE_ERR_BYMONTHDAY_ON_WEEKLY;
    }

    if (spec->bysetpos_count > 0) {
        bool has_by = (spec->bymonth_mask != 0) ||
                      (spec->bymonthday_pos_mask != 0) ||
                      (spec->bymonthday_neg_mask != 0) ||
                      (spec->byday_count != 0);
        if (!has_by) return RRULE_ERR_BYSETPOS_WITHOUT_BY;
    }

    for (uint8_t i = 0; i < spec->byday_count; i++) {
        if (spec->byday[i].ord != 0) {
            if (spec->freq != FREQ_MONTHLY && spec->freq != FREQ_YEARLY) {
                return RRULE_ERR_ORDINAL_BYDAY_INVALID;
            }
        }
    }

    return RRULE_OK;
}

rrule_status_t rrule_spec_parse(const char *str, rrule_spec_t *out) {
    if (!str || !*str) return RRULE_ERR_EMPTY_INPUT;
    memset(out, 0, sizeof(*out));
    out->interval = 1;
    out->wkst = 1; /* Понеділок за замовчуванням */

    const char *p = str;
    if (strncmp(p, "RRULE:", 6) == 0) p += 6;

    bool is_first_part = true;
    uint32_t seen_parts_mask = 0;

    while (*p) {
        const char *semicolon = strchr(p, ';');
        const char *part_end = semicolon ? semicolon : p + strlen(p);
        const char *equals = memchr(p, '=', (size_t)(part_end - p));
        if (!equals) return RRULE_ERR_INVALID_SYNTAX;

        size_t key_len = (size_t)(equals - p);
        const char *val = equals + 1;
        size_t val_len = (size_t)(part_end - val);
        if (val_len == 0) return RRULE_ERR_INVALID_SYNTAX;

        if (key_len == 4 && strncmp(p, "FREQ", 4) == 0) {
            if (!is_first_part) return RRULE_ERR_FREQ_NOT_FIRST;
            if (seen_parts_mask & (1 << 0)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 0);

            for (int i = 1; i <= 7; i++) {
                if (strlen(kFreqNames[i]) == val_len && strncmp(val, kFreqNames[i], val_len) == 0) {
                    out->freq = (rrule_freq_t)i;
                    break;
                }
            }
            if (out->freq == FREQ_UNSET) return RRULE_ERR_INVALID_SYNTAX;
        } else if (key_len == 8 && strncmp(p, "INTERVAL", 8) == 0) {
            if (seen_parts_mask & (1 << 1)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 1);
            int32_t iv = 0;
            if (parse_integer(val, part_end, &iv) != RRULE_OK || iv <= 0) {
                return RRULE_ERR_INVALID_INTERVAL;
            }
            out->interval = (uint32_t)iv;
        } else if (key_len == 5 && strncmp(p, "COUNT", 5) == 0) {
            if (seen_parts_mask & (1 << 2)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 2);
            int32_t cnt = 0;
            if (parse_integer(val, part_end, &cnt) != RRULE_OK || cnt <= 0) {
                return RRULE_ERR_INVALID_COUNT;
            }
            out->count = (uint32_t)cnt;
            out->has_count = true;
        } else if (key_len == 5 && strncmp(p, "UNTIL", 5) == 0) {
            if (seen_parts_mask & (1 << 3)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 3);
            if (val_len >= sizeof(out->until_str)) return RRULE_ERR_INVALID_UNTIL;
            memcpy(out->until_str, val, val_len);
            out->until_str[val_len] = '\0';
            out->has_until = true;
        } else if (key_len == 7 && strncmp(p, "BYMONTH", 7) == 0) {
            if (seen_parts_mask & (1 << 4)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 4);
            const char *item = val;
            while (item < part_end) {
                const char *comma = memchr(item, ',', (size_t)(part_end - item));
                const char *item_end = comma ? comma : part_end;
                int32_t m = 0;
                if (parse_integer(item, item_end, &m) != RRULE_OK || m < 1 || m > 12) {
                    return RRULE_ERR_INVALID_BYMONTH;
                }
                out->bymonth_mask |= (1 << m);
                item = item_end + (comma ? 1 : 0);
            }
        } else if (key_len == 10 && strncmp(p, "BYMONTHDAY", 10) == 0) {
            if (seen_parts_mask & (1 << 5)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 5);
            const char *item = val;
            while (item < part_end) {
                const char *comma = memchr(item, ',', (size_t)(part_end - item));
                const char *item_end = comma ? comma : part_end;
                int32_t md = 0;
                if (parse_integer(item, item_end, &md) != RRULE_OK || md == 0 || md < -31 || md > 31) {
                    return RRULE_ERR_INVALID_BYMONTHDAY;
                }
                if (md > 0) out->bymonthday_pos_mask |= (1U << md);
                else out->bymonthday_neg_mask |= (1U << (-md));
                item = item_end + (comma ? 1 : 0);
            }
        } else if (key_len == 5 && strncmp(p, "BYDAY", 5) == 0) {
            if (seen_parts_mask & (1 << 6)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 6);
            const char *item = val;
            while (item < part_end) {
                const char *comma = memchr(item, ',', (size_t)(part_end - item));
                const char *item_end = comma ? comma : part_end;
                if (out->byday_count >= 16) return RRULE_ERR_INVALID_BYDAY;

                int8_t ord = 0;
                const char *wptr = item;
                if (item_end - item > 2) {
                    int32_t ord_val = 0;
                    if (parse_integer(item, item_end - 2, &ord_val) != RRULE_OK || ord_val < -53 || ord_val > 53 || ord_val == 0) {
                        return RRULE_ERR_INVALID_BYDAY;
                    }
                    ord = (int8_t)ord_val;
                    wptr = item_end - 2;
                }
                int wd = parse_wday_code(wptr, (size_t)(item_end - wptr));
                if (wd < 0) return RRULE_ERR_INVALID_BYDAY;
                out->byday[out->byday_count].ord = ord;
                out->byday[out->byday_count].wday = (uint8_t)wd;
                out->byday_count++;
                item = item_end + (comma ? 1 : 0);
            }
        } else if (key_len == 8 && strncmp(p, "BYSETPOS", 8) == 0) {
            if (seen_parts_mask & (1 << 7)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 7);
            const char *item = val;
            while (item < part_end) {
                const char *comma = memchr(item, ',', (size_t)(part_end - item));
                const char *item_end = comma ? comma : part_end;
                if (out->bysetpos_count >= 16) return RRULE_ERR_INVALID_BYSETPOS;
                int32_t sp = 0;
                if (parse_integer(item, item_end, &sp) != RRULE_OK || sp == 0 || sp < -366 || sp > 366) {
                    return RRULE_ERR_INVALID_BYSETPOS;
                }
                out->bysetpos[out->bysetpos_count++] = (int16_t)sp;
                item = item_end + (comma ? 1 : 0);
            }
        } else if (key_len == 4 && strncmp(p, "WKST", 4) == 0) {
            if (seen_parts_mask & (1 << 8)) return RRULE_ERR_DUPLICATE_PART;
            seen_parts_mask |= (1 << 8);
            int wd = parse_wday_code(val, val_len);
            if (wd < 0) return RRULE_ERR_INVALID_WKST;
            out->wkst = (uint8_t)wd;
        }

        is_first_part = false;
        p = semicolon ? semicolon + 1 : part_end;
    }

    return rrule_spec_validate(out);
}

int rrule_spec_to_string(const rrule_spec_t *spec, char *buf, size_t buf_size) {
    if (!spec || !buf || buf_size == 0) return -1;
    if (spec->freq == FREQ_UNSET) return -1;

    size_t off = 0;
    int written = snprintf(buf + off, buf_size - off, "FREQ=%s", kFreqNames[spec->freq]);
    if (written < 0 || (size_t)written >= buf_size - off) return -1;
    off += (size_t)written;

    if (spec->interval > 1) {
        written = snprintf(buf + off, buf_size - off, ";INTERVAL=%u", spec->interval);
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
    }
    if (spec->has_count) {
        written = snprintf(buf + off, buf_size - off, ";COUNT=%u", spec->count);
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
    } else if (spec->has_until) {
        written = snprintf(buf + off, buf_size - off, ";UNTIL=%s", spec->until_str);
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
    }
    if (spec->bymonth_mask != 0) {
        written = snprintf(buf + off, buf_size - off, ";BYMONTH=");
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
        bool first = true;
        for (int m = 1; m <= 12; m++) {
            if (spec->bymonth_mask & (1 << m)) {
                written = snprintf(buf + off, buf_size - off, "%s%d", first ? "" : ",", m);
                if (written < 0 || (size_t)written >= buf_size - off) return -1;
                off += (size_t)written;
                first = false;
            }
        }
    }
    if (spec->bymonthday_pos_mask != 0 || spec->bymonthday_neg_mask != 0) {
        written = snprintf(buf + off, buf_size - off, ";BYMONTHDAY=");
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
        bool first = true;
        for (int d = 1; d <= 31; d++) {
            if (spec->bymonthday_pos_mask & (1U << d)) {
                written = snprintf(buf + off, buf_size - off, "%s%d", first ? "" : ",", d);
                if (written < 0 || (size_t)written >= buf_size - off) return -1;
                off += (size_t)written;
                first = false;
            }
        }
        for (int d = 1; d <= 31; d++) {
            if (spec->bymonthday_neg_mask & (1U << d)) {
                written = snprintf(buf + off, buf_size - off, "%s-%d", first ? "" : ",", d);
                if (written < 0 || (size_t)written >= buf_size - off) return -1;
                off += (size_t)written;
                first = false;
            }
        }
    }
    if (spec->byday_count > 0) {
        written = snprintf(buf + off, buf_size - off, ";BYDAY=");
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
        for (uint8_t i = 0; i < spec->byday_count; i++) {
            if (spec->byday[i].ord != 0) {
                written = snprintf(buf + off, buf_size - off, "%s%d%s",
                                   i == 0 ? "" : ",", spec->byday[i].ord, kWdayNames[spec->byday[i].wday]);
            } else {
                written = snprintf(buf + off, buf_size - off, "%s%s",
                                   i == 0 ? "" : ",", kWdayNames[spec->byday[i].wday]);
            }
            if (written < 0 || (size_t)written >= buf_size - off) return -1;
            off += (size_t)written;
        }
    }
    if (spec->bysetpos_count > 0) {
        written = snprintf(buf + off, buf_size - off, ";BYSETPOS=");
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
        for (uint8_t i = 0; i < spec->bysetpos_count; i++) {
            written = snprintf(buf + off, buf_size - off, "%s%d",
                               i == 0 ? "" : ",", spec->bysetpos[i]);
            if (written < 0 || (size_t)written >= buf_size - off) return -1;
            off += (size_t)written;
        }
    }
    if (spec->wkst != 1) {
        written = snprintf(buf + off, buf_size - off, ";WKST=%s", kWdayNames[spec->wkst]);
        if (written < 0 || (size_t)written >= buf_size - off) return -1;
        off += (size_t)written;
    }

    return (int)off;
}

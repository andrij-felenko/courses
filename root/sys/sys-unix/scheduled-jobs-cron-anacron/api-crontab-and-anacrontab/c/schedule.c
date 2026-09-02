/* _GNU_SOURCE — для inotify_init1() і поля st_mtim у glibc. */
#define _GNU_SOURCE

#include "schedule.h"

#include <ctype.h>
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/inotify.h>
#include <sys/stat.h>
#include <unistd.h>

typedef struct {
    int lo;
    int hi;
    const char *const *names; /* таблиця символьних назв або NULL */
    size_t names_count;
    int names_base;           /* число, якому відповідає names[0] */
    bool wrap_seven;          /* для дня тижня: 7 і 0 — та сама неділя */
} field_def_t;

static const char *const MONTH_NAMES[] = {
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "oct", "nov", "dec"
};
static const char *const DOW_NAMES[] = {
    "sun", "mon", "tue", "wed", "thu", "fri", "sat"
};

static const field_def_t FIELD_MINUTE = {0, 59, NULL, 0, 0, false};
static const field_def_t FIELD_HOUR   = {0, 23, NULL, 0, 0, false};
static const field_def_t FIELD_DOM    = {1, 31, NULL, 0, 0, false};
static const field_def_t FIELD_MONTH  = {1, 12, MONTH_NAMES, 12, 1, false};
static const field_def_t FIELD_DOW    = {0,  7, DOW_NAMES, 7, 0, true};

static void set_err(char *err, size_t err_size, const char *fmt, ...)
{
    if (err == NULL || err_size == 0) {
        return;
    }
    va_list ap;
    va_start(ap, fmt);
    vsnprintf(err, err_size, fmt, ap);
    va_end(ap);
}

static bool parse_number(const char *s, size_t len, int *out)
{
    if (len == 0 || len > 4) {
        return false;
    }
    int value = 0;
    for (size_t i = 0; i < len; i++) {
        if (!isdigit((unsigned char)s[i])) {
            return false;
        }
        value = value * 10 + (s[i] - '0');
    }
    *out = value;
    return true;
}

/* Назви місяців і днів тижня розпізнаються без урахування регістру. */
static bool parse_name(const char *s, size_t len, const field_def_t *f, int *out)
{
    if (f->names == NULL || len != 3) {
        return false;
    }
    for (size_t i = 0; i < f->names_count; i++) {
        if (strncasecmp(s, f->names[i], 3) == 0) {
            *out = f->names_base + (int)i;
            return true;
        }
    }
    return false;
}

static bool parse_value(const char *s, size_t len, const field_def_t *f,
                        int *out, bool *is_name, char *err, size_t err_size)
{
    if (parse_number(s, len, out)) {
        *is_name = false;
    } else if (parse_name(s, len, f, out)) {
        *is_name = true;
    } else {
        set_err(err, err_size, "нерозпізнане значення «%.*s»", (int)len, s);
        return false;
    }
    if (*out < f->lo || *out > f->hi) {
        set_err(err, err_size, "значення %d поза діапазоном %d..%d", *out, f->lo, f->hi);
        return false;
    }
    return true;
}

static void set_bits(uint64_t *mask, int lo, int hi, int step, const field_def_t *f)
{
    for (int v = lo; v <= hi; v += step) {
        int bit = (f->wrap_seven && v == 7) ? 0 : v;
        *mask |= (uint64_t)1 << bit;
    }
}

/* Одне поле: список елементів через кому, кожен — «*», значення, діапазон
   «a-b», з необов'язковим кроком «/n». */
static bool parse_field(const char *s, size_t len, const field_def_t *f,
                        uint64_t *mask, char *err, size_t err_size)
{
    *mask = 0;
    if (len == 0) {
        set_err(err, err_size, "порожнє поле");
        return false;
    }

    size_t pos = 0;
    while (pos < len) {
        const char *item = s + pos;
        const char *comma = memchr(item, ',', len - pos);
        size_t item_len = (comma != NULL) ? (size_t)(comma - item) : len - pos;
        pos += item_len + ((comma != NULL) ? 1 : 0);
        if (item_len == 0) {
            set_err(err, err_size, "порожній елемент списку");
            return false;
        }

        int step = 1;
        size_t range_len = item_len;
        const char *slash = memchr(item, '/', item_len);
        if (slash != NULL) {
            size_t step_len = item_len - (size_t)(slash - item) - 1;
            if (!parse_number(slash + 1, step_len, &step) || step <= 0) {
                set_err(err, err_size, "хибний крок у «%.*s»", (int)item_len, item);
                return false;
            }
            range_len = (size_t)(slash - item);
        }

        int lo = 0;
        int hi = 0;
        bool lo_named = false;
        bool hi_named = false;
        if (range_len == 1 && item[0] == '*') {
            lo = f->lo;
            hi = f->hi;
        } else {
            const char *dash = memchr(item, '-', range_len);
            if (dash != NULL) {
                size_t lo_len = (size_t)(dash - item);
                size_t hi_len = range_len - lo_len - 1;
                if (!parse_value(item, lo_len, f, &lo, &lo_named, err, err_size)) {
                    return false;
                }
                if (!parse_value(dash + 1, hi_len, f, &hi, &hi_named, err, err_size)) {
                    return false;
                }
                /* Vixie забороняє змішувати число й назву в одному діапазоні. */
                if (lo_named != hi_named) {
                    set_err(err, err_size, "у діапазоні «%.*s» змішано число й назву",
                            (int)range_len, item);
                    return false;
                }
                if (lo > hi) {
                    set_err(err, err_size, "порожній діапазон «%.*s»", (int)range_len, item);
                    return false;
                }
            } else {
                if (!parse_value(item, range_len, f, &lo, &lo_named, err, err_size)) {
                    return false;
                }
                /* «5/10» читаємо як «5-max/10» — розширення cronie. */
                hi = (slash != NULL) ? f->hi : lo;
                hi_named = lo_named;
            }
        }

        /* Крок до символьних назв не застосовується (класичний Vixie). */
        if (slash != NULL && (lo_named || hi_named)) {
            set_err(err, err_size, "крок «/» не застосовується до назв — вживайте числа");
            return false;
        }
        set_bits(mask, lo, hi, step, f);
    }
    return true;
}

typedef struct {
    const char *name;
    const char *spec;
} macro_def_t;

/* Мнемонічні макроси демон замінює на звичайні п'ять полів під час розбору. */
static const macro_def_t MACROS[] = {
    {"@yearly",   "0 0 1 1 *"},
    {"@annually", "0 0 1 1 *"},
    {"@monthly",  "0 0 1 * *"},
    {"@weekly",   "0 0 * * 0"},
    {"@daily",    "0 0 * * *"},
    {"@midnight", "0 0 * * *"},
    {"@hourly",   "0 * * * *"},
};

bool cron_schedule_parse(const char *line, cron_schedule_t *out, const char **rest,
                         char *err, size_t err_size)
{
    static const char *const FIELD_NAMES[5] = {
        "minute", "hour", "day of month", "month", "day of week"
    };
    static const field_def_t *const DEFS[5] = {
        &FIELD_MINUTE, &FIELD_HOUR, &FIELD_DOM, &FIELD_MONTH, &FIELD_DOW
    };

    memset(out, 0, sizeof(*out));
    const char *p = line;
    while (*p == ' ' || *p == '\t') {
        p++;
    }

    if (*p == '@') {
        const char *end = p;
        while (*end != '\0' && !isspace((unsigned char)*end)) {
            end++;
        }
        size_t len = (size_t)(end - p);
        if (len == strlen("@reboot") && strncasecmp(p, "@reboot", len) == 0) {
            out->flags = CRON_AT_REBOOT;
            *rest = end;
            return true;
        }
        for (size_t i = 0; i < sizeof MACROS / sizeof MACROS[0]; i++) {
            if (strlen(MACROS[i].name) == len && strncasecmp(p, MACROS[i].name, len) == 0) {
                const char *unused = NULL;
                if (!cron_schedule_parse(MACROS[i].spec, out, &unused, err, err_size)) {
                    return false;
                }
                *rest = end;
                return true;
            }
        }
        set_err(err, err_size, "невідомий макрос «%.*s»", (int)len, p);
        return false;
    }

    uint64_t masks[5] = {0};
    bool stars[5] = {false};
    for (int i = 0; i < 5; i++) {
        while (*p == ' ' || *p == '\t') {
            p++;
        }
        const char *start = p;
        while (*p != '\0' && !isspace((unsigned char)*p)) {
            p++;
        }
        if (p == start) {
            set_err(err, err_size, "bad %s: бракує поля розкладу", FIELD_NAMES[i]);
            return false;
        }
        stars[i] = (start[0] == '*');
        char detail[128] = "";
        if (!parse_field(start, (size_t)(p - start), DEFS[i], &masks[i],
                         detail, sizeof detail)) {
            set_err(err, err_size, "bad %s: %s", FIELD_NAMES[i], detail);
            return false;
        }
    }

    out->minute_mask = masks[0];
    out->hour_mask   = (uint32_t)masks[1];
    out->dom_mask    = (uint32_t)masks[2];
    out->month_mask  = (uint16_t)masks[3];
    out->dow_mask    = (uint8_t)masks[4];
    out->flags = (stars[2] ? CRON_DOM_STAR : 0u) | (stars[4] ? CRON_DOW_STAR : 0u);
    *rest = p;
    return true;
}

bool cron_schedule_matches(const cron_schedule_t *sched, const struct tm *tm_now)
{
    /* @reboot не має календарного збігу взагалі. */
    if ((sched->flags & CRON_AT_REBOOT) != 0u) {
        return false;
    }
    if (tm_now->tm_min < 0 || tm_now->tm_min > 59 ||
        tm_now->tm_hour < 0 || tm_now->tm_hour > 23 ||
        tm_now->tm_mon < 0 || tm_now->tm_mon > 11) {
        return false;
    }
    if (((sched->minute_mask >> tm_now->tm_min) & 1u) == 0u) {
        return false;
    }
    if (((sched->hour_mask >> tm_now->tm_hour) & 1u) == 0u) {
        return false;
    }
    if (((sched->month_mask >> (tm_now->tm_mon + 1)) & 1u) == 0u) {
        return false;
    }
    return cron_day_matches(sched->dom_mask, sched->dow_mask, sched->flags, tm_now);
}

unsigned cron_seconds_to_next_minute(time_t now)
{
    struct tm tm_now;
    if (localtime_r(&now, &tm_now) == NULL) {
        return 60;
    }
    int sec = tm_now.tm_sec;
    /* tm_sec == 60 буває на високосній секунді — це не привід спати нуль. */
    if (sec > 59) {
        sec = 59;
    }
    if (sec < 0) {
        sec = 0;
    }
    return (unsigned)(60 - sec);
}

/* ---- стеження за таблицями ------------------------------------------- */

#define CRON_WATCH_MAX  8
#define CRON_WATCH_PATH 256

struct cron_watch {
    int inotify_fd;                                  /* -1 → режим опитування */
    size_t count;
    char paths[CRON_WATCH_MAX][CRON_WATCH_PATH];
    struct timespec stamps[CRON_WATCH_MAX];
    bool present[CRON_WATCH_MAX];
};

static bool stamps_changed(cron_watch_t *watch)
{
    bool changed = false;
    for (size_t i = 0; i < watch->count; i++) {
        struct stat st;
        const bool present = (stat(watch->paths[i], &st) == 0);
        if (present != watch->present[i]) {
            changed = true;
        } else if (present &&
                   (st.st_mtim.tv_sec != watch->stamps[i].tv_sec ||
                    st.st_mtim.tv_nsec != watch->stamps[i].tv_nsec)) {
            changed = true;
        }
        watch->present[i] = present;
        if (present) {
            watch->stamps[i] = st.st_mtim;
        }
    }
    return changed;
}

cron_watch_t *cron_watch_open(const char *const *paths, size_t count)
{
    if (count == 0 || count > CRON_WATCH_MAX) {
        errno = EINVAL;
        return NULL;
    }
    cron_watch_t *watch = calloc(1, sizeof(*watch));
    if (watch == NULL) {
        return NULL;
    }
    watch->count = count;
    watch->inotify_fd = -1;
    for (size_t i = 0; i < count; i++) {
        snprintf(watch->paths[i], CRON_WATCH_PATH, "%s", paths[i]);
    }

    /* IN_CLOEXEC — щоб дескриптор не протік у завдання через execve;
       IN_NONBLOCK — щоб читання порожньої черги не спинило демона. */
    int fd = inotify_init1(IN_CLOEXEC | IN_NONBLOCK);
    if (fd >= 0) {
        const uint32_t mask = IN_MODIFY | IN_CREATE | IN_DELETE | IN_ATTRIB |
                              IN_MOVED_TO | IN_MOVED_FROM | IN_CLOSE_WRITE |
                              IN_DELETE_SELF | IN_MOVE_SELF;
        for (size_t i = 0; i < count; i++) {
            if (inotify_add_watch(fd, watch->paths[i], mask) < 0) {
                /* Шляху ще може не бути (порожній /etc/cron.d) — відступаємо на
                   опитування: воно переживає і зникнення, і появу файлу. */
                fprintf(stderr, "minicron: inotify %s: %s — переходжу на stat()\n",
                        watch->paths[i], strerror(errno));
                close(fd);
                fd = -1;
                break;
            }
        }
    } else {
        fprintf(stderr, "minicron: inotify_init1: %s — переходжу на stat()\n",
                strerror(errno));
    }
    watch->inotify_fd = fd;

    /* Знімок міток потрібен завжди: у режимі inotify він лишається запасним
       свідченням для першої ж перевірки після відступу. */
    (void)stamps_changed(watch);
    return watch;
}

int cron_watch_fd(const cron_watch_t *watch)
{
    return (watch != NULL) ? watch->inotify_fd : -1;
}

bool cron_watch_changed(cron_watch_t *watch)
{
    if (watch == NULL) {
        return false;
    }
    if (watch->inotify_fd < 0) {
        return stamps_changed(watch);
    }

    /* Одне збереження файлу редактором дає кілька подій — вичитуємо чергу до
       кінця й повертаємо один-єдиний факт «змінилося». */
    union {
        struct inotify_event ev; /* лише заради вирівнювання буфера */
        char raw[4096];
    } buf;
    bool any = false;
    for (;;) {
        ssize_t n = read(watch->inotify_fd, buf.raw, sizeof buf.raw);
        if (n > 0) {
            any = true;
            continue;
        }
        if (n < 0 && errno == EINTR) {
            continue;
        }
        if (n < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
            fprintf(stderr, "minicron: read inotify: %s\n", strerror(errno));
        }
        break;
    }
    return any;
}

void cron_watch_close(cron_watch_t *watch)
{
    if (watch == NULL) {
        return;
    }
    if (watch->inotify_fd >= 0) {
        close(watch->inotify_fd);
    }
    free(watch);
}

#include "genealogy.h"

#include <ctype.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ---------------------------- динамічні масиви ---------------------------- */

void boards_init(BoardSet *s) { s->items = NULL; s->count = 0; s->cap = 0; }
void boards_free(BoardSet *s) { free(s->items); boards_init(s); }

Board *boards_add(BoardSet *s) {
    if (s->count == s->cap) {
        size_t cap = s->cap ? s->cap * 2 : 1024;
        Board *items = realloc(s->items, cap * sizeof *items);
        if (!items) return NULL;
        s->items = items;
        s->cap = cap;
    }
    Board *b = &s->items[s->count++];
    memset(b, 0, sizeof *b);
    return b;
}

Board *boards_find(BoardSet *s, const char *serial) {
    /* Рекламацій одиниці-десятки, тож лінійного пошуку тут вистачає. */
    for (size_t i = 0; i < s->count; i++)
        if (strcmp(s->items[i].serial, serial) == 0) return &s->items[i];
    return NULL;
}

void feeders_init(FeederLog *l) { l->items = NULL; l->count = 0; l->cap = 0; }
void feeders_free(FeederLog *l) { free(l->items); feeders_init(l); }

FeederWindow *feeders_add(FeederLog *l) {
    if (l->count == l->cap) {
        size_t cap = l->cap ? l->cap * 2 : 32;
        FeederWindow *items = realloc(l->items, cap * sizeof *items);
        if (!items) return NULL;
        l->items = items;
        l->cap = cap;
    }
    FeederWindow *w = &l->items[l->count++];
    memset(w, 0, sizeof *w);
    return w;
}

/* ------------------------------- розбір CSV ------------------------------- */

static char *trim(char *s) {
    while (*s && isspace((unsigned char)*s)) s++;
    char *end = s + strlen(s);
    while (end > s && isspace((unsigned char)end[-1])) *--end = '\0';
    return s;
}

/* Відрізає наступне поле; NULL — полів більше немає. Рядок псується на місці. */
static char *next_field(char **cursor) {
    if (!*cursor) return NULL;
    char *start = *cursor;
    char *comma = strchr(start, ',');
    if (comma) { *comma = '\0'; *cursor = comma + 1; }
    else       { *cursor = NULL; }
    return trim(start);
}

static void copy_field(char *dst, size_t cap, const char *src) {
    snprintf(dst, cap, "%s", src);   /* задовге просто зрізаємо: імена котушок короткі */
}

static int parse_ll(const char *s, long long *out) {
    char *end;
    errno = 0;
    long long v = strtoll(s, &end, 10);
    if (end == s || *end != '\0' || errno == ERANGE) return -1;
    *out = v;
    return 0;
}

static int parse_double(const char *s, double *out) {
    char *end;
    errno = 0;
    double v = strtod(s, &end);
    if (end == s || *end != '\0' || errno == ERANGE) return -1;
    *out = v;
    return 0;
}

typedef int (*RowFn)(char *line, void *ctx, char *msg, size_t msglen);

static int read_csv(const char *path, const char *header_hint,
                    RowFn fn, void *ctx, char *err, size_t errlen) {
    FILE *f = fopen(path, "r");
    if (!f) {
        snprintf(err, errlen, "%s: не вдалося відкрити файл", path);
        return -1;
    }
    char buf[512];
    size_t lineno = 0;
    int rc = 0;
    while (fgets(buf, sizeof buf, f)) {
        lineno++;
        char *line = trim(buf);
        if (*line == '\0' || *line == '#') continue;
        if (lineno == 1 && strncmp(line, header_hint, strlen(header_hint)) == 0) continue;

        char msg[192] = "";
        if (fn(line, ctx, msg, sizeof msg) != 0) {
            snprintf(err, errlen, "%s:%zu: %s", path, lineno, msg);
            rc = -1;
            break;
        }
    }
    if (rc == 0 && ferror(f)) {
        snprintf(err, errlen, "%s: помилка читання", path);
        rc = -1;
    }
    fclose(f);
    return rc;
}

static int mes_row(char *line, void *ctx, char *msg, size_t msglen) {
    BoardSet *s = ctx;
    char *cursor = line;
    char *serial  = next_field(&cursor);
    char *smt     = next_field(&cursor);
    char *profile = next_field(&cursor);
    char *stamp   = next_field(&cursor);
    if (!serial || !smt || !profile || !stamp) {
        snprintf(msg, msglen, "очікую serial,smt_line,reflow_profile,scan_epoch");
        return -1;
    }
    if (*serial == '\0') { snprintf(msg, msglen, "порожній серійний номер"); return -1; }

    long long when;
    if (parse_ll(stamp, &when) != 0) {
        snprintf(msg, msglen, "scan_epoch='%s' не є цілим числом", stamp);
        return -1;
    }
    Board *b = boards_add(s);
    if (!b) { snprintf(msg, msglen, "не вистачило пам'яті"); return -1; }

    copy_field(b->serial,  NAME_LEN, serial);
    copy_field(b->line,    NAME_LEN, smt);
    copy_field(b->profile, NAME_LEN, profile);
    b->scan_time = when;
    return 0;
}

static int feeder_row(char *line, void *ctx, char *msg, size_t msglen) {
    FeederLog *l = ctx;
    char *cursor = line;
    char *smt   = next_field(&cursor);
    char *desig = next_field(&cursor);
    char *reel  = next_field(&cursor);
    char *lot   = next_field(&cursor);
    char *dc    = next_field(&cursor);
    char *from  = next_field(&cursor);
    char *to    = next_field(&cursor);
    char *spl   = next_field(&cursor);
    if (!smt || !desig || !reel || !lot || !dc || !from || !to) {
        snprintf(msg, msglen,
                 "очікую smt_line,designator,reel_uid,lot_code,date_code,from_epoch,to_epoch[,spliced]");
        return -1;
    }
    long long from_ts, to_ts;
    if (parse_ll(from, &from_ts) != 0 || parse_ll(to, &to_ts) != 0) {
        snprintf(msg, msglen, "межі вікна мають бути цілими Unix-часами");
        return -1;
    }
    if (to_ts <= from_ts) {
        snprintf(msg, msglen, "порожнє вікно котушки %s: %lld..%lld", reel, from_ts, to_ts);
        return -1;
    }
    FeederWindow *w = feeders_add(l);
    if (!w) { snprintf(msg, msglen, "не вистачило пам'яті"); return -1; }

    copy_field(w->line,       NAME_LEN, smt);
    copy_field(w->designator, NAME_LEN, desig);
    copy_field(w->reel_uid,   NAME_LEN, reel);
    copy_field(w->lot_code,   NAME_LEN, lot);
    copy_field(w->date_code,  NAME_LEN, dc);
    w->from_ts = from_ts;
    w->to_ts   = to_ts;
    w->spliced = (spl && (*spl == '1' || *spl == 'y' || *spl == 'Y'));
    return 0;
}

typedef struct { BoardSet *boards; size_t unknown; } ReturnCtx;

static int return_row(char *line, void *ctx, char *msg, size_t msglen) {
    ReturnCtx *rc = ctx;
    char *cursor = line;
    char *serial = next_field(&cursor);
    char *ttf    = next_field(&cursor);
    if (!serial) { snprintf(msg, msglen, "очікую serial,ttf_hours[,symptom]"); return -1; }

    Board *b = boards_find(rc->boards, serial);
    if (!b) {
        /* Повернення з чужого випуску — не привід валити аналіз. */
        rc->unknown++;
        return 0;
    }
    b->failed = 1;
    if (ttf && *ttf && parse_double(ttf, &b->ttf_hours) != 0) {
        snprintf(msg, msglen, "ttf_hours='%s' не є числом", ttf);
        return -1;
    }
    return 0;
}

int load_mes(BoardSet *s, const char *path, char *err, size_t errlen) {
    return read_csv(path, "serial", mes_row, s, err, errlen);
}

int load_feeders(FeederLog *l, const char *path, char *err, size_t errlen) {
    return read_csv(path, "smt_line", feeder_row, l, err, errlen);
}

int load_returns(BoardSet *s, const char *path, char *err, size_t errlen) {
    ReturnCtx ctx = { s, 0 };
    int rc = read_csv(path, "serial", return_row, &ctx, err, errlen);
    if (rc == 0 && ctx.unknown)
        fprintf(stderr, "Попередження: %zu рекламацій без плати в журналі MES\n", ctx.unknown);
    return rc;
}

/* ------------------------------- зшивання -------------------------------- */

static void board_add_part(Board *b, const FeederWindow *w) {
    for (int i = 0; i < b->part_count; i++) {
        if (strcmp(b->parts[i].designator, w->designator) == 0) {
            /* Два вікна на той самий десігнатор перекрилися — походження непевне. */
            b->parts[i].uncertain = 1;
            return;
        }
    }
    if (b->part_count >= MAX_PARTS) return;
    PartOrigin *p = &b->parts[b->part_count++];
    copy_field(p->designator, NAME_LEN, w->designator);
    copy_field(p->reel_uid,   NAME_LEN, w->reel_uid);
    copy_field(p->lot_code,   NAME_LEN, w->lot_code);
    copy_field(p->date_code,  NAME_LEN, w->date_code);
    p->uncertain = 0;
}

static int cmp_board_ptr(const void *x, const void *y) {
    const Board *a = *(const Board *const *)x;
    const Board *b = *(const Board *const *)y;
    int c = strcmp(a->line, b->line);
    if (c) return c;
    return (a->scan_time > b->scan_time) - (a->scan_time < b->scan_time);
}

/* Позначає непевними плати обабіч стику котушок для одного десігнатора. */
static void mark_zone(Board **idx, size_t lo, size_t hi,
                      long long boundary, const char *designator) {
    size_t left = lo, right = hi;
    while (left < right) {                       /* перша плата з scan_time >= boundary */
        size_t mid = left + (right - left) / 2;
        if (idx[mid]->scan_time < boundary) left = mid + 1;
        else                                right = mid;
    }
    size_t from = (left > lo + SPLICE_BOARDS) ? left - SPLICE_BOARDS : lo;
    size_t to   = (left + SPLICE_BOARDS < hi) ? left + SPLICE_BOARDS : hi;
    for (size_t i = from; i < to; i++)
        for (int p = 0; p < idx[i]->part_count; p++)
            if (strcmp(idx[i]->parts[p].designator, designator) == 0)
                idx[i]->parts[p].uncertain = 1;
}

static void mark_splice_zones(BoardSet *s, const FeederLog *l) {
    if (s->count == 0) return;
    Board **idx = malloc(s->count * sizeof *idx);
    if (!idx) {
        fprintf(stderr, "Попередження: без пам'яті на індекс зони склейки не розмічені\n");
        return;
    }
    for (size_t i = 0; i < s->count; i++) idx[i] = &s->items[i];
    qsort(idx, s->count, sizeof *idx, cmp_board_ptr);

    for (size_t j = 0; j < l->count; j++) {
        const FeederWindow *w = &l->items[j];
        if (!w->spliced) continue;
        size_t lo = 0;
        while (lo < s->count && strcmp(idx[lo]->line, w->line) != 0) lo++;
        size_t hi = lo;
        while (hi < s->count && strcmp(idx[hi]->line, w->line) == 0) hi++;
        if (lo < hi) mark_zone(idx, lo, hi, w->to_ts, w->designator);
    }
    free(idx);
}

void join_genealogy(BoardSet *s, const FeederLog *l) {
    for (size_t i = 0; i < s->count; i++) {
        Board *b = &s->items[i];
        b->part_count = 0;
        for (size_t j = 0; j < l->count; j++) {
            const FeederWindow *w = &l->items[j];
            if (strcmp(w->line, b->line) != 0) continue;
            if (b->scan_time < w->from_ts || b->scan_time >= w->to_ts) continue;
            board_add_part(b, w);
        }
    }
    mark_splice_zones(s, l);
}

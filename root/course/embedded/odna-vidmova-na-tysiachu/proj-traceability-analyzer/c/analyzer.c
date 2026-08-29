#include "analyzer.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define MAX_KEYS (2 + MAX_PARTS * 3)

/* ------------------- ключі факторів, які має кожна плата ------------------- */

static size_t board_keys(const Board *b, char keys[][FACTOR_LEN], int *uncertain) {
    size_t n = 0;
    snprintf(keys[n], FACTOR_LEN, "SMT_Line=%s", b->line);    uncertain[n++] = 0;
    snprintf(keys[n], FACTOR_LEN, "Reflow=%s",   b->profile); uncertain[n++] = 0;

    for (int i = 0; i < b->part_count && n + 3 <= MAX_KEYS; i++) {
        const PartOrigin *p = &b->parts[i];
        snprintf(keys[n], FACTOR_LEN, "%s.Lot=%s",      p->designator, p->lot_code);  uncertain[n++] = p->uncertain;
        snprintf(keys[n], FACTOR_LEN, "%s.DateCode=%s", p->designator, p->date_code); uncertain[n++] = p->uncertain;
        snprintf(keys[n], FACTOR_LEN, "%s.Reel=%s",     p->designator, p->reel_uid);  uncertain[n++] = p->uncertain;
    }
    return n;
}

/* Витягує десігнатор із ключа "C12.Lot=L-8921"; для факторів рівня плати — порожньо. */
static void key_designator(const char *key, char *out, size_t cap) {
    const char *dot = strchr(key, '.');
    const char *eq  = strchr(key, '=');
    if (!dot || (eq && dot > eq)) { out[0] = '\0'; return; }
    size_t len = (size_t)(dot - key);
    if (len >= cap) len = cap - 1;
    memcpy(out, key, len);
    out[len] = '\0';
}

/* Чи має плата цей фактор і чи певні ми в цьому. Викликається лише для
   кількох кандидатів, тому перебудова ключів тут не дорога. */
static int board_has_key(const Board *b, const char *key, int *uncertain) {
    char desig[NAME_LEN];
    key_designator(key, desig, sizeof desig);

    int unc = 0;
    if (desig[0])
        for (int i = 0; i < b->part_count; i++)
            if (strcmp(b->parts[i].designator, desig) == 0 && b->parts[i].uncertain) unc = 1;
    if (uncertain) *uncertain = unc;

    char keys[MAX_KEYS][FACTOR_LEN];
    int  flags[MAX_KEYS];
    size_t n = board_keys(b, keys, flags);
    for (size_t i = 0; i < n; i++)
        if (strcmp(keys[i], key) == 0) return 1;
    return 0;
}

/* ------------------- хеш-таблиця «фактор → лічильники» -------------------- */

typedef struct { char key[FACTOR_LEN]; int a, b, ua, ub; } Cell;
typedef struct { Cell *cells; size_t cap, count; } CellMap;

static size_t fnv1a(const char *s) {
    size_t h = 1469598103934665603ULL;
    while (*s) { h ^= (unsigned char)*s++; h *= 1099511628211ULL; }
    return h;
}

static int map_init(CellMap *m, size_t cap) {
    m->cells = calloc(cap, sizeof *m->cells);
    if (!m->cells) return -1;
    m->cap = cap;
    m->count = 0;
    return 0;
}

static void map_free(CellMap *m) { free(m->cells); m->cells = NULL; m->cap = m->count = 0; }

static Cell *map_slot(Cell *cells, size_t cap, const char *key) {
    size_t i = fnv1a(key) & (cap - 1);
    for (;;) {
        if (cells[i].key[0] == '\0' || strcmp(cells[i].key, key) == 0) return &cells[i];
        i = (i + 1) & (cap - 1);
    }
}

static int map_grow(CellMap *m) {
    size_t cap = m->cap * 2;
    Cell *cells = calloc(cap, sizeof *cells);
    if (!cells) return -1;
    for (size_t i = 0; i < m->cap; i++)
        if (m->cells[i].key[0]) *map_slot(cells, cap, m->cells[i].key) = m->cells[i];
    free(m->cells);
    m->cells = cells;
    m->cap = cap;
    return 0;
}

static Cell *map_get(CellMap *m, const char *key) {
    if ((m->count + 1) * 10 >= m->cap * 7 && map_grow(m) != 0) return NULL;
    Cell *c = map_slot(m->cells, m->cap, key);
    if (c->key[0] == '\0') { snprintf(c->key, FACTOR_LEN, "%s", key); m->count++; }
    return c;
}

/* --------------------------- фаза підрахунку 2x2 -------------------------- */

static int cell_usable(const Cell *cell, int failed_total, int ok_total,
                       int min_group, Table2x2 *out) {
    const int group = cell->a + cell->b;
    const int c = failed_total - cell->a - cell->ua;
    const int d = ok_total - cell->b - cell->ub;
    if (group < min_group || c < 0 || d < 0 || c + d < min_group) return 0;
    out->a = cell->a; out->b = cell->b; out->c = c; out->d = d;
    return 1;
}

static int cmp_finding(const void *x, const void *y) {
    const Finding *a = x, *b = y;
    if (a->p_adj < b->p_adj) return -1;
    if (a->p_adj > b->p_adj) return 1;
    if (a->effect.odds_ratio > b->effect.odds_ratio) return -1;
    if (a->effect.odds_ratio < b->effect.odds_ratio) return 1;
    return strcmp(a->factor, b->factor);
}

int analyze_boards(const BoardSet *s, int min_group, FindingList *out) {
    out->items = NULL;
    out->count = 0;

    CellMap map;
    if (map_init(&map, 1024) != 0) return -1;

    int failed_total = 0, ok_total = 0;
    for (size_t i = 0; i < s->count; i++) {
        const Board *b = &s->items[i];
        if (b->failed) failed_total++; else ok_total++;

        char keys[MAX_KEYS][FACTOR_LEN];
        int  unc[MAX_KEYS];
        size_t n = board_keys(b, keys, unc);
        for (size_t k = 0; k < n; k++) {
            Cell *cell = map_get(&map, keys[k]);
            if (!cell) { map_free(&map); return -1; }
            if (unc[k]) { if (b->failed) cell->ua++; else cell->ub++; }
            else        { if (b->failed) cell->a++;  else cell->b++;  }
        }
    }

    size_t kept = 0;
    for (size_t i = 0; i < map.cap; i++) {
        Table2x2 t;
        if (map.cells[i].key[0] && cell_usable(&map.cells[i], failed_total, ok_total, min_group, &t))
            kept++;
    }
    if (kept == 0) { map_free(&map); return 0; }

    Finding *items = calloc(kept, sizeof *items);
    double *p = malloc(kept * sizeof *p);
    double *q = malloc(kept * sizeof *q);
    if (!items || !p || !q) { free(items); free(p); free(q); map_free(&map); return -1; }

    size_t j = 0;
    for (size_t i = 0; i < map.cap && j < kept; i++) {
        const Cell *cell = &map.cells[i];
        Table2x2 t;
        if (!cell->key[0] || !cell_usable(cell, failed_total, ok_total, min_group, &t)) continue;

        Finding *f = &items[j];
        snprintf(f->factor, FACTOR_LEN, "%s", cell->key);
        f->table   = t;
        f->unknown = cell->ua + cell->ub;
        f->effect  = effect_size(t);
        f->p_value = fisher_exact_2x2(t);
        f->p_adj   = f->p_value;
        f->mh_p_value = NAN;
        f->mh_odds_ratio = NAN;
        p[j] = f->p_value;
        j++;
    }
    map_free(&map);

    /* Чим більше факторів перевірено, тим легше натрапити на випадковий сплеск. */
    if (benjamini_hochberg(p, kept, q) == 0)
        for (size_t i = 0; i < kept; i++) items[i].p_adj = q[i];
    free(p);
    free(q);

    qsort(items, kept, sizeof *items, cmp_finding);
    out->items = items;
    out->count = kept;
    return 0;
}

void findings_free(FindingList *f) { free(f->items); f->items = NULL; f->count = 0; }

/* ----------------------- розділення спарених факторів --------------------- */

static void strata_tables(const BoardSet *s, const char *factor,
                          const char *stratum, Table2x2 t[2]) {
    memset(t, 0, 2 * sizeof *t);
    for (size_t i = 0; i < s->count; i++) {
        const Board *b = &s->items[i];
        int unc_f = 0, unc_s = 0;
        const int has_f = board_has_key(b, factor, &unc_f);
        if (unc_f) continue;                       /* непевні плати в таблицю не йдуть */
        const int has_s = board_has_key(b, stratum, &unc_s);
        if (unc_s) continue;

        Table2x2 *tab = &t[has_s ? 0 : 1];
        if (has_f && b->failed)  tab->a++;
        else if (has_f)          tab->b++;
        else if (b->failed)      tab->c++;
        else                     tab->d++;
    }
}

static void stratify(const BoardSet *s, Finding *f, const char *stratum) {
    if (strcmp(f->factor, stratum) == 0) return;
    Table2x2 t[2];
    strata_tables(s, f->factor, stratum, t);
    MhResult mh = mantel_haenszel(t, 2);

    snprintf(f->stratified_by, FACTOR_LEN, "%s", stratum);
    f->mh_odds_ratio = mh.odds_ratio;
    f->mh_p_value    = mh.p_value;
    f->mh_strata     = mh.strata_used;
    if (mh.strata_used < 2) return;               /* фактори збіглися — судити нема з чого */

    /* Сигнал, що зникає всередині страт, породжений не цим фактором. */
    f->confounded = (mh.p_value > 0.01) ||
                    (f->effect.odds_ratio > 3.0 && mh.odds_ratio < f->effect.odds_ratio / 3.0);
}

void check_confounding(const BoardSet *s, FindingList *fl, double alpha) {
    if (fl->count < 2) return;
    Finding *top = &fl->items[0];

    /* Решту факторів стратифікуємо за найсильнішим сигналом. */
    for (size_t i = 1; i < fl->count; i++) {
        Finding *f = &fl->items[i];
        if (f->p_adj > alpha) continue;
        stratify(s, f, top->factor);
    }
    /* Самого лідера перевіряємо першим фактором, що дає дві змістовні страти. */
    for (size_t i = 1; i < fl->count; i++) {
        stratify(s, top, fl->items[i].factor);
        if (top->mh_strata >= 2) break;
        top->stratified_by[0] = '\0';
    }
}

const Finding *pick_root_cause(const FindingList *fl, double max_p, double min_or) {
    for (size_t i = 0; i < fl->count; i++) {
        const Finding *f = &fl->items[i];
        if (f->confounded) continue;
        if (f->p_adj < max_p && f->effect.odds_ratio > min_or) return f;
    }
    return NULL;
}

/* --------------------------------- звіт ---------------------------------- */

static void fmt_ratio(double v, char *buf, size_t n) {
    if (isnan(v))      snprintf(buf, n, "%s", "-");
    else if (isinf(v)) snprintf(buf, n, "%s", "inf");
    else               snprintf(buf, n, "%.1f", v);
}

void print_report(const BoardSet *s, const FindingList *fl, size_t top, FILE *out) {
    size_t failed = 0;
    for (size_t i = 0; i < s->count; i++) failed += (size_t)(s->items[i].failed != 0);

    fprintf(out, "\nПлат у випуску: %zu, польових відмов: %zu (%.3f%%)\n",
            s->count, failed, s->count ? 100.0 * (double)failed / (double)s->count : 0.0);
    fprintf(out, "Перевірено факторів: %zu\n\n", fl->count);
    fprintf(out, "%-26s %5s %6s %5s %6s  %8s %8s %9s %11s\n",
            "фактор", "a", "b", "c", "d", "брак%", "фон%", "OR", "q(BH)");

    const size_t shown = (fl->count < top) ? fl->count : top;
    for (size_t i = 0; i < shown; i++) {
        const Finding *f = &fl->items[i];
        const Table2x2 t = f->table;
        const double rate_in  = (t.a + t.b) ? 100.0 * t.a / (double)(t.a + t.b) : 0.0;
        const double rate_out = (t.c + t.d) ? 100.0 * t.c / (double)(t.c + t.d) : 0.0;
        char or_txt[24];
        fmt_ratio(f->effect.odds_ratio, or_txt, sizeof or_txt);

        fprintf(out, "%-26s %5d %6d %5d %6d  %7.3f%% %7.4f%% %9s %11.2e\n",
                f->factor, t.a, t.b, t.c, t.d, rate_in, rate_out, or_txt, f->p_adj);
        fprintf(out, "    95%% CI [%.1f .. %.1f]%s, точний тест Фішера p=%.2e",
                f->effect.ci_low, f->effect.ci_high,
                f->effect.haldane ? " (Холдейн-Енскомб)" : "", f->p_value);
        if (f->unknown) fprintf(out, ", непевних плат зі стику котушок: %d", f->unknown);
        fputc('\n', out);

        if (f->stratified_by[0]) {
            char mh_txt[24];
            fmt_ratio(f->mh_odds_ratio, mh_txt, sizeof mh_txt);
            if (f->mh_strata < 2)
                fprintf(out, "    стратифікація за [%s] неможлива: фактори збігаються\n",
                        f->stratified_by);
            else
                fprintf(out, "    Мантель-Гензель за [%s]: OR=%s p=%.2e -> %s\n",
                        f->stratified_by, mh_txt, f->mh_p_value,
                        f->confounded ? "спарений фактор, власного внеску немає"
                                      : "фактор витримує стратифікацію");
        }
    }
}

int export_quarantine(const BoardSet *s, const Finding *guilty, const char *path, FILE *log) {
    FILE *f = fopen(path, "w");
    if (!f) {
        fprintf(stderr, "Не вдалося відкрити %s на запис\n", path);
        return -1;
    }
    char desig[NAME_LEN];
    key_designator(guilty->factor, desig, sizeof desig);

    fprintf(f, "serial,factor,confidence\n");
    int count = 0, uncertain_count = 0;
    const char *first = NULL, *last = NULL;

    for (size_t i = 0; i < s->count; i++) {
        const Board *b = &s->items[i];
        int unc = 0;
        const int has = board_has_key(b, guilty->factor, &unc);
        /* Плати зі стику котушок беремо теж: їхнє походження ми не знаємо,
           а помилитися дешевше в бік карантину. */
        if (!has && !(unc && desig[0])) continue;

        fprintf(f, "%s,%s,%s\n", b->serial, guilty->factor, unc ? "splice-zone" : "exact");
        if (unc) uncertain_count++;
        if (!first || strcmp(b->serial, first) < 0) first = b->serial;
        if (!last  || strcmp(b->serial, last)  > 0) last  = b->serial;
        count++;
    }
    if (fclose(f) != 0) {
        fprintf(stderr, "Помилка запису %s\n", path);
        return -1;
    }
    fprintf(log, "\n[КАРАНТИН] фактор %s\n", guilty->factor);
    fprintf(log, "  плат до вилучення: %d (з них %d із зони склейки стрічок)\n",
            count, uncertain_count);
    if (first && last) fprintf(log, "  діапазон серійних номерів: %s .. %s\n", first, last);
    fprintf(log, "  список збережено у %s\n", path);
    return count;
}

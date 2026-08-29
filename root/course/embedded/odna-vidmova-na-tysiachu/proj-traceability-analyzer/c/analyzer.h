#ifndef ANALYZER_H
#define ANALYZER_H

#include <stdio.h>

#include "genealogy.h"
#include "stats.h"

#define FACTOR_LEN 64

/* Один перевірений виробничий фактор: "C12.Lot=L-8921", "SMT_Line=Line-2". */
typedef struct {
    char factor[FACTOR_LEN];
    Table2x2 table;
    int    unknown;              /* плати зі стику котушок, виключені з таблиці */
    Effect effect;
    double p_value;
    double p_adj;                /* після поправки на множинність */

    char   stratified_by[FACTOR_LEN];
    double mh_odds_ratio;
    double mh_p_value;
    size_t mh_strata;
    int    confounded;           /* сигнал зникає після стратифікації */
} Finding;

typedef struct { Finding *items; size_t count; } FindingList;

int  analyze_boards(const BoardSet *s, int min_group, FindingList *out);
void findings_free(FindingList *f);

/* Розділення спарених факторів за критерієм Мантеля — Гензеля. */
void check_confounding(const BoardSet *s, FindingList *f, double alpha);

const Finding *pick_root_cause(const FindingList *f, double max_p, double min_or);
void print_report(const BoardSet *s, const FindingList *f, size_t top, FILE *out);

/* Повертає кількість плат у карантині або -1. */
int export_quarantine(const BoardSet *s, const Finding *guilty, const char *path, FILE *log);

#endif /* ANALYZER_H */

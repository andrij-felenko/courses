#include <stdio.h>
#include <string.h>

#include "analyzer.h"
#include "genealogy.h"

#define MIN_GROUP        30            /* менші групи статистики не витримують */
#define QUARANTINE_PATH  "quarantine.csv"

/* --------------------- синтетичний випуск для показу ---------------------- */

#define DEMO_BOARDS 20000
#define DEMO_TAKT   10                 /* секунд на плату в наскрізному потоці */
#define DEMO_T0     1772409600LL       /* 2026-03-02 00:00:00 UTC */

static unsigned long long rng_state = 20260302ULL;

static double rng_u01(void) {
    rng_state = rng_state * 6364136223846793005ULL + 1442695040888963407ULL;
    return (double)((rng_state >> 33) & 0x7FFFFFFFu) / 2147483648.0;
}

static int add_window(FeederLog *l, const char *line, const char *desig, const char *reel,
                      const char *lot, const char *dc,
                      long long from, long long to, int spliced) {
    FeederWindow *w = feeders_add(l);
    if (!w) return -1;
    snprintf(w->line,       NAME_LEN, "%s", line);
    snprintf(w->designator, NAME_LEN, "%s", desig);
    snprintf(w->reel_uid,   NAME_LEN, "%s", reel);
    snprintf(w->lot_code,   NAME_LEN, "%s", lot);
    snprintf(w->date_code,  NAME_LEN, "%s", dc);
    w->from_ts = from;
    w->to_ts   = to;
    w->spliced = spliced;
    return 0;
}

static int build_demo_run(BoardSet *s, FeederLog *l) {
    const long long t_end      = DEMO_T0 + (long long)DEMO_BOARDS * DEMO_TAKT;
    const long long t_mcu      = DEMO_T0 + 10000LL * DEMO_TAKT;
    const long long t_bad_from = DEMO_T0 + 14000LL * DEMO_TAKT;
    const long long t_bad_to   = DEMO_T0 + 15000LL * DEMO_TAKT;
    static const char *lines[2] = { "Line-1", "Line-2" };

    for (int k = 0; k < 2; k++) {
        const char *ln = lines[k];
        if (add_window(l, ln, "U1", "R-501", "L-7001", "DC2130", DEMO_T0, t_mcu, 0) != 0) return -1;
        if (add_window(l, ln, "U1", "R-502", "L-7002", "DC2134", t_mcu, t_end, 0) != 0) return -1;
        if (add_window(l, ln, "U4", "R-101", "L-2201", "DC2129", DEMO_T0, t_bad_to, 0) != 0) return -1;
        if (add_window(l, ln, "U4", "R-102", "L-2202", "DC2133", t_bad_to, t_end, 0) != 0) return -1;
        /* Обидва стики котушок C12 зроблені склейкою стрічок на ходу. */
        if (add_window(l, ln, "C12", "R-901", "L-4410", "DC2125", DEMO_T0, t_bad_from, 1) != 0) return -1;
        if (add_window(l, ln, "C12", "R-902", "L-8921", "DC2133", t_bad_from, t_bad_to, 1) != 0) return -1;
        if (add_window(l, ln, "C12", "R-903", "L-4410", "DC2126", t_bad_to, t_end, 0) != 0) return -1;
    }

    for (int i = 0; i < DEMO_BOARDS; i++) {
        Board *b = boards_add(s);
        if (!b) return -1;
        snprintf(b->serial, NAME_LEN, "SN%05d", i + 1);
        b->scan_time = DEMO_T0 + (long long)i * DEMO_TAKT;

        const int in_bad_lot = (i >= 14000 && i < 15000);
        /* Дефектну котушку доїдали переважно на другій лінії — саме звідси
           береться хибна кореляція «винна Line-2». */
        const double p_line2 = in_bad_lot ? 0.85 : 0.5;
        snprintf(b->line, NAME_LEN, "%s", rng_u01() < p_line2 ? "Line-2" : "Line-1");
        snprintf(b->profile, NAME_LEN, "%s", (i < 12000) ? "P-7" : "P-9");

        const double risk = in_bad_lot ? 0.040 : 0.0002;
        b->failed = rng_u01() < risk;
        b->ttf_hours = b->failed ? 200.0 + rng_u01() * 900.0 : 0.0;
    }
    return 0;
}

static void usage(const char *argv0) {
    fprintf(stderr,
            "Використання:\n"
            "  %s <mes.csv> <feeders.csv> <returns.csv>\n"
            "  %s --demo\n\n"
            "  mes.csv      serial,smt_line,reflow_profile,scan_epoch\n"
            "  feeders.csv  smt_line,designator,reel_uid,lot_code,date_code,"
            "from_epoch,to_epoch,spliced\n"
            "  returns.csv  serial,ttf_hours,symptom\n",
            argv0, argv0);
}

int main(int argc, char **argv) {
    BoardSet boards;
    FeederLog feeders;
    FindingList findings = { NULL, 0 };
    char err[256];
    int rc = 0;

    boards_init(&boards);
    feeders_init(&feeders);

    printf("=== Аналізатор виробничої генеалогії PCBA ===\n");

    if (argc == 2 && strcmp(argv[1], "--demo") == 0) {
        printf("Джерело: синтетичний випуск на %d плат\n", DEMO_BOARDS);
        if (build_demo_run(&boards, &feeders) != 0) {
            fprintf(stderr, "Не вистачило пам'яті\n");
            rc = 1;
            goto out;
        }
    } else if (argc == 4) {
        if (load_mes(&boards, argv[1], err, sizeof err) != 0 ||
            load_feeders(&feeders, argv[2], err, sizeof err) != 0 ||
            load_returns(&boards, argv[3], err, sizeof err) != 0) {
            fprintf(stderr, "Помилка читання: %s\n", err);
            rc = 1;
            goto out;
        }
    } else {
        usage(argv[0]);
        rc = 1;
        goto out;
    }

    if (boards.count == 0) {
        fprintf(stderr, "Журнал MES порожній — немає чого зіставляти\n");
        rc = 1;
        goto out;
    }
    if (feeders.count == 0)
        fprintf(stderr, "Попередження: логи живильників порожні, лишаються лише "
                        "фактори рівня плати\n");

    join_genealogy(&boards, &feeders);

    if (analyze_boards(&boards, MIN_GROUP, &findings) != 0) {
        fprintf(stderr, "Не вистачило пам'яті на матриці спряженості\n");
        rc = 1;
        goto out;
    }
    check_confounding(&boards, &findings, 0.05);
    print_report(&boards, &findings, 8, stdout);

    {
        const Finding *guilty = pick_root_cause(&findings, 1e-5, 10.0);
        if (!guilty) {
            printf("\nЖоден фактор не перетнув поріг карантину (q<1e-5, OR>10).\n");
        } else if (export_quarantine(&boards, guilty, QUARANTINE_PATH, stdout) < 0) {
            rc = 1;
        } else {
            /* Код 2 — гачок для нічного сервісу: відкрити аварійний тікет. */
            rc = 2;
        }
    }

out:
    findings_free(&findings);
    boards_free(&boards);
    feeders_free(&feeders);
    return rc;
}

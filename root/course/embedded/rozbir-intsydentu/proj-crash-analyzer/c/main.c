#include "crashlog.h"

#include <stdio.h>

/* Коди виходу для конвеєра обробки польотних даних:
 * 0 — чисто, 3 — знайдено сигнатуру, 1 — журнал не прочитався, 2 — виклик. */
enum {
    EXIT_CLEAN = 0,
    EXIT_BAD_LOG = 1,
    EXIT_USAGE = 2,
    EXIT_FAULT = 3
};

static void print_mark(const char *label, uint64_t us)
{
    if (us != 0) {
        printf("  %s T = %.6f с\n", label, (double)us / 1e6);
    }
}

static void print_report(const IncidentReport *r)
{
    printf("Кадрів прийнято: %zu, відкинуто: %zu\n", r->frames_used, r->frames_skipped);
    printf("Сигнатура: %s\n", fault_name(r->fault));
    if (r->fault != FAULT_NONE) {
        printf("Мітка: T = %.6f с (%llu мкс)\n",
               (double)r->timestamp_us / 1e6, (unsigned long long)r->timestamp_us);
        printf("Впевненість: %.2f\n", (double)r->confidence);
    }
    printf("Висновок: %s\n", r->description);

    if (r->impact_us != 0 || r->env_anomaly_us != 0 || r->depletion_us != 0) {
        printf("Контекст (події, відкинуті як не-першопричина):\n");
        print_mark("зіткнення, сплеск гіроскопа випередив мотори:", r->impact_us);
        print_mark("магнітна аномалія середовища без власного струму:", r->env_anomaly_us);
        print_mark("плавне вичерпання заряду батареї:", r->depletion_us);
    }
}

int main(int argc, char **argv)
{
    if (argc != 2) {
        fprintf(stderr, "Виклик: %s <журнал.csv>\n"
                        "CSV — розпакований ULog/DataFlash із шапкою імен колонок.\n",
                argv[0]);
        return EXIT_USAGE;
    }

    FrameLog log;
    LoadStatus st = log_load_csv(argv[1], &log);
    if (!st.ok) {
        if (st.line > 0) {
            fprintf(stderr, "Журнал %s, рядок %zu: %s\n", argv[1], st.line, st.message);
        } else {
            fprintf(stderr, "Журнал %s: %s\n", argv[1], st.message);
        }
        log_free(&log);
        return EXIT_BAD_LOG;
    }

    IncidentReport report = analyze_incident(log.frames, log.count);
    print_report(&report);
    log_free(&log);

    return report.fault == FAULT_NONE ? EXIT_CLEAN : EXIT_FAULT;
}

/* Аналізатор перехідної характеристики контуру кутової швидкості.
 *
 *   analyzer <лог.csv> [поріг_відсічки_В]
 *
 * Лог — CSV: t_us,setpoint,gyro,d_term,vbat.
 * Збірка: cc -std=c99 -O2 -o analyzer *.c -lm
 */
#include "diagnose.h"
#include "log.h"
#include "metrics.h"
#include "step_detect.h"

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#define MAX_STEPS      64
#define DEFAULT_CUTOFF 13.6     /* 4S під навантаженням, 3.4 В на банку */

static void print_header(void)
{
    printf("\n  №  ампл,°/с   τ,мс  t_нар,мс   M_p,%%  t_вст,мс  D-шум  дзвін  примітка\n");
    printf("  --------------------------------------------------------------------------\n");
}

static void print_row(size_t idx, const StepMetrics *m, const StepWindow *w)
{
    char note[64];

    note[0] = '\0';
    if (w->distorted & DIST_GYRO_CLIP) {
        snprintf(note, sizeof note, "кліпінг гіро");
    }
    if (w->distorted & DIST_VBAT_SAG) {
        snprintf(note, sizeof note, "%sпросідання АКБ",
                 (w->distorted & DIST_GYRO_CLIP) ? "кліпінг гіро + " : "");
    }

    printf("  %2zu  %8.1f  %5.1f  ", idx, m->amplitude, m->tau_ms);
    if (m->reached_90) {
        printf("%8.1f", m->rise_time_ms);
    } else {
        printf("%8s", "<90%");
    }
    printf("  %6.1f  %8.1f%s  ", m->overshoot_pct, m->settling_time_ms, m->settled ? " " : "+");
    if (m->noise_measured) {
        printf("%5.1f", m->d_noise_rms);
    } else {
        printf("%5s", "н/д");
    }
    printf("  %5d  %s\n", m->ring_crossings, note);
}

static void print_verdict(const StepMetrics *m, size_t used)
{
    MetricBands b = diagnose_bands(m);
    TuneVerdict v = diagnose(m, b);

    printf("\n  Медіана по %zu чистих сходинках:\n", used);
    printf("    затримка τ .......... %5.1f мс   (%s)\n", m->tau_ms, band_mark(b.tau));
    if (m->reached_90) {
        printf("    час наростання ...... %5.1f мс   (%s)\n", m->rise_time_ms, band_mark(b.rise));
    } else {
        printf("    час наростання ...... не досягнуто 90%% завдання (%s)\n", band_mark(b.rise));
    }
    printf("    перерегулювання ..... %5.1f %%    (%s)\n", m->overshoot_pct, band_mark(b.overshoot));
    printf("    час встановлення .... %5.1f мс%s\n", m->settling_time_ms,
           m->settled ? "" : "   (у вікно не вклався)");
    if (m->noise_measured) {
        printf("    шум D-терма ......... %5.1f      (%s)\n", m->d_noise_rms, band_mark(b.noise));
    } else {
        printf("    шум D-терма ......... не виміряно: плато закоротке\n");
    }
    printf("    перетинів після піка  %5d\n", m->ring_crossings);

    printf("\n  ВЕРДИКТ: %s\n", verdict_title(v));
    printf("  ДІЯ:     %s\n\n", verdict_advice(v));
}

int main(int argc, char **argv)
{
    FlightLog log;
    DetectConfig cfg;
    DetectStats stats;
    StepWindow windows[MAX_STEPS];
    StepMetrics measured[MAX_STEPS];
    StepMetrics clean[MAX_STEPS];
    StepMetrics summary;
    char err[256];
    double cutoff = DEFAULT_CUTOFF;
    size_t nwin;
    size_t nclean = 0;
    size_t shown = 0;
    size_t i;

    if (argc < 2 || argc > 3) {
        fprintf(stderr, "вжиток: %s <лог.csv> [поріг_відсічки_В]\n", argv[0]);
        return 2;
    }
    if (argc == 3) {
        char *endp;

        errno = 0;
        cutoff = strtod(argv[2], &endp);
        if (endp == argv[2] || *endp != '\0' || errno != 0 || cutoff <= 0.0 || cutoff > 60.0) {
            fprintf(stderr, "поріг відсічки «%s» безглуздий: чекали напругу в вольтах\n", argv[2]);
            return 2;
        }
    }

    if (flightlog_load(argv[1], &log, err, sizeof err) != 0) {
        fprintf(stderr, "лог не прочитано: %s\n", err);
        return 1;
    }

    {
        double dt = flightlog_mean_dt_us(&log);

        printf("лог «%s»: %zu відліків, крок %.0f мкс (%.0f Гц), поріг АКБ %.1f В\n",
               argv[1], log.count, dt, (dt > 0.0) ? 1e6 / dt : 0.0, cutoff);
    }

    cfg = detect_default_config(cutoff);
    nwin = detect_steps(&log, &cfg, windows, MAX_STEPS, &stats);

    printf("фронтів понад поріг: %zu; відкинуто — повільних %zu, дрібних %zu, "
           "по неспокійній передісторії %zu, без плато %zu\n",
           stats.edges, stats.rejected_ramp, stats.rejected_small,
           stats.rejected_noisy, stats.rejected_plateau);

    if (nwin == 0) {
        printf("придатних сходинок не знайдено: політ або надто плавний, або надто рваний\n");
        flightlog_free(&log);
        return 1;
    }
    if (nwin == MAX_STEPS) {
        printf("увага: узято лише перші %d сходинок\n", MAX_STEPS);
    }

    print_header();
    for (i = 0; i < nwin; ++i) {
        if (metrics_compute(&log, &windows[i], &measured[shown]) != 0) {
            continue;                   /* реакції немає — рядок нічого не скаже */
        }
        print_row(shown + 1, &measured[shown], &windows[i]);
        if (windows[i].distorted == 0) {
            clean[nclean++] = measured[shown];
        }
        shown++;
    }

    if (shown == 0) {
        printf("\n  жодна сходинка не дала вимірної реакції\n\n");
        flightlog_free(&log);
        return 1;
    }
    if (nclean == 0) {
        printf("\n  усі сходинки спотворені кліпінгом або просіданням АКБ:\n"
               "  вердикту не буде, спершу приберіть причину\n\n");
        flightlog_free(&log);
        return 1;
    }

    if (metrics_median(clean, nclean, &summary) != 0) {
        fprintf(stderr, "не вдалося звести серію\n");
        flightlog_free(&log);
        return 1;
    }
    print_verdict(&summary, nclean);

    flightlog_free(&log);
    return 0;
}

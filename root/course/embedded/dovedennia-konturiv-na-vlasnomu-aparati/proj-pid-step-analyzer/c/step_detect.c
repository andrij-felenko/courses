#include "step_detect.h"

#include <math.h>
#include <string.h>

DetectConfig detect_default_config(double vbat_cutoff)
{
    DetectConfig c;
    c.edge_slope_min = 600.0;    /* повільніший рух стіка резонансів не збуджує */
    c.edge_min_amp   = 40.0;
    c.edge_max_ms    = 30.0;
    c.quiet_ms       = 80.0;
    c.quiet_err_max  = 15.0;
    c.plateau_ms     = 150.0;
    c.plateau_tol    = 5.0;      /* тремтіння рук на утриманому стіку */
    c.analysis_ms    = 250.0;
    c.gyro_clip      = 2000.0;
    c.vbat_cutoff    = vbat_cutoff;
    return c;
}

static double us_between(const FlightLog *log, size_t a, size_t b)
{
    return (double)(log->s[b].t_us - log->s[a].t_us);
}

/* Друга ступінь фільтрації: 80 мс до фронту апарат має йти за завданням.
   Якщо він ще дзвенить після попереднього фліпу, накладені коливання
   зіпсують і перерегулювання, і час встановлення. */
static int quiescent_before(const FlightLog *log, size_t edge, const DetectConfig *cfg,
                            size_t *quiet_begin)
{
    double window_us = cfg->quiet_ms * 1000.0;
    size_t i = edge;
    size_t k;

    while (i > 0 && us_between(log, i - 1, edge) <= window_us) {
        i--;
    }
    if (us_between(log, i, edge) < window_us * 0.9) {
        return 0;                       /* передісторії в лозі просто немає */
    }
    for (k = i; k <= edge; ++k) {
        if (fabs(log->s[k].setpoint - log->s[k].gyro) > cfg->quiet_err_max) {
            return 0;
        }
    }
    *quiet_begin = i;
    return 1;
}

/* Третя ступінь: завдання має простояти на новому рівні щонайменше plateau_ms.
   Вікно аналізу тягнемо далі, до analysis_ms, поки стік тримають. */
static int plateau_holds(const FlightLog *log, size_t edge_end, const DetectConfig *cfg,
                         size_t *end_out)
{
    double hold_us = cfg->plateau_ms * 1000.0;
    double full_us = cfg->analysis_ms * 1000.0;
    double level = log->s[edge_end].setpoint;
    size_t k = edge_end;

    while (k + 1 < log->count && us_between(log, edge_end, k + 1) <= full_us) {
        if (fabs(log->s[k + 1].setpoint - level) > cfg->plateau_tol) {
            break;
        }
        k++;
    }
    if (us_between(log, edge_end, k) < hold_us * 0.95) {
        return 0;                       /* стік смикнули назад — сходинка неповна */
    }
    *end_out = k;
    return 1;
}

static unsigned scan_distortion(const FlightLog *log, size_t from, size_t to,
                                const DetectConfig *cfg)
{
    unsigned flags = 0;
    size_t i;

    for (i = from; i <= to; ++i) {
        if (fabs(log->s[i].gyro) >= cfg->gyro_clip) {
            flags |= DIST_GYRO_CLIP;
        }
        if (log->s[i].vbat > 0.0 && log->s[i].vbat < cfg->vbat_cutoff) {
            flags |= DIST_VBAT_SAG;
        }
    }
    return flags;
}

size_t detect_steps(const FlightLog *log, const DetectConfig *cfg,
                    StepWindow *out, size_t max_out, DetectStats *stats)
{
    size_t found = 0;
    size_t i;

    memset(stats, 0, sizeof *stats);
    if (log->count < 3) {
        return 0;
    }

    for (i = 1; i + 1 < log->count && found < max_out; ++i) {
        double dt_s = us_between(log, i - 1, i) * 1e-6;
        double slope;
        double dir;
        double amp;
        size_t start;
        size_t j;
        size_t quiet_begin;
        size_t end;
        int edge_done = 0;

        if (dt_s <= 0.0) {
            continue;
        }
        /* Перша ступінь: фронт за швидкістю наростання завдання. */
        slope = (log->s[i].setpoint - log->s[i - 1].setpoint) / dt_s;
        if (fabs(slope) < cfg->edge_slope_min) {
            continue;
        }
        stats->edges++;

        dir = (slope > 0.0) ? 1.0 : -1.0;
        start = i - 1;
        j = i;
        while (j + 1 < log->count) {
            if ((log->s[j + 1].setpoint - log->s[j].setpoint) * dir <= 0.0) {
                edge_done = 1;          /* завдання зупинилось — фронт скінчився */
                break;
            }
            if (us_between(log, start, j + 1) > cfg->edge_max_ms * 1000.0) {
                break;                  /* стік їде далі: це плавний рух, не сходинка */
            }
            j++;
        }
        if (!edge_done) {
            stats->rejected_ramp++;
            i = j;
            continue;
        }

        amp = log->s[j].setpoint - log->s[start].setpoint;
        if (fabs(amp) < cfg->edge_min_amp) {
            stats->rejected_small++;
            i = j;
            continue;
        }
        if (!quiescent_before(log, start, cfg, &quiet_begin)) {
            stats->rejected_noisy++;
            i = j;
            continue;
        }
        if (!plateau_holds(log, j, cfg, &end)) {
            stats->rejected_plateau++;
            i = j;
            continue;
        }

        out[found].quiet_begin = quiet_begin;
        out[found].begin       = start;
        out[found].edge_end    = j;
        out[found].end         = end;
        out[found].amplitude   = amp;
        out[found].distorted   = scan_distortion(log, start, end, cfg);
        found++;

        i = end;                        /* наступну сходинку шукаємо за вікном */
    }

    return found;
}

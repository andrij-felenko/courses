#include "metrics.h"

#include <math.h>
#include <stdlib.h>
#include <string.h>

#define PI              3.14159265358979323846
#define D_NOISE_FC_HZ   30.0    /* усе, що вище, вважаємо шумом D-терма */
#define PLATEAU_SKIP_US 50000.0 /* перші 50 мс плато ще зайняті перехідним процесом */
#define MEDIAN_MAX      256

static double us_between(const FlightLog *log, size_t a, size_t b)
{
    return (double)(log->s[b].t_us - log->s[a].t_us);
}

static double clamp01(double v)
{
    if (v < 0.0) return 0.0;
    if (v > 1.0) return 1.0;
    return v;
}

/* Мить перетину рівня level, лінійно між сусідніми відліками: на 8 кГц лозі
   крок 125 мкс, і без інтерполяції час наростання квантується так грубо,
   що різниця між добрим і перетюненим контуром губиться. */
static int first_cross(const FlightLog *log, size_t from, size_t to,
                       double level, double dir, double *t_us)
{
    size_t i;

    for (i = from + 1; i <= to; ++i) {
        double prev = log->s[i - 1].gyro;
        double cur  = log->s[i].gyro;

        if ((cur - level) * dir >= 0.0 && (prev - level) * dir < 0.0) {
            double span = cur - prev;
            double frac = (span != 0.0) ? clamp01((level - prev) / span) : 0.0;
            *t_us = (double)log->s[i - 1].t_us + frac * us_between(log, i - 1, i);
            return 1;
        }
    }
    return 0;
}

static void measure_settling(const FlightLog *log, const StepWindow *w,
                             double target, double band, double t0_us, StepMetrics *m)
{
    size_t last_out = w->begin;
    int ever_out = 0;
    size_t i;

    for (i = w->begin; i <= w->end; ++i) {
        if (fabs(log->s[i].gyro - target) > band) {
            last_out = i;
            ever_out = 1;
        }
    }
    if (!ever_out) {
        m->settling_time_ms = 0.0;
        m->settled = 1;
        return;
    }
    if (last_out == w->end) {
        /* До кінця вікна так і не заспокоївся: віддаємо нижню оцінку. */
        m->settling_time_ms = ((double)log->s[w->end].t_us - t0_us) / 1000.0;
        m->settled = 0;
        return;
    }
    {
        double a = log->s[last_out].gyro;
        double b = log->s[last_out + 1].gyro;
        double edge = target + ((a > target) ? band : -band);
        double frac = (b != a) ? clamp01((edge - a) / (b - a)) : 1.0;
        double t_cross = (double)log->s[last_out].t_us + frac * us_between(log, last_out, last_out + 1);

        m->settling_time_ms = (t_cross - t0_us) / 1000.0;
        m->settled = 1;
    }
}

/* Шум D-терма: одно­полюсний ФНЧ дає «повільну» складову d_filtered,
   а нас цікавить середньоквадратичний залишок d_out − d_filtered —
   саме та потужність, що гріє мідь статора, не рухаючи апарата. */
static void measure_d_noise(const FlightLog *log, const StepWindow *w, StepMetrics *m)
{
    double rc = 1.0 / (2.0 * PI * D_NOISE_FC_HZ);
    double filt;
    double sum_sq = 0.0;
    size_t n = 0;
    size_t p = w->edge_end;
    size_t i;

    while (p < w->end && us_between(log, w->edge_end, p) < PLATEAU_SKIP_US) {
        p++;
    }
    if (w->end < p + 16) {
        m->noise_measured = 0;
        return;
    }

    filt = log->s[p].d_term;
    for (i = p + 1; i <= w->end; ++i) {
        double dt = us_between(log, i - 1, i) * 1e-6;
        double alpha = dt / (dt + rc);
        double resid;

        if (alpha > 1.0) {
            alpha = 1.0;
        }
        filt += alpha * (log->s[i].d_term - filt);
        resid = log->s[i].d_term - filt;
        sum_sq += resid * resid;
        n++;
    }
    m->d_noise_rms = sqrt(sum_sq / (double)n);
    m->noise_measured = 1;
}

static void measure_ringing(const FlightLog *log, const StepWindow *w,
                            size_t peak_idx, double target, double dead, StepMetrics *m)
{
    int last_sign = 0;
    int crossings = 0;
    size_t i;

    for (i = peak_idx; i <= w->end; ++i) {
        double e = log->s[i].gyro - target;
        int sign;

        if (fabs(e) < dead) {
            continue;                   /* у мертвій зоні шум дав би десятки «перетинів» */
        }
        sign = (e > 0.0) ? 1 : -1;
        if (last_sign != 0 && sign != last_sign) {
            crossings++;
        }
        last_sign = sign;
    }
    m->ring_crossings = crossings;
}

int metrics_compute(const FlightLog *log, const StepWindow *w, StepMetrics *m)
{
    double base = 0.0;
    double target;
    double amp;
    double dir;
    double t0_us;
    double t5;
    double t10;
    double t90;
    double peak_excess = 0.0;
    size_t peak_idx;
    size_t i;
    size_t n = 0;

    memset(m, 0, sizeof *m);
    if (w->end <= w->edge_end || w->end - w->begin < 8) {
        return -1;
    }

    /* Базова лінія — середнє гіро на спокійній передісторії, а не один відлік:
       окремий відлік містить і турбулентність, і шум давача. */
    for (i = w->quiet_begin; i <= w->begin; ++i) {
        base += log->s[i].gyro;
        n++;
    }
    base /= (double)n;

    target = log->s[w->edge_end].setpoint;
    amp = target - base;
    if (fabs(amp) < 1e-6) {
        return -1;
    }
    dir = (amp > 0.0) ? 1.0 : -1.0;
    m->amplitude = amp;

    t0_us = (double)log->s[w->begin].t_us;

    if (!first_cross(log, w->begin, w->end, base + 0.05 * amp, dir, &t5)) {
        return -1;                      /* реакції немає взагалі — міряти нічого */
    }
    m->tau_ms = (t5 - t0_us) / 1000.0;

    if (first_cross(log, w->begin, w->end, base + 0.10 * amp, dir, &t10) &&
        first_cross(log, w->begin, w->end, base + 0.90 * amp, dir, &t90) && t90 > t10) {
        m->rise_time_ms = (t90 - t10) / 1000.0;
        m->reached_90 = 1;
    }

    /* Перший екстремум після фронту. Ділимо на амплітуду сходинки, а не на
       абсолютне завдання: маневр із ненульової кутової швидкості інакше дав би
       нісенітницю, а біля завдання ≈ 0 — ділення на нуль. */
    peak_idx = w->edge_end;
    for (i = w->edge_end; i <= w->end; ++i) {
        double excess = (log->s[i].gyro - target) * dir;

        if (excess > peak_excess) {
            peak_excess = excess;
            peak_idx = i;
        }
    }
    m->overshoot_pct = (peak_excess > 0.0) ? (peak_excess / fabs(amp)) * 100.0 : 0.0;

    measure_settling(log, w, target, 0.05 * fabs(amp), t0_us, m);
    measure_ringing(log, w, peak_idx, target, 0.02 * fabs(amp), m);
    measure_d_noise(log, w, m);

    return 0;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *)a;
    double y = *(const double *)b;

    if (x < y) return -1;
    if (x > y) return 1;
    return 0;
}

static double median_of(double *v, size_t n)
{
    qsort(v, n, sizeof *v, cmp_double);
    if (n % 2 == 1) {
        return v[n / 2];
    }
    return 0.5 * (v[n / 2 - 1] + v[n / 2]);
}

int metrics_median(const StepMetrics *m, size_t n, StepMetrics *out)
{
    double buf[MEDIAN_MAX];
    double ring[MEDIAN_MAX];
    size_t noise_n = 0;
    size_t i;

    if (n == 0 || n > MEDIAN_MAX) {
        return -1;
    }
    memset(out, 0, sizeof *out);

#define MEDIAN_FIELD(field)                                   \
    do {                                                      \
        for (i = 0; i < n; ++i) buf[i] = m[i].field;          \
        out->field = median_of(buf, n);                       \
    } while (0)

    MEDIAN_FIELD(amplitude);
    MEDIAN_FIELD(tau_ms);
    MEDIAN_FIELD(overshoot_pct);
    MEDIAN_FIELD(settling_time_ms);
#undef MEDIAN_FIELD

    /* Час наростання беремо лише зі сходинок, що справді дійшли до 90%. */
    {
        size_t k = 0;

        for (i = 0; i < n; ++i) {
            if (m[i].reached_90) {
                buf[k++] = m[i].rise_time_ms;
            }
        }
        if (k > 0) {
            out->rise_time_ms = median_of(buf, k);
            out->reached_90 = 1;
        }
    }
    for (i = 0; i < n; ++i) {
        if (m[i].noise_measured) {
            buf[noise_n++] = m[i].d_noise_rms;
        }
    }
    if (noise_n > 0) {
        out->d_noise_rms = median_of(buf, noise_n);
        out->noise_measured = 1;
    }
    out->settled = 1;
    for (i = 0; i < n; ++i) {
        ring[i] = (double)m[i].ring_crossings;
        if (!m[i].settled) {
            out->settled = 0;      /* хоч одна сходинка не згасла — це вже сигнал */
        }
    }
    out->ring_crossings = (int)(median_of(ring, n) + 0.5);
    return 0;
}

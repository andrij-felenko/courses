/* decibel_dsp.h — Акустичні та логарифмічні розрахунки на C99 */
#ifndef DECIBEL_DSP_H
#define DECIBEL_DSP_H

#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define DB_P0_AIR_PA       20.0e-6       /* Опорний тиск у повітрі: 20 мкПа */
#define DB_I0_AIR_W_M2     1.0e-12       /* Опорна інтенсивність: 1 пВт/м² */
#define DB_V0_DBU          0.7745966692  /* Опорна напруга 0 dBu (600 Ом, 1 мВт) */
#define DB_V0_DBV          1.0           /* Опорна напруга 0 dBV: 1.0 В */
#define DB_P0_DBM_W        1.0e-3        /* Опорна потужність 0 dBm: 1 мВт */

/* Часові константи детектора (секунди) */
#define DB_TIME_CONST_FAST 0.125         /* Fast: 125 мс */
#define DB_TIME_CONST_SLOW 1.000         /* Slow: 1000 мс */

/* Структура біквадратного цифрового фільтра Direct Form II Transposed */
typedef struct {
    double b0, b1, b2;
    double a1, a2;
    double s1, s2;
} biquad_filter_t;

/* Каскад зважувального фільтра A-weighting (3 біквадрати для fs = 48 кГц) */
typedef struct {
    biquad_filter_t stages[3];
} a_weighting_filter_t;

/* Структура детектора часового усереднення (Fast / Slow) */
typedef struct {
    double alpha;
    double mean_square;
} time_weighting_detector_t;

/* Базові логарифмічні перетворення */
static inline double db_from_power_ratio(double p, double p0) {
    if (p <= 0.0 || p0 <= 0.0) return -INFINITY;
    return 10.0 * log10(p / p0);
}

static inline double db_from_voltage_ratio(double v, double v0) {
    if (v <= 0.0 || v0 <= 0.0) return -INFINITY;
    return 20.0 * log10(v / v0);
}

static inline double power_ratio_from_db(double db) {
    return pow(10.0, db / 10.0);
}

static inline double voltage_ratio_from_db(double db) {
    return pow(10.0, db / 20.0);
}

/* Опорні шкали електроніки та радіотехніки */
static inline double voltage_to_dbu(double v_rms) {
    return db_from_voltage_ratio(v_rms, DB_V0_DBU);
}

static inline double dbu_to_voltage(double dbu) {
    return DB_V0_DBU * voltage_ratio_from_db(dbu);
}

static inline double voltage_to_dbv(double v_rms) {
    return db_from_voltage_ratio(v_rms, DB_V0_DBV);
}

static inline double dbv_to_voltage(double dbv) {
    return DB_V0_DBV * voltage_ratio_from_db(dbv);
}

static inline double power_to_dbm(double power_watts) {
    return db_from_power_ratio(power_watts, DB_P0_DBM_W);
}

static inline double dbm_to_power(double dbm) {
    return DB_P0_DBM_W * power_ratio_from_db(dbm);
}

static inline double voltage_to_dbm(double v_rms, double load_ohms) {
    if (load_ohms <= 0.0 || v_rms <= 0.0) return -INFINITY;
    double p_watts = (v_rms * v_rms) / load_ohms;
    return power_to_dbm(p_watts);
}

/* Акустичні розрахунки SPL */
static inline double pressure_to_spl(double p_rms_pa) {
    return db_from_voltage_ratio(p_rms_pa, DB_P0_AIR_PA);
}

static inline double spl_to_pressure(double spl_db) {
    return DB_P0_AIR_PA * voltage_ratio_from_db(spl_db);
}

/* Швидке наближення двійкового логарифма для цілих 32-бітних чисел */
static inline float fast_log2_u32(uint32_t val) {
    if (val == 0) return -128.0f;
    int clz = __builtin_clz(val);
    int exp = 31 - clz;
    float frac = (float)(val - (1u << exp)) / (float)(1u << exp);
    return (float)exp + (frac * (1.442695f - 0.442695f * frac));
}

static inline float fast_log10_u32(uint32_t val) {
    return fast_log2_u32(val) * 0.30102999566f;
}

/* Енергетичне підсумовування некогерентних джерел */
static inline double sum_noncoherent_spl(const double *levels_db, size_t count) {
    if (count == 0) return -INFINITY;
    double sum_linear = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_linear += pow(10.0, levels_db[i] / 10.0);
    }
    return 10.0 * log10(sum_linear);
}

/* Розрахунок RMS та SPL за масивом вибірок тиску */
static inline double calculate_rms(const double *samples, size_t count) {
    if (count == 0) return 0.0;
    double sum_sq = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_sq += samples[i] * samples[i];
    }
    return sqrt(sum_sq / (double)count);
}

/* Ініціалізація A-weighting фільтра для частоти дискретизації fs = 48 кГц */
static inline void a_weighting_init_48k(a_weighting_filter_t *f) {
    f->stages[0].b0 = 0.169994948147430;
    f->stages[0].b1 = 0.339989896294859;
    f->stages[0].b2 = 0.169994948147430;
    f->stages[0].a1 = -0.270409810398048;
    f->stages[0].a2 = -0.050478631380962;
    f->stages[0].s1 = 0.0;
    f->stages[0].s2 = 0.0;

    f->stages[1].b0 = 1.0;
    f->stages[1].b1 = -2.0;
    f->stages[1].b2 = 1.0;
    f->stages[1].a1 = -1.990047454833980;
    f->stages[1].a2 = 0.990072166948332;
    f->stages[1].s1 = 0.0;
    f->stages[1].s2 = 0.0;

    f->stages[2].b0 = 1.0;
    f->stages[2].b1 = 2.0;
    f->stages[2].b2 = 1.0;
    f->stages[2].a1 = -0.485685718742828;
    f->stages[2].a2 = 0.000000000000000;
    f->stages[2].s1 = 0.0;
    f->stages[2].s2 = 0.0;
}

/* Фільтрація однієї вибірки через A-weighting */
static inline double a_weighting_process_sample(a_weighting_filter_t *f, double in) {
    double x = in;
    for (int i = 0; i < 3; ++i) {
        biquad_filter_t *st = &f->stages[i];
        double out = st->b0 * x + st->s1;
        st->s1 = st->b1 * x - st->a1 * out + st->s2;
        st->s2 = st->b2 * x - st->a2 * out;
        x = out;
    }
    return x;
}

/* Ініціалізація детектора часового зважування Fast/Slow */
static inline void time_detector_init(time_weighting_detector_t *det, double tau_sec, double fs_hz) {
    det->alpha = 1.0 - exp(-1.0 / (fs_hz * tau_sec));
    det->mean_square = 0.0;
}

/* Оновлення детектора часового зважування однією вибіркою тиску (Па) */
static inline double time_detector_update(time_weighting_detector_t *det, double sample_pa) {
    double x2 = sample_pa * sample_pa;
    det->mean_square = (1.0 - det->alpha) * det->mean_square + det->alpha * x2;
    double p_rms = sqrt(det->mean_square);
    return pressure_to_spl(p_rms);
}

#endif /* DECIBEL_DSP_H */

#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#define CIE_V_MIN_NM 380
#define CIE_V_MAX_NM 780
#define CIE_V_STEP_NM 5
#define CIE_V_POINTS  81

static const double KM_PHOTOPIC = 683.002; /* лм/Вт */

/* Таблиця CIE 1924 V(λ) з кроком 5 нм від 380 до 780 нм */
static const double CIE_V_LAMBDA[CIE_V_POINTS] = {
    0.000039, 0.000064, 0.000120, 0.000217, 0.000396, /* 380-400 */
    0.000640, 0.001210, 0.002180, 0.004000, 0.007300, /* 405-425 */
    0.011600, 0.016840, 0.023000, 0.029800, 0.038000, /* 430-450 */
    0.048000, 0.060000, 0.073900, 0.090980, 0.112600, /* 455-475 */
    0.139020, 0.169300, 0.208020, 0.258600, 0.323000, /* 480-500 */
    0.407300, 0.503000, 0.608200, 0.710000, 0.793200, /* 505-525 */
    0.862000, 0.914850, 0.954000, 0.980300, 0.994950, /* 530-550 */
    1.000000, 0.995000, 0.978600, 0.952000, 0.915400, /* 555-575 */
    0.870000, 0.816300, 0.757000, 0.694900, 0.631000, /* 580-600 */
    0.566800, 0.503000, 0.441200, 0.381000, 0.321000, /* 605-625 */
    0.265000, 0.217000, 0.175000, 0.138200, 0.107000, /* 630-650 */
    0.081600, 0.061000, 0.044580, 0.032000, 0.023200, /* 655-675 */
    0.017000, 0.011920, 0.008210, 0.005723, 0.004102, /* 680-700 */
    0.002929, 0.002091, 0.001484, 0.001047, 0.000740, /* 705-725 */
    0.000520, 0.000361, 0.000249, 0.000172, 0.000120, /* 730-750 */
    0.000085, 0.000059, 0.000041, 0.000029, 0.000020, /* 755-775 */
    0.000015                                          /* 780 */
};

typedef struct {
    double wavelength_nm; /* Довжина хвилі в нанометрах */
    double spectral_power; /* Вт/нм або Вт/(м²·нм) */
} SpectralSample;

typedef struct {
    double radiant_flux_w;      /* Радіометрична потужність (Вт) */
    double luminous_flux_lm;    /* Світловий потік (лм) або освітленість (лк) */
    double luminous_efficacy;   /* Світлова віддача (лм/Вт) */
} PhotometricResult;

/* Лінійна інтерполяція табличної функції V(lambda) */
static double interpolate_v_lambda(double wavelength_nm) {
    if (wavelength_nm < (double)CIE_V_MIN_NM || wavelength_nm > (double)CIE_V_MAX_NM) {
        return 0.0;
    }
    double pos = (wavelength_nm - CIE_V_MIN_NM) / (double)CIE_V_STEP_NM;
    int idx = (int)pos;
    if (idx >= CIE_V_POINTS - 1) {
        return CIE_V_LAMBDA[CIE_V_POINTS - 1];
    }
    double frac = pos - (double)idx;
    return CIE_V_LAMBDA[idx] * (1.0 - frac) + CIE_V_LAMBDA[idx + 1] * frac;
}

/* Обчислення фотометричного результату методом трапецій */
bool calculate_photometry(const SpectralSample samples[], size_t count, PhotometricResult *result) {
    if (!samples || count < 2 || !result) {
        return false;
    }

    double total_radiant_flux = 0.0;
    double total_weighted_integral = 0.0;

    for (size_t i = 0; i < count - 1; ++i) {
        double w1 = samples[i].wavelength_nm;
        double w2 = samples[i + 1].wavelength_nm;
        double dw = w2 - w1;

        if (dw <= 0.0) {
            return false; /* Порушення монотонності спектра */
        }

        double p1 = samples[i].spectral_power;
        double p2 = samples[i + 1].spectral_power;

        /* Радіометричний інтеграл повної потужності */
        total_radiant_flux += 0.5 * (p1 + p2) * dw;

        /* Фотометричний інтеграл зі зважуванням за кривою V(lambda) */
        double v1 = interpolate_v_lambda(w1);
        double v2 = interpolate_v_lambda(w2);
        total_weighted_integral += 0.5 * (p1 * v1 + p2 * v2) * dw;
    }

    result->radiant_flux_w = total_radiant_flux;
    result->luminous_flux_lm = KM_PHOTOPIC * total_weighted_integral;
    result->luminous_efficacy = (total_radiant_flux > 1e-12)
        ? (result->luminous_flux_lm / total_radiant_flux)
        : 0.0;

    return true;
}

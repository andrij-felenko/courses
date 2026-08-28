#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define C_SPEED 299792458.0 /* швидкість світла у м/с */

/* Структура вхідних параметрів параболічної антени */
typedef struct {
    double diameter_m;     /* діаметр рефлектора у метрах */
    double freq_hz;        /* робоча частота у герцах */
    double eta_aperture;   /* апертурна ефективність (0.5..0.8) */
    double rms_error_m;    /* шорсткість поверхні ε_rms у метрах */
} ParabolicDishConfig;

/* Структура обчислених характеристик */
typedef struct {
    double wavelength_m;   /* довжина хвилі λ */
    double aperture_area;  /* геометрична площа A = π D² / 4 */
    double eff_area;       /* ефективна площа A_eff = η_a · A */
    double directivity_iso;/* спрямованість D₀ (безрозмірна) */
    double gain_dbi_ideal; /* підсилення без втрат поверхні (dBi) */
    double ruze_efficiency;/* коефіцієнт Рузе η_r */
    double gain_dbi_real;  /* реальне підсилення з урахуванням Рузе (dBi) */
    double hpbw_deg;       /* ширина променя за рівнем -3 dB (градуси) */
    double first_null_deg; /* кут першого нуля (градуси) */
} ParabolicDishResults;

/* Поліноміальне наближення функції Бесселя першого роду J1(x) */
static double bessel_j1(double x) {
    double ax = fabs(x);
    if (ax < 3.75) {
        double y = (x / 3.75) * (x / 3.75);
        return x * (0.5 + y * (-0.56249985 + y * (0.21093573 + y * (-0.03954289 + y * 0.00443319))));
    } else {
        double y = 3.75 / ax;
        double f1 = 0.79788456 + y * (-0.00000077 + y * (-0.00552740 + y * 0.00009512)));
        double theta1 = ax - 2.35619449 + y * (0.00000257 + y * (0.00552740 + y * (0.00009512)));
        return (1.0 / sqrt(ax)) * f1 * cos(theta1) * (x < 0 ? -1.0 : 1.0);
    }
}

/* Обчислення характеристик антени */
bool calculate_dish_performance(const ParabolicDishConfig *cfg, ParabolicDishResults *res) {
    if (!cfg || !res || cfg->diameter_m <= 0.0 || cfg->freq_hz <= 0.0) {
        return false;
    }

    res->wavelength_m = C_SPEED / cfg->freq_hz;
    res->aperture_area = (M_PI * cfg->diameter_m * cfg->diameter_m) / 4.0;
    res->eff_area = cfg->eta_aperture * res->aperture_area;

    /* Пряма спрямованість D₀ = (π D / λ)² */
    double ratio = (M_PI * cfg->diameter_m) / res->wavelength_m;
    res->directivity_iso = ratio * ratio;

    /* Підсилення в dBi: G_ideal = 10 log10(η_a · D₀) */
    double gain_lin_ideal = cfg->eta_aperture * res->directivity_iso;
    res->gain_dbi_ideal = 10.0 * log10(gain_lin_ideal);

    /* Формула Рузе: η_r = exp( -(4 π ε / λ)² ) */
    double phase_err = (4.0 * M_PI * cfg->rms_error_m) / res->wavelength_m;
    res->ruze_efficiency = exp(-(phase_err * phase_err));
    res->gain_dbi_real = res->gain_dbi_ideal + 10.0 * log10(res->ruze_efficiency);

    /* Кути променя у градусах */
    res->hpbw_deg = 70.0 * (res->wavelength_m / cfg->diameter_m);
    res->first_null_deg = 1.22 * (res->wavelength_m / cfg->diameter_m) * (180.0 / M_PI);

    return true;
}

/* Обчислення нормованого підсилення у напрямку кута theta_deg (dBi) */
double evaluate_pattern_db(const ParabolicDishConfig *cfg, const ParabolicDishResults *res, double theta_deg) {
    if (fabs(theta_deg) < 1e-6) {
        return res->gain_dbi_real;
    }

    double theta_rad = theta_deg * (M_PI / 180.0);
    double u = (M_PI * cfg->diameter_m / res->wavelength_m) * sin(theta_rad);

    double field_norm = fabs(2.0 * bessel_j1(u) / u);
    if (field_norm < 1e-4) {
        field_norm = 1e-4; /* нижня межа -80 dB */
    }

    double pattern_relative_db = 20.0 * log10(field_norm);
    return res->gain_dbi_real + pattern_relative_db;
}

int main(void) {
    ParabolicDishConfig dish = {
        .diameter_m = 1.2,      /* 1.2 метри (типова супутникова тарілка) */
        .freq_hz = 12.0e9,      /* 12 ГГц (Ku-діапазон) */
        .eta_aperture = 0.60,   /* 60% апертурна ефективність */
        .rms_error_m = 0.0008   /* 0.8 мм шорсткість поверхні */
    };

    ParabolicDishResults res;
    if (!calculate_dish_performance(&dish, &res)) {
        fprintf(stderr, "Помилка розрахунку параметрів антени!\n");
        return 1;
    }

    printf("=== РЕЗУЛЬТАТИ РОЗРАХУНКУ ПАРАБОЛІЧНОЇ АНТЕНИ ===\n");
    printf("Діаметр: %.2f м, Частота: %.2f ГГц (λ = %.2f см)\n", 
           dish.diameter_m, dish.freq_hz / 1e9, res.wavelength_m * 100.0);
    printf("Геометрична площа: %.3f м², Ефективна площа: %.3f м²\n", 
           res.aperture_area, res.eff_area);
    printf("Ідеальне підсилення: %.2f dBi\n", res.gain_dbi_ideal);
    printf("Ефективність Рузе (ε = %.2f мм): %.1f%%\n", 
           dish.rms_error_m * 1000.0, res.ruze_efficiency * 100.0);
    printf("Реальне підсилення з урахуванням втрат: %.2f dBi\n", res.gain_dbi_real);
    printf("Ширина променя HPBW (-3 dB): %.2f°\n", res.hpbw_deg);
    printf("Кут першого нуля: %.2f°\n\n", res.first_null_deg);

    printf("--- ЗРІЗ ДІАГРАМИ СПРЯМОВАНОСТІ (Кут vs Підсилення) ---\n");
    for (double theta = -3.0; theta <= 3.0; theta += 0.5) {
        double g_dir = evaluate_pattern_db(&dish, &res, theta);
        printf("Кут %5.1f° : %6.2f dBi  [%6.2f dB відносно осі]\n", 
               theta, g_dir, g_dir - res.gain_dbi_real);
    }

    return 0;
}

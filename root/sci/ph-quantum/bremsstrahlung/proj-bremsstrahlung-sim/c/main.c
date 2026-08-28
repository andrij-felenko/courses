#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PLANCK_H 6.62607015e-34    /* Стала Планка (Дж·с) */
#define SPEED_LIGHT 299792458.0     /* Швидкість світла (м/с) */
#define ELEC_CHARGE 1.602176634e-19 /* Заряд електрона (Кл) */

typedef struct {
    double energy_kev;          /* Енергія фотона (кеВ) */
    double wavelength_nm;       /* Довжина хвилі (нм) */
    double raw_intensity;       /* Первинна інтенсивність за Крамерсом (Вт/кеВ) */
    double filtered_intensity;  /* Інтенсивність після фільтрації (Вт/кеВ) */
} SpectrumPoint;

typedef struct {
    SpectrumPoint *points;
    size_t count;
    double lambda_min_nm;
    double total_power_watts;
} XRaySpectrum;

/* Обчислення короткохвильової межі Дуана — Ганта (нм) */
double get_duane_hunt_limit_nm(double voltage_kv) {
    if (voltage_kv <= 0.0) return 0.0;
    double voltage_volts = voltage_kv * 1000.0;
    double lambda_m = (PLANCK_H * SPEED_LIGHT) / (ELEC_CHARGE * voltage_volts);
    return lambda_m * 1e9; /* Переведення м -> нм */
}

/* Модель коефіцієнта фотоелектричного поглинання алюмінію (см^-1) */
double get_aluminum_attenuation(double energy_kev) {
    if (energy_kev <= 0.1) return 1000.0;
    /* Наближена формула масового коефіцієнта поглинання mu ~ E^-2.8 */
    double mu_per_cm = 500.0 * pow(10.0 / energy_kev, 2.8);
    return mu_per_cm;
}

/* Генерація спектра рентгенівського випромінювання */
XRaySpectrum* generate_xray_spectrum(double voltage_kv, double current_ma, double target_z,
                                     double al_filter_mm, size_t num_bins) {
    if (voltage_kv <= 0.0 || current_ma <= 0.0 || num_bins == 0) return NULL;

    XRaySpectrum *spec = (XRaySpectrum*)malloc(sizeof(XRaySpectrum));
    if (!spec) return NULL;

    spec->count = num_bins;
    spec->points = (SpectrumPoint*)malloc(num_bins * sizeof(SpectrumPoint));
    if (!spec->points) {
        free(spec);
        return NULL;
    }

    spec->lambda_min_nm = get_duane_hunt_limit_nm(voltage_kv);
    spec->total_power_watts = 0.0;

    double max_energy_kev = voltage_kv;
    double step_kev = max_energy_kev / (double)num_bins;
    double filter_cm = al_filter_mm / 10.0;

    /* Константа Крамерса C_K ≈ 1e-9 V^-1 */
    double k_cramers = 1e-9;

    for (size_t i = 0; i < num_bins; ++i) {
        double energy = (i + 0.5) * step_kev;
        double wavelength = (1239.84 / energy); /* нм */

        spec->points[i].energy_kev = energy;
        spec->points[i].wavelength_nm = wavelength;

        /* Модель Крамерса: dI/dE ~ Z * I_e * (E_max - E) */
        if (energy <= max_energy_kev) {
            double raw_i = k_cramers * target_z * (current_ma * 1e-3) * (max_energy_kev - energy);
            spec->points[i].raw_intensity = (raw_i > 0.0) ? raw_i : 0.0;
        } else {
            spec->points[i].raw_intensity = 0.0;
        }

        /* Закон Бугера — Ламберта — Бера: I = I0 * exp(-mu * d) */
        double mu = get_aluminum_attenuation(energy);
        double transmission = exp(-mu * filter_cm);
        spec->points[i].filtered_intensity = spec->points[i].raw_intensity * transmission;

        spec->total_power_watts += spec->points[i].filtered_intensity * step_kev;
    }

    return spec;
}

void free_xray_spectrum(XRaySpectrum *spec) {
    if (spec) {
        if (spec->points) free(spec->points);
        free(spec);
    }
}

int main(void) {
    double voltage_kv = 50.0;  /* 50 кВ */
    double current_ma = 10.0;  /* 10 мА */
    double target_z = 74.0;    /* Вольфрам */
    double filter_mm = 1.5;    /* 1.5 мм Al */

    XRaySpectrum *spec = generate_xray_spectrum(voltage_kv, current_ma, target_z, filter_mm, 10);
    if (!spec) {
        fprintf(stderr, "Помилка виділення пам'яті.\n");
        return 1;
    }

    printf("=== Спектр гальмівного випромінювання ===\n");
    printf("Напруга: %.1f кВ, Струм: %.1f мА, Анод: Z=%.0f\n", voltage_kv, current_ma, target_z);
    printf("Межа Дуана — Ганта λ_min: %.4f нм\n\n", spec->lambda_min_nm);
    printf("%-12s %-12s %-18s %-18s\n", "Енергія(кеВ)", "Довжина(нм)", "Первинна(Вт/кеВ)", "Фільтрована(Вт/кеВ)");

    for (size_t i = 0; i < spec->count; ++i) {
        printf("%-12.2f %-12.4f %-18.6e %-18.6e\n",
               spec->points[i].energy_kev,
               spec->points[i].wavelength_nm,
               spec->points[i].raw_intensity,
               spec->points[i].filtered_intensity);
    }

    printf("\nЗагальна випромінена потужність: %.6f Вт\n", spec->total_power_watts);

    free_xray_spectrum(spec);
    return 0;
}

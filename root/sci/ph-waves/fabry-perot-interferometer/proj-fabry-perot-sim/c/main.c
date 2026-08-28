#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846
#define SPEED_OF_LIGHT 299792458.0

typedef struct {
    double gap_d;         /* Відстань між дзеркалами у метрах */
    double ref_index;     /* Показник заломлення */
    double reflectivity;  /* Коефіцієнт відбиття R */
} fabry_perot_config_t;

typedef struct {
    double fsr_freq_hz;
    double fsr_wavelength_m;
    double finesse;
    double fwhm_wavelength_m;
    double f_coeff;
} fabry_perot_metrics_t;

/* Обчислення інтегральних метрик інтерферометра */
fabry_perot_metrics_t calculate_metrics(const fabry_perot_config_t *cfg, double center_lambda_m) {
    fabry_perot_metrics_t m;
    double R = cfg->reflectivity;
    double n = cfg->ref_index;
    double d = cfg->gap_d;

    m.fsr_freq_hz = SPEED_OF_LIGHT / (2.0 * n * d);
    m.fsr_wavelength_m = (center_lambda_m * center_lambda_m) / (2.0 * n * d);
    m.f_coeff = (4.0 * R) / ((1.0 - R) * (1.0 - R));
    m.finesse = (PI * sqrt(R)) / (1.0 - R);
    m.fwhm_wavelength_m = m.fsr_wavelength_m / m.finesse;

    return m;
}

/* Обчислення пропускання Ейрі для конкретної довжини хвилі та кута падіння */
double calculate_airy_transmission(const fabry_perot_config_t *cfg, double lambda_m, double theta_rad) {
    double delta = (4.0 * PI * cfg->ref_index * cfg->gap_d * cos(theta_rad)) / lambda_m;
    double sin_half = sin(delta / 2.0);
    double f_coeff = (4.0 * cfg->reflectivity) / ((1.0 - cfg->reflectivity) * (1.0 - cfg->reflectivity));
    
    return 1.0 / (1.0 + f_coeff * sin_half * sin_half);
}

/* Генерація спектрального масиву інтенсивностей */
int generate_spectrum_array(const fabry_perot_config_t *cfg, double start_lambda, double end_lambda, 
                            int num_points, double *out_lambdas, double *out_intensities) {
    if (!cfg || !out_lambdas || !out_intensities || num_points <= 1) {
        return -1;
    }

    double step = (end_lambda - start_lambda) / (num_points - 1);
    for (int i = 0; i < num_points; ++i) {
        out_lambdas[i] = start_lambda + i * step;
        out_intensities[i] = calculate_airy_transmission(cfg, out_lambdas[i], 0.0);
    }
    return 0;
}

/* Симуляція спектра проходження та вивід ASCII-графіка */
void simulate_spectrum_ascii(const fabry_perot_config_t *cfg, double lambda_start, double lambda_end, int steps) {
    double center_lambda = (lambda_start + lambda_end) / 2.0;
    fabry_perot_metrics_t metrics = calculate_metrics(cfg, center_lambda);

    printf("=== МЕТРИКИ РЕЗОНАТОРА ФАБРІ — ПЕРО ===\n");
    printf("Товщина проміжку d: %.4f мм\n", cfg->gap_d * 1e3);
    printf("Коефіцієнт відбиття R: %.2f%%\n", cfg->reflectivity * 100.0);
    printf("FSR (частотний): %.3f ГГц\n", metrics.fsr_freq_hz / 1e9);
    printf("FSR (за довжиною хвилі): %.4f нм\n", metrics.fsr_wavelength_m * 1e9);
    printf("Різкість (Finesse F): %.2f\n", metrics.finesse);
    printf("FWHM піку: %.5f нм\n\n", metrics.fwhm_wavelength_m * 1e9);

    printf("=== СПЕКТР ПРОПУСКАННЯ (ASCII) ===\n");
    double step_size = (lambda_end - lambda_start) / (steps - 1);
    for (int i = 0; i < steps; ++i) {
        double current_lambda = lambda_start + i * step_size;
        double transmission = calculate_airy_transmission(cfg, current_lambda, 0.0);
        
        int bar_length = (int)(transmission * 40.0);
        printf("%8.3f нм | ", current_lambda * 1e9);
        for (int b = 0; b < bar_length; ++b) {
            putchar('#');
        }
        printf(" (%.1f%%)\n", transmission * 100.0);
    }
}

int main(void) {
    fabry_perot_config_t config = {
        .gap_d = 0.5e-3,       /* 0.5 мм проміжок */
        .ref_index = 1.0,      /* повітряний проміжок */
        .reflectivity = 0.85   /* R = 85% */
    };

    /* Моделювання у діапазоні 632.0 нм - 633.0 нм (гелій-неоновий лазер) */
    simulate_spectrum_ascii(&config, 632.0e-9, 633.0e-9, 21);

    return 0;
}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef enum {
    END_CORRECTION_UNFLANGED, // Вільний торець (0.6133 * r)
    END_CORRECTION_FLANGED    // Фланцевий торець (0.8488 * r)
} end_correction_type_t;

typedef struct {
    double cavity_volume_m3;    // Об'єм каверни V (м³)
    double neck_length_m;       // Фізична довжина шийки L (м)
    double neck_radius_m;       // Радіус шийки r (м)
    double air_density_kg_m3;   // Густина повітря ρ (кг/м³)
    double sound_speed_m_s;     // Швидкість звуку c (м/с)
    double air_viscosity_pa_s;  // Динамічна в'язкість μ (Па·с)
    end_correction_type_t inner_end;
    end_correction_type_t outer_end;
} helmholtz_config_t;

typedef struct {
    double area_m2;             // Площа перерізу шийки S (м²)
    double delta_l_in_m;        // Внутрішня кінцева поправка (м)
    double delta_l_out_m;       // Зовнішня кінцева поправка (м)
    double effective_length_m;  // Ефективна довжина L_eff (м)
    double acoustic_mass;       // Акустична маса M_A (кг/м⁴)
    double acoustic_compliance; // Акустична гнучкість C_A (м⁵/Н)
    double resonance_freq_hz;   // Власна частота f_H (Гц)
    double quality_factor_q;    // Добротність Q
} helmholtz_result_t;

typedef struct {
    double frequency_hz;
    double real_impedance_pa_s_m3; // Активний опір R_A
    double imag_reactance_pa_s_m3; // Реактивний опір X_A
    double impedance_magnitude;    // Модуль імпедансу |Z_A|
    double absorption_coeff;       // Коефіцієнт поглинання α
} helmholtz_spectrum_point_t;

static double get_end_correction(double radius, end_correction_type_t type) {
    if (type == END_CORRECTION_FLANGED) {
        return 0.848826 * radius;
    }
    return 0.613300 * radius;
}

bool helmholtz_analyze(const helmholtz_config_t* cfg, helmholtz_result_t* res) {
    if (!cfg || !res) return false;
    if (cfg->cavity_volume_m3 <= 0.0 || cfg->neck_radius_m <= 0.0 || cfg->sound_speed_m_s <= 0.0) {
        return false;
    }

    res->area_m2 = M_PI * cfg->neck_radius_m * cfg->neck_radius_m;
    res->delta_l_in_m = get_end_correction(cfg->neck_radius_m, cfg->inner_end);
    res->delta_l_out_m = get_end_correction(cfg->neck_radius_m, cfg->outer_end);
    res->effective_length_m = cfg->neck_length_m + res->delta_l_in_m + res->delta_l_out_m;

    res->acoustic_mass = (cfg->air_density_kg_m3 * res->effective_length_m) / res->area_m2;
    res->acoustic_compliance = cfg->cavity_volume_m3 / (cfg->air_density_kg_m3 * cfg->sound_speed_m_s * cfg->sound_speed_m_s);

    double omega0 = 1.0 / sqrt(res->acoustic_mass * res->acoustic_compliance);
    res->resonance_freq_hz = omega0 / (2.0 * M_PI);

    // Втрати випромінювання та в'язкості на резонансій частоті
    double r_rad = (cfg->air_density_kg_m3 * omega0 * omega0) / (2.0 * M_PI * cfg->sound_speed_m_s);
    double r_visc = (sqrt(2.0 * cfg->air_density_kg_m3 * cfg->air_viscosity_pa_s * omega0) / 
                    (M_PI * cfg->neck_radius_m * cfg->neck_radius_m * cfg->neck_radius_m)) * res->effective_length_m;
    double r_total = r_rad + r_visc;

    res->quality_factor_q = (omega0 * res->acoustic_mass) / r_total;

    return true;
}

void helmholtz_calculate_spectrum(const helmholtz_config_t* cfg,
                                 const helmholtz_result_t* res,
                                 double start_freq_hz, double end_freq_hz, size_t num_points,
                                 helmholtz_spectrum_point_t* spectrum) {
    if (!cfg || !res || !spectrum || num_points == 0) return;

    double z_characteristic = (cfg->air_density_kg_m3 * cfg->sound_speed_m_s) / res->area_m2;

    for (size_t i = 0; i < num_points; ++i) {
        double f = start_freq_hz + (end_freq_hz - start_freq_hz) * ((double)i / (double)(num_points - 1));
        double omega = 2.0 * M_PI * f;

        double r_rad = (cfg->air_density_kg_m3 * omega * omega) / (2.0 * M_PI * cfg->sound_speed_m_s);
        double r_visc = (sqrt(2.0 * cfg->air_density_kg_m3 * cfg->air_viscosity_pa_s * omega) / 
                        (M_PI * cfg->neck_radius_m * cfg->neck_radius_m * cfg->neck_radius_m)) * res->effective_length_m;
        double r_total = r_rad + r_visc;

        double x_reactance = omega * res->acoustic_mass - (1.0 / (omega * res->acoustic_compliance));
        double z_mag = sqrt(r_total * r_total + x_reactance * x_reactance);

        // Коефіцієнт поглинання для бокового резонатора у трубі
        double alpha = (4.0 * r_total * z_characteristic) / 
                       ((2.0 * r_total + z_characteristic) * (2.0 * r_total + z_characteristic) + x_reactance * x_reactance);

        spectrum[i].frequency_hz = f;
        spectrum[i].real_impedance_pa_s_m3 = r_total;
        spectrum[i].imag_reactance_pa_s_m3 = x_reactance;
        spectrum[i].impedance_magnitude = z_mag;
        spectrum[i].absorption_coeff = alpha;
    }
}

int main(void) {
    helmholtz_config_t cfg = {
        .cavity_volume_m3 = 0.001,      // 1 літр (0.001 м³)
        .neck_length_m = 0.05,          // 5 см
        .neck_radius_m = 0.01,          // 1 см
        .air_density_kg_m3 = 1.204,     // 20 °C
        .sound_speed_m_s = 343.2,       // 20 °C
        .air_viscosity_pa_s = 1.81e-5,  // в'язкість повітря
        .inner_end = END_CORRECTION_FLANGED,
        .outer_end = END_CORRECTION_UNFLANGED
    };

    helmholtz_result_t res;
    if (!helmholtz_analyze(&cfg, &res)) {
        fprintf(stderr, "Помилка аналізу резонатора\n");
        return 1;
    }

    printf("=== Розрахунок резонатора Гельмгольца ===\n");
    printf("Об'єм каверни V:        %.2f см³\n", cfg.cavity_volume_m3 * 1e6);
    printf("Фізична довжина шийки L: %.2f см\n", cfg.neck_length_m * 100.0);
    printf("Радіус шийки r:         %.2f см\n", cfg.neck_radius_m * 100.0);
    printf("Ефективна довжина L_eff: %.2f см (ΔL_in=%.2f мм, ΔL_out=%.2f мм)\n",
           res.effective_length_m * 100.0, res.delta_l_in_m * 1000.0, res.delta_l_out_m * 1000.0);
    printf("Резонансна частота f_H:  %.2f Гц\n", res.resonance_freq_hz);
    printf("Добротність Q:          %.2f\n\n", res.quality_factor_q);

    const size_t num_points = 5;
    helmholtz_spectrum_point_t spectrum[5];
    helmholtz_calculate_spectrum(&cfg, &res, 100.0, 300.0, num_points, spectrum);

    printf("Частота (Гц) | Re(Z_A) (Па·с/м³) | Im(Z_A) (Па·с/м³) | |Z_A| | Поглинання α\n");
    printf("-------------------------------------------------------------------------\n");
    for (size_t i = 0; i < num_points; ++i) {
        printf("%12.1f | %17.2e | %17.2e | %5.2e | %12.4f\n",
               spectrum[i].frequency_hz,
               spectrum[i].real_impedance_pa_s_m3,
               spectrum[i].imag_reactance_pa_s_m3,
               spectrum[i].impedance_magnitude,
               spectrum[i].absorption_coeff);
    }

    return 0;
}

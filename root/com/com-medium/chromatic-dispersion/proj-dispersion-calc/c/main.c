#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// Параметри оптичного волокна
typedef struct {
    double zero_disp_wavelength_nm; // Точка нульової дисперсії λ₀ (напр. 1310.0 нм)
    double zero_disp_slope;         // Нахил дисперсії S₀ (напр. 0.092 пс/(нм²·км))
    double attenuation_db_km;       // Загасання α (напр. 0.20 дБ/км)
} FiberParams;

// Результати розрахунку траси
typedef struct {
    double dispersion_coeff;        // Коефіцієнт D(λ), пс/(нм·км)
    double accumulated_dispersion;  // Загальна накопичена дисперсія, пс/нм
    double pulse_broadening_ps;     // Часове розширення імпульсу Δt, пс
    double max_uncompensated_km;    // Максимальна дальність без компенсації, км
    bool dispersion_limit_exceeded; // Прапорець перевищення бюджету
} LinkDispersionResult;

// Емпіричний розрахунок D(λ) за стандартом ITU-T G.652
double calc_fiber_dispersion(const FiberParams* fiber, double wavelength_nm) {
    if (!fiber || wavelength_nm <= 0.0) return 0.0;
    
    double lambda0 = fiber->zero_disp_wavelength_nm;
    double s0 = fiber->zero_disp_slope;
    
    // Формула G.652: D(λ) = (S₀ / 4) * (λ - λ₀⁴ / λ³)
    double lambda_ratio = pow(lambda0, 4.0) / pow(wavelength_nm, 3.0);
    return (s0 / 4.0) * (wavelength_nm - lambda_ratio);
}

// Розрахунок аналізу дисперсійного бюджету траси
bool analyze_link_dispersion(const FiberParams* fiber,
                            double wavelength_nm,
                            double link_length_km,
                            double spectral_width_nm,
                            double bit_rate_gbps,
                            double max_allowed_dispersion_ps_nm,
                            LinkDispersionResult* out_result) {
    if (!fiber || !out_result || link_length_km <= 0.0) {
        return false;
    }

    double d_coeff = calc_fiber_dispersion(fiber, wavelength_nm);
    double accum_disp = d_coeff * link_length_km;
    
    // Часове розширення імпульсу Δt = |D| * Δλ * L
    double broadening_ps = fabs(d_coeff) * spectral_width_nm * link_length_km;
    
    // Оцінка граничної дальності за критерієм B² * |D| * L <= 104000 (для 1550 нм)
    // Або через затримку 25% від тривалості біта T_bit = 1000 / bit_rate_gbps
    double bit_period_ps = 1000.0 / bit_rate_gbps;
    double max_allowed_broadening_ps = 0.25 * bit_period_ps;
    
    double max_len_km = 0.0;
    if (fabs(d_coeff) > 1e-6 && spectral_width_nm > 1e-6) {
        max_len_km = max_allowed_broadening_ps / (fabs(d_coeff) * spectral_width_nm);
    }
    
    out_result->dispersion_coeff = d_coeff;
    out_result->accumulated_dispersion = accum_disp;
    out_result->pulse_broadening_ps = broadening_ps;
    out_result->max_uncompensated_km = max_len_km;
    out_result->dispersion_limit_exceeded = (fabs(accum_disp) > max_allowed_dispersion_ps_nm);

    return true;
}

// Розрахунок потрібної довжини волокна DCF для компенсації
double calc_dcf_required_length(double accum_disp_ps_nm, double dcf_disp_coeff_ps_nm_km) {
    if (fabs(dcf_disp_coeff_ps_nm_km) < 1e-6) return 0.0;
    // L_dcf = - D_accum / D_dcf
    return -accum_disp_ps_nm / dcf_disp_coeff_ps_nm_km;
}

int main(void) {
    // Стандартні параметри волокна SMF-28 (G.652.D)
    FiberParams smf28 = {
        .zero_disp_wavelength_nm = 1312.0,
        .zero_disp_slope = 0.090,
        .attenuation_db_km = 0.20
    };

    double wavelength = 1550.0;     // 1550 нм (C-band)
    double link_len = 80.0;         // 80 км траса
    double laser_linewidth = 0.1;   // DFB-лазер Δλ = 0.1 нм
    double bit_rate = 10.0;         // 10 Гбіт/с
    double sfp_max_cd = 800.0;      // Ліміт SFP+ ER = 800 пс/нм

    LinkDispersionResult res;
    if (analyze_link_dispersion(&smf28, wavelength, link_len, laser_linewidth, 
                                bit_rate, sfp_max_cd, &res)) {
        printf("=== Аналіз оптичної траси %.1f км (1550 нм) ===\n", link_len);
        printf("Коефіцієнт D(λ):          %.2f пс/(нм·км)\n", res.dispersion_coeff);
        printf("Накопичена дисперсія:     %.1f пс/нм\n", res.accumulated_dispersion);
        printf("Розширення імпульсу Δt:  %.2f пс\n", res.pulse_broadening_ps);
        printf("Макс. безкомпенс. дальність: %.1f км\n", res.max_uncompensated_km);
        printf("Перевищення бюджету CD:   %s\n", res.dispersion_limit_exceeded ? "ТАК (ПОТРІБНА КОМПЕНСАЦІЯ)" : "НІ");

        if (res.dispersion_limit_exceeded) {
            double dcf_coeff = -100.0; // Модуль DCF з D = -100 пс/(нм·км)
            double dcf_len = calc_dcf_required_length(res.accumulated_dispersion, dcf_coeff);
            printf("Необхідна довжина DCF:    %.2f км (при D_dcf = %.1f)\n", dcf_len, dcf_coeff);
        }
    }

    return 0;
}

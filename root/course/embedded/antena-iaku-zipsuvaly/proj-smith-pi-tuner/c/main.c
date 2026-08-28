#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define PI 3.14159265358979323846
#define Z0 50.0

typedef struct {
    double r;  // активний опір (Ом)
    double x;  // реактивний опір (Ом, + індуктивний, - ємнісний)
} ComplexZ;

typedef struct {
    double c_shunt_pf;    // паралельна ємність (пФ)
    double l_series_nh;   // послідовна індуктивність (нГн)
    double vswr_ideal;    // КСВ з теоретичними номіналами (1.0)
    double c_real_pf;     // підібраний номінал E24 (пФ)
    double l_real_nh;     // підібраний номінал E24 (нГн)
    double vswr_real;     // фактичний КСВ з компонентами E24
    double s11_db_real;   // фактичні зворотні втрати S11 (дБ)
    double refl_power_pct;// частка відбитої потужності (%)
} MatchingResult;

// Стандартний ряд номіналів E24 (мантиси)
static const double E24_VALUES[] = {
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1
};
#define E24_SIZE (sizeof(E24_VALUES) / sizeof(E24_VALUES[0]))

// Підбір найближчого значення зі стандартного ряду E24
static double quantize_to_e24(double val) {
    if (val <= 0.0) return 0.0;
    double exponent = floor(log10(val));
    double mantissa = val / pow(10.0, exponent);
    
    double best = E24_VALUES[0];
    double min_diff = fabs(mantissa - best);
    for (size_t i = 1; i < E24_SIZE; ++i) {
        double diff = fabs(mantissa - E24_VALUES[i]);
        if (diff < min_diff) {
            min_diff = diff;
            best = E24_VALUES[i];
        }
    }
    return best * pow(10.0, exponent);
}

// Розрахунок КСВ за комплексним імпедансом
static double calculate_vswr(ComplexZ z, double *out_s11_db) {
    double num_r = z.r - Z0;
    double num_x = z.x;
    double den_r = z.r + Z0;
    double den_x = z.x;
    
    double num_mag = sqrt(num_r * num_r + num_x * num_x);
    double den_mag = sqrt(den_r * den_r + den_x * den_x);
    if (den_mag == 0.0) return 999.0;
    
    double gamma = num_mag / den_mag;
    if (gamma >= 1.0) gamma = 0.9999;
    
    if (out_s11_db) {
        *out_s11_db = (gamma > 1e-6) ? (20.0 * log10(gamma)) : -120.0;
    }
    return (1.0 + gamma) / (1.0 - gamma);
}

// Розрахунок L-ланки для антени з R_L < 50 Ом
bool calculate_l_match(double freq_hz, ComplexZ z_ant, MatchingResult *res) {
    if (z_ant.r <= 0.0 || z_ant.r >= Z0) {
        return false; // Потрібна інша топологія, якщо R_L >= 50 Ом
    }
    
    double w = 2.0 * PI * freq_hz;
    
    // 1. Теоретичний розрахунок
    double q = sqrt((Z0 / z_ant.r) - 1.0);
    double b_shunt = q / Z0;                  // провідність паралельного конденсатора (См)
    double x_series = (q * z_ant.r) - z_ant.x;// реактивний опір послідовного індуктора (Ом)
    
    res->c_shunt_pf = (b_shunt / w) * 1e12;
    res->l_series_nh = (x_series / w) * 1e9;
    res->vswr_ideal = 1.0;
    
    // 2. Квантування до ряду E24
    res->c_real_pf = quantize_to_e24(res->c_shunt_pf);
    res->l_real_nh = quantize_to_e24(res->l_series_nh);
    
    // 3. Пряме моделювання вхідного імпедансу з компонентами E24
    double c_farads = res->c_real_pf * 1e-12;
    double l_henries = res->l_real_nh * 1e-9;
    
    // Додаємо послідовний індуктор до антени: Z1 = Z_ant + j*w*L
    double z1_r = z_ant.r;
    double z1_x = z_ant.x + (w * l_henries);
    
    // Переходимо до провідності Y1 = 1 / Z1
    double denom1 = z1_r * z1_r + z1_x * z1_x;
    double y1_g = z1_r / denom1;
    double y1_b = -z1_x / denom1;
    
    // Додаємо паралельний конденсатор: Yin = Y1 + j*w*C
    double yin_g = y1_g;
    double yin_b = y1_b + (w * c_farads);
    
    // Повертаємося до імпедансу Zin = 1 / Yin
    double denom_in = yin_g * yin_g + yin_b * yin_b;
    ComplexZ z_in = {
        .r = yin_g / denom_in,
        .x = -yin_b / denom_in
    };
    
    res->vswr_real = calculate_vswr(z_in, &res->s11_db_real);
    double gamma_real = (res->vswr_real - 1.0) / (res->vswr_real + 1.0);
    res->refl_power_pct = gamma_real * gamma_real * 100.0;
    
    return true;
}

int main(void) {
    double freq = 2.44e9; // 2.44 ГГц ISM
    ComplexZ z_detuned = { .r = 15.0, .x = -35.0 }; // розладнана антена в корпусі
    
    MatchingResult res;
    if (calculate_l_match(freq, z_detuned, &res)) {
        printf("--- Узгодження антени 2.44 ГГц ---\n");
        printf("Вхідний імпеданс антени: %.1f + j(%.1f) Ом\n", z_detuned.r, z_detuned.x);
        printf("Теоретичні номінали: C_shunt = %.2f пФ, L_series = %.2f нГн\n", 
               res.c_shunt_pf, res.l_series_nh);
        printf("Реальні номінали E24:  C = %.1f пФ, L = %.1f нГн\n", 
               res.c_real_pf, res.l_real_nh);
        printf("Фактичний КСВ з E24:   %.2f (S11 = %.1f дБ, відбито %.2f%% потужності)\n", 
               res.vswr_real, res.s11_db_real, res.refl_power_pct);
    }
    return 0;
}

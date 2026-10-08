#include <stdio.h>
#include <math.h>

// Розрахунок фазообертача та оцінка зсуву
typedef struct {
    double carrier_freq_hz;  // Несуча частота (Гц)
    double sensor_phase_deg; // Фазовий зсув датчика LVDT (градуси)
    double capacitor_f;      // Ємність конденсатора фазообертача (Ф)
} phase_shifter_cfg_t;

void calculate_phase_compensation(const phase_shifter_cfg_t* cfg) {
    double omega = 2.0 * M_PI * cfg->carrier_freq_hz;
    double target_phase_rad = cfg->sensor_phase_deg * (M_PI / 180.0);
    
    // Для фазообертача H(s) = (1 - sRC)/(1 + sRC), phi = -2 * atan(omega * R * C)
    // tan(-phi / 2) = omega * R * C  => R = tan(phi_target / 2) / (omega * C)
    double r_val = tan(fabs(target_phase_rad) / 2.0) / (omega * cfg->capacitor_f);
    
    // Оцінка втрати сигналу при відсутності компенсації: cos(phi)
    double uncompensated_gain_factor = cos(target_phase_rad);
    double loss_percent = (1.0 - uncompensated_gain_factor) * 100.0;

    printf("--- Розрахунок кола фазової компенсації ---\n");
    printf("Кут зсуву датчика: %.1f deg\n", cfg->sensor_phase_deg);
    printf("Втрата чутливості без компенсації: %.2f%%\n", loss_percent);
    printf("Необхідний опір резистора R: %.1f Ом (при C = %.2f нФ)\n", 
           r_val, cfg->capacitor_f * 1e9);
}

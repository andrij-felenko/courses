#include <math.h>

/**
 * @brief Обчислює максимально припустимий струм збудження RTD (у Амперах).
 * 
 * @param r0_resistance Номінальний опір сенсора при 0 °C (Ом), наприклад 100.0 або 1000.0.
 * @param max_temp_c Поточна максимальна робоча температура (°C).
 * @param max_allowed_self_heat_err Максимально припустима похибка самонагріву (°C).
 * @param dissipation_factor_mw_per_c Коефіцієнт розсіювання E_h (мВт/°C).
 * @return Максимальний струм збудження в Амперах.
 */
double rtd_calculate_max_excitation_current(double r0_resistance, 
                                           double max_temp_c, 
                                           double max_allowed_self_heat_err, 
                                           double dissipation_factor_mw_per_c) 
{
    // Оцінка опору платини за лінійним коефіцієнтом alpha = 0.003851
    double approx_r_t = r0_resistance * (1.0 + 0.003851 * max_temp_c);
    
    // Переведення коефіцієнта розсіювання з мВт/°C у Вт/°C
    double dissipation_w_per_c = dissipation_factor_mw_per_c * 1e-3;
    
    // Максимальна припустима теплова потужність: P_max = ΔT_allowed * E_h
    double p_max = max_allowed_self_heat_err * dissipation_w_per_c;
    
    // З формули P = I^2 * R визначаємо I_max = sqrt(P_max / R_t)
    if (approx_r_t <= 0.0 || p_max <= 0.0) {
        return 0.0;
    }
    
    return sqrt(p_max / approx_r_t);
}

#include <math.h>
#include <stdbool.h>

// Параметри коаксіального сервомодуля для розрахунку моменту
typedef struct {
    float k_t;         // Моментна стала двигуна, Н·м/А
    float gear_ratio;  // Передавальне відношення N
    float efficiency;  // ККД редуктора (0.85 .. 0.95)
    float j_ref;       // Зведений момент інерції, кг·м²
    float b_viscous;   // Коефіцієнт в'язкого тертя, Н·м·с/рад
    float tau_coulomb; // Момент сухого тертя Кулона, Н·м
} servo_torque_params_t;

// Оцінка зовнішнього механічного моменту на валу за квадратурним струмом I_q
float estimate_external_torque(const servo_torque_params_t *servo, float i_q, float speed_rad_s, float accel_rad_s2) {
    // 1. Електромеханічний момент ротора за квадратурним струмом
    float tau_motor = servo->k_t * i_q;
    
    // 2. Силовий момент на вихідному валу з урахуванням редукції та ККД
    float tau_shaft_raw = tau_motor * servo->gear_ratio * servo->efficiency;
    
    // 3. Динамічна компенсація моменту прискорення ротора
    float tau_inertia = servo->j_ref * accel_rad_s2;
    
    // 4. Компенсація в'язкого тертя редуктора та вальниць
    float tau_viscous = servo->b_viscous * speed_rad_s;
    
    // 5. Компенсація сухого тертя Кулона
    float tau_coulomb = 0.0f;
    if (fabsf(speed_rad_s) > 1e-3f) {
        tau_coulomb = (speed_rad_s > 0.0f ? 1.0f : -1.0f) * servo->tau_coulomb;
    }
    
    // Зовнішній момент, прикладений до суглоба
    return tau_shaft_raw - tau_inertia - tau_viscous - tau_coulomb;
}

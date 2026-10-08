#include <math.h>
#include <stdbool.h>

// Характеристики безкорпусного двигуна
typedef struct {
    float j_motor;       // Момент інерції ротора, кг·м²
    float tau_peak_max;  // Максимальний піковий момент ротора, Н·м
    float tau_cont_max;  // Тривалий момент ротора, Н·м
} motor_specs_t;

// Вимоги до навантаження ланки робота
typedef struct {
    float j_load;        // Момент інерції ланки, кг·м²
    float tau_load_req;  // Необхідний момент суглоба, Н·м
    float accel_req;     // Необхідне кутове прискорення, рад/с²
} load_req_t;

// Розрахунок оптимального N та коефіцієнта інерційного узгодження
float calculate_optimal_gear_ratio(const motor_specs_t *motor, const load_req_t *load, float *out_inertia_ratio, bool *out_fits_limits) {
    // 1. Оптимальне N для максимального прискорення навантаження
    float n_opt = sqrtf(load->j_load / motor->j_motor);
    
    // 2. Зведений момент інерції при N_opt
    float j_ref = n_opt * n_opt * motor->j_motor;
    
    // 3. Коефіцієнт інерційного узгодження
    *out_inertia_ratio = load->j_load / j_ref;
    
    // 4. Перевірка необхідного моменту ротора з урахуванням власного прискорення
    float tau_motor_req = (load->tau_load_req / n_opt) + (motor->j_motor * n_opt * load->accel_req);
    *out_fits_limits = (tau_motor_req <= motor->tau_peak_max);
    
    return n_opt;
}

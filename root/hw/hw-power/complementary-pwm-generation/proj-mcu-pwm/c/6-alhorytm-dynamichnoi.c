#include <stdint.h>
#include <math.h>

typedef struct {
    uint32_t ccr_compensation_ticks; // Кількість тактів таймера для компенсації (t_dead / T_tick)
    float current_threshold_a;       // Поріг зони лінійного переходу (наприклад, 0.2 А)
} foc_deadtime_comp_t;

/**
 * @brief Розрахунок скомпенсованих значень регістрів порівняння ШІМ
 * @param comp Покажчик на структуру конфігурації
 * @param i_a Струм фази A (Ампери)
 * @param i_b Струм фази B (Ампери)
 * @param i_c Струм фази C (Ампери)
 * @param[in,out] ccr_a Значення CCR фази A
 * @param[in,out] ccr_b Значення CCR фази B
 * @param[in,out] ccr_c Значення CCR фази C
 */
void foc_apply_deadtime_compensation(const foc_deadtime_comp_t *comp,
                                     float i_a, float i_b, float i_c,
                                     uint32_t *ccr_a, uint32_t *ccr_b, uint32_t *ccr_c) {
    float sign_a = i_a / comp->current_threshold_a;
    float sign_b = i_b / comp->current_threshold_a;
    float sign_c = i_c / comp->current_threshold_a;

    // Обмеження діапазону від -1.0 до +1.0 (функція насичення)
    if (sign_a > 1.0f) sign_a = 1.0f; else if (sign_a < -1.0f) sign_a = -1.0f;
    if (sign_b > 1.0f) sign_b = 1.0f; else if (sign_b < -1.0f) sign_b = -1.0f;
    if (sign_c > 1.0f) sign_c = 1.0f; else if (sign_c < -1.0f) sign_c = -1.0f;

    // Внесення поправки у вольт-секундну площу
    int32_t delta_a = (int32_t)(sign_a * (float)comp->ccr_compensation_ticks);
    int32_t delta_b = (int32_t)(sign_b * (float)comp->ccr_compensation_ticks);
    int32_t delta_c = (int32_t)(sign_c * (float)comp->ccr_compensation_ticks);

    *ccr_a = (uint32_t)((int32_t)*ccr_a + delta_a);
    *ccr_b = (uint32_t)((int32_t)*ccr_b + delta_b);
    *ccr_c = (uint32_t)((int32_t)*ccr_c + delta_c);
}

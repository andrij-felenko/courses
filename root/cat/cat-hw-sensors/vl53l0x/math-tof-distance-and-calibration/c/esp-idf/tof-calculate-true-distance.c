// Алгоритм векторної компенсації crosstalk та offset у C (ESP-IDF / Generic C)
#include <math.h>

typedef struct {
    float i_cross;     // Синфазна складова завади від скла
    float q_cross;     // Квадратурна складова завади від скла
    float d_offset_m;  // Постійний системний зсув (у метрах)
    float f_mod_hz;    // Частота модуляції (наприклад, 30e6 Гц)
} tof_calib_params_t;

// Обчислення істинного значення відстані з компенсацією спотворень
float tof_calculate_true_distance(float i_meas, float q_meas, const tof_calib_params_t *cal) {
    const float c = 3.0e8f; // Швидкість світла (м/с)
    
    // 1. Векторне віднімання паразитного наведення crosstalk
    float i_target = i_meas - cal->i_cross;
    float q_target = q_meas - cal->q_cross;
    
    // 2. Обчислення відновленої фази корисного сигналу
    float phi_target = atan2f(q_target, i_target);
    if (phi_target < 0.0f) {
        phi_target += 2.0f * (float)M_PI; // Нормалізація у діапазон [0, 2π)
    }
    
    // 3. Перетворення фази у невідкалібровану відстань
    float d_uncorrected = (c * phi_target) / (4.0f * (float)M_PI * cal->f_mod_hz);
    
    // 4. Компенсація лінійного зсуву offset
    float d_final = d_uncorrected - cal->d_offset_m;
    return d_final;
}

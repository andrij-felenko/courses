#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_F 3.1415926535f

// Структура конфігурації та стану цифрового ФАПЧ-контролера PZT
typedef struct {
    float target_phase_rad;  // Цільовий фазовий зсув (0.0 рад для резонансу f_r)
    float kp;                // Пропорційний коефіцієнт ПІД-регулятора
    float ki;                // Інтегральний коефіцієнт ПІД-регулятора
    float kd;                // Диференціальний коефіцієнт ПІД-регулятора
    float current_freq_hz;   // Поточна генерується частота
    float min_freq_hz;       // Межа мінімальної робочої частоти
    float max_freq_hz;       // Межа максимальної робочої частоти
    float integral_sum;      // Накопичена інтегральна сума
    float prev_error;        // Попереднє значення помилки для диф-ланки
} PztPllController;

// Ініціалізація ФАПЧ-контролера
void pzt_pll_init(PztPllController *pll, float init_freq, float min_f, float max_f) {
    pll->target_phase_rad = 0.0f;
    pll->kp = 25.0f;
    pll->ki = 4.5f;
    pll->kd = 0.5f;
    pll->current_freq_hz = init_freq;
    pll->min_freq_hz = min_f;
    pll->max_freq_hz = max_f;
    pll->integral_sum = 0.0f;
    pll->prev_error = 0.0f;
}

// Оновлення частоти драйвера за виміряним фазовим зсувом (в радіанах)
float pzt_pll_update(PztPllController *pll, float measured_phase_rad, float dt_sec) {
    if (dt_sec <= 0.0f) return pll->current_freq_hz;

    // Помилка фази (відхилення від нульового фазового зсуву ZVS)
    float error = pll->target_phase_rad - measured_phase_rad;
    
    // Накопичення інтегральної суми з антинасиченням (anti-windup)
    pll->integral_sum += error * dt_sec;
    if (pll->integral_sum > 200.0f) pll->integral_sum = 200.0f;
    if (pll->integral_sum < -200.0f) pll->integral_sum = -200.0f;

    // Диференціальна складова
    float derivative = (error - pll->prev_error) / dt_sec;
    pll->prev_error = error;

    // Обчислення поправки частоти
    float freq_delta = (pll->kp * error) + (pll->ki * pll->integral_sum) + (pll->kd * derivative);
    pll->current_freq_hz += freq_delta;

    // Захисне обмеження діапазону частот
    if (pll->current_freq_hz < pll->min_freq_hz) {
        pll->current_freq_hz = pll->min_freq_hz;
    } else if (pll->current_freq_hz > pll->max_freq_hz) {
        pll->current_freq_hz = pll->max_freq_hz;
    }

    return pll->current_freq_hz;
}

// Розрахунок компенсаційної індуктивності L_comp
float pzt_calculate_l_comp_henry(float static_cap_farad, float resonant_freq_hz) {
    if (static_cap_farad <= 0.0f || resonant_freq_hz <= 0.0f) return 0.0f;
    float omega = 2.0f * PI_F * resonant_freq_hz;
    return 1.0f / (omega * omega * static_cap_farad);
}

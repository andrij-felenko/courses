/* 
 * pll_induction_controller.c — Промисловий алгоритм фазового автоналаштування
 * частоти (PLL/ZVS) для силового інвертора індукційного нагріву.
 * Мова: C (C99 / MISRA C сумісний код для мікроконтролерів)
 */

#include <stdint.h>
#include <stdbool.h>

#define PI_F 3.1415926535f

/* Конфігураційні параметри резонансного контуру та таймера MCU */
typedef struct {
    float f_min_hz;           /* Мінімальна допустима частота (наприклад, 20000 Гц) */
    float f_max_hz;           /* Максимальна допустима частота (наприклад, 100000 Гц) */
    float target_phase_rad;   /* Цільовий фазовий зсув ZVS (наприклад, +0.1 rad / ~5.7 deg) */
    float kp;                 /* Пропорційний коефіцієнт ПІ-регулятора */
    float ki;                 /* Інтегральний коефіцієнт ПІ-регулятора */
    float dt_sec;             /* Період дискретизації розрахунку (сек) */
    float dead_time_ns;       /* Мертвий час між ключами стійки (нс) */
} pll_config_t;

/* Стан системи фазового автоналаштування */
typedef struct {
    float current_freq_hz;    /* Поточна частота генерації ШІМ */
    float integrator_sum;     /* Накопичувач інтегральної ланки */
    float phase_error_rad;    /* Поточна фазова похибка */
    bool  zvs_locked;         /* Прапор успішного захоплення резонансу */
    uint32_t timer_period_ticks; /* Обчислене значення регістра періоду таймера */
} pll_state_t;

/* Ініціалізація стану PLL */
void pll_init(pll_state_t *state, const pll_config_t *cfg, float initial_freq_hz) {
    if (initial_freq_hz < cfg->f_min_hz) initial_freq_hz = cfg->f_min_hz;
    if (initial_freq_hz > cfg->f_max_hz) initial_freq_hz = cfg->f_max_hz;
    
    state->current_freq_hz = initial_freq_hz;
    state->integrator_sum = 0.0f;
    state->phase_error_rad = 0.0f;
    state->zvs_locked = false;
    state->timer_period_ticks = 0;
}

/*
 * Обчислення фазового зсуву за часовою затримкою між перетинами нуля.
 * delta_t_sec: час між зростаючим фронтом напруги та струму (позитивний, якщо струм відстає)
 */
float compute_phase_shift(float delta_t_sec, float current_freq_hz) {
    float phase_rad = 2.0f * PI_F * current_freq_hz * delta_t_sec;
    /* Нормалізація фази у діапазон [-PI, +PI] */
    while (phase_rad > PI_F)  phase_rad -= 2.0f * PI_F;
    while (phase_rad < -PI_F) phase_rad += 2.0f * PI_F;
    return phase_rad;
}

/*
 * Основний крок фазового автоналаштування (викликається у перериванні таймера / АЦП)
 */
void pll_update(pll_state_t *state, const pll_config_t *cfg, float measured_delta_t_sec) {
    /* 1. Обчислення виміряного фазового зсуву */
    float measured_phase_rad = compute_phase_shift(measured_delta_t_sec, state->current_freq_hz);
    
    /* 2. Обчислення похибки фази відносно уставки ZVS */
    state->phase_error_rad = cfg->target_phase_rad - measured_phase_rad;
    
    /* 3. Пропорційна ланка */
    float p_out = cfg->kp * state->phase_error_rad;
    
    /* 4. Інтегральна ланка з анти-віндапом (Anti-Windup) */
    state->integrator_sum += cfg->ki * state->phase_error_rad * cfg->dt_sec;
    
    /* Обмеження інтегратора */
    float max_freq_step = (cfg->f_max_hz - cfg->f_min_hz) * 0.5f;
    if (state->integrator_sum > max_freq_step)  state->integrator_sum = max_freq_step;
    if (state->integrator_sum < -max_freq_step) state->integrator_sum = -max_freq_step;
    
    /* 5. Сумарний регулювальний вплив (зміна частоти) */
    float freq_adjustment = p_out + state->integrator_sum;
    
    /* 6. Оновлення поточної частоти з обмеженням безпечного діапазону */
    float new_freq = state->current_freq_hz + freq_adjustment;
    if (new_freq > cfg->f_max_hz) {
        new_freq = cfg->f_max_hz;
    } else if (new_freq < cfg->f_min_hz) {
        new_freq = cfg->f_min_hz;
    }
    state->current_freq_hz = new_freq;
    
    /* 7. Оцінка стану захоплення резонансу (похибка < 2 градусів) */
    float abs_error_deg = (state->phase_error_rad >= 0.0f ? state->phase_error_rad : -state->phase_error_rad) * (180.0f / PI_F);
    state->zvs_locked = (abs_error_deg < 2.0f);
    
    /* 8. Розрахунок періоду для регістра ARR таймера MCU (при тактовій частоті 160 МГц) */
    const float mcu_clk_hz = 160000000.0f;
    state->timer_period_ticks = (uint32_t)(mcu_clk_hz / (2.0f * new_freq));
}

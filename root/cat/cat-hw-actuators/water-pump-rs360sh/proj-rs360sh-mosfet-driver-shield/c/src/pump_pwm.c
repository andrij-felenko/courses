#include "pump_pwm.h"
#include <math.h>
#include <stdio.h>

/**
 * @file pump_pwm.c
 * @brief Реалізація низькорівневого C-драйвера водяної помпи RS-360SH.
 */

/* Допоміжна функція для обмеження значень у діапазоні [min_val, max_val] */
static float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

pump_err_t pump_init(pump_t *pump, const pump_config_t *config) {
    if (pump == NULL || config == NULL || config->timer_hw == NULL) {
        return PUMP_ERR_NULL_PTR;
    }

    if (config->sys_clock_hz == 0U || config->pwm_freq_hz == 0U ||
        config->min_operational_duty < 0.0f || config->max_operational_duty > 100.0f ||
        config->min_operational_duty >= config->max_operational_duty ||
        config->ramp_rate_pct_per_sec <= 0.0f) {
        return PUMP_ERR_INVALID_PARAM;
    }

    /* Копіюємо конфігурацію */
    pump->config = *config;
    pump->state = PUMP_STATE_STOPPED;
    pump->current_duty_pct = 0.0f;
    pump->target_duty_pct = 0.0f;
    pump->last_update_ms = 0U;
    pump->total_volume_ml = 0.0;
    pump->is_initialized = false;

    /*
     * НИЗЬКОРІВНЕВИЙ РОЗРАХУНОК РЕГІСТРІВ ТАЙМЕРА (PSC та ARR):
     * Припустимо, ми прагнемо отримати роздільну здатність ШІМ приблизно 1000 дискрет (0.1%).
     * Необхідна частота тиків таймера: f_timer_tick = pwm_freq_hz * 1000.
     * Дільник prescaler (PSC) = (sys_clock_hz / f_timer_tick) - 1.
     */
    uint32_t target_resolution = 1000U;
    uint32_t req_timer_clk = config->pwm_freq_hz * target_resolution;
    uint32_t psc_val = 0U;

    if (config->sys_clock_hz >= req_timer_clk) {
        psc_val = (config->sys_clock_hz / req_timer_clk) - 1U;
    } else {
        psc_val = 0U; /* Тікає на максимальній частоті шини */
    }

    /* Фактична частота лічильника після встановлення PSC */
    uint32_t actual_timer_clk = config->sys_clock_hz / (psc_val + 1U);
    if (actual_timer_clk < config->pwm_freq_hz) {
        return PUMP_ERR_HARDWARE_FAIL;
    }

    /* Розрахунок періоду автоперезавантаження ARR = (f_timer_clk / f_pwm) - 1 */
    uint32_t arr_val = (actual_timer_clk / config->pwm_freq_hz) - 1U;

    if (arr_val == 0U) {
        return PUMP_ERR_HARDWARE_FAIL;
    }

    /* Пряма маніпуляція апаратними реєстрами MCU */
    timer_reg_t *hw = config->timer_hw;

    /* 1. Зупинка таймера перед конфігурацією */
    hw->CR1 &= ~TIMER_CR1_CEN;

    /* 2. Запис розрахованого Prescaler та Auto-Reload періоду */
    hw->PSC = psc_val;
    hw->ARR = arr_val;

    /* 3. Конфігурація режиму каналу 1 у CCMR1: PWM Mode 1 + Preload Enable */
    hw->CCMR1 &= ~(0xFFU); /* Очищення бітів CH1 */
    hw->CCMR1 |= (TIMER_CCMR1_OC1M_PWM1 | TIMER_CCMR1_OC1PE);

    /* 4. Ввімкнення виходу каналу 1 у CCER */
    hw->CCER |= TIMER_CCER_CC1E;

    /* 5. Увімкнення головного виходу (MOE) для розширених таймерів */
    hw->BDTR |= TIMER_BDTR_MOE;

    /* 6. Увімкнення буферизації ARR у CR1 */
    hw->CR1 |= TIMER_CR1_ARPE;

    /* 7. Початкове значення коефіцієнта заповнення (0% ШІМ) */
    hw->CCR1 = 0U;

    /* 8. Генерація події оновлення (EGR Update) для перезавантаження таймера */
    hw->EGR |= (1U << 0);

    /* 9. Активація таймера (Counter Enable) */
    hw->CR1 |= TIMER_CR1_CEN;

    pump->is_initialized = true;
    return PUMP_OK;
}

pump_err_t pump_set_speed(pump_t *pump, float target_duty_pct) {
    if (pump == NULL) {
        return PUMP_ERR_NULL_PTR;
    }
    if (!pump->is_initialized) {
        return PUMP_ERR_NOT_INIT;
    }
    if (pump->state == PUMP_STATE_EMERGENCY_STOP) {
        return PUMP_ERR_HARDWARE_FAIL;
    }

    /*
     * ОБРОБКА БЕЗПЕЧНИХ МЕЖ ПОМПИ RS-360SH:
     * Колекторний двигун з мембранною помпою не здатний обертатися при < 20% ШІМ
     * через високий пусковий момент тертя. Спроба подати 1..15% ШІМ приведе
     * до нагріву обмоток без руху рідини (ризик заклинювання).
     */
    if (target_duty_pct <= 0.0f) {
        pump->target_duty_pct = 0.0f;
    } else if (target_duty_pct < pump->config.min_operational_duty) {
        /* Коригуємо до безпечного мінімального робочого порогу */
        pump->target_duty_pct = pump->config.min_operational_duty;
    } else {
        pump->target_duty_pct = clampf(target_duty_pct, 
                                       pump->config.min_operational_duty, 
                                       pump->config.max_operational_duty);
    }

    return PUMP_OK;
}

pump_err_t pump_set_speed_immediate(pump_t *pump, float duty_pct) {
    if (pump == NULL) {
        return PUMP_ERR_NULL_PTR;
    }
    if (!pump->is_initialized) {
        return PUMP_ERR_NOT_INIT;
    }

    float safe_duty = 0.0f;
    if (duty_pct > 0.0f) {
        if (duty_pct < pump->config.min_operational_duty) {
            safe_duty = pump->config.min_operational_duty;
        } else {
            safe_duty = clampf(duty_pct, pump->config.min_operational_duty, pump->config.max_operational_duty);
        }
    }

    pump->target_duty_pct = safe_duty;
    pump->current_duty_pct = safe_duty;

    /* Обчислення та атомарний запис у регістр порівняння CCR1 */
    uint32_t arr = pump->config.timer_hw->ARR;
    uint32_t ccr = (uint32_t)((safe_duty / 100.0f) * (float)(arr + 1U));
    pump->config.timer_hw->CCR1 = ccr;

    if (safe_duty == 0.0f) {
        pump->state = PUMP_STATE_STOPPED;
    } else {
        pump->state = PUMP_STATE_RUNNING;
    }

    return PUMP_OK;
}

pump_err_t pump_update(pump_t *pump, uint32_t current_time_ms) {
    if (pump == NULL) {
        return PUMP_ERR_NULL_PTR;
    }
    if (!pump->is_initialized) {
        return PUMP_ERR_NOT_INIT;
    }

    if (pump->state == PUMP_STATE_EMERGENCY_STOP || pump->state == PUMP_STATE_FAULT) {
        return PUMP_OK;
    }

    /* Перший крок оновлення */
    if (pump->last_update_ms == 0U) {
        pump->last_update_ms = current_time_ms;
        return PUMP_OK;
    }

    uint32_t dt_ms = current_time_ms - pump->last_update_ms;
    if (dt_ms == 0U) {
        return PUMP_OK;
    }
    pump->last_update_ms = current_time_ms;

    /* 1. РОЗРАХУНОК ТА ЗМІНА ШІМ ЗГІДНО З ПРОФІЛЕМ РАМПИ */
    if (fabsf(pump->current_duty_pct - pump->target_duty_pct) > 0.01f) {
        pump->state = PUMP_STATE_RAMPING;

        /* Максимальний приріст відсотків ШІМ за час dt_ms */
        float max_step = (pump->config.ramp_rate_pct_per_sec * (float)dt_ms) / 1000.0f;
        float diff = pump->target_duty_pct - pump->current_duty_pct;

        if (fabsf(diff) <= max_step) {
            pump->current_duty_pct = pump->target_duty_pct;
        } else if (diff > 0.0f) {
            pump->current_duty_pct += max_step;
        } else {
            pump->current_duty_pct -= max_step;
        }

        /* Запис нового коефіцієнта заповнення у регістр порівняння CCR1 */
        uint32_t arr = pump->config.timer_hw->ARR;
        uint32_t ccr = (uint32_t)((pump->current_duty_pct / 100.0f) * (float)(arr + 1U));
        pump->config.timer_hw->CCR1 = ccr;
    } else {
        pump->current_duty_pct = pump->target_duty_pct;
        pump->state = (pump->current_duty_pct > 0.0f) ? PUMP_STATE_RUNNING : PUMP_STATE_STOPPED;
    }

    /* 2. НАКОПИЧЕННЯ ОБ'ЄМУ ПРОКАЧАНОЇ РІДИНИ */
    float instant_flow = pump_get_estimated_flow_ml_min(pump);
    if (instant_flow > 0.0f) {
        double dt_sec = (double)dt_ms / 1000.0;
        double volume_added_ml = ((double)instant_flow / 60.0) * dt_sec;
        pump->total_volume_ml += volume_added_ml;
    }

    return PUMP_OK;
}

pump_err_t pump_stop(pump_t *pump) {
    return pump_set_speed(pump, 0.0f);
}

pump_err_t pump_emergency_stop(pump_t *pump) {
    if (pump == NULL) {
        return PUMP_ERR_NULL_PTR;
    }
    if (pump->config.timer_hw != NULL) {
        /* Атомарне знеструмлення виходу ШІМ */
        pump->config.timer_hw->CCR1 = 0U;
    }
    pump->current_duty_pct = 0.0f;
    pump->target_duty_pct = 0.0f;
    pump->state = PUMP_STATE_EMERGENCY_STOP;
    return PUMP_OK;
}

float pump_get_current_speed(const pump_t *pump) {
    if (pump == NULL) return 0.0f;
    return pump->current_duty_pct;
}

float pump_get_estimated_flow_ml_min(const pump_t *pump) {
    if (pump == NULL || pump->current_duty_pct < pump->config.min_operational_duty) {
        return 0.0f;
    }

    /*
     * Лінійна апроксимація продуктивності між min_operational_duty та 100%.
     * При мінімальному робочому ШІМ подача становить початковий мінімум,
     * а при 100% досягає max_flow_ml_min (1800 мл/хв).
     */
    float range = pump->config.max_operational_duty - pump->config.min_operational_duty;
    if (range <= 0.0f) return 0.0f;

    float normalized_duty = (pump->current_duty_pct - pump->config.min_operational_duty) / range;
    return normalized_duty * pump->config.max_flow_ml_min;
}

double pump_get_total_volume_ml(const pump_t *pump) {
    if (pump == NULL) return 0.0;
    return pump->total_volume_ml;
}

pump_state_t pump_get_state(const pump_t *pump) {
    if (pump == NULL) return PUMP_STATE_FAULT;
    return pump->state;
}

const char* pump_err_to_str(pump_err_t err) {
    switch (err) {
        case PUMP_OK:               return "Успішно (PUMP_OK)";
        case PUMP_ERR_NULL_PTR:      return "Помилка: Нульовий вказівник (PUMP_ERR_NULL_PTR)";
        case PUMP_ERR_INVALID_PARAM: return "Помилка: Некоректний параметр (PUMP_ERR_INVALID_PARAM)";
        case PUMP_ERR_NOT_INIT:      return "Помилка: Драйвер не ініціалізовано (PUMP_ERR_NOT_INIT)";
        case PUMP_ERR_HARDWARE_FAIL: return "Помилка: Збій апаратного таймера (PUMP_ERR_HARDWARE_FAIL)";
        case PUMP_ERR_STALL_RISK:    return "Попередження: Ризик заклинювання (PUMP_ERR_STALL_RISK)";
        default:                     return "Невідома помилка";
    }
}

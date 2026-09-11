#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t shunt_mohm;                // Опір шунта у міліомах (наприклад, 100 мОм)
    uint16_t amplifier_gain;            // Коефіцієнт підсилення сигналу шунта (наприклад, 20)
    uint16_t adc_vref_mv;               // Опорна напруга АЦП у мілівольтах (наприклад, 3300 мВ)
    uint16_t adc_max_ticks;             // Максимальне значення АЦП (4095 для 12-бітного перетворювача)
    uint16_t stall_current_ma;          // Поріг струму заклинювання при 100% ШІМ (наприклад, 800 мА)
    uint16_t min_stall_current_ma;      // Мінімальний поріг струму заклинювання (наприклад, 250 мА)
    uint16_t min_detect_duty_permille;  // Мінімальна шпаруватість для захисту в проміле (наприклад, 150 = 15%)
    uint16_t blanking_time_ms;          // Тривалість вікна бланкування у мілісекундах (наприклад, 80 мс)
    uint16_t stall_timeout_ms;          // Інтервал перевантаження до вимкнення (наприклад, 250 мс)
} motor_current_config_t;

typedef struct {
    motor_current_config_t current_cfg;
    uint16_t               filtered_current_ma;  // Згладжене значення струму
    uint32_t               motion_start_ms;      // Час початку руху
    uint32_t               overcurrent_start_ms; // Час початку фіксації перевантаження
    bool                   is_stalled;           // Прапорець зафіксованого заклинювання
} motor_stall_detector_t;

// Зовнішні функції апаратного рівня
extern uint16_t hal_adc_read_raw(void);
extern void hal_hbridge_emergency_shutdown(void);

void motor_stall_init(motor_stall_detector_t *det, const motor_current_config_t *cfg) {
    det->current_cfg = *cfg;
    det->filtered_current_ma = 0;
    det->motion_start_ms = 0;
    det->overcurrent_start_ms = 0;
    det->is_stalled = false;
}

uint16_t motor_get_current_ma(motor_stall_detector_t *det) {
    uint16_t adc_raw = hal_adc_read_raw();

    // Обчислюємо напругу на вході АЦП у мікровольтах
    uint32_t v_adc_uv = ((uint32_t)adc_raw * (uint32_t)det->current_cfg.adc_vref_mv * 1000UL) /
                        (uint32_t)det->current_cfg.adc_max_ticks;

    // Спад напруги на шунті V_shunt = V_adc / Gain, а струм I = V_shunt / R_shunt
    uint32_t divisor = (uint32_t)det->current_cfg.amplifier_gain * (uint32_t)det->current_cfg.shunt_mohm;
    uint32_t current_instant_ma = (divisor > 0) ? (v_adc_uv * 1000UL) / divisor : 0;

    // Цифрове експоненційне згладжування з коефіцієнтом α = 0.25
    det->filtered_current_ma = (uint16_t)(((uint32_t)det->filtered_current_ma * 3UL + current_instant_ma) / 4UL);

    return det->filtered_current_ma;
}

uint16_t motor_calc_stall_threshold(const motor_stall_detector_t *det, uint16_t duty_permille) {
    if (duty_permille < det->current_cfg.min_detect_duty_permille) {
        return 0; // Нижче мінімальної шпаруватості детекція заклинювання не проводиться
    }
    if (duty_permille >= 1000) {
        return det->current_cfg.stall_current_ma;
    }

    // Лінійна інтерполяція між min_stall_current_ma та stall_current_ma
    uint32_t duty_span = 1000UL - (uint32_t)det->current_cfg.min_detect_duty_permille;
    uint32_t current_span = (uint32_t)det->current_cfg.stall_current_ma - (uint32_t)det->current_cfg.min_stall_current_ma;
    uint32_t duty_rel = (uint32_t)duty_permille - (uint32_t)det->current_cfg.min_detect_duty_permille;

    return (uint16_t)((uint32_t)det->current_cfg.min_stall_current_ma + (duty_rel * current_span) / duty_span);
}

bool motor_check_stall(motor_stall_detector_t *det, bool is_motor_active, uint16_t duty_permille, uint32_t now_ms) {
    if (det->is_stalled) {
        return true; // Аварійний стан уже активний
    }

    if (!is_motor_active) {
        det->motion_start_ms = 0;
        det->overcurrent_start_ms = 0;
        return false;
    }

    // Фіксуємо момент запуску мотора
    if (det->motion_start_ms == 0) {
        det->motion_start_ms = now_ms;
        det->overcurrent_start_ms = 0;
        return false;
    }

    // Вікно бланкування: ігноруємо пусковий викид струму
    if ((now_ms - det->motion_start_ms) < det->current_cfg.blanking_time_ms) {
        det->overcurrent_start_ms = 0;
        return false;
    }

    // Обчислюємо динамічний поріг струму для поточної шпаруватості ШІМ
    uint16_t dynamic_threshold_ma = motor_calc_stall_threshold(det, duty_permille);
    if (dynamic_threshold_ma == 0) {
        det->overcurrent_start_ms = 0;
        return false; // Шпаруватість замала для коректної фіксації блокування
    }

    // Вимірюємо поточний згладжений струм
    uint16_t current_ma = motor_get_current_ma(det);

    if (current_ma >= dynamic_threshold_ma) {
        if (det->overcurrent_start_ms == 0) {
            det->overcurrent_start_ms = now_ms; // Початок фіксації небезпечного струму
        } else if ((now_ms - det->overcurrent_start_ms) >= det->current_cfg.stall_timeout_ms) {
            // Заклинювання підтверджено тайм-аутом
            det->is_stalled = true;
            hal_hbridge_emergency_shutdown();
            return true;
        }
    } else {
        det->overcurrent_start_ms = 0;
    }

    return false;
}

void motor_clear_fault(motor_stall_detector_t *det) {
    det->is_stalled = false;
    det->motion_start_ms = 0;
    det->overcurrent_start_ms = 0;
    det->filtered_current_ma = 0;
}

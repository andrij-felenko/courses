#include <stdint.h>
#include <stdbool.h>

/* Стани скінченного автомата e-Fuse */
typedef enum {
    EFUSE_STATE_OFF = 0,
    EFUSE_STATE_SOFT_START,
    EFUSE_STATE_ON,
    EFUSE_STATE_CURRENT_LIMIT,
    EFUSE_STATE_FAULT
} efuse_state_t;

/* Причина виникнення аварії */
typedef enum {
    FAULT_NONE = 0,
    FAULT_SHORT_CIRCUIT,
    FAULT_THERMAL_I2T,
    FAULT_SOA_VIOLATION,
    FAULT_STARTUP_TIMEOUT,
    FAULT_UNDERVOLTAGE
} efuse_fault_t;

/* Конфігурація параметрів захисту */
typedef struct {
    float v_in_min_v;           /* Поріг UVLO (В) */
    float i_nominal_a;          /* Номінальний струм (А) */
    float i_short_circuit_a;    /* Поріг миттєвого відсікання КЗ (А) */
    float i2t_threshold_a2s;    /* Максимальний тепловий інтеграл (А²·с) */
    float max_linear_power_w;   /* Максимальна потужність у лінійному режимі (Вт) */
    float soft_start_step_v;    /* Крок наростання напруги затвора (В/тік) */
    uint32_t startup_timeout_ms;/* Максимальний час запуску (мс) */
    uint32_t cool_down_time_ms; /* Час паузи перед автоперезапуском (мс) */
    bool auto_retry_enabled;    /* Дозвіл автоматичного повторного старту */
} efuse_config_t;

/* Структура контексту драйвера */
typedef struct {
    efuse_state_t state;
    efuse_fault_t last_fault;
    efuse_config_t config;
    
    float v_gate_target_v;      /* Цільова напруга затвора */
    float v_gate_current_v;     /* Поточна напруга затвора */
    float accumulated_i2t;      /* Накопичений тепловий інтеграл (А²·с) */
    float linear_mode_energy_j; /* Енергія розсіювання в лінійному режимі (Дж) */
    
    uint32_t state_timer_ms;    /* Внутрішній таймер стану */
    uint32_t retry_count;       /* Лічильник спроб перезапуску */
} efuse_controller_t;

/* Апаратні виклики (HAL) */
extern void hal_set_gate_voltage(float voltage_v);
extern void hal_fast_gate_shutdown(void);
extern float hal_read_vin_voltage(void);
extern float hal_read_vout_voltage(void);
extern float hal_read_load_current(void);

/* Ініціалізація контролера */
void efuse_init(efuse_controller_t *dev, const efuse_config_t *cfg) {
    dev->state = EFUSE_STATE_OFF;
    dev->last_fault = FAULT_NONE;
    dev->config = *cfg;
    dev->v_gate_target_v = 10.0f; /* 10 В для повного відкриття N-MOSFET */
    dev->v_gate_current_v = 0.0f;
    dev->accumulated_i2t = 0.0f;
    dev->linear_mode_energy_j = 0.0f;
    dev->state_timer_ms = 0;
    dev->retry_count = 0;
    
    hal_fast_gate_shutdown();
}

/* Періодичний крок обробки (викликається кожні delta_ms, наприклад 1 мс) */
void efuse_process_tick(efuse_controller_t *dev, bool enable_cmd, uint32_t delta_ms) {
    float v_in = hal_read_vin_voltage();
    float v_out = hal_read_vout_voltage();
    float i_load = hal_read_load_current();
    float dt_sec = (float)delta_ms / 1000.0f;
    float v_ds = (v_in > v_out) ? (v_in - v_out) : 0.0f;

    /* Перевірка мінімальної напруги живлення (UVLO) */
    if (v_in < dev->config.v_in_min_v && dev->state != EFUSE_STATE_OFF) {
        hal_fast_gate_shutdown();
        dev->state = EFUSE_STATE_FAULT;
        dev->last_fault = FAULT_UNDERVOLTAGE;
        dev->state_timer_ms = 0;
        return;
    }

    switch (dev->state) {
    case EFUSE_STATE_OFF:
        if (enable_cmd && v_in >= dev->config.v_in_min_v) {
            dev->state = EFUSE_STATE_SOFT_START;
            dev->v_gate_current_v = 0.0f;
            dev->state_timer_ms = 0;
            dev->accumulated_i2t = 0.0f;
            dev->linear_mode_energy_j = 0.0f;
        }
        break;

    case EFUSE_STATE_SOFT_START:
        dev->state_timer_ms += delta_ms;

        /* Миттєве відсікання, якщо струм перевищив поріг КЗ */
        if (i_load >= dev->config.i_short_circuit_a) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SHORT_CIRCUIT;
            dev->state_timer_ms = 0;
            return;
        }

        /* Контроль теплового розсіювання на MOSFET під час заряду ємності */
        float power_now = v_ds * i_load;
        dev->linear_mode_energy_j += power_now * dt_sec;
        if (power_now > dev->config.max_linear_power_w && dev->linear_mode_energy_j > 2.0f) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SOA_VIOLATION;
            dev->state_timer_ms = 0;
            return;
        }

        /* Плавне наростання напруги на затворі */
        dev->v_gate_current_v += dev->config.soft_start_step_v;
        if (dev->v_gate_current_v > dev->v_gate_target_v) {
            dev->v_gate_current_v = dev->v_gate_target_v;
        }
        hal_set_gate_voltage(dev->v_gate_current_v);

        /* Перевірка успішного виходу на режим */
        if (v_out >= (v_in * 0.90f)) {
            dev->state = EFUSE_STATE_ON;
            dev->v_gate_current_v = dev->v_gate_target_v;
            hal_set_gate_voltage(dev->v_gate_current_v);
            dev->state_timer_ms = 0;
            dev->linear_mode_energy_j = 0.0f;
        } else if (dev->state_timer_ms > dev->config.startup_timeout_ms) {
            /* Таймаут пуску — занадто велика ємність або витік на виході */
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_STARTUP_TIMEOUT;
            dev->state_timer_ms = 0;
        }
        break;

    case EFUSE_STATE_ON:
        /* 1. Апаратне відсікання короткого замикання (< 500 нс) */
        if (i_load >= dev->config.i_short_circuit_a) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SHORT_CIRCUIT;
            dev->state_timer_ms = 0;
            return;
        }

        /* 2. Інтегрування теплового навантаження I²t */
        if (i_load > dev->config.i_nominal_a) {
            float excess_current = i_load - dev->config.i_nominal_a;
            dev->accumulated_i2t += (excess_current * excess_current) * dt_sec;

            if (dev->accumulated_i2t >= dev->config.i2t_threshold_a2s) {
                hal_fast_gate_shutdown();
                dev->state = EFUSE_STATE_FAULT;
                dev->last_fault = FAULT_THERMAL_I2T;
                dev->state_timer_ms = 0;
                return;
            }
        } else {
            /* Експоненційне охолодження при роботі нижче номіналу */
            dev->accumulated_i2t -= dev->accumulated_i2t * 0.1f * dt_sec;
            if (dev->accumulated_i2t < 0.0f) {
                dev->accumulated_i2t = 0.0f;
            }
        }

        if (!enable_cmd) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_OFF;
        }
        break;

    case EFUSE_STATE_CURRENT_LIMIT:
        /* Режим активного обмеження струму */
        dev->state_timer_ms += delta_ms;
        if (v_ds * i_load > dev->config.max_linear_power_w) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SOA_VIOLATION;
            dev->state_timer_ms = 0;
        }
        break;

    case EFUSE_STATE_FAULT:
        dev->state_timer_ms += delta_ms;

        /* Логіка автоперезапуску після охолодження */
        if (dev->config.auto_retry_enabled && enable_cmd) {
            if (dev->state_timer_ms >= dev->config.cool_down_time_ms) {
                dev->retry_count++;
                dev->state = EFUSE_STATE_SOFT_START;
                dev->v_gate_current_v = 0.0f;
                dev->state_timer_ms = 0;
                dev->accumulated_i2t = 0.0f;
                dev->linear_mode_energy_j = 0.0f;
            }
        } else if (!enable_cmd) {
            /* Скидання аварії ручною командою вимкнення */
            dev->state = EFUSE_STATE_OFF;
            dev->last_fault = FAULT_NONE;
            dev->retry_count = 0;
        }
        break;
    }
}

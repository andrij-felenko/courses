/* Контролер формування імпульсів силового драйвера GTO (C99 / C11) */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    GTO_STATE_OFF = 0,         /* Стан закритого приладу: утримання V_GR (-18 В) */
    GTO_STATE_TURN_ON_PULSE,   /* Формування пікового імпульсу увімкнення I_GM */
    GTO_STATE_ON_BACKPORCH,    /* Стан відкритого приладу: утримання полиці I_G_cont */
    GTO_STATE_TURN_OFF_PULSE,  /* Формування пікового імпульсу вимикання -I_GQ */
    GTO_STATE_FAULT            /* Стан аварії: зрив комутації або тайм-аут */
} GtoDriverState;

typedef struct {
    uint32_t t_on_pulse_us;     /* Тривалість пускового імпульсу увімкнення (мкс) */
    uint32_t t_min_on_us;       /* Мінімальний дозволений час увімкненого стану (мкс) */
    uint32_t t_off_pulse_us;    /* Тривалість імпульсу вимикання затвора (мкс) */
    uint32_t t_min_off_us;      /* Мінімальний дозволений час закритого стану (мкс) */
    uint32_t t_storage_max_us;  /* Максимальний час очікування спаду струму (мкс) */
} GtoTimingConfig;

typedef struct {
    GtoDriverState state;
    GtoTimingConfig config;
    uint32_t state_timer_us;
    uint32_t on_time_accumulator_us;
    uint32_t off_time_accumulator_us;
    bool command_on;
    bool fault_flag;
} GtoGateDriver;

void gto_driver_init(GtoGateDriver *drv, const GtoTimingConfig *cfg) {
    if (!drv || !cfg) return;
    drv->config = *cfg;
    drv->state = GTO_STATE_OFF;
    drv->state_timer_us = 0;
    drv->on_time_accumulator_us = 0;
    drv->off_time_accumulator_us = cfg->t_min_off_us;
    drv->command_on = false;
    drv->fault_flag = false;
}

/* Низькорівневе апаратне керування ключами драйвера */
static inline void hw_set_gate_outputs(bool pos_pulse, bool pos_porch, bool neg_pulse, bool neg_bias) {
    /* Тут здійснюється запис у вихідні регістри GPIO або таймера ШІМ контролера */
    (void)pos_pulse; (void)pos_porch; (void)neg_pulse; (void)neg_bias;
}

/* Періодичний виклик обробника автомата станів (типовий квант 1 мкс) */
void gto_driver_tick_1us(GtoGateDriver *drv, bool anode_voltage_high) {
    if (!drv || drv->state == GTO_STATE_FAULT) {
        hw_set_gate_outputs(false, false, false, true); /* Завжди тримати -18 В */
        return;
    }

    drv->state_timer_us++;

    switch (drv->state) {
        case GTO_STATE_OFF:
            drv->off_time_accumulator_us++;
            hw_set_gate_outputs(false, false, false, true); /* Активне зміщення -18 В */

            if (drv->command_on && (drv->off_time_accumulator_us >= drv->config.t_min_off_us)) {
                drv->state = GTO_STATE_TURN_ON_PULSE;
                drv->state_timer_us = 0;
                drv->on_time_accumulator_us = 0;
            }
            break;

        case GTO_STATE_TURN_ON_PULSE:
            drv->on_time_accumulator_us++;
            hw_set_gate_outputs(true, true, false, false); /* Увімкнення банку I_GM */

            if (drv->state_timer_us >= drv->config.t_on_pulse_us) {
                drv->state = GTO_STATE_ON_BACKPORCH;
                drv->state_timer_us = 0;
            }
            break;

        case GTO_STATE_ON_BACKPORCH:
            drv->on_time_accumulator_us++;
            hw_set_gate_outputs(false, true, false, false); /* Утримання полиці 5 А */

            if (!drv->command_on && (drv->on_time_accumulator_us >= drv->config.t_min_on_us)) {
                drv->state = GTO_STATE_TURN_OFF_PULSE;
                drv->state_timer_us = 0;
                drv->off_time_accumulator_us = 0;
            }
            break;

        case GTO_STATE_TURN_OFF_PULSE:
            hw_set_gate_outputs(false, false, true, false); /* Потужний банк -I_GQ */

            /* Перевірка детектора відновлення анодної напруги (успішне вимикання) */
            if (drv->state_timer_us > drv->config.t_storage_max_us && !anode_voltage_high) {
                drv->state = GTO_STATE_FAULT;
                drv->fault_flag = true;
                break;
            }

            if (drv->state_timer_us >= drv->config.t_off_pulse_us) {
                drv->state = GTO_STATE_OFF;
                drv->state_timer_us = 0;
            }
            break;

        case GTO_STATE_FAULT:
        default:
            hw_set_gate_outputs(false, false, false, true);
            break;
    }
}

void gto_driver_set_command(GtoGateDriver *drv, bool enable) {
    if (drv) drv->command_on = enable;
}

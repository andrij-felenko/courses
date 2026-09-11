/**
 * @file motor_driver.c
 * @brief Драйвер колекторного мотора з неблокувальним струмовим захистом редуктора.
 */

#include <stdint.h>
#include <stdbool.h>

#define STALL_FILTER_WINDOW_SIZE 8

/* Стани кінцевого автомата захисту */
typedef enum {
    MOTOR_FSM_IDLE = 0,
    MOTOR_FSM_BLANKING,
    MOTOR_FSM_RUNNING,
    MOTOR_FSM_OVERLOAD,
    MOTOR_FSM_FAULT
} motor_fsm_state_t;

/* Напрямок обертання приводу */
typedef enum {
    MOTOR_DIR_STOP = 0,
    MOTOR_DIR_FORWARD,
    MOTOR_DIR_REVERSE
} motor_dir_t;

/* Апаратні прототипи взаємодії з периферією мікроконтролера */
extern void hal_pwm_set_duty(uint8_t channel, uint16_t duty_0_to_1000);
extern void hal_gpio_set_direction(uint8_t channel, motor_dir_t dir);
extern void hal_hbridge_active_brake(uint8_t channel);

/* Структура фільтра ковзного середнього */
typedef struct {
    uint16_t buffer[STALL_FILTER_WINDOW_SIZE];
    uint32_t accumulator;
    uint8_t  head;
    bool     is_primed;
} moving_average_t;

/* Структура стану каналу мотора */
typedef struct {
    uint8_t           channel_id;
    motor_fsm_state_t state;
    motor_dir_t       direction;
    uint16_t          target_duty;

    /* Параметри алгоритму захисту */
    uint16_t          i_trip_ma;          /* Поріг струму аварії */
    uint16_t          i_hyst_ma;          /* Гістерезис скидання перевантаження */
    uint32_t          blanking_ms;        /* Тривалість вікна маскування пуску */
    uint32_t          stall_timeout_ms;   /* Час підтвердження заклинювання */

    /* Часові мітки переходів станів */
    uint32_t          state_timestamp_ms;
    uint32_t          overload_start_ms;

    /* Поточні вимірювання */
    uint16_t          current_ma;
    moving_average_t  filter;
    bool              fault_flag;
} motor_channel_t;

static void filter_init(moving_average_t *f) {
    f->accumulator = 0;
    f->head = 0;
    f->is_primed = false;
    for (uint8_t i = 0; i < STALL_FILTER_WINDOW_SIZE; ++i) {
        f->buffer[i] = 0;
    }
}

static uint16_t filter_update(moving_average_t *f, uint16_t raw_adc) {
    f->accumulator -= f->buffer[f->head];
    f->buffer[f->head] = raw_adc;
    f->accumulator += raw_adc;
    f->head = (f->head + 1) & (STALL_FILTER_WINDOW_SIZE - 1);

    /* Ділення на 8 через бітовий зсув праворуч на 3 */
    return (uint16_t)(f->accumulator >> 3);
}

static uint16_t adc_to_milliamps(uint16_t adc_val) {
    /* Підсумкова формула: I_mA = (ADC * V_ref_mV) / (ADC_max * R_shunt) = (ADC * 3300) / (1023 * 0.22) ≈ ADC * 14.66 мА -> (ADC * 1466) / 100 */
    return (uint16_t)(((uint32_t)adc_val * 1466U) / 100U);
}

void motor_driver_init(motor_channel_t *ch, uint8_t channel_id, uint16_t i_trip_ma,
                       uint16_t i_hyst_ma, uint32_t blanking_ms, uint32_t stall_timeout_ms) {
    ch->channel_id = channel_id;
    ch->state = MOTOR_FSM_IDLE;
    ch->direction = MOTOR_DIR_STOP;
    ch->target_duty = 0;
    ch->i_trip_ma = i_trip_ma;
    ch->i_hyst_ma = i_hyst_ma;
    ch->blanking_ms = blanking_ms;
    ch->stall_timeout_ms = stall_timeout_ms;
    ch->state_timestamp_ms = 0;
    ch->overload_start_ms = 0;
    ch->current_ma = 0;
    ch->fault_flag = false;
    filter_init(&ch->filter);

    hal_gpio_set_direction(ch->channel_id, MOTOR_DIR_STOP);
    hal_pwm_set_duty(ch->channel_id, 0);
}

void motor_driver_set_speed(motor_channel_t *ch, motor_dir_t dir, uint16_t duty, uint32_t now_ms) {
    if (ch->state == MOTOR_FSM_FAULT) {
        /* Привід заблокований аварією; керування ігнорується до скидання */
        return;
    }

    if (dir == MOTOR_DIR_STOP || duty == 0) {
        ch->direction = MOTOR_DIR_STOP;
        ch->target_duty = 0;
        ch->state = MOTOR_FSM_IDLE;
        hal_pwm_set_duty(ch->channel_id, 0);
        hal_gpio_set_direction(ch->channel_id, MOTOR_DIR_STOP);
        return;
    }

    bool need_blanking = (ch->state == MOTOR_FSM_IDLE) || (ch->direction != dir);

    ch->direction = dir;
    ch->target_duty = (duty > 1000) ? 1000 : duty;

    hal_gpio_set_direction(ch->channel_id, ch->direction);
    hal_pwm_set_duty(ch->channel_id, ch->target_duty);

    if (need_blanking) {
        ch->state = MOTOR_FSM_BLANKING;
        ch->state_timestamp_ms = now_ms;
    }
}

void motor_driver_emergency_stop(motor_channel_t *ch) {
    ch->target_duty = 0;
    ch->direction = MOTOR_DIR_STOP;
    ch->state = MOTOR_FSM_FAULT;
    ch->fault_flag = true;

    /* Миттєве зняття ШІМ та увімкнення активного реостатного гальмування */
    hal_pwm_set_duty(ch->channel_id, 0);
    hal_hbridge_active_brake(ch->channel_id);
}

bool motor_driver_clear_fault(motor_channel_t *ch) {
    if (ch->state != MOTOR_FSM_FAULT) {
        return false;
    }
    ch->fault_flag = false;
    ch->state = MOTOR_FSM_IDLE;
    ch->direction = MOTOR_DIR_STOP;
    ch->target_duty = 0;
    filter_init(&ch->filter);
    hal_pwm_set_duty(ch->channel_id, 0);
    hal_gpio_set_direction(ch->channel_id, MOTOR_DIR_STOP);
    return true;
}

void motor_driver_process(motor_channel_t *ch, uint16_t raw_adc, uint32_t now_ms) {
    uint16_t filtered_adc = filter_update(&ch->filter, raw_adc);
    ch->current_ma = adc_to_milliamps(filtered_adc);

    switch (ch->state) {
    case MOTOR_FSM_IDLE:
        /* Мотор вимкнений; очікуємо команду на запуск */
        break;

    case MOTOR_FSM_BLANKING:
        /* Вікно маскування пускового стрибка струму */
        if ((now_ms - ch->state_timestamp_ms) >= ch->blanking_ms) {
            ch->state = MOTOR_FSM_RUNNING;
        }
        break;

    case MOTOR_FSM_RUNNING:
        /* Моніторинг струму під час штатного руху */
        if (ch->current_ma >= ch->i_trip_ma) {
            ch->state = MOTOR_FSM_OVERLOAD;
            ch->overload_start_ms = now_ms;
        }
        break;

    case MOTOR_FSM_OVERLOAD:
        /* Перевірка тривалості перевантаження для захисту зубців редуктора */
        if (ch->current_ma < (ch->i_trip_ma - ch->i_hyst_ma)) {
            /* Струм спав нижче порогу повернення: хибна тривога від нерівності */
            ch->state = MOTOR_FSM_RUNNING;
        } else if ((now_ms - ch->overload_start_ms) >= ch->stall_timeout_ms) {
            /* Заклинювання підтверджено: аварійний захист редуктора */
            motor_driver_emergency_stop(ch);
        }
        break;

    case MOTOR_FSM_FAULT:
        /* Стан аварії: залишаємося знеструмленими до явного виклику clear_fault */
        break;
    }
}

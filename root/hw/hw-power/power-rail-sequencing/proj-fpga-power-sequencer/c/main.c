#include <stdint.h>
#include <stdbool.h>

#define NUM_RAILS 3
#define TIMEOUT_TICKS 25
#define STABILIZE_TICKS 5

typedef enum {
    SEQ_STATE_IDLE = 0,
    SEQ_STATE_START_CORE,
    SEQ_STATE_START_AUX,
    SEQ_STATE_START_IO,
    SEQ_STATE_RUNNING,
    SEQ_STATE_STOP_IO,
    SEQ_STATE_STOP_AUX,
    SEQ_STATE_STOP_CORE,
    SEQ_STATE_FAULT
} SequencerState_t;

typedef enum {
    FAULT_NONE = 0,
    FAULT_CORE_TIMEOUT,
    FAULT_AUX_TIMEOUT,
    FAULT_IO_TIMEOUT,
    FAULT_RUNTIME_CORE_DROP,
    FAULT_RUNTIME_AUX_DROP,
    FAULT_RUNTIME_IO_DROP
} FaultReason_t;

typedef struct {
    const char* name;
    uint16_t v_min_mv;      /* Мінімальна напруга в мілівольтах */
    uint16_t v_max_mv;      /* Максимальна напруга в мілівольтах */
    uint8_t  enable_pin;    /* Номер GPIO виводу Enable */
    uint8_t  discharge_pin; /* Номер GPIO виводу Active Discharge */
} PowerRailConfig_t;

typedef struct {
    SequencerState_t state;
    FaultReason_t    fault_reason;
    uint32_t         timer_ticks;
    uint16_t         measured_mv[NUM_RAILS];
    PowerRailConfig_t rails[NUM_RAILS];
} PowerSequencer_t;

/* Прототипи апаратних функцій платформи */
extern void gpio_set_pin(uint8_t pin, bool level);
extern uint16_t adc_read_rail_mv(uint8_t rail_index);

void sequencer_init(PowerSequencer_t* seq) {
    seq->state = SEQ_STATE_IDLE;
    seq->fault_reason = FAULT_NONE;
    seq->timer_ticks = 0;

    /* Конфігурація трьох шин: Core (0.85V), Aux (1.8V), IO (3.3V) */
    seq->rails[0] = (PowerRailConfig_t){ "V_CORE", 800,  900,  10, 11 };
    seq->rails[1] = (PowerRailConfig_t){ "V_AUX",  1710, 1890, 12, 13 };
    seq->rails[2] = (PowerRailConfig_t){ "V_IO",   3130, 3470, 14, 15 };

    /* Початковий стан: усі перетворювачі вимкнено, розрядні ключі закрито */
    for (int i = 0; i < NUM_RAILS; i++) {
        gpio_set_pin(seq->rails[i].enable_pin, false);
        gpio_set_pin(seq->rails[i].discharge_pin, true); /* Активний розряд увімкнено */
    }
}

static bool is_rail_in_range(const PowerSequencer_t* seq, uint8_t idx) {
    uint16_t v = seq->measured_mv[idx];
    return (v >= seq->rails[idx].v_min_mv && v <= seq->rails[idx].v_max_mv);
}

void sequencer_start(PowerSequencer_t* seq) {
    if (seq->state == SEQ_STATE_IDLE) {
        /* Знімаємо активний розряд з шини ядра та вмикаємо перетворювач */
        gpio_set_pin(seq->rails[0].discharge_pin, false);
        gpio_set_pin(seq->rails[0].enable_pin, true);
        seq->state = SEQ_STATE_START_CORE;
        seq->timer_ticks = 0;
        seq->fault_reason = FAULT_NONE;
    }
}

void sequencer_shutdown(PowerSequencer_t* seq) {
    if (seq->state == SEQ_STATE_RUNNING) {
        /* Починаємо реверсивне вимкнення з шини I/O */
        gpio_set_pin(seq->rails[2].enable_pin, false);
        gpio_set_pin(seq->rails[2].discharge_pin, true);
        seq->state = SEQ_STATE_STOP_IO;
        seq->timer_ticks = 0;
    }
}

/* Періодичний крок опитування (викликається за таймером щомілісекунди) */
void sequencer_poll_1ms(PowerSequencer_t* seq) {
    /* Зчитування напруг через АЦП */
    for (uint8_t i = 0; i < NUM_RAILS; i++) {
        seq->measured_mv[i] = adc_read_rail_mv(i);
    }
    seq->timer_ticks++;

    switch (seq->state) {
        case SEQ_STATE_IDLE:
            break;

        case SEQ_STATE_START_CORE:
            if (is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    /* Ядро стабільне, запускаємо шину Aux */
                    gpio_set_pin(seq->rails[1].discharge_pin, false);
                    gpio_set_pin(seq->rails[1].enable_pin, true);
                    seq->state = SEQ_STATE_START_AUX;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_CORE_TIMEOUT;
                seq->state = SEQ_STATE_STOP_CORE;
            }
            break;

        case SEQ_STATE_START_AUX:
            if (is_rail_in_range(seq, 1) && is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    /* Aux стабільна, запускаємо периферію I/O */
                    gpio_set_pin(seq->rails[2].discharge_pin, false);
                    gpio_set_pin(seq->rails[2].enable_pin, true);
                    seq->state = SEQ_STATE_START_IO;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_AUX_TIMEOUT;
                seq->state = SEQ_STATE_STOP_AUX;
            }
            break;

        case SEQ_STATE_START_IO:
            if (is_rail_in_range(seq, 2) && is_rail_in_range(seq, 1) && is_rail_in_range(seq, 0)) {
                if (seq->timer_ticks >= STABILIZE_TICKS) {
                    seq->state = SEQ_STATE_RUNNING;
                    seq->timer_ticks = 0;
                }
            } else if (seq->timer_ticks > TIMEOUT_TICKS) {
                seq->fault_reason = FAULT_IO_TIMEOUT;
                seq->state = SEQ_STATE_STOP_IO;
            }
            break;

        case SEQ_STATE_RUNNING:
            /* Безперервний моніторинг шин під час роботи */
            if (!is_rail_in_range(seq, 0)) {
                seq->fault_reason = FAULT_RUNTIME_CORE_DROP;
                sequencer_shutdown(seq);
            } else if (!is_rail_in_range(seq, 1)) {
                seq->fault_reason = FAULT_RUNTIME_AUX_DROP;
                sequencer_shutdown(seq);
            } else if (!is_rail_in_range(seq, 2)) {
                seq->fault_reason = FAULT_RUNTIME_IO_DROP;
                sequencer_shutdown(seq);
            }
            break;

        case SEQ_STATE_STOP_IO:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                /* I/O розряджено, вимикаємо Aux */
                gpio_set_pin(seq->rails[1].enable_pin, false);
                gpio_set_pin(seq->rails[1].discharge_pin, true);
                seq->state = SEQ_STATE_STOP_AUX;
                seq->timer_ticks = 0;
            }
            break;

        case SEQ_STATE_STOP_AUX:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                /* Aux розряджено, останнім вимикаємо Core */
                gpio_set_pin(seq->rails[0].enable_pin, false);
                gpio_set_pin(seq->rails[0].discharge_pin, true);
                seq->state = SEQ_STATE_STOP_CORE;
                seq->timer_ticks = 0;
            }
            break;

        case SEQ_STATE_STOP_CORE:
            if (seq->timer_ticks >= STABILIZE_TICKS) {
                seq->state = (seq->fault_reason == FAULT_NONE) ? SEQ_STATE_IDLE : SEQ_STATE_FAULT;
            }
            break;

        case SEQ_STATE_FAULT:
            /* Блокування в аварійному стані до зовнішнього скидання */
            break;
    }
}

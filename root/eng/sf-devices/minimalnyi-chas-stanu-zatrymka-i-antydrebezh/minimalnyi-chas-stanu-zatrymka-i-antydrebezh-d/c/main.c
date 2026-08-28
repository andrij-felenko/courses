#include <stdint.h>
#include <stdbool.h>

/* --- 1. Модуль несиметричної часової кваліфікації сигналу --- */
typedef struct {
    uint32_t t_trip_ms;      /* Час утримання для активації (мс) */
    uint32_t t_recover_ms;   /* Час утримання для відновлення (мс) */
    uint32_t t_change_start; /* Мітка часу початку зміни сирого входу */
    bool raw_sample_last;    /* Попереднє значення сирого сигналу */
    bool state_debounced;    /* Поточний кваліфікований стан */
} time_qualifier_t;

void time_qualifier_init(time_qualifier_t *q, uint32_t trip_ms, uint32_t recover_ms, bool init_val, uint32_t now) {
    q->t_trip_ms = trip_ms;
    q->t_recover_ms = recover_ms;
    q->t_change_start = now;
    q->raw_sample_last = init_val;
    q->state_debounced = init_val;
}

bool time_qualifier_update(time_qualifier_t *q, bool raw_in, uint32_t now) {
    /* Якщо сирий сигнал змінив значення, перезапускаємо відлік стабільності */
    if (raw_in != q->raw_sample_last) {
        q->raw_sample_last = raw_in;
        q->t_change_start = now;
    }

    /* Якщо сирий сигнал відрізняється від кваліфікованого стану */
    if (raw_in != q->state_debounced) {
        uint32_t hold_required = raw_in ? q->t_trip_ms : q->t_recover_ms;
        if ((uint32_t)(now - q->t_change_start) >= hold_required) {
            q->state_debounced = raw_in;
        }
    }

    return q->state_debounced;
}

/* --- 2. Модуль контролю Minimum Dwell Time --- */
typedef struct {
    uint32_t t_entry;        /* Мітка часу входу в стан */
    uint32_t min_duration;   /* Мінімальна тривалість перебування (мс) */
} dwell_guard_t;

void dwell_guard_reset(dwell_guard_t *g, uint32_t duration_ms, uint32_t now) {
    g->t_entry = now;
    g->min_duration = duration_ms;
}

bool dwell_guard_is_expired(const dwell_guard_t *g, uint32_t now) {
    return ((uint32_t)(now - g->t_entry) >= g->min_duration);
}

/* --- 3. Автомат керування компресором із часовим захистом --- */
typedef enum {
    STATE_OFF = 0,
    STATE_RUN,
    STATE_FAULT
} compressor_state_t;

typedef struct {
    compressor_state_t state;
    dwell_guard_t dwell;
    time_qualifier_t temp_demand_qual;
    time_qualifier_t pressure_fault_qual;
    bool compressor_relay_cmd;
} compressor_fsm_t;

#define T_MIN_RUN_MS        (60000U)  /* Мінімум 60 с роботи */
#define T_MIN_OFF_MS        (180000U) /* Мінімум 180 с паузи для вирівнювання тиску */
#define T_TEMP_ON_QUAL_MS   (2000U)   /* 2 с перегріву для старту */
#define T_TEMP_OFF_QUAL_MS  (4000U)   /* 4 с нормальної температури для стопу */
#define T_OIL_FAULT_TRIP_MS (400U)    /* 400 мс падіння тиску мастила -> аварія */
#define T_OIL_FAULT_REC_MS  (10000U)  /* 10 с стабілізації тиску для скидання аварії */

void compressor_fsm_init(compressor_fsm_t *fsm, uint32_t now) {
    fsm->state = STATE_OFF;
    /* Безпечний консервативний старт: примусова витримка T_min_off після рестарту */
    dwell_guard_reset(&fsm->dwell, T_MIN_OFF_MS, now);
    time_qualifier_init(&fsm->temp_demand_qual, T_TEMP_ON_QUAL_MS, T_TEMP_OFF_QUAL_MS, false, now);
    time_qualifier_init(&fsm->pressure_fault_qual, T_OIL_FAULT_TRIP_MS, T_OIL_FAULT_REC_MS, false, now);
    fsm->compressor_relay_cmd = false;
}

void compressor_fsm_update(compressor_fsm_t *fsm, bool raw_cooling_demand, bool raw_oil_pressure_low, bool emergency_stop_btn, uint32_t now) {
    /* 1. Оновлюємо кваліфікатори вхідних сигналів */
    bool cooling_needed = time_qualifier_update(&fsm->temp_demand_qual, raw_cooling_demand, now);
    bool oil_fault = time_qualifier_update(&fsm->pressure_fault_qual, raw_oil_pressure_low, now);

    /* 2. Обробка переходів скінченного автомата */
    switch (fsm->state) {
    case STATE_OFF:
        fsm->compressor_relay_cmd = false;
        
        if (emergency_stop_btn || oil_fault) {
            fsm->state = STATE_FAULT;
            dwell_guard_reset(&fsm->dwell, T_MIN_OFF_MS, now);
        } else if (cooling_needed) {
            /* Перехід у RUN дозволено ЛИШЕ після завершення T_min_off */
            if (dwell_guard_is_expired(&fsm->dwell, now)) {
                fsm->state = STATE_RUN;
                dwell_guard_reset(&fsm->dwell, T_MIN_RUN_MS, now);
            }
        }
        break;

    case STATE_RUN:
        fsm->compressor_relay_cmd = true;

        /* Критична аварія має право МИТТЄВО перервати T_min_run */
        if (emergency_stop_btn || oil_fault) {
            fsm->state = STATE_FAULT;
            dwell_guard_reset(&fsm->dwell, T_MIN_OFF_MS, now);
        } else if (!cooling_needed) {
            /* Звичайна зупинка можлива ЛИШЕ після відпрацювання T_min_run */
            if (dwell_guard_is_expired(&fsm->dwell, now)) {
                fsm->state = STATE_OFF;
                dwell_guard_reset(&fsm->dwell, T_MIN_OFF_MS, now);
            }
        }
        break;

    case STATE_FAULT:
        fsm->compressor_relay_cmd = false;

        /* Вихід з аварії вимагає відновлення сигналів І витримки паузи захисту */
        if (!emergency_stop_btn && !oil_fault && dwell_guard_is_expired(&fsm->dwell, now)) {
            fsm->state = STATE_OFF;
            dwell_guard_reset(&fsm->dwell, T_MIN_OFF_MS, now);
        }
        break;
    }
}

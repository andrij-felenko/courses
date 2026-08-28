#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Бітові прапорці фізичних умов та датчиків */
#define SENSOR_DOOR_CLOSED       (1u << 0) /* Кінцевик кришки (NC): 1 = закрита */
#define SENSOR_PRESSURE_OK       (1u << 1) /* Реле тиску: 1 = тиск у межах норми */
#define SENSOR_WATER_FLOW_OK     (1u << 2) /* Датчик протоку: 1 = потік достатній */
#define SENSOR_TEMP_SAFE         (1u << 3) /* Термостат безпеки: 1 = температура < 80C */
#define SENSOR_ESTOP_NORMAL      (1u << 4) /* Кнопка E-Stop (NC): 1 = не натиснута */
#define SENSOR_PUMP_FEEDBACK     (1u << 5) /* Зворотний зв'язок контактора помпи */

/* Стани установки */
typedef enum {
    STATE_IDLE = 0,
    STATE_PREPARING,
    STATE_HEATING,
    STATE_TRIPPED
} system_state_t;

/* Опис каналу датчика з часовою кваліфікацією */
typedef struct {
    uint32_t pin_mask;
    uint32_t stable_delay_ms;
    uint32_t last_change_ms;
    bool last_raw_val;
    bool qualified_val;
} interlock_channel_t;

/* Структура конфігурації умов допуску та заборони для конкретного стану */
typedef struct {
    uint32_t permissive_req_mask; /* Обов'язкові біти = 1 для старту */
    uint32_t permissive_forbid_mask; /* Заборонені біти = 0 для старту */
    uint32_t inhibit_trip_mask; /* Біти, поява 1 у яких негайно зриває стан */
} state_interlock_rule_t;

/* Диспетчер підсистеми блокувань */
typedef struct {
    interlock_channel_t channels[6];
    size_t channel_count;
    uint32_t qualified_bitmap;
    uint32_t trip_latch_cause;
    system_state_t current_state;
} interlock_manager_t;

/* Матриця правил блокувань для кожного стану */
static const state_interlock_rule_t STATE_RULES[] = {
    [STATE_IDLE] = {
        .permissive_req_mask = 0,
        .permissive_forbid_mask = 0,
        .inhibit_trip_mask = 0
    },
    [STATE_PREPARING] = {
        /* Для переходу в PREPARING: двері закриті, E-Stop в нормі */
        .permissive_req_mask = SENSOR_DOOR_CLOSED | SENSOR_ESTOP_NORMAL,
        .permissive_forbid_mask = 0,
        /* Зрив якщо натиснуто E-Stop або відкрили двері */
        .inhibit_trip_mask = SENSOR_ESTOP_NORMAL /* якщо пропав 1 — трип */
    },
    [STATE_HEATING] = {
        /* Для переходу в HEATING: двері закриті, тиск OK, потік води OK, темп. норма */
        .permissive_req_mask = SENSOR_DOOR_CLOSED | SENSOR_PRESSURE_OK | 
                               SENSOR_WATER_FLOW_OK | SENSOR_TEMP_SAFE | SENSOR_ESTOP_NORMAL,
        .permissive_forbid_mask = 0,
        /* Зрив якщо пропав будь-який критичний параметр */
        .inhibit_trip_mask = SENSOR_DOOR_CLOSED | SENSOR_PRESSURE_OK | 
                             SENSOR_WATER_FLOW_OK | SENSOR_TEMP_SAFE | SENSOR_ESTOP_NORMAL
    }
};

void interlock_init(interlock_manager_t *mgr) {
    mgr->channel_count = 5;
    mgr->qualified_bitmap = 0;
    mgr->trip_latch_cause = 0;
    mgr->current_state = STATE_IDLE;

    /* Налаштування часу стабілізації для кожного датчика */
    mgr->channels[0] = (interlock_channel_t){ SENSOR_DOOR_CLOSED,   50, 0, false, false };
    mgr->channels[1] = (interlock_channel_t){ SENSOR_PRESSURE_OK,  200, 0, false, false };
    mgr->channels[2] = (interlock_channel_t){ SENSOR_WATER_FLOW_OK, 500, 0, false, false };
    mgr->channels[3] = (interlock_channel_t){ SENSOR_TEMP_SAFE,     100, 0, false, false };
    mgr->channels[4] = (interlock_channel_t){ SENSOR_ESTOP_NORMAL,   10, 0, false, false };
}

/* Оновлення фізичних входів та часова фільтрація (викликається в tick-перериванні або циклі) */
void interlock_update_inputs(interlock_manager_t *mgr, uint32_t raw_inputs, uint32_t now_ms) {
    uint32_t current_bitmap = 0;

    for (size_t i = 0; i < mgr->channel_count; i++) {
        interlock_channel_t *ch = &mgr->channels[i];
        bool raw_state = (raw_inputs & ch->pin_mask) != 0;

        if (raw_state != ch->last_raw_val) {
            ch->last_raw_val = raw_state;
            ch->last_change_ms = now_ms;
        }

        if ((now_ms - ch->last_change_ms) >= ch->stable_delay_ms) {
            ch->qualified_val = ch->last_raw_val;
        }

        if (ch->qualified_val) {
            current_bitmap |= ch->pin_mask;
        }
    }

    mgr->qualified_bitmap = current_bitmap;
}

/* Перевірка умов допуску ПЕРЕД переходом у цільовий стан (Permissive Check) */
bool interlock_can_enter_state(const interlock_manager_t *mgr, system_state_t target_state, uint32_t *missing_mask) {
    if (target_state >= sizeof(STATE_RULES)/sizeof(STATE_RULES[0])) {
        return false;
    }

    const state_interlock_rule_t *rule = &STATE_RULES[target_state];
    uint32_t present = mgr->qualified_bitmap;

    /* Перевіряємо чи всі необхідні біти присутні */
    uint32_t missing = (rule->permissive_req_mask & ~present);
    /* Перевіряємо чи немає заборонених бітів */
    uint32_t forbidden = (present & rule->permissive_forbid_mask);

    if (missing != 0 || forbidden != 0) {
        if (missing_mask) {
            *missing_mask = missing | forbidden;
        }
        return false;
    }

    return true;
}

/* Безперервний нагляд активного стану (Inhibit Trip Check) */
bool interlock_check_active_invariants(interlock_manager_t *mgr) {
    if (mgr->current_state == STATE_IDLE || mgr->current_state == STATE_TRIPPED) {
        return true;
    }

    const state_interlock_rule_t *rule = &STATE_RULES[mgr->current_state];
    uint32_t present = mgr->qualified_bitmap;

    /* Усі біти inhibit_trip_mask повинні бути 1 (норма). Якщо хоча б один зник — трип */
    uint32_t tripped_signals = (rule->inhibit_trip_mask & ~present);

    if (tripped_signals != 0) {
        /* Фіксуємо першопричину аварійного відключення (First-Out Latch) */
        mgr->trip_latch_cause = tripped_signals;
        mgr->current_state = STATE_TRIPPED;
        return false; /* Аварійний зрив! */
    }

    return true;
}

/* Скидання заблокованого стану оператором */
bool interlock_trip_reset(interlock_manager_t *mgr) {
    if (mgr->current_state != STATE_TRIPPED) {
        return false;
    }

    /* Дозволяємо скидання лише якщо E-Stop та базова безпека повернулися в норму */
    if ((mgr->qualified_bitmap & SENSOR_ESTOP_NORMAL) != 0) {
        mgr->trip_latch_cause = 0;
        mgr->current_state = STATE_IDLE;
        return true;
    }

    return false;
}

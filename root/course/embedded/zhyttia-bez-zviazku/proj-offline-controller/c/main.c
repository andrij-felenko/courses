/* =========================================================================
 * C99 Реалізація автономного контролера для вбудованих систем (No Heap)
 * ========================================================================= */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_RULES            8
#define TELEMETRY_QUEUE_SIZE 32
#define AUDIT_QUEUE_SIZE     16
#define ALARM_QUEUE_SIZE     8

/* Рівні критичності подій */
typedef enum {
    EVENT_PRIO_ALARM = 0,    /* Аварія: жорстке збереження, найвищий пріоритет */
    EVENT_PRIO_AUDIT = 1,    /* Аудит: зміна режиму, відкриття замка */
    EVENT_PRIO_TELEMETRY = 2 /* Телеметрія: періодичні дані, проріджування */
} event_prio_t;

/* Структура збереженої події */
typedef struct {
    uint32_t timestamp_s;    /* Локальний час RTC (Unix секунди) */
    uint32_t sequence_id;    /* Монотонний лічильник події */
    uint16_t event_code;     /* Код події (наприклад, 0xE001 - Overheat) */
    int16_t  payload_val;    /* Значення датчика або аргумент */
    uint8_t  priority;       /* event_prio_t */
    uint8_t  acknowledged;   /* Прапорець підтвердження бекендом */
} offline_event_t;

/* Структура кільцевого буфера подій одного пріоритету */
typedef struct {
    offline_event_t buffer[TELEMETRY_QUEUE_SIZE];
    uint16_t head;
    uint16_t tail;
    uint16_t count;
    uint16_t capacity;
    uint32_t dropped_count;  /* Лічильник витіснених записів при переповненні */
} event_ring_t;

/* Правило локального автомата */
typedef struct {
    int16_t  temp_threshold_c_x10; /* Поріг увімкнення (наприклад, 22.0 C -> 220) */
    int16_t  temp_hysteresis_c_x10;/* Гістерезис (наприклад, 1.5 C -> 15) */
    uint32_t safe_mode_timeout_s;  /* Час без зв'язку до переходу у Fail-Safe */
    bool     heater_forced_off;    /* Захисне блокування */
} local_rules_t;

/* Актуальний та бажаний стан пристрою */
typedef struct {
    uint32_t state_version;        /* Локальний лічильник мутацій */
    uint32_t cloud_known_version;  /* Остання версія, підтверджена хмарою */
    bool     heater_active;        /* Поточний фізичний стан нагрівача */
    bool     alarm_latched;        /* Стан аварійного блокування */
    int16_t  last_temperature;     /* Останній вимір температури */
} device_state_t;

/* Головний контекст автономного вузла */
typedef struct {
    local_rules_t   rules;
    device_state_t  state;
    event_ring_t    q_alarm;
    event_ring_t    q_audit;
    event_ring_t    q_telemetry;
    uint32_t        global_seq;
    uint32_t        offline_duration_s;
    bool            network_online;
} offline_controller_t;

/* Ініціалізація кільцевого буфера */
static void ring_init(event_ring_t *ring, uint16_t capacity) {
    memset(ring->buffer, 0, sizeof(ring->buffer));
    ring->head = 0;
    ring->tail = 0;
    ring->count = 0;
    ring->capacity = capacity;
    ring->dropped_count = 0;
}

/* Запис події в буфер відповідного пріоритету */
static bool ring_push(event_ring_t *ring, const offline_event_t *ev, bool allow_overwrite) {
    if (ring->count >= ring->capacity) {
        if (!allow_overwrite) {
            /* Для критичних аварій: відхиляємо, якщо немає права перезапису */
            ring->dropped_count++;
            return false;
        }
        /* Для телеметрії та аудиту: зсуваємо хвіст (витісняємо найстаріший елемент) */
        ring->tail = (ring->tail + 1) % ring->capacity;
        ring->count--;
        ring->dropped_count++;
    }
    ring->buffer[ring->head] = *ev;
    ring->head = (ring->head + 1) % ring->capacity;
    ring->count++;
    return true;
}

/* Вичитування події з черги без видалення */
static bool ring_peek(event_ring_t *ring, offline_event_t *out_ev) {
    if (ring->count == 0) {
        return false;
    }
    *out_ev = ring->buffer[ring->tail];
    return true;
}

/* Підтвердження передачі та видалення з черги */
static void ring_pop(event_ring_t *ring) {
    if (ring->count > 0) {
        ring->tail = (ring->tail + 1) % ring->capacity;
        ring->count--;
    }
}

/* Ініціалізація контролера */
void offline_controller_init(offline_controller_t *ctrl) {
    memset(ctrl, 0, sizeof(*ctrl));
    ctrl->rules.temp_threshold_c_x10 = 220;  /* 22.0 °C */
    ctrl->rules.temp_hysteresis_c_x10 = 15;  /* 1.5 °C */
    ctrl->rules.safe_mode_timeout_s = 3600;  /* 1 година */
    ctrl->rules.heater_forced_off = false;

    ctrl->state.state_version = 1;
    ctrl->state.cloud_known_version = 0;
    ctrl->state.heater_active = false;
    ctrl->state.alarm_latched = false;

    ring_init(&ctrl->q_alarm, ALARM_QUEUE_SIZE);
    ring_init(&ctrl->q_audit, AUDIT_QUEUE_SIZE);
    ring_init(&ctrl->q_telemetry, TELEMETRY_QUEUE_SIZE);
}

/* Локальний контур керування (виклик у RTOS-задачі або головному циклі раз на 100 мс) */
void offline_controller_process_loop(offline_controller_t *ctrl,
                                     int16_t current_temp_x10,
                                     uint32_t rtc_now_s,
                                     uint32_t dt_ms) {
    ctrl->state.last_temperature = current_temp_x10;

    if (!ctrl->network_online) {
        ctrl->offline_duration_s += (dt_ms / 1000);
    } else {
        ctrl->offline_duration_s = 0;
    }

    /* 1. Захисна перевірка на критичний перегрів (> 50.0 °C) */
    if (current_temp_x10 > 500 && !ctrl->state.alarm_latched) {
        ctrl->state.alarm_latched = true;
        ctrl->state.heater_active = false;
        ctrl->state.state_version++;

        offline_event_t ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0xE001, /* Emergency Overheat */
            .payload_val = current_temp_x10,
            .priority = EVENT_PRIO_ALARM,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_alarm, &ev, false);
        return;
    }

    /* 2. Якщо зафіксовано аварію або захисне блокування — актуатор вимкнено */
    if (ctrl->state.alarm_latched || ctrl->rules.heater_forced_off) {
        ctrl->state.heater_active = false;
        return;
    }

    /* 3. Автономний гістерезисний терморегулятор */
    int16_t target = ctrl->rules.temp_threshold_c_x10;
    int16_t hyst = ctrl->rules.temp_hysteresis_c_x10;

    bool prev_heater = ctrl->state.heater_active;
    if (current_temp_x10 < (target - hyst)) {
        ctrl->state.heater_active = true;
    } else if (current_temp_x10 > (target + hyst)) {
        ctrl->state.heater_active = false;
    }

    /* Фіксація зміни стану в аудит-лозі */
    if (prev_heater != ctrl->state.heater_active) {
        ctrl->state.state_version++;
        offline_event_t audit_ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0xA010, /* State Transition */
            .payload_val = (int16_t)ctrl->state.heater_active,
            .priority = EVENT_PRIO_AUDIT,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_audit, &audit_ev, true);
    }
}

/* Періодичне збереження телеметрії з фільтрацією Deadband */
void offline_controller_log_telemetry(offline_controller_t *ctrl,
                                      uint32_t rtc_now_s,
                                      int16_t current_temp_x10) {
    static int16_t last_logged_temp = -9999;
    int16_t diff = current_temp_x10 - last_logged_temp;
    if (diff < 0) diff = -diff;

    /* Зберігаємо лише якщо температура змінилася більш ніж на 0.5 °C (5 одиниць) */
    if (diff >= 5 || last_logged_temp == -9999) {
        last_logged_temp = current_temp_x10;
        offline_event_t telem_ev = {
            .timestamp_s = rtc_now_s,
            .sequence_id = ++ctrl->global_seq,
            .event_code = 0x1001, /* Telemetry sample */
            .payload_val = current_temp_x10,
            .priority = EVENT_PRIO_TELEMETRY,
            .acknowledged = 0
        };
        ring_push(&ctrl->q_telemetry, &telem_ev, true);
    }
}

/* Процедура реконсиліації: обробка отриманого від хмари бажаного стану (Desired State) */
bool offline_controller_reconcile_cloud_command(offline_controller_t *ctrl,
                                                uint32_t cloud_version,
                                                int16_t new_temp_target_x10,
                                                bool force_heater_off) {
    /* ПРАВИЛО БЕЗПЕКИ 1: Якщо на пристрої активна апаратна аварія (Overheat),
     * хмара не може скинути її звичайною зміною уставки без прямого скидання тривоги */
    if (ctrl->state.alarm_latched && !force_heater_off) {
        return false; /* Конфлікт: локальна безпека має абсолютний пріоритет */
    }

    /* ПРАВИЛО УСТАВОК 2: Якщо версія конфігурації з хмари новіша — застосовуємо */
    if (cloud_version > ctrl->state.cloud_known_version) {
        ctrl->rules.temp_threshold_c_x10 = new_temp_target_x10;
        ctrl->rules.heater_forced_off = force_heater_off;
        ctrl->state.cloud_known_version = cloud_version;
        ctrl->state.state_version = cloud_version + 1;
        return true;
    }

    return false;
}

/* Дренаж черг після відновлення зв'язку: вибирає наступну найпріоритетнішу подію */
bool offline_controller_get_next_event_to_sync(offline_controller_t *ctrl,
                                               offline_event_t *out_ev,
                                               event_ring_t **out_source_ring) {
    /* Спершу аварії */
    if (ring_peek(&ctrl->q_alarm, out_ev)) {
        *out_source_ring = &ctrl->q_alarm;
        return true;
    }
    /* Потім аудит */
    if (ring_peek(&ctrl->q_audit, out_ev)) {
        *out_source_ring = &ctrl->q_audit;
        return true;
    }
    /* Насамкінець телеметрія */
    if (ring_peek(&ctrl->q_telemetry, out_ev)) {
        *out_source_ring = &ctrl->q_telemetry;
        return true;
    }
    return false;
}

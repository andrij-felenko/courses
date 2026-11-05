#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ACTUATORS 16

typedef struct {
    uint32_t actuator_id;
    float target_value;
    uint32_t timestamp_ms;
    bool is_occupied;
} conflated_slot_t;

typedef struct {
    conflated_slot_t slots[MAX_ACTUATORS];
    uint32_t last_dispatch_time[MAX_ACTUATORS];
    float last_dispatch_value[MAX_ACTUATORS];
    bool has_dispatched[MAX_ACTUATORS];
    uint32_t cooldown_ms;
    uint32_t suppressed_count;
} conflating_buffer_t;

void conflating_buffer_init(conflating_buffer_t *buf, uint32_t cooldown_ms) {
    memset(buf, 0, sizeof(conflating_buffer_t));
    buf->cooldown_ms = cooldown_ms;
}

bool conflating_buffer_push(conflating_buffer_t *buf, uint32_t actuator_id, float value, uint32_t now_ms) {
    if (actuator_id >= MAX_ACTUATORS) {
        return false;
    }

    /* Фільтрація дублікатів щодо останнього відправленого значення */
    if (buf->has_dispatched[actuator_id] && buf->last_dispatch_value[actuator_id] == value) {
        buf->suppressed_count++;
        return true;
    }

    /* Якщо слот вже містить незчитане значення, воно витісняється найновішим */
    if (buf->slots[actuator_id].is_occupied) {
        buf->suppressed_count++;
    }

    buf->slots[actuator_id].actuator_id = actuator_id;
    buf->slots[actuator_id].target_value = value;
    buf->slots[actuator_id].timestamp_ms = now_ms;
    buf->slots[actuator_id].is_occupied = true;
    return true;
}

bool conflating_buffer_pop_ready(conflating_buffer_t *buf, uint32_t actuator_id, float *out_value, uint32_t now_ms) {
    if (actuator_id >= MAX_ACTUATORS || !out_value) {
        return false;
    }

    conflated_slot_t *slot = &buf->slots[actuator_id];
    if (!slot->is_occupied) {
        return false;
    }

    /* Перевірка часового інтервалу охолодження */
    if (buf->has_dispatched[actuator_id]) {
        uint32_t elapsed = now_ms - buf->last_dispatch_time[actuator_id];
        if (elapsed < buf->cooldown_ms) {
            return false; /* Триває захисна пауза приводу */
        }
    }

    *out_value = slot->target_value;
    buf->last_dispatch_time[actuator_id] = now_ms;
    buf->last_dispatch_value[actuator_id] = slot->target_value;
    buf->has_dispatched[actuator_id] = true;
    slot->is_occupied = false;
    return true;
}

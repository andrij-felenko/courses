#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_ACTUATORS 8

typedef struct {
    uint32_t actuator_id;
    float target_value;
    uint32_t timestamp_ms;
    bool is_valid;
} actuator_command_t;

typedef struct {
    actuator_command_t slots[MAX_ACTUATORS];
    uint32_t cooldown_ms;
    uint32_t last_sent_time[MAX_ACTUATORS];
    float last_sent_value[MAX_ACTUATORS];
    uint32_t suppressed_count;
} conflator_t;

void conflator_init(conflator_t *confl, uint32_t cooldown_ms) {
    memset(confl, 0, sizeof(conflator_t));
    confl->cooldown_ms = cooldown_ms;
}

bool conflator_push(conflator_t *confl, uint32_t actuator_id, float value, uint32_t now_ms) {
    if (actuator_id >= MAX_ACTUATORS) return false;

    /* Стратегія Deduplication: ігноруємо ідентичні значення */
    if (confl->last_sent_value[actuator_id] == value && confl->slots[actuator_id].is_valid) {
        confl->suppressed_count++;
        return true;
    }

    /* Стратегія Latest-Wins: перезаписуємо слот найновішою уставою */
    if (confl->slots[actuator_id].is_valid) {
        confl->suppressed_count++; /* Попереднє незабране значення згорнуто */
    }

    confl->slots[actuator_id].actuator_id = actuator_id;
    confl->slots[actuator_id].target_value = value;
    confl->slots[actuator_id].timestamp_ms = now_ms;
    confl->slots[actuator_id].is_valid = true;
    return true;
}

bool conflator_pop_ready(conflator_t *confl, uint32_t actuator_id, float *out_value, uint32_t now_ms) {
    if (actuator_id >= MAX_ACTUATORS) return false;
    actuator_command_t *slot = &confl->slots[actuator_id];

    if (!slot->is_valid) return false;

    /* Перевірка Cooldown Enforcement: перевіряємо мінімальний інтервал перемикання */
    if ((now_ms - confl->last_sent_time[actuator_id]) < confl->cooldown_ms) {
        return false; /* Ще триває інтервал охолодження актуатора */
    }

    *out_value = slot->target_value;
    confl->last_sent_time[actuator_id] = now_ms;
    confl->last_sent_value[actuator_id] = slot->target_value;
    slot->is_valid = false;
    return true;
}

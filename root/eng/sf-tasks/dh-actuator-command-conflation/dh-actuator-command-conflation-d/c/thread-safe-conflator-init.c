#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>

#define MAX_ACTUATORS 16

typedef struct {
    uint64_t sequence_num;
    float target_value;
    uint32_t timestamp_ms;
    bool is_occupied;
} ts_conflated_slot_t;

typedef struct {
    ts_conflated_slot_t slots[MAX_ACTUATORS];
    uint64_t last_processed_seq[MAX_ACTUATORS];
    _Atomic uint32_t suppressed_count;
} thread_safe_conflator_t;

void thread_safe_conflator_init(thread_safe_conflator_t *confl) {
    for (int i = 0; i < MAX_ACTUATORS; i++) {
        confl->slots[i].sequence_num = 0;
        confl->slots[i].target_value = 0.0f;
        confl->slots[i].timestamp_ms = 0;
        confl->slots[i].is_occupied = false;
        confl->last_processed_seq[i] = 0;
    }
    atomic_store(&confl->suppressed_count, 0);
}

bool thread_safe_conflator_push(thread_safe_conflator_t *confl, uint32_t actuator_id, 
                                float value, uint64_t seq_num, uint32_t now_ms) {
    if (actuator_id >= MAX_ACTUATORS) return false;

    /* Захист від інверсії хронологічного порядку устав */
    if (seq_num <= confl->last_processed_seq[actuator_id]) {
        atomic_fetch_add(&confl->suppressed_count, 1);
        return false; /* Застаріла команда відкинута */
    }

    ts_conflated_slot_t *slot = &confl->slots[actuator_id];
    if (slot->is_occupied) {
        if (seq_num <= slot->sequence_num) {
            atomic_fetch_add(&confl->suppressed_count, 1);
            return false; /* У слоті вже лежить новіша команда */
        }
        atomic_fetch_add(&confl->suppressed_count, 1); /* Перезапис старішої команди */
    }

    slot->sequence_num = seq_num;
    slot->target_value = value;
    slot->timestamp_ms = now_ms;
    slot->is_occupied = true;
    return true;
}

bool thread_safe_conflator_pop(thread_safe_conflator_t *confl, uint32_t actuator_id, 
                               float *out_value, uint64_t *out_seq) {
    if (actuator_id >= MAX_ACTUATORS || !out_value) return false;

    ts_conflated_slot_t *slot = &confl->slots[actuator_id];
    if (!slot->is_occupied) return false;

    *out_value = slot->target_value;
    if (out_seq) *out_seq = slot->sequence_num;
    confl->last_processed_seq[actuator_id] = slot->sequence_num;
    slot->is_occupied = false;
    return true;
}

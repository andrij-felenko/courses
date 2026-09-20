typedef enum {
    STATE_RELEASED,
    STATE_ENABLED,
    STATE_PANIC,
    STATE_FAULT
} enabling_fsm_state_t;

typedef struct {
    enabling_fsm_state_t current_state;
    uint64_t sync_start_time;
    bool sync_pending;
    uint32_t discrepancy_timeout_us;
} enabling_fsm_t;

enabling_fsm_state_t enabling_fsm_process(enabling_fsm_t *fsm, bool ch_a, bool ch_b, uint64_t now) {
    bool mismatch = (ch_a != ch_b);

    if (mismatch) {
        if (!fsm->sync_pending) {
            fsm->sync_pending = true;
            fsm->sync_start_time = now;
        } else if ((now - fsm->sync_start_time) > fsm->discrepancy_timeout_us) {
            fsm->current_state = STATE_FAULT;
            return fsm->current_state;
        }
    } else {
        fsm->sync_pending = false;
    }

    if (fsm->current_state == STATE_FAULT) {
        if (!ch_a && !ch_b) {
            fsm->current_state = STATE_RELEASED;
        }
        return fsm->current_state;
    }

    if (!ch_a && !ch_b) {
        fsm->current_state = STATE_RELEASED;
    } else if (ch_a && ch_b) {
        if (fsm->current_state != STATE_PANIC) {
            fsm->current_state = STATE_ENABLED;
        }
    } else if (fsm->current_state == STATE_ENABLED && mismatch) {
        // Очікування синхронізації або перехід в паніка/аварія
    }
    return fsm->current_state;
}

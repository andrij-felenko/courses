#include <stdbool.h>
#include <stdint.h>

typedef enum {
    PIEZO_STATE_IDLE,
    PIEZO_STATE_INTEGRATING,
    PIEZO_STATE_BLANKING
} piezo_state_t;

typedef struct {
    float v_th_start;
    float v_th_stop;
    float e_min;
    uint32_t blank_ticks;
    piezo_state_t state;
    float accumulated_energy;
    uint32_t timer;
} piezo_detector_t;

bool piezo_process_sample(piezo_detector_t *det, float voltage, float dt) {
    bool event_detected = false;
    float v_sq = voltage * voltage;

    switch (det->state) {
        case PIEZO_STATE_IDLE:
            if (voltage >= det->v_th_start) {
                det->accumulated_energy = v_sq * dt;
                det->state = PIEZO_STATE_INTEGRATING;
            }
            break;
        case PIEZO_STATE_INTEGRATING:
            det->accumulated_energy += v_sq * dt;
            if (voltage < det->v_th_stop) {
                if (det->accumulated_energy >= det->e_min) {
                    event_detected = true;
                    det->timer = det->blank_ticks;
                    det->state = PIEZO_STATE_BLANKING;
                } else {
                    det->state = PIEZO_STATE_IDLE;
                }
            }
            break;
        case PIEZO_STATE_BLANKING:
            if (det->timer > 0) {
                det->timer--;
            } else if (voltage < det->v_th_stop) {
                det->state = PIEZO_STATE_IDLE;
            }
            break;
    }
    return event_detected;
}

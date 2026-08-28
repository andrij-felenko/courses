#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

#define MAVLINK_PARAM_ID_LEN 16
#define MAX_PARAMS_CAPACITY 2048
#define MASK_BYTES (MAX_PARAMS_CAPACITY / 8)
#define MAX_RETRIES 3
#define MAX_BATCH_MISSING 8

typedef enum {
    SYNC_STATE_IDLE,
    SYNC_STATE_REQUESTING_ALL,
    SYNC_STATE_RECEIVING_STREAM,
    SYNC_STATE_REQUESTING_MISSING,
    SYNC_STATE_SYNCED,
    SYNC_STATE_ERROR
} sync_state_t;

typedef struct {
    char name[17];
    float raw_value;
    uint8_t type;
    uint16_t index;
} param_record_t;

typedef struct {
    char name[17];
    float raw_value;
    uint8_t type;
    int retries;
    uint32_t last_sent_ms;
} pending_write_t;

typedef struct {
    uint8_t sys_id;
    uint8_t comp_id;
    uint8_t target_sys;
    uint8_t target_comp;

    sync_state_t state;
    uint16_t total_count;
    uint16_t received_count;
    uint8_t bitmask[MASK_BYTES];
    param_record_t params[MAX_PARAMS_CAPACITY];

    uint32_t last_packet_ms;
    int retries_count;
    uint16_t sweep_index;

    pending_write_t write_queue[8];
    size_t write_queue_len;

    void (*send_fn)(const uint8_t *buf, size_t len);
} param_sync_c_engine_t;

/* Робота з бітовою маскою */
static inline bool is_bit_set(const uint8_t *mask, uint16_t idx) {
    return (mask[idx / 8] & (1 << (idx % 8))) != 0;
}

static inline void set_bit(uint8_t *mask, uint16_t idx) {
    mask[idx / 8] |= (1 << (idx % 8));
}

void param_engine_init(param_sync_c_engine_t *eng,
                       uint8_t sys_id, uint8_t comp_id,
                       uint8_t target_sys, uint8_t target_comp,
                       void (*send_fn)(const uint8_t*, size_t)) {
    memset(eng, 0, sizeof(*eng));
    eng->sys_id = sys_id;
    eng->comp_id = comp_id;
    eng->target_sys = target_sys;
    eng->target_comp = target_comp;
    eng->send_fn = send_fn;
    eng->state = SYNC_STATE_IDLE;
}

void param_engine_start_sync(param_sync_c_engine_t *eng, uint32_t now_ms) {
    eng->state = SYNC_STATE_REQUESTING_ALL;
    eng->total_count = 0;
    eng->received_count = 0;
    eng->retries_count = 0;
    eng->last_packet_ms = now_ms;
    memset(eng->bitmask, 0, sizeof(eng->bitmask));

    /* Відправка PARAM_REQUEST_LIST */
    uint8_t dummy[16] = {0};
    if (eng->send_fn) eng->send_fn(dummy, sizeof(dummy));
}

void param_engine_handle_param_value(param_sync_c_engine_t *eng,
                                     const char raw_id[16], float val, uint8_t type,
                                     uint16_t count, uint16_t index, uint32_t now_ms) {
    eng->last_packet_ms = now_ms;

    if (eng->state == SYNC_STATE_REQUESTING_ALL || eng->total_count == 0) {
        eng->total_count = (count > MAX_PARAMS_CAPACITY) ? MAX_PARAMS_CAPACITY : count;
        eng->state = SYNC_STATE_RECEIVING_STREAM;
    }

    if (index < eng->total_count) {
        if (!is_bit_set(eng->bitmask, index)) {
            set_bit(eng->bitmask, index);
            eng->received_count++;

            param_record_t *p = &eng->params[index];
            memcpy(p->name, raw_id, 16);
            p->name[16] = '\0';
            p->raw_value = val;
            p->type = type;
            p->index = index;
        }
    }

    if (eng->received_count == eng->total_count && eng->total_count > 0) {
        eng->state = SYNC_STATE_SYNCED;
    }
}

void param_engine_update(param_sync_c_engine_t *eng, uint32_t now_ms) {
    uint32_t elapsed = now_ms - eng->last_packet_ms;

    switch (eng->state) {
    case SYNC_STATE_REQUESTING_ALL:
        if (elapsed > 1500) {
            if (++eng->retries_count > MAX_RETRIES) {
                eng->state = SYNC_STATE_ERROR;
            } else {
                eng->last_packet_ms = now_ms;
                uint8_t dummy[16] = {0};
                if (eng->send_fn) eng->send_fn(dummy, sizeof(dummy));
            }
        }
        break;

    case SYNC_STATE_RECEIVING_STREAM:
        if (elapsed > 600) {
            eng->state = SYNC_STATE_REQUESTING_MISSING;
            eng->sweep_index = 0;
            eng->last_packet_ms = now_ms;
        }
        break;

    case SYNC_STATE_REQUESTING_MISSING:
        if (elapsed > 600) {
            size_t batch = 0;
            while (eng->sweep_index < eng->total_count && batch < MAX_BATCH_MISSING) {
                if (!is_bit_set(eng->bitmask, eng->sweep_index)) {
                    /* Відправка PARAM_REQUEST_READ за індексом sweep_index */
                    uint8_t dummy[24] = {0};
                    if (eng->send_fn) eng->send_fn(dummy, sizeof(dummy));
                    batch++;
                }
                eng->sweep_index++;
            }
            if (eng->sweep_index >= eng->total_count) {
                eng->sweep_index = 0;
                if (eng->received_count == eng->total_count) {
                    eng->state = SYNC_STATE_SYNCED;
                }
            }
            eng->last_packet_ms = now_ms;
        }
        break;

    default:
        break;
    }
}

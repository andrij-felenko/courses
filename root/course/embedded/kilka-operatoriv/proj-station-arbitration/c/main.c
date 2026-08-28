#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define ARBITER_MAX_STATIONS        8
#define ARBITER_HEARTBEAT_TIMEOUT   1000  /* мс */
#define ARBITER_HANDOVER_TIMEOUT    5000  /* мс */
#define ARBITER_DEADBAND_LIMIT        30  /* 3% від діапазону 1000 */

typedef enum {
    ROLE_FLAG_NONE      = 0x00,
    ROLE_FLAG_MONITOR   = 0x01,
    ROLE_FLAG_PILOT     = 0x02,
    ROLE_FLAG_PAYLOAD   = 0x04,
    ROLE_FLAG_COMMANDER = 0x08
} role_flag_t;

typedef enum {
    STATE_IDLE = 0,
    STATE_PILOT_ACTIVE,
    STATE_HANDOVER_WAIT_STICK,
    STATE_LINK_LOST,
    STATE_COMMANDER_LOCKED
} arbiter_state_t;

typedef struct {
    int16_t roll;      /* -1000 .. +1000 */
    int16_t pitch;     /* -1000 .. +1000 */
    int16_t yaw;       /* -1000 .. +1000 */
    int16_t throttle;  /* 0 .. 1000 */
} stick_axes_t;

typedef struct {
    uint8_t         pilot_gcs_id;
    uint8_t         payload_gcs_id;
    uint8_t         pending_pilot_gcs_id;
    uint32_t        pilot_lease_deadline;
    uint32_t        handover_deadline;
    uint32_t        token_nonce;
    arbiter_state_t state;
} arbiter_context_t;

static arbiter_context_t g_arbiter;

static uint32_t generate_next_nonce(void) {
    static uint32_t s_seed = 0x1337BEEF;
    s_seed = s_seed * 1664525u + 1013904223u;
    return s_seed;
}

static bool is_axis_in_deadband(int16_t val, int16_t limit) {
    return (val >= -limit) && (val <= limit);
}

void arbiter_init(void) {
    memset(&g_arbiter, 0, sizeof(g_arbiter));
    g_arbiter.state = STATE_IDLE;
    g_arbiter.token_nonce = generate_next_nonce();
}

bool arbiter_request_pilot_token(uint8_t gcs_id, uint32_t now_ms, uint32_t *out_nonce) {
    if (g_arbiter.state == STATE_COMMANDER_LOCKED) {
        return false;
    }
    if (g_arbiter.state == STATE_IDLE || g_arbiter.state == STATE_LINK_LOST) {
        g_arbiter.pilot_gcs_id = gcs_id;
        g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
        g_arbiter.token_nonce = generate_next_nonce();
        g_arbiter.state = STATE_PILOT_ACTIVE;
        if (out_nonce) {
            *out_nonce = g_arbiter.token_nonce;
        }
        return true;
    }
    return false;
}

bool arbiter_process_heartbeat(uint8_t gcs_id, uint8_t roles, uint32_t now_ms) {
    if (gcs_id == g_arbiter.pilot_gcs_id && (roles & ROLE_FLAG_PILOT)) {
        g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
        if (g_arbiter.state == STATE_LINK_LOST) {
            g_arbiter.state = STATE_PILOT_ACTIVE;
        }
        return true;
    }
    if (roles & ROLE_FLAG_PAYLOAD) {
        g_arbiter.payload_gcs_id = gcs_id;
    }
    return true;
}

bool arbiter_initiate_handover(uint8_t current_pilot_id, uint8_t target_gcs_id, uint32_t now_ms) {
    if (g_arbiter.state != STATE_PILOT_ACTIVE || current_pilot_id != g_arbiter.pilot_gcs_id) {
        return false;
    }
    g_arbiter.pending_pilot_gcs_id = target_gcs_id;
    g_arbiter.handover_deadline = now_ms + ARBITER_HANDOVER_TIMEOUT;
    g_arbiter.state = STATE_HANDOVER_WAIT_STICK;
    return true;
}

bool arbiter_confirm_handover_sticks(uint8_t candidate_id, const stick_axes_t *sticks, uint32_t now_ms, uint32_t *out_nonce) {
    if (g_arbiter.state != STATE_HANDOVER_WAIT_STICK || candidate_id != g_arbiter.pending_pilot_gcs_id) {
        return false;
    }
    if (now_ms > g_arbiter.handover_deadline) {
        g_arbiter.state = STATE_PILOT_ACTIVE;
        g_arbiter.pending_pilot_gcs_id = 0;
        return false;
    }
    /* Перевірка нейтралі: крен, тангаж, рискання у межах 3% */
    if (!is_axis_in_deadband(sticks->roll, ARBITER_DEADBAND_LIMIT) ||
        !is_axis_in_deadband(sticks->pitch, ARBITER_DEADBAND_LIMIT) ||
        !is_axis_in_deadband(sticks->yaw, ARBITER_DEADBAND_LIMIT)) {
        return false;
    }

    /* Атомарне перемикання володаря */
    g_arbiter.pilot_gcs_id = candidate_id;
    g_arbiter.pending_pilot_gcs_id = 0;
    g_arbiter.pilot_lease_deadline = now_ms + ARBITER_HEARTBEAT_TIMEOUT;
    g_arbiter.token_nonce = generate_next_nonce();
    g_arbiter.state = STATE_PILOT_ACTIVE;

    if (out_nonce) {
        *out_nonce = g_arbiter.token_nonce;
    }
    return true;
}

void arbiter_commander_override(uint8_t commander_id, uint32_t now_ms) {
    (void)commander_id;
    (void)now_ms;
    g_arbiter.state = STATE_COMMANDER_LOCKED;
    g_arbiter.pilot_gcs_id = 0;
    g_arbiter.pending_pilot_gcs_id = 0;
    g_arbiter.token_nonce = generate_next_nonce();
}

bool arbiter_is_flight_command_allowed(uint8_t src_gcs_id, uint32_t nonce) {
    if (g_arbiter.state != STATE_PILOT_ACTIVE && g_arbiter.state != STATE_HANDOVER_WAIT_STICK) {
        return false;
    }
    return (src_gcs_id == g_arbiter.pilot_gcs_id) && (nonce == g_arbiter.token_nonce);
}

void arbiter_periodic_tick(uint32_t now_ms) {
    if (g_arbiter.state == STATE_PILOT_ACTIVE || g_arbiter.state == STATE_HANDOVER_WAIT_STICK) {
        if (now_ms >= g_arbiter.pilot_lease_deadline) {
            g_arbiter.state = STATE_LINK_LOST;
        }
    }
    if (g_arbiter.state == STATE_HANDOVER_WAIT_STICK) {
        if (now_ms >= g_arbiter.handover_deadline) {
            g_arbiter.state = STATE_PILOT_ACTIVE;
            g_arbiter.pending_pilot_gcs_id = 0;
        }
    }
}

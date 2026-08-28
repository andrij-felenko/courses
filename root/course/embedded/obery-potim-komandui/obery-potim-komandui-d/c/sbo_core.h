/* sbo_core.h — Структури та функції перевірки стану мовою C */
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    SBO_STATE_IDLE = 0,
    SBO_STATE_ARMED,
    SBO_STATE_EXECUTED
} sbo_state_t;

typedef struct {
    uint8_t     my_node_id;
    sbo_state_t state;
    uint32_t    active_token;
    uint32_t    expiry_time_ms;
    uint16_t    expected_cmd;
} sbo_gate_t;

void sbo_gate_init(sbo_gate_t *gate, uint8_t node_id);
bool sbo_gate_arm(sbo_gate_t *gate, uint16_t cmd, uint32_t token, uint32_t window_ms, uint32_t now_ms);
bool sbo_gate_verify_and_consume(sbo_gate_t *gate, uint16_t cmd, uint32_t token, uint32_t now_ms);
void sbo_gate_tick(sbo_gate_t *gate, uint32_t now_ms);

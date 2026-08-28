#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STATE_STANDBY,
    STATE_CONNECTED,
    STATE_CHARGING,
    STATE_FAULT
} FsmState;

typedef enum {
    EVT_PLUG_IN,
    EVT_AUTH_SUCCESS,
    EVT_UNPLUG,
    EVT_OVERCURRENT,
    EVT_RESET_BTN
} FsmEvent;

typedef struct {
    FsmState state;
    uint16_t current_ma;
    bool is_locked;
} EvseController;

void evse_fsm_dispatch(EvseController *ctx, FsmEvent evt) {
    switch (ctx->state) {
        case STATE_STANDBY:
            if (evt == EVT_PLUG_IN) {
                // Дія переходу
                ctx->is_locked = true;
                ctx->state = STATE_CONNECTED;
            }
            break;

        case STATE_CONNECTED:
            if (evt == EVT_AUTH_SUCCESS) {
                // Вмикаємо контактор
                ctx->state = STATE_CHARGING;
            } else if (evt == EVT_UNPLUG) {
                ctx->is_locked = false;
                ctx->state = STATE_STANDBY;
            }
            break;

        case STATE_CHARGING:
            if (evt == EVT_OVERCURRENT) {
                // Аварія: негайно розмикаємо реле
                ctx->state = STATE_FAULT;
            } else if (evt == EVT_UNPLUG) {
                ctx->is_locked = false;
                ctx->state = STATE_STANDBY;
            }
            break;

        case STATE_FAULT:
            if (evt == EVT_RESET_BTN) {
                ctx->state = STATE_STANDBY;
            }
            break;
    }
}

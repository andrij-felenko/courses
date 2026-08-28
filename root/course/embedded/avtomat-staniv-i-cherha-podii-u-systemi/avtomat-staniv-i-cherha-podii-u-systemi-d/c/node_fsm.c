// node_fsm.c — Реалізація автомата польового вузла на C
#include "hsm_engine.h"
#include <stdio.h>

enum {
    SIG_TIMER_TICK = Q_SIG_USER_START,
    SIG_DATA_READY,
    SIG_NET_OK,
    SIG_NET_TIMEOUT,
    SIG_LOW_BATTERY,
    SIG_BUTTON_PRESS
};

typedef struct {
    hsm_t super;
    uint32_t battery_mv;
    uint16_t samples[16];
} iot_node_t;

static q_result_t state_root(hsm_t *me, const event_t *e);
static q_result_t state_operational(hsm_t *me, const event_t *e);
static q_result_t state_idle(hsm_t *me, const event_t *e);
static q_result_t state_sampling(hsm_t *me, const event_t *e);
static q_result_t state_communicating(hsm_t *me, const event_t *e);
static q_result_t state_modem_connecting(hsm_t *me, const event_t *e);
static q_result_t state_data_publishing(hsm_t *me, const event_t *e);
static q_result_t state_fault(hsm_t *me, const event_t *e);

// 1. Кореневий стан
static q_result_t state_root(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_INIT:
            return Q_TRAN(state_operational);

        case SIG_LOW_BATTERY:
            printf("[Root] Low battery (%u mV)! Emergency shutdown.\n", (unsigned)e->param);
            return Q_TRAN(state_fault);

        default:
            return Q_SUPER(hsm_top_state);
    }
}

// 2. Суперстан нормальної роботи
static q_result_t state_operational(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Operational] Entry: Enable 3V3 sensor power rail\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Operational] Exit: Disable 3V3 rail, ensure radio OFF\n");
            return Q_HANDLED();

        case Q_SIG_INIT:
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_root);
    }
}

// 3. Підстан очікування (Idle)
static q_result_t state_idle(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Idle] Entry: Arm periodic wakeup timer\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Idle] Exit: Disarm wakeup timer\n");
            return Q_HANDLED();

        case SIG_TIMER_TICK:
        case SIG_BUTTON_PRESS:
            return Q_TRAN(state_sampling);

        default:
            return Q_SUPER(state_operational);
    }
}

// 4. Підстан збору даних (Sampling)
static q_result_t state_sampling(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Sampling] Entry: Start ADC conversion over DMA\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Sampling] Exit: Stop ADC DMA\n");
            return Q_HANDLED();

        case SIG_DATA_READY:
            printf("[Sampling] Acquired %u samples! Transition to Connect\n", (unsigned)e->param);
            return Q_TRAN(state_modem_connecting);

        default:
            return Q_SUPER(state_operational);
    }
}

// 5. Суперстан зв'язку (Communicating)
static q_result_t state_communicating(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Communicating] Entry: Power on cellular modem\n");
            return Q_HANDLED();

        case Q_SIG_EXIT:
            printf("[Communicating] Exit: Send AT+CPOWD power down to modem\n");
            return Q_HANDLED();

        case SIG_NET_TIMEOUT:
            printf("[Communicating] Network timeout! Return to idle.\n");
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_operational);
    }
}

// 6. Підстан реєстрації в мережі
static q_result_t state_modem_connecting(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[ModemConnecting] Entry: Send AT+CREG? check registration\n");
            return Q_HANDLED();

        case SIG_NET_OK:
            printf("[ModemConnecting] Network registered! Publish telemetry.\n");
            return Q_TRAN(state_data_publishing);

        default:
            return Q_SUPER(state_communicating);
    }
}

// 7. Підстан передачі даних
static q_result_t state_data_publishing(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[DataPublishing] Entry: Publish MQTT telemetry packet\n");
            return Q_HANDLED();

        case SIG_NET_OK:
            printf("[DataPublishing] Telemetry ACK received!\n");
            return Q_TRAN(state_idle);

        default:
            return Q_SUPER(state_communicating);
    }
}

// 8. Аварійний стан
static q_result_t state_fault(hsm_t *me, const event_t *e) {
    switch (e->sig) {
        case Q_SIG_ENTRY:
            printf("[Fault] Entry: Disconnect relays, write crashlog, sleep.\n");
            return Q_HANDLED();

        default:
            return Q_SUPER(state_root);
    }
}

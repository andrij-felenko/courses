#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PDOS 7
#define V_SAFE_MAX_MV 20000
#define V_TARGET_MV   12000
#define I_REQUIRED_MA 2000
#define R_CABLE_MOHM  200

typedef enum {
    PE_SNK_DISCOVERY,
    PE_SNK_WAIT_FOR_CAP,
    PE_SNK_EVALUATE_CAP,
    PE_SNK_SELECT_CAP,
    PE_SNK_TRANSITION_SINK,
    PE_SNK_READY,
    PE_SNK_GIVEBACK,
    PE_SNK_HARD_RESET
} pe_state_t;

typedef enum {
    EV_NONE,
    EV_VBUS_DETECTED,
    EV_SOURCE_CAPS_RECEIVED,
    EV_ACCEPT_RECEIVED,
    EV_REJECT_RECEIVED,
    EV_WAIT_RECEIVED,
    EV_PS_RDY_RECEIVED,
    EV_GOTOMIN_RECEIVED,
    EV_TIMEOUT,
    EV_ERROR
} pe_event_t;

typedef struct {
    uint8_t  position;     // Позиція PDO (1-based: 1..7)
    uint8_t  type;         // 0: Fixed, 1: Variable, 2: Battery, 3: PPS
    uint32_t voltage_mv;
    uint32_t max_current_ma;
    uint32_t max_power_mw;
} pdo_info_t;

typedef struct {
    pe_state_t state;
    uint32_t   timer_ms;
    uint8_t    active_pdo_pos;
    uint32_t   negotiated_mv;
    uint32_t   negotiated_ma;
    bool       gate_closed;
    pdo_info_t source_pdos[MAX_PDOS];
    uint8_t    pdo_count;
} sink_policy_engine_t;

// Декодування сирого 32-бітного слова PDO від джерела
void parse_source_pdo(uint32_t raw_pdo, uint8_t pos, pdo_info_t *out) {
    out->position = pos;
    out->type = (raw_pdo >> 30) & 0x03;
    if (out->type == 0) { // Fixed Supply
        out->voltage_mv = ((raw_pdo >> 10) & 0x3FF) * 50;
        out->max_current_ma = (raw_pdo & 0x3FF) * 10;
        out->max_power_mw = (out->voltage_mv * out->max_current_ma) / 1000;
    } else {
        out->voltage_mv = 5000;
        out->max_current_ma = 500;
        out->max_power_mw = 2500;
    }
}

// Вибір найкращого профілю за багатокритеріальною цільовою функцією
int evaluate_best_pdo(const pdo_info_t *pdos, uint8_t count, uint32_t *req_ma, bool *cap_mismatch) {
    int best_index = -1;
    int32_t best_score = -1000000;

    for (uint8_t i = 0; i < count; i++) {
        if (pdos[i].voltage_mv > V_SAFE_MAX_MV) continue; // Захист чутливої схеми

        int32_t score = 0;
        // 1. Оцінка корисної потужності
        score += (int32_t)(pdos[i].max_power_mw / 100);

        // 2. Бонус за точний збіг напруги (обхід DC-DC)
        if (pdos[i].voltage_mv == V_TARGET_MV) {
            score += 500;
        }

        // 3. Штраф за втрати нагріву в кабелі: I^2 * R
        int32_t cur_a = pdos[i].max_current_ma / 1000;
        int32_t loss_mw = (cur_a * cur_a * R_CABLE_MOHM);
        score -= (loss_mw / 10);

        if (score > best_score) {
            best_score = score;
            best_index = i;
        }
    }

    if (best_index >= 0) {
        uint32_t avail_ma = pdos[best_index].max_current_ma;
        *req_ma = (avail_ma < I_REQUIRED_MA) ? avail_ma : I_REQUIRED_MA;
        *cap_mismatch = (avail_ma < I_REQUIRED_MA);
    }
    return best_index;
}

// Формування бітового 32-бітного слова RDO
uint32_t build_request_rdo(uint8_t obj_pos, uint32_t oper_ma, uint32_t max_ma, bool mismatch, bool giveback) {
    uint32_t rdo = 0;
    rdo |= ((uint32_t)(obj_pos & 0x0F)) << 28;
    if (giveback) rdo |= (1UL << 27);
    if (mismatch) rdo |= (1UL << 26);
    rdo |= (1UL << 25); // USB Communications Capable
    rdo |= (1UL << 24); // No USB Suspend
    rdo |= (((oper_ma / 10) & 0x3FF) << 10);
    rdo |= (((max_ma / 10) & 0x3FF));
    return rdo;
}

// Апаратні заглушки взаємодії з драйвером PHY
extern void phy_send_request(uint32_t rdo);
extern void phy_send_hard_reset(void);
extern void power_gate_set(bool closed);

// Головний крок машини станів стіка
void sink_fsm_step(sink_policy_engine_t *pe, pe_event_t event, uint32_t elapsed_ms) {
    if (pe->timer_ms > elapsed_ms) pe->timer_ms -= elapsed_ms;
    else pe->timer_ms = 0;

    switch (pe->state) {
    case PE_SNK_DISCOVERY:
        pe->gate_closed = false;
        power_gate_set(false);
        if (event == EV_VBUS_DETECTED) {
            pe->state = PE_SNK_WAIT_FOR_CAP;
            pe->timer_ms = 620; // tTypeCSinkWaitCap
        }
        break;

    case PE_SNK_WAIT_FOR_CAP:
        if (event == EV_SOURCE_CAPS_RECEIVED) {
            pe->state = PE_SNK_EVALUATE_CAP;
        } else if (pe->timer_ms == 0) {
            // Джерело без підтримки PD -> залишаємося на 5 В
            pe->negotiated_mv = 5000;
            pe->negotiated_ma = 500;
            pe->gate_closed = true;
            power_gate_set(true);
            pe->state = PE_SNK_READY;
        }
        break;

    case PE_SNK_EVALUATE_CAP: {
        uint32_t req_ma = 0;
        bool mismatch = false;
        int idx = evaluate_best_pdo(pe->source_pdos, pe->pdo_count, &req_ma, &mismatch);
        if (idx >= 0) {
            pe->active_pdo_pos = pe->source_pdos[idx].position;
            pe->negotiated_mv = pe->source_pdos[idx].voltage_mv;
            pe->negotiated_ma = req_ma;
            uint32_t rdo = build_request_rdo(pe->active_pdo_pos, req_ma, pe->source_pdos[idx].max_current_ma, mismatch, false);
            phy_send_request(rdo);
            pe->state = PE_SNK_SELECT_CAP;
            pe->timer_ms = 30; // tSenderResponse
        } else {
            pe->state = PE_SNK_HARD_RESET;
        }
        break;
    }

    case PE_SNK_SELECT_CAP:
        if (event == EV_ACCEPT_RECEIVED) {
            pe->state = PE_SNK_TRANSITION_SINK;
            pe->timer_ms = 550; // tPSTransition
        } else if (event == EV_REJECT_RECEIVED || event == EV_WAIT_RECEIVED || pe->timer_ms == 0) {
            pe->state = PE_SNK_WAIT_FOR_CAP;
            pe->timer_ms = 100; // tSinkWaitCap
        }
        break;

    case PE_SNK_TRANSITION_SINK:
        if (event == EV_PS_RDY_RECEIVED) {
            pe->gate_closed = true;
            power_gate_set(true); // Замикання ключа лише після стабілізації PS_RDY!
            pe->state = PE_SNK_READY;
        } else if (pe->timer_ms == 0) {
            pe->state = PE_SNK_HARD_RESET;
        }
        break;

    case PE_SNK_READY:
        if (event == EV_SOURCE_CAPS_RECEIVED) {
            pe->state = PE_SNK_EVALUATE_CAP; // Гаряче переузгодження
        } else if (event == EV_GOTOMIN_RECEIVED) {
            pe->state = PE_SNK_GIVEBACK;
        }
        break;

    case PE_SNK_GIVEBACK:
        pe->negotiated_ma = 500; // Оперативне зниження навантаження
        pe->state = PE_SNK_READY;
        break;

    case PE_SNK_HARD_RESET:
        pe->gate_closed = false;
        power_gate_set(false);
        phy_send_hard_reset();
        pe->state = PE_SNK_DISCOVERY;
        break;
    }
}

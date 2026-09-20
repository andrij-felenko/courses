#include "phase_selector.h"

void phase_selector_init(phase_selector_t *ps, const phase_selector_config_t *cfg) {
    if (!ps || !cfg) return;
    ps->config = *cfg;
    ps->state = STATE_INIT;
    ps->active_phase = PHASE_NONE;
    ps->target_phase = PHASE_NONE;
    ps->state_timer_ms = 0;
}

bool phase_selector_is_phase_valid(const phase_selector_t *ps, phase_id_t phase, float voltage) {
    if (!ps) return false;
    
    // Якщо фаза вже активна, використовуємо розширені межі з гістерезисом
    if (ps->active_phase == phase) {
        return (voltage >= (ps->config.u_min - ps->config.u_hysteresis)) &&
               (voltage <= (ps->config.u_max + ps->config.u_hysteresis));
    }
    
    // Для підключення нової фази вимагаємо суворе попадання в уставки
    return (voltage >= ps->config.u_min) && (voltage <= ps->config.u_max);
}

// Вибір найкращої доступної фази з урахуванням пріоритету L1 > L2 > L3
static phase_id_t select_best_phase(const phase_selector_t *ps, float u_l1, float u_l2, float u_l3) {
    if (phase_selector_is_phase_valid(ps, PHASE_L1, u_l1)) {
        return PHASE_L1;
    }
    if (phase_selector_is_phase_valid(ps, PHASE_L2, u_l2)) {
        return PHASE_L2;
    }
    if (phase_selector_is_phase_valid(ps, PHASE_L3, u_l3)) {
        return PHASE_L3;
    }
    return PHASE_NONE;
}

void phase_selector_update(phase_selector_t *ps, float u_l1, float u_l2, float u_l3, uint32_t dt_ms) {
    if (!ps) return;

    ps->state_timer_ms += dt_ms;

    switch (ps->state) {
        case STATE_INIT: {
            phase_id_t best = select_best_phase(ps, u_l1, u_l2, u_l3);
            if (best != PHASE_NONE) {
                ps->target_phase = best;
                ps->state = STATE_DEAD_TIME;
                ps->state_timer_ms = 0;
            } else {
                ps->state = STATE_ALL_PHASES_FAULT;
            }
            break;
        }

        case STATE_MONITORING: {
            float current_u = (ps->active_phase == PHASE_L1) ? u_l1 :
                              (ps->active_phase == PHASE_L2) ? u_l2 : u_l3;

            bool current_valid = phase_selector_is_phase_valid(ps, ps->active_phase, current_u);
            bool l1_recovered = (ps->active_phase != PHASE_L1) && 
                                phase_selector_is_phase_valid(ps, PHASE_L1, u_l1);

            if (!current_valid) {
                phase_id_t best = select_best_phase(ps, u_l1, u_l2, u_l3);
                ps->active_phase = PHASE_NONE; // Відключаємо всі контактори
                ps->target_phase = best;
                ps->state = STATE_DEAD_TIME;
                ps->state_timer_ms = 0;
            } else if (l1_recovered) {
                ps->target_phase = PHASE_L1;
                ps->state = STATE_RETURN_DELAY;
                ps->state_timer_ms = 0;
            }
            break;
        }

        case STATE_RETURN_DELAY: {
            float current_u = (ps->active_phase == PHASE_L1) ? u_l1 :
                              (ps->active_phase == PHASE_L2) ? u_l2 : u_l3;

            if (!phase_selector_is_phase_valid(ps, ps->active_phase, current_u)) {
                ps->active_phase = PHASE_NONE;
                ps->target_phase = select_best_phase(ps, u_l1, u_l2, u_l3);
                ps->state = STATE_DEAD_TIME;
                ps->state_timer_ms = 0;
            } else if (!phase_selector_is_phase_valid(ps, PHASE_L1, u_l1)) {
                ps->state = STATE_MONITORING;
            } else if (ps->state_timer_ms >= ps->config.return_delay_ms) {
                ps->active_phase = PHASE_NONE;
                ps->state = STATE_DEAD_TIME;
                ps->state_timer_ms = 0;
            }
            break;
        }

        case STATE_DEAD_TIME: {
            if (ps->state_timer_ms >= ps->config.dead_time_ms) {
                if (ps->target_phase != PHASE_NONE) {
                    ps->active_phase = ps->target_phase;
                    ps->state = STATE_MONITORING;
                } else {
                    ps->state = STATE_ALL_PHASES_FAULT;
                }
            }
            break;
        }

        case STATE_ALL_PHASES_FAULT: {
            phase_id_t best = select_best_phase(ps, u_l1, u_l2, u_l3);
            if (best != PHASE_NONE) {
                ps->target_phase = best;
                ps->state = STATE_DEAD_TIME;
                ps->state_timer_ms = 0;
            }
            break;
        }
    }
}

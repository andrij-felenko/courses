typedef struct {
    EscalationState state;
    EscalationTrigger active_trigger;
    uint16_t current_query_id;
    uint32_t request_started_ms;
    uint32_t dynamic_deadline_ms;
    uint8_t selected_option_id;
    BreadcrumbTrail trail;
    uint32_t last_breadcrumb_time_ms;
} EscalationManager;

void escalation_manager_init(EscalationManager* mgr) {
    memset(mgr, 0, sizeof(EscalationManager));
    mgr->state = FSM_STATE_AUTONOMOUS;
}

/* Періодичний запис пройденої траєкторії для можливого відкату */
void update_breadcrumb_trail(EscalationManager* mgr, float x, float y, float z, float yaw, int8_t rssi, uint32_t now_ms) {
    if (now_ms - mgr->last_breadcrumb_time_ms >= 1000) { /* 1 раз на секунду */
        mgr->last_breadcrumb_time_ms = now_ms;
        BreadcrumbPoint pt = { x, y, z, yaw, now_ms, rssi };
        mgr->trail.buffer[mgr->trail.head] = pt;
        mgr->trail.head = (mgr->trail.head + 1) % BREADCRUMB_CAPACITY;
        if (mgr->trail.count < BREADCRUMB_CAPACITY) {
            mgr->trail.count++;
        }
    }
}

/* Головний такт автомата */
void escalation_manager_tick(EscalationManager* mgr,
                             EscalationTrigger current_trigger,
                             float dist_to_obstacle_m,
                             float speed_mps,
                             bool radio_link_alive,
                             uint32_t now_ms)
{
    switch (mgr->state) {
        case FSM_STATE_AUTONOMOUS:
            if (current_trigger != ESCALATION_TRIGGER_NONE) {
                mgr->active_trigger = current_trigger;
                mgr->current_query_id++;
                mgr->request_started_ms = now_ms;
                mgr->dynamic_deadline_ms = calculate_dynamic_deadline_ms(
                    dist_to_obstacle_m, speed_mps, 2.0f, 4.0f, 200);
                
                mgr->state = (mgr->dynamic_deadline_ms == 0) 
                             ? FSM_STATE_FAILSAFE_HOLD 
                             : FSM_STATE_ESCALATION_REQUESTED;
            }
            break;

        case FSM_STATE_ESCALATION_REQUESTED:
            /* Тут формується та відправляється пакет по MAVLink */
            mgr->state = FSM_STATE_AWAITING_OPERATOR;
            break;

        case FSM_STATE_AWAITING_OPERATOR: {
            uint32_t elapsed = now_ms - mgr->request_started_ms;
            
            /* Перевірка обриву зв'язку або вичерпання дедлайну */
            if (!radio_link_alive || elapsed >= mgr->dynamic_deadline_ms) {
                mgr->state = FSM_STATE_FAILSAFE_HOLD;
                break;
            }
            break;
        }

        case FSM_STATE_APPLYING_OVERRIDE:
            /* Виконання підтвердженої оператором опції; по завершенню повернення */
            mgr->state = FSM_STATE_AUTONOMOUS;
            mgr->active_trigger = ESCALATION_TRIGGER_NONE;
            break;

        case FSM_STATE_FAILSAFE_HOLD:
            /* Апарат зупинився. Якщо зв'язок не відновлено протягом 5 с — відкат назад */
            if (now_ms - mgr->request_started_ms > (mgr->dynamic_deadline_ms + 5000)) {
                mgr->state = FSM_STATE_FAILSAFE_BACKTRACK;
            }
            break;

        case FSM_STATE_FAILSAFE_BACKTRACK:
            /* Реверс за точками з буфера. Якщо буфер вичерпано — контрольована посадка */
            if (mgr->trail.count == 0) {
                mgr->state = FSM_STATE_FAILSAFE_SAFE_ABORT;
            }
            break;

        case FSM_STATE_FAILSAFE_SAFE_ABORT:
            /* Аварійна зупинка, вимкнення моторів, запис у NVRAM */
            break;
    }
}

/* Обробка відповіді оператора від наземної станції */
bool escalation_manager_handle_response(EscalationManager* mgr, uint16_t query_id, uint8_t option_id, uint32_t now_ms) {
    if (mgr->state != FSM_STATE_AWAITING_OPERATOR) {
        return false; /* Запізніла відповідь відкинута */
    }
    if (query_id != mgr->current_query_id) {
        return false; /* Не той ID запиту */
    }
    if (now_ms - mgr->request_started_ms > mgr->dynamic_deadline_ms) {
        return false; /* Таймаут минув */
    }

    mgr->selected_option_id = option_id;
    mgr->state = FSM_STATE_APPLYING_OVERRIDE;
    return true;
}

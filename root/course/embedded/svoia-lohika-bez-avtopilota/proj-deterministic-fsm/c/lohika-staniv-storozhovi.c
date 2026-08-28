/* Контекст апарата */
typedef struct {
    Hsm hsm;
    EventQueue event_queue;
    GoalEngine goal_engine;
    float battery_voltage;
    bool obstacle_present;
    int16_t current_x;
    int16_t current_y;
} AutonomousRover;

/* Прототипи функцій станів */
HsmResult state_idle(Hsm *me, const Event *e);
HsmResult state_operational(Hsm *me, const Event *e);
HsmResult state_navigating(Hsm *me, const Event *e);
HsmResult state_avoiding(Hsm *me, const Event *e);
HsmResult state_failsafe(Hsm *me, const Event *e);

/* Охоронні умови (Guard Conditions) */
static inline bool guard_is_battery_ok(const AutonomousRover *rover) {
    return rover->battery_voltage > 10.5f; /* Поріг відсічки для 3S Li-ion */
}

/* 1. Стан IDLE */
HsmResult state_idle(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_ENTRY:
            /* Знеструмити мотори */
            return RES_HANDLED;
        case EV_START_MISSION:
            if (guard_is_battery_ok(rover)) {
                hsm_transition(me, state_navigating);
                return RES_TRANSITION;
            }
            return RES_HANDLED; /* Батарея розряджена — відхилити старт */
        default:
            return RES_IGNORED;
    }
}

/* 2. Суперстан OPERATIONAL (Батьківський для дій у русі) */
HsmResult state_operational(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            /* Аварійне скидання місії */
            goal_engine_abort_all(&rover->goal_engine);
            hsm_transition(me, state_failsafe);
            return RES_TRANSITION;
        default:
            return RES_SUPER;
    }
}

/* 3. Підстан NAVIGATING */
HsmResult state_navigating(Hsm *me, const Event *e) {
    AutonomousRover *rover = (AutonomousRover *)me->user_data;
    switch (e->id) {
        case EV_ENTRY:
            /* Увімкнути ПІД регулятори коліс */
            return RES_HANDLED;
        case EV_EXIT:
            /* Скинути уставки швидкості в 0 */
            return RES_HANDLED;
        case EV_OBSTACLE_DETECTED:
            hsm_transition(me, state_avoiding);
            return RES_TRANSITION;
        case EV_WAYPOINT_REACHED:
            /* Завершити поточну ціль, взяти наступну */
            return RES_HANDLED;
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            /* Спливання до батьківського суперстану */
            return state_operational(me, e);
        default:
            return RES_IGNORED;
    }
}

/* 4. Підстан AVOIDING */
HsmResult state_avoiding(Hsm *me, const Event *e) {
    switch (e->id) {
        case EV_ENTRY:
            /* Зупинити лінійний рух, увімкнути пошуковий розворот */
            return RES_HANDLED;
        case EV_OBSTACLE_CLEARED:
            hsm_transition(me, state_navigating);
            return RES_TRANSITION;
        case EV_CRITICAL_FAULT:
        case EV_BATTERY_LOW:
            return state_operational(me, e);
        default:
            return RES_IGNORED;
    }
}

/* 5. Аварійний стан FAILSAFE */
HsmResult state_failsafe(Hsm *me, const Event *e) {
    switch (e->id) {
        case EV_ENTRY:
            /* Активація аварійного гальма, подача світлозвукового сигналу */
            return RES_HANDLED;
        default:
            return RES_IGNORED;
    }
}

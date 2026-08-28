struct AutonomousRover {
    Hsm hsm{state_idle};
    LockFreeRingQueue<Event, 16> event_queue{};
    GoalEngine<8> goal_engine{};
    float battery_voltage{12.4f};
    bool obstacle_present{false};
    int16_t current_x{0};
    int16_t current_y{0};
};

constexpr bool guard_battery_ok(float voltage) noexcept {
    return voltage > 10.5f;
}

/* 1. Стан Idle */
HsmResult state_idle(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::StartMission:
            hsm.transition_to(state_navigating);
            return HsmResult::Transition;
        default:
            return HsmResult::Ignored;
    }
}

/* 2. Суперстан Operational */
HsmResult state_operational(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            hsm.transition_to(state_failsafe);
            return HsmResult::Transition;
        default:
            return HsmResult::Super;
    }
}

/* 3. Підстан Navigating */
HsmResult state_navigating(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::Exit:
            return HsmResult::Handled;
        case EventId::ObstacleDetected:
            hsm.transition_to(state_avoiding);
            return HsmResult::Transition;
        case EventId::WaypointReached:
            return HsmResult::Handled;
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            return state_operational(hsm, e);
        default:
            return HsmResult::Ignored;
    }
}

/* 4. Підстан Avoiding */
HsmResult state_avoiding(Hsm& hsm, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        case EventId::ObstacleCleared:
            hsm.transition_to(state_navigating);
            return HsmResult::Transition;
        case EventId::CriticalFault:
        case EventId::BatteryLow:
            return state_operational(hsm, e);
        default:
            return HsmResult::Ignored;
    }
}

/* 5. Стан Failsafe */
HsmResult state_failsafe(Hsm& /*hsm*/, const Event& e) {
    switch (e.id) {
        case EventId::Entry:
            return HsmResult::Handled;
        default:
            return HsmResult::Ignored;
    }
}

void isr_obstacle_trigger(AutonomousRover& rover, uint32_t now_ms) noexcept {
    Event alert{EventId::ObstacleDetected, now_ms, {}};
    rover.event_queue.post(alert);
}

void app_step(AutonomousRover& rover, uint32_t now_ms) noexcept {
    // 1. Послідовне спустошення черги подій
    while (auto ev = rover.event_queue.pop()) {
        rover.hsm.dispatch(*ev);
    }

    // 2. Моніторинг активного кроку місії
    if (rover.goal_engine.has_active()) {
        const auto& g = rover.goal_engine.active().value();
        if (now_ms - g.start_time_ms > g.timeout_ms) {
            rover.event_queue.post(Event{EventId::GoalTimeout, now_ms, {}});
        }
    }
}

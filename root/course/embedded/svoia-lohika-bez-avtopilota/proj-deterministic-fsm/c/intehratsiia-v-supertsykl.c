/* Глобальний екземпляр ровера */
AutonomousRover g_rover;

/* Обробник зовнішнього переривання EXTI від ToF далекоміра */
void EXTI4_IRQHandler(void) {
    Event alert_ev = {
        .id = EV_OBSTACLE_DETECTED,
        .timestamp_ms = 123456 /* Системний таймер мікроконтролера */
    };
    /* Неблокуючий запис у чергу */
    event_queue_post(&g_rover.event_queue, &alert_ev);
}

/* Головний крок диспетчеризації суперциклу */
void app_main_loop(AutonomousRover *rover, uint32_t current_time_ms) {
    Event ev;

    /* 1. Вичитування всіх накопичених подій черги за принципом Run-to-Completion */
    while (event_queue_pop(&rover->event_queue, &ev)) {
        hsm_dispatch(&rover->hsm, &ev);
    }

    /* 2. Контроль таймауту активної цілі */
    if (rover->goal_engine.has_active_goal) {
        uint32_t elapsed = current_time_ms - rover->goal_engine.active_goal.start_time_ms;
        if (elapsed > rover->goal_engine.active_goal.timeout_ms) {
            Event timeout_ev = {
                .id = EV_GOAL_TIMEOUT,
                .timestamp_ms = current_time_ms
            };
            event_queue_post(&rover->event_queue, &timeout_ev);
        }
    }
}

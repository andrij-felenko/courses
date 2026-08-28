// Спрощена логіка вибору C-state у регуляторі cpuidle
s32 latency_req = cpu_latency_qos_limit();

for (i = 0; i < drv->state_count; i++) {
    struct cpuidle_state *s = &drv->states[i];
    if (s->exit_latency_ns / 1000 > latency_req) {
        // Стан надто повільний для виходу — ігноруємо його та всі глибші
        break;
    }
    target_state = i;
}

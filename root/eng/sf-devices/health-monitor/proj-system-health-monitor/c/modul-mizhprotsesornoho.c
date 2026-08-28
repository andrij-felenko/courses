typedef struct {
    uint16_t current_challenge;
    uint32_t missed_heartbeats;
    bool     safety_relay_state;
} health_intercore_monitor_t;

void health_intercore_init(health_intercore_monitor_t *mon) {
    if (!mon) return;
    mon->current_challenge = 0x1234;
    mon->missed_heartbeats = 0;
    mon->safety_relay_state = true;
}

uint16_t health_intercore_generate_challenge(health_intercore_monitor_t *mon) {
    if (!mon) return 0;
    // Простий лінійний конгруентний генератор для тесту зв'язку
    mon->current_challenge = (uint16_t)(mon->current_challenge * 31421U + 6927U);
    return mon->current_challenge;
}

bool health_intercore_verify_response(health_intercore_monitor_t *mon, uint16_t response) {
    if (!mon) return false;

    // Очікувана трансформація: побітова інверсія з циклічним зсувом
    uint16_t expected = (uint16_t)(~mon->current_challenge ^ 0x5A5AU);

    if (response == expected) {
        mon->missed_heartbeats = 0;
        mon->safety_relay_state = true;
        return true;
    }

    mon->missed_heartbeats++;
    if (mon->missed_heartbeats >= 3) {
        mon->safety_relay_state = false; // Вимикання силового контактора
    }
    return false;
}

typedef enum {
    ST_BOOT, ST_READY, ST_ARMED, ST_FLYING, ST_LANDING, ST_DISARMED
} mission_state_t;

static mission_state_t state = ST_BOOT;

// Викликається зрідка (напр. 50 Гц) — це ПОВІЛЬНИЙ годинник, не контур.
void mission_tick(void) {
    switch (state) {
    case ST_BOOT:
        if (selftest_passed())          // брама: самоперевірка пройдена
            set_state(ST_READY);        //   вхід у READY: двигуни лишаються мертві
        break;

    case ST_READY:
        // Озброєння йде лише через try_arm() — вона й перевіряє браму.
        // Тут автомат просто чекає команди оператора.
        break;

    case ST_ARMED:
        if (cmd_takeoff() && arming_allowed(NULL, 0)) {
            set_target_altitude(TAKEOFF_ALT);   // СТАВИМО ЦІЛЬ контуру
            set_state(ST_FLYING);               // а тримати її — його робота
        }
        break;

    case ST_FLYING:
        run_mission_legs();                 // ведемо цілі по маршруту (не блокуючи!)
        if (mission_complete())
            set_state(ST_LANDING);          // остання ціль — на посадку
        break;

    case ST_LANDING:
        if (land_detected())                // брама: апарат СПРАВДІ торкнувся землі
            set_state(ST_DISARMED);         //   і лише тоді ріжемо двигуни
        break;

    case ST_DISARMED:
        motors_cut();                       // двигуни мертві — місію завершено
        break;
    }
}

// ПОВІЛЬНИЙ годинник: викликається зрідка (напр. 50 Гц), ПОРЯД із контуром,
// але НЕ в ньому. Ніде не блокує: лише читає події й, якщо брама відкрита,
// просить перехід. Тримання цілей — робота контуру, не ця.
void mission_tick(void) {
    switch (state) {

    case ST_BOOT:
        if (selftest_passed())                 // брама: самоперевірка пройдена
            mission_transition(ST_READY);
        break;

    case ST_READY:
        // Озброєння — лише за командою оператора І з пройденими arming-перевірками.
        if (cmd_arm() && arming_allowed())
            mission_transition(ST_ARMED);
        break;

    case ST_ARMED:
        if (failsafe_now())                     // аварія на землі → назад у безпечне
            mission_transition(ST_READY);       //   (роззброїти — на землі це безпечно)
        else if (cmd_takeoff())                 // брама: команда зльоту
            mission_transition(ST_FLYING);
        break;

    case ST_FLYING:
        run_mission_legs();                     // веде цілі по маршруту — НЕ блокуючи
        if (failsafe_now())                     // аварія в повітрі → КЕРОВАНО вниз,
            mission_transition(ST_LANDING);     //   а не «вимкнути двигуни»
        else if (mission_complete())
            mission_transition(ST_LANDING);
        break;

    case ST_LANDING:
        if (go_around_requested())              // зрив посадки → друге коло
            mission_transition(ST_FLYING);
        else if (land_detected())               // брама: СТІЙКЕ торкання землі
            mission_transition(ST_DISARMED);
        break;

    case ST_DISARMED:
        // Кінцевий стан-«тупик»: двигуни вже дорізано у on_state_enter,
        // лог закрито. Нічого не крутимо. Вихід — лише через окрему
        // команду reset у READY (рядок DISARM у таблиці це дозволяє).
        break;
    }
}

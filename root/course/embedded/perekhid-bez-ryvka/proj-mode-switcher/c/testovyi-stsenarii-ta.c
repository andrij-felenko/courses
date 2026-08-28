int main(void) {
    flight_manager_t mgr;
    flight_manager_init(&mgr);

    float dt = 0.02f; // 50 Гц
    float alt = 42.0f;
    float stick = 0.56f;

    printf("Час[с] | Режим | Висота[м] | Вихід[%%] | Стрибок dU\n");
    printf("--------------------------------------------------\n");

    float prev_out = 0.56f;

    for (int step = 0; step <= 750; ++step) {
        float t = step * dt;

        // Подія 1: t = 5.0с -> перемикаємося в AltHold
        if (step == 250) {
            flight_manager_switch_mode(&mgr, MODE_ALT_HOLD, alt, alt);
            printf(">>> [t=5.0s] ПЕРЕМИКАННЯ: MANUAL -> ALT_HOLD <<<\n");
        }

        // Подія 2: t = 10.0с -> перемикаємося в AutoMission (ціль 80м)
        if (step == 500) {
            flight_manager_switch_mode(&mgr, MODE_AUTO_MISSION, alt, 80.0f);
            printf(">>> [t=10.0s] ПЕРЕМИКАННЯ: ALT_HOLD -> AUTO_MISSION (Target=80m) <<<\n");
        }

        float out = flight_manager_step(&mgr, stick, alt, dt);
        float du = fabsf(out - prev_out);

        // Друк ключових точок
        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            printf("%5.2f  | %5d | %8.2f  | %8.4f | %10.6f\n",
                   t, mgr.current_mode, alt, out, du);
        }

        // Проста фізична модель реакції висоти на тягу
        alt += (out - 0.56f) * 10.0f * dt;
        prev_out = out;
    }

    return 0;
}

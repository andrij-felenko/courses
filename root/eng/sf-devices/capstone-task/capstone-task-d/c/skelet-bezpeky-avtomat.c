typedef enum { ST_BOOT, ST_SELFTEST, ST_IDLE, ST_RUN, ST_FAILSAFE } mode_t;

static mode_t mode = ST_BOOT;

void control_step(void) {
    switch (mode) {
    case ST_BOOT:
        init_peripherals();
        mode = ST_SELFTEST;
        break;

    case ST_SELFTEST:
        mode = self_test_ok() ? ST_IDLE : ST_FAILSAFE;   // не пройшов → одразу failsafe
        break;

    case ST_IDLE:
        actuators_safe();                    // виходи в безпечному стані, поки чекаємо
        if (arm_requested() && arming_ok())  // у RUN — лише через перевірки
            mode = ST_RUN;
        break;

    case ST_RUN:
        if (!health_ok()) { mode = ST_FAILSAFE; break; }  // біда → failsafe, поза чергою
        run_control();                       // нормальна робота контуру
        if (disarm_requested()) mode = ST_IDLE;
        break;

    case ST_FAILSAFE:
        failsafe_action();                   // заздалегідь задана безпечна дія
        break;
    }
}

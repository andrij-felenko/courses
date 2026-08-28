// Перехід у RUN: buck у повний PWM, шини — за порядком, кожна чекає PGOOD.
static bool power_enter_run(void)
{
    buck_set_mode_pwm();   // спершу повний PWM — шини мусять тягти струм (крок 4)

    for (size_t i = 0; i < RAIL_COUNT; i++) {
        if (!rail_enable_and_wait(&RAILS[i])) {
            // Одна шина не піднялася — відкат: гасимо вже ввімкнені у зворотному
            // порядку, щоб не лишити плату в напів-увімкненому стані.
            for (size_t j = i; j-- > 0; )
                gpio_set_level(RAILS[j].en_pin, 0);
            return false;
        }
    }
    return true;
}

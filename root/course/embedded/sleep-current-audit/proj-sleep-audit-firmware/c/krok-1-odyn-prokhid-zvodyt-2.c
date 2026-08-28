static void apply_sleep_profile(void)
{
    for (size_t i = 0; i < SLEEP_PROFILE_LEN; i++) {
        const sleep_pin_t *s = &SLEEP_PROFILE[i];

        if (s->state == SLEEP_LOW) {
            gpio_set_direction(s->pin, GPIO_MODE_OUTPUT);
            gpio_set_level(s->pin, 0);                 // 0 В: діод вузла замкнений
        } else { // SLEEP_HIZ
            gpio_set_direction(s->pin, GPIO_MODE_INPUT);
            gpio_set_pull_mode(s->pin, GPIO_FLOATING); // зняти обидві підтяжки
        }
    }
}

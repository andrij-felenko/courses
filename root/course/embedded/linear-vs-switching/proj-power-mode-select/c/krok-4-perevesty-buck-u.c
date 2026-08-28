// Ніжка MODE buck-перетворювача виведена на GPIO.
//   MODE = 1 (HIGH) → примусовий фіксований PWM (передбачувані завади, гірший ККД);
//   MODE = 0 (LOW)  → power-save: авто PWM/PFM, малий струм спокою на легкому струмі.

static void buck_set_mode_pwm(void)
{
    gpio_set_level(BUCK_MODE_PIN, 1);   // повний PWM: робочий режим
}

static void buck_set_mode_skip(void)
{
    gpio_set_level(BUCK_MODE_PIN, 0);   // режим пропуску: сплячий режим
}

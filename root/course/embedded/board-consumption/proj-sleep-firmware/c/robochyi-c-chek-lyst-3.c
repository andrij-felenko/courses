// ── Крок 2: опустити сигнали ДО зняття живлення гілки ─────────────────────
// Якщо зробити навпаки, лінії у "1" живитимуть мертвий давач крізь діоди.
static void quiesce_signals(void)
{
    // Лінії шини до давача — у нуль (підтяжки шини зовнішні, тож нуль безпечний).
    gpio_set_direction(PIN_I2C_SDA, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_I2C_SCL, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_I2C_SDA, 0);
    gpio_set_level(PIN_I2C_SCL, 0);

    // Status-LED — погасити напевно.
    gpio_reset_pin(PIN_STATUS_LED);
    gpio_set_direction(PIN_STATUS_LED, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_STATUS_LED, 0);
}

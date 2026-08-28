// Увімкнути одну шину й дочекатися, що вона СПРАВДІ в нормі.
// Повертає true, якщо PGOOD підтвердив (або LDO без PGOOD відстояв таймер);
// false — якщо шина не піднялася за max_rise_us (несправність).
static bool rail_enable_and_wait(const power_rail_t *r)
{
    gpio_set_level(r->en_pin, 1);

    if (r->pgood_pin == GPIO_NUM_NC) {
        // Шина без PGOOD: лишається тільки чесно відстояти час наростання.
        esp_rom_delay_us(r->max_rise_us);
        return true;
    }

    // Є PGOOD — чекаємо на HIGH, але не довше за страхову стелю.
    int64_t deadline = esp_timer_get_time() + r->max_rise_us;
    while (gpio_get_level(r->pgood_pin) == 0) {
        if (esp_timer_get_time() > deadline) {
            ESP_LOGE("PWR", "шина '%s': PGOOD не піднявся за %u мкс — несправність?",
                     r->name, r->max_rise_us);
            gpio_set_level(r->en_pin, 0);   // не лишаємо кволу шину під живленням
            return false;
        }
    }
    return true;
}

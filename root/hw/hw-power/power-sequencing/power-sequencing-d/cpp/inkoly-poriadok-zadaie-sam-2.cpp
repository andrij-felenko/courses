#define PG_SENSORS  GPIO_PIN(C, 0)   // Power-Good шини давачів (вхід)

// Чекати, доки шина підтвердить готовність; не зависати назавжди.
static bool wait_power_good(gpio_t pg, uint32_t timeout_ms) {
    while (timeout_ms--) {
        if (gpio_read(pg)) return true;   // шина дійшла номіналу
        delay_ms(1);
    }
    return false;                          // не піднялася — несправність
}

void power_up_sequence(void) {
    gpio_high(EN_SENSORS);
    if (!wait_power_good(PG_SENSORS, 50)) {
        fault_shutdown();                  // шина не встала — гасимо все
        return;
    }
    gpio_high(EN_RADIO);
    // ... далі за тією ж схемою
}

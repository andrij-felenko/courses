// STAT від зарядного чипа заведено на вхід МК із внутрішньою підтяжкою вгору.
#define PIN_STAT  4          // номер виводу мікроконтролера

bool charging_active(void) {
    // відкритий стік притягує лінію до 0, поки йде заряд → інвертуємо
    return gpio_read(PIN_STAT) == 0;
}

void update_led(void) {
    if (charging_active())
        led_on();            // світиться, поки заряджається
    else
        led_off();           // погасло → готово (або заряд не йде)
}

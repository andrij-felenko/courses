// EN веде GPIO МК, PG читаємо як цифровий вхід зі стану модуля
gpio_set_level(MODULE_EN, 1);           // дозволяємо запуск

// чекаємо power-good, а не «наосліп» через delay:
// PG — відкритий стік, тому потрібен підтяг до 3.3 В
int waited_us = 0;
while (gpio_get_level(MODULE_PG) == 0) {
    esp_rom_delay_us(100);
    waited_us += 100;
    if (waited_us > 5000) {             // 5 мс — модуль не піднявся
        // коротке замикання чи перевантаження на шині — у захист
        fault_handler(FAULT_RAIL_DOWN);
        break;
    }
}
// сюди потрапляємо лише коли шина реально в нормі

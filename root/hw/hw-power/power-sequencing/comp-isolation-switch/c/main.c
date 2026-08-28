// Канал розв'язувача між раннім і пізнім доменами.
// EN: 1 — канал відкритий, 0 — Hi-Z (домени роз'єднані).
#define EN_ISO   GPIO_PIN(B, 4)   // дозвіл каналу розв'язувача
#define PG_LATE  GPIO_PIN(C, 2)   // Power-Good пізнього домену (вхід)

void open_isolation_when_ready(void) {
    gpio_low(EN_ISO);                 // старт: канал розірвано, домени нарізно

    power_up_late_domain();           // піднімаємо пізній домен

    // чекаємо, доки пізній бік справді дійде номіналу — не наосліп
    uint32_t t = 200;                 // сторож: 200 мс і не довше
    while (t-- && !gpio_read(PG_LATE)) delay_ms(1);
    if (!gpio_read(PG_LATE)) {        // не піднявся — несправність
        fault_shutdown();             // канал лишаємо розірваним
        return;
    }
    gpio_high(EN_ISO);                // ОБИДВА живі → лише тепер відкриваємо канал
}

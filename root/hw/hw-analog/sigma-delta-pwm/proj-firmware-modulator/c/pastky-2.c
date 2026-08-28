// ПРАВИЛЬНО: в ISR — лише цілочислова дешева робота.
void TIMER_ISR(void)
{
    TIMER_CLEAR_FLAG();
    uint8_t level = next_sine_level();          // вибірка з таблиці — дешево
    uint8_t bit   = sd1_tick(add_dither(level));// додавання + порівняння — дешево
    if (bit) GPIO_SET(SPK_PORT, SPK_PIN);
    else     GPIO_CLR(SPK_PORT, SPK_PIN);
}

// НЕПРАВИЛЬНО (так робити НЕ можна): важка математика просто в ISR.
void TIMER_ISR_bad(void)
{
    TIMER_CLEAR_FLAG();
    double s = sin(2.0 * M_PI * t);             // ← сотні тактів, не вкладемось
    uint8_t level = (uint8_t)(128 + 120 * s);   // ← плаваюча кома в перериванні
    t += dt;
    // ... наступний тик уже прийшов, поки ми тут рахували sin() → тракт зламано
}

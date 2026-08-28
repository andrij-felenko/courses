// ── Прив'язка до заліза (макроси — під конкретний МК) ────────────────────────
void gate_write(bool on) {
    // Верхній ключ через драйвер затвора: on → підняти затвор, off → притиснути до 0.
    if (on) GPIO_SET(GATE_PORT, GATE_PIN);
    else    GPIO_CLR(GATE_PORT, GATE_PIN);
}

ReverseGuard guard({
    .trip_uA  = 300000,   // 300 мА реверсу — аварія
    .rearm_uA = 150000,   // 150 мА впевненого прямого — умова повернення
    .deglitch = 3,        // три вибірки поспіль
    .latching = true,     // фіксуємось, чекаємо явного reset()
});

// Обробник переривання таймера на 10 кГц (кожні 100 мкс):
extern "C" void TIM_IRQHandler(void) {
    TIM_CLEAR_FLAG();
    uint16_t raw = adc_read(CURRENT_CH);   // одне перетворення АЦП
    guard.tick(counts_to_uA(raw));         // уся логіка — тут
}

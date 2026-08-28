volatile uint32_t pulse_count;     // міняє ISR, читає цикл → ОБОВ'ЯЗКОВО volatile

void IRAM_ATTR on_pulse(void) {    // ISR: коротка, лише лічить
    pulse_count++;
}

uint32_t take_pulses(void) {
    uint32_t v;
    noInterrupts();                // забороняємо переривання на мить
    v = pulse_count;               // читаємо цілим — ISR не втрутиться
    pulse_count = 0;               // і одразу обнуляємо
    interrupts();                  // повертаємо переривання
    return v;                      // критична секція — 3 інструкції, не більше
}

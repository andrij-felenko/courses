// Arduino Uno/Nano (AVR): пін D4 -> біт 4 порту D
// перемикання за ~0.1 мкс замість кількох мкс digitalWrite
void carrierFast(uint16_t cycles) {
    for (uint16_t i = 0; i < cycles; i++) {
        PORTD |=  (1 << PD4);      // S у «1»
        delayMicroseconds(11);     // трохи менше 13 — компенсуємо накладні
        PORTD &= ~(1 << PD4);      // S у «0»
        delayMicroseconds(11);
    }
}

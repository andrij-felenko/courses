// A0->PB0, A1->PB1, A2->PB2 (один порт, сусідні ніжки)
static inline void decoder_select(uint8_t dev) {   // dev = 0..7
    // вставляємо три біти адреси, не чіпаючи решту порту
    PORTB = (PORTB & ~0x07u) | (dev & 0x07u);
}

void talk_to_device5(void) {
    decoder_select(5);          // 101 -> Y5 падає в 0 -> ~CS пристрою 5 = 0
    uint8_t reply = spi_xfer(0x9F);   // обмін по спільній шині, поки CS5 активний
    decoder_select(0);          // 000 -> тепер активний Y0; пристрій 5 відпущено
    (void)reply;
}

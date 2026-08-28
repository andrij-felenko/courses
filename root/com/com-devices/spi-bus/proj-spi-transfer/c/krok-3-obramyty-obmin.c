static inline void cs_low(void)  { CS_PORT &= ~CS_PIN; }  // 0 → обрали веденого
static inline void cs_high(void) { CS_PORT |=  CS_PIN; }  // 1 → відпустили

// Обмін блоком байтів за одне опускання CS: дзеркалимо tx[i] ↔ rx[i].
void spi_xfer_block(const uint8_t *tx, uint8_t *rx, uint16_t n) {
    cs_low();
    for (uint16_t i = 0; i < n; i++) {
        uint8_t in = spi_transfer(tx ? tx[i] : 0xFF);  // нема даних на відсил → шлемо пусте
        if (rx) {
            rx[i] = in;                                // нема куди приймати → просто відкидаємо
        }
    }
    cs_high();
}

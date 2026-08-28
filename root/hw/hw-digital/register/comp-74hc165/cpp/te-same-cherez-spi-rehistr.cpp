// CP → SCK,  Q7 → MISO (апаратні виводи SPI).
// PL лишається звичайним GPIO (защіпка).
#define PIN_PL  5

uint8_t hc165_read_spi(void) {
    // 1. Защіпнути входи імпульсом PL=0 (так само, як у bit-bang).
    pinWrite(PIN_PL, 0);
    delayUs(1);
    pinWrite(PIN_PL, 1);

    // 2. Один обмін по SPI: висуваємо «сміття», приймаємо 8 бітів з Q7.
    //    Режим SPI: CPOL=0, CPHA=0 (вибірка по фронту 0→1, як любить 165).
    return spi_transfer(0x00);   // повертає прийнятий байт
}

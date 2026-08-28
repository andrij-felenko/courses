// На STM32 порт — це структура регістрів; шину D[7..0] заведено на молодший байт.
#define DATA_PORT   GPIOB

void bus_write(uint8_t value) {
    // Зберегти старші 8 ліній порту, замінити лише молодші 8 — нашу шину.
    DATA_PORT->ODR = (DATA_PORT->ODR & 0xFF00) | value;   // D7..D0 за одну дію
}

uint8_t bus_read(void) {
    return (uint8_t)(DATA_PORT->IDR & 0x00FF);            // прочитати весь вектор
}

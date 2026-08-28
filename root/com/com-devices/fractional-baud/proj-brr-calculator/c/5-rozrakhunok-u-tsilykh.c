/* Цілочисельний розрахунок USART_BRR для режиму OVER8 = 0 (16x) */
uint16_t stm32_calc_brr_integer_only(uint32_t f_ck, uint32_t baud) {
    /* Додавання половини дільника (baud / 2) реалізує точне округлення round() */
    return (uint16_t)(((2 * f_ck) + baud) / (2 * baud));
}

/* Цілочисельний розрахунок USART_BRR для режиму OVER8 = 1 (8x) */
uint16_t stm32_calc_brr_over8_integer_only(uint32_t f_ck, uint32_t baud) {
    uint32_t div = ((4 * f_ck) + baud) / (2 * baud);
    uint32_t mantissa = div / 16;
    uint32_t fraction = div % 16;
    /* У режимі OVER8 = 1 дріб квантується як F/8 у бітах [2:0], біт [3] скидається */
    return (uint16_t)((mantissa << 4) | ((fraction >> 1) & 0x07));
}

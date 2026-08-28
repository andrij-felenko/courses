/* Файл uart_driver.c */
void uart1_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    GPIOA->MODER |= (2u << (9 * 2)) | (2u << (10 * 2)); /* AF mode */
    GPIOA->AFR[1] |= (7u << ((9 - 8) * 4)) | (7u << ((10 - 8) * 4)); /* AF7 */
}

/* Файл spi_driver.c */
void spi1_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    GPIOA->MODER |= (2u << (5 * 2)) | (2u << (6 * 2)) | (2u << (7 * 2));
    GPIOA->AFR[0] |= (5u << (5 * 4)) | (5u << (6 * 4)) | (5u << (7 * 4));
}

/* Файл board_led.c */
void led_init(void) {
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    /* Помилка: LED помилково налаштовує PA9 замість PA8 */
    GPIOA->MODER &= ~(3u << (9 * 2));
    GPIOA->MODER |= (1u << (9 * 2)); /* Затерто конфігурацію USART1_TX! */
}

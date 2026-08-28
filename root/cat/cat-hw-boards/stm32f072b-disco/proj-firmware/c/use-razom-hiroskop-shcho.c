int main(void) {
    clock_48mhz();
    // LD3 (PC6) як «серцебиття» — щоб очима бачити, що прошивка жива.
    RCC->AHBENR |= RCC_AHBENR_GPIOCEN;
    GPIOC->MODER &= ~(3u << (6 * 2));
    GPIOC->MODER |=  (1u << (6 * 2));

    uart1_init();
    l3gd20_init();
    l3gd20_start();

    uart_print("L3GD20 ok, WHO_AM_I=0xD4\r\n");

    for (;;) {
        int16_t rx, ry, rz;
        l3gd20_read_xyz(&rx, &ry, &rz);

        // Вивести три осі в °/с ×100 (щоб не морочитися з float у консолі).
        uart_print("wx="); uart_print_int(rx * 875 / 100000);
        uart_print(" wy="); uart_print_int(ry * 875 / 100000);
        uart_print(" wz="); uart_print_int(rz * 875 / 100000);
        uart_print(" dps\r\n");

        GPIOC->ODR ^= (1u << 6);                // моргнути LD3
        for (volatile int d = 0; d < 800000; d++) { }  // ~пів секунди
    }
}

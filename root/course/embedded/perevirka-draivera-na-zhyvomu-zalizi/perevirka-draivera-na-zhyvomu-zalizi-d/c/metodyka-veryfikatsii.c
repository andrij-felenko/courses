/* Тестовий сценарій: штучне блокування обробки переривань на мові C */
void test_inject_fifo_starvation_c(sensor_context_t *ctx) {
    /* 1. Налаштовуємо сенсор на високу частоту вибірок ODR = 1600 Гц */
    sensor_set_odr(ctx, 1600);
    
    /* 2. Примусово маскуємо лінію переривання на 500 мс */
    mask_sensor_interrupt(true);
    delay_ms(500); /* Буфер переповнюється (800 вибірок) */
    mask_sensor_interrupt(false);
    
    /* 3. Викликаємо відновлення драйвера після переповнення */
    sensor_handle_fifo_overflow(ctx);
}

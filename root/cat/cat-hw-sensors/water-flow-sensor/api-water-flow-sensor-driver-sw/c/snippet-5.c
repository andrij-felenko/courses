water_flow_err_t err = water_flow_get_rate_lmin(&sensor_dev, &flow_rate);
if (err != WATER_FLOW_OK) {
    switch (err) {
        case WATER_FLOW_ERR_NOT_INITIALIZED:
            printf("Помилка: Драйвер не ініціалізовано!\n");
            water_flow_init(&sensor_dev, &sensor_cfg);
            break;
        case WATER_FLOW_ERR_TURBINE_JAMMED:
            printf("Аварія: Заклинювання турбінки! Перевірте відсутність сторонніх часток.\n");
            // Безпечне вимкнення насоса
            break;
        case WATER_FLOW_ERR_OUT_OF_RANGE:
            printf("Попередження: Витрата вийшла за межі допустимого діапазону.\n");
            break;
        default:
            printf("Помилка драйвера з кодом: %d\n", err);
            break;
    }
}

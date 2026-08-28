bmp280_handle_t baro_primary;
bmp280_handle_t baro_secondary;

/* Ініціалізація першого сенсора на адресі 0x76 */
bus_if_1.dev_addr = 0x76U;
bmp280_init(&baro_primary, &bus_if_1);

/* Ініціалізація другого сенсора на адресі 0x77 */
bus_if_2.dev_addr = 0x77U;
bmp280_init(&baro_secondary, &bus_if_2);

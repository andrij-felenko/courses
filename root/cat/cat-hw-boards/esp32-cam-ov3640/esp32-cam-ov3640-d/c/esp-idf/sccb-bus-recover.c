// Алгоритм відновлення шини SCCB при блокуванні веденого пристрою
esp_err_t sccb_bus_recover(gpio_num_t scl_pin, gpio_num_t sda_pin) {
    gpio_set_direction(scl_pin, GPIO_MODE_OUTPUT);
    gpio_set_direction(sda_pin, GPIO_MODE_INPUT_OUTPUT_OD);
    
    // Подача 9 тактових імпульсів для розблокування шини
    for (int i = 0; i < 9; i++) {
        gpio_set_level(scl_pin, 0);
        esp_rom_delay_us(5);
        gpio_set_level(scl_pin, 1);
        esp_rom_delay_us(5);
        if (gpio_get_level(sda_pin) == 1) {
            break; // Ведений пристрій відпустив лінію даних
        }
    }
    
    // Формування СТОП-умови на шині
    gpio_set_level(sda_pin, 0);
    esp_rom_delay_us(5);
    gpio_set_level(scl_pin, 1);
    esp_rom_delay_us(5);
    gpio_set_level(sda_pin, 1);
    
    // Програмне скидання сенсора через регістр конфігурації 0x12
    return sccb_write_reg(OV3640_SCCB_ADDR, 0x12, 0x80);
}

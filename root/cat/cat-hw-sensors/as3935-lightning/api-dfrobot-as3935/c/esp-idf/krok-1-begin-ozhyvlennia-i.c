void app_main(void) {
    i2c_config_t conf = {                   // те, що в Arduino робить Wire.begin()
        .mode             = I2C_MODE_MASTER,
        .sda_io_num       = GPIO_NUM_21,
        .scl_io_num       = GPIO_NUM_22,
        .sda_pullup_en    = GPIO_PULLUP_ENABLE,   // на Gravity-модулі підтяжки вже є
        .scl_pullup_en    = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 400000,               // 400 кГц
    };
    ESP_ERROR_CHECK(i2c_param_config(I2C_PORT, &conf));
    ESP_ERROR_CHECK(i2c_driver_install(I2C_PORT, conf.mode, 0, 0, 0));

    uint8_t probe;                          // чи озивається чіп за цією адресою
    while (as3935_read(0x00, &probe) != ESP_OK) {
        ESP_LOGE(TAG, "AS3935 не відповідає — звір адресу з DIP і дроти");
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
    ESP_LOGI(TAG, "AS3935 на шині, адресу знайдено");

void sensor_hardware_reset(void) {
    /* 1. Вимкнути живлення сенсорів (відпустити затвор P-MOSFET) */
    gpio_set_level(PIN_SENSOR_POWER_EN, 1);
    
    /* 2. Притягнути SDA та SCL до нуля, щоб уникнути паразитного живлення через ESD-діоди */
    gpio_set_direction(PIN_I2C_SDA, GPIO_MODE_OUTPUT);
    gpio_set_direction(PIN_I2C_SCL, GPIO_MODE_OUTPUT);
    gpio_set_level(PIN_I2C_SDA, 0);
    gpio_set_level(PIN_I2C_SCL, 0);
    
    /* 3. Витримати паузу для повного розряду блокувальних конденсаторів */
    delay_ms(50);
    
    /* 4. Відновити живлення та повернути режим I2C */
    gpio_set_level(PIN_SENSOR_POWER_EN, 0);
    delay_ms(20);
    i2c_bus_reinit();
}

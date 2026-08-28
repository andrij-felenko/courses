/* Катастрофічна вразливість: зависання при апаратному розриві лінії */
driver_status_t i2c_poll_byte_naive(I2C_TypeDef *i2c, uint8_t *byte) {
    while (!(i2c->SR1 & I2C_SR1_RXNE)) {
        /* Якщо тактовий імпульс не дійшов до сенсора, процесор назавжди зависає тут */
    }
    *byte = (uint8_t)i2c->DR;
    return DRIVER_OK;
}

/* Захищена реалізація з апаратним таймаутом */
driver_status_t i2c_poll_byte_guarded(I2C_TypeDef *i2c, uint8_t *byte, uint32_t timeout_us) {
    uint32_t start_tick = get_microsecond_tick();
    while (!(i2c->SR1 & I2C_SR1_RXNE)) {
        if ((get_microsecond_tick() - start_tick) >= timeout_us) {
            return DRIVER_ERR_TIMEOUT;
        }
    }
    *byte = (uint8_t)i2c->DR;
    return DRIVER_OK;
}

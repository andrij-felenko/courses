/* Адаптер I2C до структури bus_interface_t на C99 */
static driver_status_t i2c_adapter_write(void* ctx, uint8_t dev_addr, uint8_t reg_addr,
                                         const uint8_t* data, size_t len) {
    i2c_handle_t* i2c = (i2c_handle_t*)ctx;
    /* Формування буфера [reg_addr, data...] та виклик i2c_master_write */
    uint8_t pkt[33];
    if (len > 32) return DRIVER_STATUS_INVALID_PARAM;
    pkt[0] = reg_addr;
    for (size_t i = 0; i < len; ++i) pkt[i + 1] = data[i];
    return i2c_master_write(i2c, dev_addr, pkt, len + 1);
}

// C99: Опитування готовності даних із гарантованим тайм-аутом
chip_status_t chip_wait_data_ready(chip_dev_t *dev, uint32_t timeout_ms) {
    uint32_t elapsed = 0;
    const uint32_t poll_interval_ms = 1;
    
    while (elapsed < timeout_ms) {
        uint8_t status = 0;
        int32_t res = dev->bus_ops->read(dev->user_ctx, dev->dev_addr, CHIP_REG_STATUS_REG, &status, 1);
        if (res == 0 && (status & STATUS_ZYXDA_FLAG) != 0) {
            return CHIP_OK; // Дані готові
        }
        dev->bus_ops->delay_ms(poll_interval_ms);
        elapsed += poll_interval_ms;
    }
    return CHIP_ERR_TIMEOUT;
}

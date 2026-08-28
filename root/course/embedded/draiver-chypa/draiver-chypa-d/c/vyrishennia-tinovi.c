// C99: Безпечне оновлення бітового поля через тіньовий регістр
#define CTRL1_ODR_MASK   (0x0F << 4) // Біти [7:4]
#define CTRL1_ODR_SHIFT  4

chip_status_t chip_set_odr(chip_dev_t *dev, uint8_t odr_code) {
    if (!dev || !dev->is_initialized) return CHIP_ERR_NOT_INIT;
    
    // Модифікація локальної копії без читання по шині
    uint8_t new_val = (dev->shadow_ctrl1 & ~CTRL1_ODR_MASK) | 
                      ((odr_code << CTRL1_ODR_SHIFT) & CTRL1_ODR_MASK);
    
    // Запис оновленого байта в залізо
    int32_t res = dev->bus_ops->write(dev->user_ctx, dev->dev_addr, CHIP_REG_CTRL_REG1, &new_val, 1);
    if (res != 0) return CHIP_ERR_COMM;
    
    dev->shadow_ctrl1 = new_val;
    return CHIP_OK;
}

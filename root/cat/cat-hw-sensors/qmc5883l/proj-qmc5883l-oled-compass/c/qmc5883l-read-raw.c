qmc5883l_err_t qmc5883l_read_raw(qmc5883l_t *dev, qmc5883l_raw_t *raw) {
    uint8_t status = 0;
    i2c_read_reg(dev->i2c_addr, QMC5883L_REG_STATUS, &status);
    if (status & QMC5883L_STAT_OVL) {
        return QMC5883L_ERR_OVERFLOW;
    }

    uint8_t buf[6];
    if (i2c_read_regs(dev->i2c_addr, QMC5883L_REG_DATA_X_LSB, buf, 6) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    raw->x = (int16_t)((uint16_t)buf[0] | ((uint16_t)buf[1] << 8));
    raw->y = (int16_t)((uint16_t)buf[2] | ((uint16_t)buf[3] << 8));
    raw->z = (int16_t)((uint16_t)buf[4] | ((uint16_t)buf[5] << 8));

    return QMC5883L_OK;
}

qmc5883l_err_t qmc5883l_init(qmc5883l_t *dev, uint8_t i2c_addr, qmc5883l_mode_t mode,
                            qmc5883l_odr_t odr, qmc5883l_rng_t rng, qmc5883l_osr_t osr) {
    dev->i2c_addr = i2c_addr;
    dev->mode = mode;
    dev->odr = odr;
    dev->rng = rng;
    dev->osr = osr;

    if (!i2c_ping(dev->i2c_addr)) {
        return QMC5883L_ERR_I2C;
    }

    /* Програмний скид */
    i2c_write_reg(dev->i2c_addr, QMC5883L_REG_CTRL2, 0x80);

    /* Запис періоду Set/Reset */
    i2c_write_reg(dev->i2c_addr, QMC5883L_REG_SETRST, 0x01);

    /* Формування Control Register 1 */
    uint8_t ctrl1 = ((uint8_t)osr << 6) | ((uint8_t)rng << 4) | ((uint8_t)odr << 2) | ((uint8_t)mode);
    return i2c_write_reg(dev->i2c_addr, QMC5883L_REG_CTRL1, ctrl1);
}

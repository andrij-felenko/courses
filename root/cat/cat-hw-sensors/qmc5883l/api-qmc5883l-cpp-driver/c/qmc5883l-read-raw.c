typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
    bool    overflow;
} qmc5883l_data_t;

qmc5883l_status_t qmc5883l_read_raw(const qmc5883l_dev_t* dev, qmc5883l_data_t* data) {
    if (!dev || !dev->read_regs || !data) {
        return QMC5883L_ERR_PARAM;
    }

    uint8_t status = 0;
    if (!dev->read_regs(dev->dev_addr, 0x06, &status, 1)) {
        return QMC5883L_ERR_I2C;
    }

    if ((status & 0x01) == 0) {
        return QMC5883L_ERR_NOT_READY;
    }

    uint8_t raw_buf[6];
    if (!dev->read_regs(dev->dev_addr, 0x00, raw_buf, 6)) {
        return QMC5883L_ERR_I2C;
    }

    data->x = (int16_t)((raw_buf[1] << 8) | raw_buf[0]);
    data->y = (int16_t)((raw_buf[3] << 8) | raw_buf[2]);
    data->z = (int16_t)((raw_buf[5] << 8) | raw_buf[4]);
    data->overflow = (status & 0x02) != 0;

    return QMC5883L_OK;
}

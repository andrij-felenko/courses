typedef enum {
    QMC5883L_OK = 0,
    QMC5883L_ERR_I2C,
    QMC5883L_ERR_PARAM
} qmc5883l_status_t;

typedef bool (*i2c_write_fn)(uint8_t dev_addr, uint8_t reg_addr, uint8_t val);
typedef bool (*i2c_read_fn)(uint8_t dev_addr, uint8_t reg_addr, uint8_t* buf, size_t len);

typedef struct {
    uint8_t       dev_addr;
    i2c_write_fn  write_reg;
    i2c_read_fn   read_regs;
} qmc5883l_dev_t;

qmc5883l_status_t qmc5883l_init(qmc5883l_dev_t* dev, const qmc5883l_config_t* config) {
    if (!dev || !dev->write_reg || !config) {
        return QMC5883L_ERR_PARAM;
    }

    // 1. Програмне скидання (SOFT_RST = 0x80 у регістр 0x0A)
    if (!dev->write_reg(dev->dev_addr, 0x0A, 0x80)) {
        return QMC5883L_ERR_I2C;
    }

    // 2. Встановити період SET/RESET (0x0B = 0x01)
    if (!dev->write_reg(dev->dev_addr, 0x0B, 0x01)) {
        return QMC5883L_ERR_I2C;
    }

    // 3. Записати конфігурацію в CR1 (0x09)
    uint8_t cr1 = qmc5883l_config_to_cr1(config);
    if (!dev->write_reg(dev->dev_addr, 0x09, cr1)) {
        return QMC5883L_ERR_I2C;
    }

    return QMC5883L_OK;
}

#include "qmc5883l.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846f
#endif

/**
 * @file qmc5883l.c
 * @brief Реалізація функцій драйвера магнітометра QMC5883L.
 */

qmc5883l_err_t qmc5883l_init(qmc5883l_t *dev, uint8_t i2c_addr, qmc5883l_mode_t mode,
                            qmc5883l_odr_t odr, qmc5883l_rng_t rng, qmc5883l_osr_t osr) {
    if (dev == NULL) return QMC5883L_ERR_PARAM;

    dev->i2c_addr = i2c_addr;
    dev->mode = mode;
    dev->odr = odr;
    dev->rng = rng;
    dev->osr = osr;
    dev->declination_deg = 0.0f;

    qmc5883l_calib_init(&dev->calib);

    /* Перевірка наявності чипа на шині I2C */
    if (!i2c_ping(dev->i2c_addr)) {
        return QMC5883L_ERR_I2C;
    }

    /* Програмне скидання */
    if (qmc5883l_reset(dev) != QMC5883L_OK) {
        return QMC5883L_ERR_I2C;
    }

    /* Запис періоду SET/RESET (0x0B = 0x01 за рекомендацією специфікації QMC5883L) */
    if (i2c_write_reg(dev->i2c_addr, QMC5883L_REG_SETRST, 0x01) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    /* Формування значення регістра Control Register 1 (0x09)
     * Біти [7:6] = OSR
     * Біти [5:4] = RNG
     * Біти [3:2] = ODR
     * Біти [1:0] = MODE
     */
    uint8_t ctrl1 = ((uint8_t)osr << 6) | ((uint8_t)rng << 4) | ((uint8_t)odr << 2) | ((uint8_t)mode);
    if (i2c_write_reg(dev->i2c_addr, QMC5883L_REG_CTRL1, ctrl1) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    return QMC5883L_OK;
}

qmc5883l_err_t qmc5883l_reset(qmc5883l_t *dev) {
    if (dev == NULL) return QMC5883L_ERR_PARAM;

    /* Регістр 0x0A: біт Soft Reset = 0x80 */
    if (i2c_write_reg(dev->i2c_addr, QMC5883L_REG_CTRL2, 0x80) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    return QMC5883L_OK;
}

bool qmc5883l_is_data_ready(qmc5883l_t *dev) {
    if (dev == NULL) return false;

    uint8_t status = 0;
    if (i2c_read_reg(dev->i2c_addr, QMC5883L_REG_STATUS, &status) != I2C_OK) {
        return false;
    }

    return (status & QMC5883L_STAT_DRDY) != 0U;
}

qmc5883l_err_t qmc5883l_read_raw(qmc5883l_t *dev, qmc5883l_raw_t *raw) {
    if (dev == NULL || raw == NULL) return QMC5883L_ERR_PARAM;

    uint8_t status = 0;
    if (i2c_read_reg(dev->i2c_addr, QMC5883L_REG_STATUS, &status) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    if (status & QMC5883L_STAT_OVL) {
        return QMC5883L_ERR_OVERFLOW;
    }

    uint8_t buf[6];
    /* Безперервне читання 6 байтів: X_LSB, X_MSB, Y_LSB, Y_MSB, Z_LSB, Z_MSB (Little-Endian) */
    if (i2c_read_regs(dev->i2c_addr, QMC5883L_REG_DATA_X_LSB, buf, 6) != I2C_OK) {
        return QMC5883L_ERR_I2C;
    }

    raw->x = (int16_t)((uint16_t)buf[0] | ((uint16_t)buf[1] << 8));
    raw->y = (int16_t)((uint16_t)buf[2] | ((uint16_t)buf[3] << 8));
    raw->z = (int16_t)((uint16_t)buf[4] | ((uint16_t)buf[5] << 8));

    return QMC5883L_OK;
}

qmc5883l_err_t qmc5883l_read_scaled(qmc5883l_t *dev, float *x_gauss, float *y_gauss, float *z_gauss) {
    if (dev == NULL || x_gauss == NULL || y_gauss == NULL || z_gauss == NULL) {
        return QMC5883L_ERR_PARAM;
    }

    qmc5883l_raw_t raw;
    qmc5883l_err_t err = qmc5883l_read_raw(dev, &raw);
    if (err != QMC5883L_OK) return err;

    /* Коефіцієнт чутливості LSB/G залежно від обраного діапазону */
    float lsb_per_g = (dev->rng == QMC5883L_RNG_2G) ? 12000.0f : 3000.0f;

    *x_gauss = (float)raw.x / lsb_per_g;
    *y_gauss = (float)raw.y / lsb_per_g;
    *z_gauss = (float)raw.z / lsb_per_g;

    return QMC5883L_OK;
}

void qmc5883l_calib_init(qmc5883l_calib_t *calib) {
    if (calib == NULL) return;

    calib->x_min = 32767;
    calib->x_max = -32768;
    calib->y_min = 32767;
    calib->y_max = -32768;
    calib->z_min = 32767;
    calib->z_max = -32768;

    calib->x_offset = 0.0f;
    calib->y_offset = 0.0f;
    calib->z_offset = 0.0f;

    calib->x_scale = 1.0f;
    calib->y_scale = 1.0f;
    calib->z_scale = 1.0f;

    calib->is_calibrated = false;
}

void qmc5883l_calib_update(qmc5883l_calib_t *calib, const qmc5883l_raw_t *raw) {
    if (calib == NULL || raw == NULL) return;

    /* Ігноруємо аномальні сплески або помилкові дані 0 / -1 */
    if (raw->x == 0 && raw->y == 0 && raw->z == 0) return;

    if (raw->x < calib->x_min) calib->x_min = raw->x;
    if (raw->x > calib->x_max) calib->x_max = raw->x;

    if (raw->y < calib->y_min) calib->y_min = raw->y;
    if (raw->y > calib->y_max) calib->y_max = raw->y;

    if (raw->z < calib->z_min) calib->z_min = raw->z;
    if (raw->z > calib->z_max) calib->z_max = raw->z;

    /* Динамічний розрахунок Hard-Iron offset (центр сфери/еліпсоїда) */
    calib->x_offset = (float)(calib->x_min + calib->x_max) / 2.0f;
    calib->y_offset = (float)(calib->y_min + calib->y_max) / 2.0f;
    calib->z_offset = (float)(calib->z_min + calib->z_max) / 2.0f;

    /* Розрахунок Soft-Iron scale factors (нормалізація радіусів осей) */
    float x_delta = (float)(calib->x_max - calib->x_min) / 2.0f;
    float y_delta = (float)(calib->y_max - calib->y_min) / 2.0f;
    float z_delta = (float)(calib->z_max - calib->z_min) / 2.0f;

    float avg_delta = (x_delta + y_delta + z_delta) / 3.0f;

    if (x_delta > 0.0f) calib->x_scale = avg_delta / x_delta;
    if (y_delta > 0.0f) calib->y_scale = avg_delta / y_delta;
    if (z_delta > 0.0f) calib->z_scale = avg_delta / z_delta;

    calib->is_calibrated = true;
}

void qmc5883l_calib_apply(const qmc5883l_calib_t *calib, const qmc5883l_raw_t *raw,
                          float *cal_x, float *cal_y, float *cal_z) {
    if (raw == NULL || cal_x == NULL || cal_y == NULL || cal_z == NULL) return;

    if (calib != NULL && calib->is_calibrated) {
        *cal_x = ((float)raw->x - calib->x_offset) * calib->x_scale;
        *cal_y = ((float)raw->y - calib->y_offset) * calib->y_scale;
        *cal_z = ((float)raw->z - calib->z_offset) * calib->z_scale;
    } else {
        *cal_x = (float)raw->x;
        *cal_y = (float)raw->y;
        *cal_z = (float)raw->z;
    }
}

float qmc5883l_compute_heading(float x, float y, float declination_deg) {
    /* Обчислення тригонометричного кута у радіанах */
    float heading_rad = atan2f(y, x);

    /* Перетворення у градуси */
    float heading_deg = heading_rad * (180.0f / M_PI);

    /* Врахування магнітного схилення */
    heading_deg += declination_deg;

    /* Нормалізація у діапазоні [0°, 360°) */
    if (heading_deg < 0.0f) {
        heading_deg += 360.0f;
    }
    if (heading_deg >= 360.0f) {
        heading_deg -= 360.0f;
    }

    return heading_deg;
}

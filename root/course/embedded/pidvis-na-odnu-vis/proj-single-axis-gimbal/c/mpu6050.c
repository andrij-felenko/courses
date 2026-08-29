#include "mpu6050.h"

#include <util/delay.h>

/* Карта регістрів MPU-6050 */
#define REG_SMPLRT_DIV   0x19
#define REG_CONFIG       0x1A
#define REG_GYRO_CONFIG  0x1B
#define REG_ACCEL_CONFIG 0x1C
#define REG_ACCEL_XOUT_H 0x3B
#define REG_PWR_MGMT_1   0x6B
#define REG_WHO_AM_I     0x75

#define WHO_AM_I_VALUE   0x68

/* Масштаби з паспорта: ±500 °/с дає 65.5 LSB на °/с,
 * ±2 g дає 16384 LSB на g. */
#define GYRO_LSB_PER_DPS 65.5f
#define ACCEL_LSB_PER_G  16384.0f

i2c_status_t mpu6050_init(void)
{
    uint8_t who = 0;

    i2c_status_t st = i2c_read_regs(MPU6050_ADDR, REG_WHO_AM_I, &who, 1);
    if (st != I2C_OK) {
        return st;
    }
    if (who != WHO_AM_I_VALUE) {
        /* Відповів хтось інший: або переплутана адреса, або на шині
         * висить чужа мікросхема. Далі йти немає сенсу. */
        return I2C_ERR_BUS;
    }

    /* Вихід зі сну + джерело такту від осцилятора гіроскопа X:
     * він стабільніший за внутрішній RC-генератор давача. */
    st = i2c_write_reg(MPU6050_ADDR, REG_PWR_MGMT_1, 0x01);
    if (st != I2C_OK) return st;
    _delay_ms(50);

    /* DLPF 44 Гц (акселерометр) / 42 Гц (гіроскоп): половина смуги нашого
     * такту 200 Гц. Ширша смуга притягла б у контур вібрацію мотора. */
    st = i2c_write_reg(MPU6050_ADDR, REG_CONFIG, 0x03);
    if (st != I2C_OK) return st;

    /* Із увімкненим DLPF внутрішня частота 1 кГц; дільник 4 дає 200 Гц —
     * рівно наш такт, тож кожне читання приносить свіжу вибірку. */
    st = i2c_write_reg(MPU6050_ADDR, REG_SMPLRT_DIV, 0x04);
    if (st != I2C_OK) return st;

    /* ±500 °/с: стенд рукою розгойдують до ~300 °/с, запас є,
     * а роздільність удвічі краща за ±1000. */
    st = i2c_write_reg(MPU6050_ADDR, REG_GYRO_CONFIG, 0x08);
    if (st != I2C_OK) return st;

    /* ±2 g — найточніший діапазон, а нахил ми міряємо в спокої. */
    st = i2c_write_reg(MPU6050_ADDR, REG_ACCEL_CONFIG, 0x00);
    if (st != I2C_OK) return st;

    return I2C_OK;
}

static int16_t be16(const uint8_t *p)
{
    /* MPU-6050 віддає старший байт першим. */
    return (int16_t)(((uint16_t)p[0] << 8) | p[1]);
}

i2c_status_t mpu6050_read(imu_sample_t *out)
{
    uint8_t raw[14];

    /* 0x3B…0x48: ax, ay, az, температура, gx, gy, gz — одним блоком. */
    const i2c_status_t st = i2c_read_regs(MPU6050_ADDR, REG_ACCEL_XOUT_H, raw, sizeof raw);
    if (st != I2C_OK) {
        return st;
    }

    const int16_t ay_raw = be16(&raw[2]);
    const int16_t az_raw = be16(&raw[4]);
    const int16_t gx_raw = be16(&raw[8]);

    out->accel_y_g  = (float)ay_raw / ACCEL_LSB_PER_G;
    out->accel_z_g  = (float)az_raw / ACCEL_LSB_PER_G;
    out->gyro_x_dps = (float)gx_raw / GYRO_LSB_PER_DPS;

    return I2C_OK;
}

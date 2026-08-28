#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Адреса пристрою I2C */
#define MMC5983MA_I2C_ADDR      0x30

/* Регістри */
#define REG_XOUT_LOW            0x00
#define REG_STATUS              0x07
#define REG_CTRL_0              0x08
#define REG_CTRL_1              0x09
#define REG_CTRL_2              0x0A
#define REG_PRODUCT_ID          0x2F

/* Маски регістра CONTROL_0 */
#define CTRL0_TM_M              (1 << 0)
#define CTRL0_SET               (1 << 3)
#define CTRL0_RESET             (1 << 4)
#define CTRL0_AUTO_SR_EN        (1 << 5)
#define CTRL0_SW_RST            (1 << 7)

/* Маски регістра STATUS */
#define STATUS_MEAS_DONE        (1 << 0)

/* Коди помилок драйвера */
typedef enum {
    MAG_OK = 0,
    MAG_ERR_I2C,
    MAG_ERR_DEV_NOT_FOUND,
    MAG_ERR_TIMEOUT
} mag_error_t;

/* Структура результатів вимірювання (в Гаусах) */
typedef struct {
    float x_gauss;
    float y_gauss;
    float z_gauss;
} mag_data_t;

/* Прототипи низькорівневих шинних функцій (реалізуються платформою) */
extern mag_error_t i2c_read_bytes(uint8_t dev_addr, uint8_t reg_addr, uint8_t* data, size_t len);
extern mag_error_t i2c_write_byte(uint8_t dev_addr, uint8_t reg_addr, uint8_t data);
extern void delay_ms(uint32_t ms);

/* Програмне скидання та перевірка ID */
mag_error_t mag_init(void) {
    mag_error_t err;
    uint8_t id = 0;

    /* Скидання пристрою */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_SW_RST);
    if (err != MAG_OK) return err;
    delay_ms(15);

    /* Перевірка Product ID */
    err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_PRODUCT_ID, &id, 1);
    if (err != MAG_OK) return err;
    if (id != 0x30) return MAG_ERR_DEV_NOT_FOUND;

    /* Вмикаємо автоматичний SET/RESET та 18-бітний режим (BW = 100 Гц) */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_1, 0x03);
    if (err != MAG_OK) return err;

    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_AUTO_SR_EN);
    return err;
}

/* Примусовий розмагнічувальний імпульс SET/RESET */
mag_error_t mag_degauss_pulse(void) {
    mag_error_t err;
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_SET);
    if (err != MAG_OK) return err;
    delay_ms(1);

    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_RESET);
    if (err != MAG_OK) return err;
    delay_ms(1);

    return i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_AUTO_SR_EN);
}

/* Одиничне вимірювання поля по трьох осях */
mag_error_t mag_read_field(mag_data_t* out_data) {
    mag_error_t err;
    uint8_t raw_buf[7];
    uint8_t status = 0;
    uint32_t timeout = 100;

    /* Запуск вимірювання */
    err = i2c_write_byte(MMC5983MA_I2C_ADDR, REG_CTRL_0, CTRL0_TM_M | CTRL0_AUTO_SR_EN);
    if (err != MAG_OK) return err;

    /* Очікування прапорця Meas_Done */
    while (timeout > 0) {
        err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_STATUS, &status, 1);
        if (err == MAG_OK && (status & STATUS_MEAS_DONE)) {
            break;
        }
        delay_ms(1);
        timeout--;
    }
    if (timeout == 0) return MAG_ERR_TIMEOUT;

    /* Зчитування 7 байт даних (X, Y, Z + розширення 18 біт) */
    err = i2c_read_bytes(MMC5983MA_I2C_ADDR, REG_XOUT_LOW, raw_buf, 7);
    if (err != MAG_OK) return err;

    /* Збирання 18-бітних чисел */
    uint32_t raw_x = ((uint32_t)raw_buf[0] << 10) | ((uint32_t)raw_buf[1] << 2) | ((raw_buf[6] >> 6) & 0x03);
    uint32_t raw_y = ((uint32_t)raw_buf[2] << 10) | ((uint32_t)raw_buf[3] << 2) | ((raw_buf[6] >> 4) & 0x03);
    uint32_t raw_z = ((uint32_t)raw_buf[4] << 10) | ((uint32_t)raw_buf[5] << 2) | ((raw_buf[6] >> 2) & 0x03);

    /* Перетворення у Гауси (нульова точка 131072, масштаб 16384 LSB/Gauss) */
    out_data->x_gauss = ((float)raw_x - 131072.0f) / 16384.0f;
    out_data->y_gauss = ((float)raw_y - 131072.0f) / 16384.0f;
    out_data->z_gauss = ((float)raw_z - 131072.0f) / 16384.0f;

    return MAG_OK;
}

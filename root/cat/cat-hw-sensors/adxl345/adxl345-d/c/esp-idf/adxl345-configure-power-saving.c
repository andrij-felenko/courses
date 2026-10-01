#include <stdint.h>
#include <math.h>

#define ADXL345_REG_OFSX        0x1E
#define ADXL345_REG_OFSY        0x1F
#define ADXL345_REG_OFSZ        0x20
#define ADXL345_REG_BW_RATE     0x2C
#define ADXL345_REG_POWER_CTL   0x2D

extern int i2c_write_reg(uint8_t reg, uint8_t value);

// Налаштування режимів живлення та Auto-Sleep
void adxl345_configure_power_saving(void) {
    // 1. Перехід у Standby для конфігурування (Measure = 0)
    i2c_write_reg(ADXL345_REG_POWER_CTL, 0x00);

    // 2. Встановлення ODR 100 Гц (BW_RATE = 0x0A)
    i2c_write_reg(ADXL345_REG_BW_RATE, 0x0A);

    // 3. Увімкнення Auto-Sleep (Link = 1, AUTO_SLEEP = 1, Measure = 1)
    i2c_write_reg(ADXL345_REG_POWER_CTL, 0x38);
}

// Калібрування нульового зсуву за осями
void adxl345_calibrate_zero_g(int16_t raw_x, int16_t raw_y, int16_t raw_z) {
    int16_t target_z = 256; // 1g у режимі Full Resolution (~3.9 мг/МЗР)

    int8_t offset_x = (int8_t)(-round((double)raw_x / 4.0));
    int8_t offset_y = (int8_t)(-round((double)raw_y / 4.0));
    int8_t offset_z = (int8_t)(-round((double)(raw_z - target_z) / 4.0));

    i2c_write_reg(ADXL345_REG_OFSX, (uint8_t)offset_x);
    i2c_write_reg(ADXL345_REG_OFSY, (uint8_t)offset_y);
    i2c_write_reg(ADXL345_REG_OFSZ, (uint8_t)offset_z);
}

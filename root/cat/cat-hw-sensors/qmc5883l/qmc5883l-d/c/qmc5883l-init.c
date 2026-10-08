#include <stdint.h>
#include <stdbool.h>

#define QMC5883L_ADDR       0x0D
#define REG_OUT_X_L         0x00
#define REG_STATUS          0x06
#define REG_CONTROL_1       0x09
#define REG_CONTROL_2       0x0A
#define REG_SET_RESET       0x0B

// Зовнішні функції адаптера I2C для конкретної платформи
extern bool i2c_write_reg(uint8_t dev_addr, uint8_t reg_addr, uint8_t data);
extern bool i2c_read_bytes(uint8_t dev_addr, uint8_t reg_addr, uint8_t *buffer, uint16_t length);

bool qmc5883l_init(void) {
    // 1. Програмне скидання чипа
    if (!i2c_write_reg(QMC5883L_ADDR, REG_CONTROL_2, 0x80)) return false;
    
    // 2. Налаштування періоду Set/Reset (обов'язково 0x01 за специфікацією)
    if (!i2c_write_reg(QMC5883L_ADDR, REG_SET_RESET, 0x01)) return false;
    
    // 3. Конфігурація: OSR = 512 (00b), RNG = ±2G (00b), ODR = 200Hz (11b), MODE = Continuous (01b)
    // Значення для Control Register 1: 00 00 11 01 = 0x0D
    uint8_t ctrl1_val = (0x00 << 6) | (0x00 << 4) | (0x03 << 2) | 0x01;
    return i2c_write_reg(QMC5883L_ADDR, REG_CONTROL_1, ctrl1_val);
}

bool qmc5883l_read_raw(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t status;
    if (!i2c_read_bytes(QMC5883L_ADDR, REG_STATUS, &status, 1)) return false;
    
    // Перевірка готовності даних (біт DRDY = 1)
    if (!(status & 0x01)) return false;
    
    uint8_t buffer[6];
    if (!i2c_read_bytes(QMC5883L_ADDR, REG_OUT_X_L, buffer, 6)) return false;
    
    // Формування підписаних 16-бітних значень з Little-Endian байтів
    *x = (int16_t)((uint16_t)buffer[1] << 8 | buffer[0]);
    *y = (int16_t)((uint16_t)buffer[3] << 8 | buffer[2]);
    *z = (int16_t)((uint16_t)buffer[5] << 8 | buffer[4]);
    
    return true;
}

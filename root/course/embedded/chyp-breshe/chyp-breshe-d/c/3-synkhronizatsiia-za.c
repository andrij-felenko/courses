#include <stdint.h>
#include <stdbool.h>

// Приклад налаштування BDU та пакетного читання 6 осей акселерометра
#define REG_CTRL_REG4   0x23
#define REG_OUT_X_L     0x28
#define BDU_ENABLE_MASK 0x80
#define I2C_AUTO_INC    0x80  // Біт автоінкременту адреси для деяких чипів (ST)

typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} AccelAxes_t;

// Пакетне читання 6 байтів за одну I2C транзакцію
bool read_accel_atomic(uint8_t dev_addr, AccelAxes_t *out_axes) {
    uint8_t raw_buf[6];
    uint8_t start_reg = REG_OUT_X_L | I2C_AUTO_INC;
    
    // Пакетне зчитування: передача адреси стартового регістра 
    // і вичитування 6 байтів поспіль без проміжних STOP умов
    if (!i2c_write_read(dev_addr, &start_reg, 1, raw_buf, 6)) {
        return false;
    }
    
    // Розпакування пар Little-Endian байтів
    out_axes->x = (int16_t)(((uint16_t)raw_buf[1] << 8) | (uint16_t)raw_buf[0]);
    out_axes->y = (int16_t)(((uint16_t)raw_buf[3] << 8) | (uint16_t)raw_buf[2]);
    out_axes->z = (int16_t)(((uint16_t)raw_buf[5] << 8) | (uint16_t)raw_buf[4]);
    
    return true;
}

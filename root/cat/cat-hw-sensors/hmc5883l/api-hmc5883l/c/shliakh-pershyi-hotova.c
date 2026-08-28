#include <Wire.h>

#define ADDR_HMC  0x1E   // HMC5883L (Honeywell)
#define ADDR_QMC  0x0D   // QMC5883L (QST)

enum ChipKind { CHIP_NONE, CHIP_HMC, CHIP_QMC };
ChipKind chip = CHIP_NONE;

// Перевірити, чи відповідає пристрій на даній адресі (ACK на шині)
static bool i2c_present(uint8_t addr) {
    Wire.beginTransmission(addr);
    return Wire.endTransmission() == 0;   // 0 = отримали ACK
}

// Записати один байт у регістр
static void reg_write(uint8_t addr, uint8_t reg, uint8_t val) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    Wire.write(val);
    Wire.endTransmission();
}

// Прочитати n байтів, починаючи з reg (I²C-автоінкремент)
static uint8_t reg_read(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(addr);
    Wire.write(reg);
    if (Wire.endTransmission(false) != 0)  // repeated START, шину не відпускаємо
        return 0;
    uint8_t got = Wire.requestFrom(addr, n);
    for (uint8_t i = 0; i < got && i < n; i++)
        buf[i] = Wire.read();
    return got;
}

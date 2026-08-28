#include <stdint.h>

#define LSM6_ADDR      0x6B   // адреса LSM6DS33 на шині
#define REG_WHO_AM_I   0x0F
#define REG_CTRL1_XL   0x10   // акселерометр
#define REG_CTRL2_G    0x11   // гіроскоп

int lsm6_init(void) {
    uint8_t id = i2c_read_reg(LSM6_ADDR, REG_WHO_AM_I);
    if (id != 0x69) return -1;          // чип не відповів — далі немає сенсу

    // 0x80 = 1.66 кГц, 0x00 = ±2 g  → акселерометр увімкнено
    i2c_write_reg(LSM6_ADDR, REG_CTRL1_XL, 0x80);
    // 0x80 = 1.66 кГц, 0x00 = ±245 °/с → гіроскоп увімкнено
    i2c_write_reg(LSM6_ADDR, REG_CTRL2_G, 0x80);
    return 0;
}

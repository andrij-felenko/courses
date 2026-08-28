#include <stdint.h>

#define MPU_ADDR   0x68      // AD0 до землі → 0x68 (до живлення → 0x69)
#define AK_ADDR    0x0C      // магнетометр AK8963, коли він на зовнішній шині
#define BMP_ADDR   0x76      // барометр BMP280 (на деяких платах 0x77)

// Записати один байт у регістр пристрою dev.
int  i2c_write_reg(uint8_t dev, uint8_t reg, uint8_t val);
// Прочитати n байтів поспіль, починаючи з регістра reg, у буфер buf.
int  i2c_read_regs(uint8_t dev, uint8_t reg, uint8_t *buf, uint8_t n);

// Зручні похідні:
static uint8_t read_u8(uint8_t dev, uint8_t reg) {
    uint8_t b; i2c_read_regs(dev, reg, &b, 1); return b;
}

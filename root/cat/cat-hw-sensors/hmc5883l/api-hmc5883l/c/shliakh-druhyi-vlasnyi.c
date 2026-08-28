#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// ── Ці дві функції реалізуєш під свою платформу (STM32 HAL, ESP-IDF, тощо) ──
// Записати один байт val у регістр reg пристрою addr. Повернути 0 при успіху.
extern int  i2c_write_reg(uint8_t addr, uint8_t reg, uint8_t val);
// Прочитати n байтів у buf, починаючи з reg. Повернути 0 при успіху.
extern int  i2c_read_regs(uint8_t addr, uint8_t reg, uint8_t *buf, uint8_t n);

#define HMC_ADDR 0x1E

// Регістри HMC5883L
#define HMC_CONFIG_A 0x00
#define HMC_CONFIG_B 0x01
#define HMC_MODE     0x02
#define HMC_DATA     0x03   // далі 6 байтів: X(H,L) Z(H,L) Y(H,L)
#define HMC_STATUS   0x09
#define HMC_ID_A     0x0A   // 'H' (0x48)

// Підсилення для типового ±1.3 Гаус (Config B = 0x20): 1090 LSb/Gauss
#define HMC_LSB_PER_GAUSS 1090.0f

// Повернути true, якщо чип на 0x1E справді HMC5883L (ID = 'H','4','3')
bool hmc_detect(void) {
    uint8_t id[3];
    if (i2c_read_regs(HMC_ADDR, HMC_ID_A, id, 3) != 0) return false;
    return id[0] == 'H' && id[1] == '4' && id[2] == '3';   // 0x48 0x34 0x33
}

void hmc_init(void) {
    i2c_write_reg(HMC_ADDR, HMC_CONFIG_A, 0x70);   // 8 усереднень, 15 Гц
    i2c_write_reg(HMC_ADDR, HMC_CONFIG_B, 0x20);   // ±1.3 Гаус
    i2c_write_reg(HMC_ADDR, HMC_MODE,     0x00);   // безперервний вимір
}

// Прочитати три осі. Повертає false при переповненні або помилці шини.
bool hmc_read_raw(int16_t *x, int16_t *y, int16_t *z) {
    uint8_t b[6];
    if (i2c_read_regs(HMC_ADDR, HMC_DATA, b, 6) != 0) return false;
    // Порядок у чипі: X, Z, Y — big-endian (старший байт першим)
    *x = (int16_t)((b[0] << 8) | b[1]);
    *z = (int16_t)((b[2] << 8) | b[3]);
    *y = (int16_t)((b[4] << 8) | b[5]);
    // -4096 (0xF000) = ADC-переповнення: поле сильніше за обраний діапазон
    if (*x == -4096 || *y == -4096 || *z == -4096) return false;
    return true;
}

// Перевести сирий відлік у Гауси (для діагностики / нахилокомпенсації)
float hmc_to_gauss(int16_t raw) {
    return (float)raw / HMC_LSB_PER_GAUSS;
}

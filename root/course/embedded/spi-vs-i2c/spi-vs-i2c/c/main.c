#include <stdint.h>

// Три давачі живуть на I2C — одна шина, різні адреси (7 біт).
#define IMU_ADDR   0x68
#define BARO_ADDR  0x76
#define MAG_ADDR   0x1E

// Дисплей і картка живуть на SPI — спільні лінії, окремий CS у кожного.
#define TFT_CS_PIN  5
#define SD_CS_PIN   17

void board_buses_init(void) {
    i2c_init(/*scl=*/22, /*sda=*/21, /*hz=*/400000);   // 3 давачі, 2 ніжки
    spi_init(/*sck=*/18, /*mosi=*/23, /*miso=*/19,     // 3 спільні лінії
             /*hz=*/20000000);                          // десятки МГц для TFT/SD
    gpio_output(TFT_CS_PIN); gpio_set(TFT_CS_PIN, 1);  // CS у спокої — високий
    gpio_output(SD_CS_PIN);  gpio_set(SD_CS_PIN, 1);
}

// Звернення до пристрою I2C адресує його по шині; SPI — опускає його CS.
int imu_read(uint8_t reg, uint8_t *buf, int n) {
    return i2c_read_reg(IMU_ADDR, reg, buf, n);        // адреса замість дроту
}

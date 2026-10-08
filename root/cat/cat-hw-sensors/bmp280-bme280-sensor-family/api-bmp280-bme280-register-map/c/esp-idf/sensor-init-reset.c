#include <stdint.h>
#include <stdbool.h>

#define BMP280_REG_ID        0xD0
#define BMP280_REG_RESET     0xE0
#define BMP280_REG_STATUS    0xF3

#define BMP280_CHIP_ID       0x58
#define BME280_CHIP_ID       0x60
#define BMP280_RESET_CMD     0xB6

// Приклад перевірки та скидання давача через I2C
bool sensor_init_reset(uint8_t dev_addr) {
    uint8_t chip_id = 0;
    i2c_read_reg(dev_addr, BMP280_REG_ID, &chip_id, 1);
    
    if (chip_id != BMP280_CHIP_ID && chip_id != BME280_CHIP_ID) {
        return false; // Пристрій не знайдено або збій шини
    }
    
    // Надсилання команди програмного скидання
    uint8_t reset_cmd = BMP280_RESET_CMD;
    i2c_write_reg(dev_addr, BMP280_REG_RESET, &reset_cmd, 1);
    
    // Очікування завершення перезавантаження NVM (im_update == 0)
    uint8_t status = 0;
    do {
        i2c_read_reg(dev_addr, BMP280_REG_STATUS, &status, 1);
    } while (status & 0x01);
    
    return true;
}

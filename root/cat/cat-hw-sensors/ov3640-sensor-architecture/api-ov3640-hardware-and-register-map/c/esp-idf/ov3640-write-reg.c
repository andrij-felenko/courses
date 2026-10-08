// Приклад ініціалізації OV3640 та перемикання банок у C (ESP-IDF)
#include <stdio.h>
#include <stdint.h>
#include "driver/i2c.h"

#define OV3640_SCCB_ADDR   0x3C  // 7-бітна адреса пристрою на шині SCCB
#define REG_BANK_SEL       0xFF  // Регістр вибору банки
#define REG_CHIP_ID_HIGH   0x0A  // Верхній байт ID пристрою
#define REG_CHIP_ID_LOW    0x0B  // Нижній байт ID пристрою

// Функція запису байта в регістр OV3640 через SCCB/I2C
esp_err_t ov3640_write_reg(uint8_t reg_addr, uint8_t value) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg_addr, true);
    i2c_master_write_byte(cmd, value, true);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, 1000 / portTICK_PERIOD_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Функція зчитування байта з регістру OV3640
esp_err_t ov3640_read_reg(uint8_t reg_addr, uint8_t *value) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, reg_addr, true);
    i2c_master_start(cmd); // Repeated start
    i2c_master_write_byte(cmd, (OV3640_SCCB_ADDR << 1) | I2C_MASTER_READ, true);
    i2c_master_read_byte(cmd, value, I2C_MASTER_NACK);
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(I2C_NUM_0, cmd, 1000 / portTICK_PERIOD_MS);
    i2c_cmd_link_delete(cmd);
    return ret;
}

// Перевірка ID та ініціалізація банок
bool ov3640_init_sensor(void) {
    uint8_t id_high = 0, id_low = 0;
    
    // Спочатку перемикаємося на Bank 1 для зчитування системних регістрів
    if (ov3640_write_reg(REG_BANK_SEL, 0x01) != ESP_OK) return false;
    
    ov3640_read_reg(REG_CHIP_ID_HIGH, &id_high);
    ov3640_read_reg(REG_CHIP_ID_LOW, &id_low);
    
    uint16_t chip_id = ((uint16_t)id_high << 8) | id_low;
    if (chip_id != 0x3640) {
        printf("Помилка: невідомий Chip ID 0x%04X (очікувалося 0x3640)\n", chip_id);
        return false;
    }
    
    printf("Сенсор OV3640 успішно виявлено! ID: 0x%04X\n", chip_id);
    return true;
}

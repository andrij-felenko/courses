#include <stdint.h>
#include <stdbool.h>
#include "driver/i2c.h"

#define OLED_I2C_ADDR 0x3C

// Структура для керування піксельним зміщенням
typedef struct {
    int8_t shift_x;
    int8_t shift_y;
    uint8_t step;
} oled_shift_state_t;

static oled_shift_state_t g_shift = {0, 0, 0};

// Зміна зміщення по замкненому контуру 2x2 пікселі
void oled_update_pixel_shift(void) {
    g_shift.step = (g_shift.step + 1) % 4;
    switch (g_shift.step) {
        case 0: g_shift.shift_x = 0; g_shift.shift_y = 0; break;
        case 1: g_shift.shift_x = 1; g_shift.shift_y = 0; break;
        case 2: g_shift.shift_x = 1; g_shift.shift_y = 1; break;
        case 3: g_shift.shift_x = 0; g_shift.shift_y = 1; break;
    }
}

// Встановлення контрастності (яскравість люмінофора)
esp_err_t oled_set_contrast(i2c_port_t i2c_num, uint8_t contrast) {
    uint8_t cmd_buf[4] = {0x00, 0x81, contrast, 0x00};
    return i2c_master_write_to_device(i2c_num, OLED_I2C_ADDR, cmd_buf, 3, pdMS_TO_TICKS(100));
}

// Управління живленням дисплея та помпи підкачки заряду
esp_err_t oled_set_power_save(i2c_port_t i2c_num, bool enable_sleep) {
    i2c_cmd_handle_t cmd = i2c_cmd_link_create();
    i2c_master_start(cmd);
    i2c_master_write_byte(cmd, (OLED_I2C_ADDR << 1) | I2C_MASTER_WRITE, true);
    i2c_master_write_byte(cmd, 0x00, true); // Режим команд
    
    if (enable_sleep) {
        i2c_master_write_byte(cmd, 0xAE, true); // Дисплей ВИМК
        i2c_master_write_byte(cmd, 0x8D, true); // Налаштування charge pump
        i2c_master_write_byte(cmd, 0x10, true); // Вимкнути charge pump
    } else {
        i2c_master_write_byte(cmd, 0x8D, true); // Налаштування charge pump
        i2c_master_write_byte(cmd, 0x14, true); // Увімкнути charge pump
        i2c_master_write_byte(cmd, 0xAF, true); // Дисплей УВІМК
    }
    
    i2c_master_stop(cmd);
    esp_err_t ret = i2c_master_cmd_begin(i2c_num, cmd, pdMS_TO_TICKS(100));
    i2c_cmd_link_delete(cmd);
    return ret;
}

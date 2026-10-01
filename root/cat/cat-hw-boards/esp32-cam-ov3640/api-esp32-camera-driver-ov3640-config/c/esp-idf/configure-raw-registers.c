#include "esp_camera.h"

void configure_raw_registers(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (!s) {
        return;
    }

    // Зчитування 16-бітного регістра id сенсора OV3640 (адреси 0x300A та 0x300B)
    uint8_t pid_high = s->get_reg(s, 0x300A, 0xFF);
    uint8_t pid_low = s->get_reg(s, 0x300B, 0xFF);

    // Запис у регістр налаштування тактування PLL з маскою
    s->set_reg(s, 0x3010, 0x7F, 0x20);
}

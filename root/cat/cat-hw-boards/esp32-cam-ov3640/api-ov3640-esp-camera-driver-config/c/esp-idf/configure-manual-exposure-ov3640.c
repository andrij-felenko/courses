#include "esp_camera.h"

// Пряме програмування регістрів OV3640 через SCCB для фіксації експозиції
void configure_manual_exposure_ov3640(void) {
    sensor_t *s = esp_camera_sensor_get();
    if (s == NULL) {
        return;
    }

    // Відключення апаратних блоків AEC та AGC через метод set_reg
    // Регістр 0x3013: біт 0 - AEC, біт 2 - AGC
    uint8_t reg_val = s->get_reg(s, 0x3013, 0xFF);
    reg_val &= ~(0x01 | 0x04); // Скидання бітів AEC та AGC
    s->set_reg(s, 0x3013, 0xFF, reg_val);

    // Запис 16-бітного значення витримки в регістри 0x3015 (старший) та 0x3016 (молодший)
    uint16_t exposure_val = 0x0280; // Фіксоване значення експозиції
    s->set_reg(s, 0x3015, 0xFF, (exposure_val >> 8) & 0xFF);
    s->set_reg(s, 0x3016, 0xFF, exposure_val & 0xFF);

    // Встановлення фіксованого коефіцієнта підсилення в регістр 0x3010
    s->set_reg(s, 0x3010, 0xFF, 0x10); // Базове підсилення без шуму
}

#include "esp_camera.h"

// Ручне налаштування регістрів сенсора OV3640 у середовищі Arduino IDE
void setupManualExposureOV3640() {
  sensor_t *s = esp_camera_sensor_get();
  if (s != nullptr) {
    // Читання та модифікація регістра керування автоматикою
    uint8_t reg_val = s->get_reg(s, 0x3013, 0xFF);
    reg_val &= ~(0x01 | 0x04); // Вимкнення AEC та AGC
    s->set_reg(s, 0x3013, 0xFF, reg_val);

    // Ручна фіксація тривалості накопичення заряду
    uint16_t exposure = 0x0280;
    s->set_reg(s, 0x3015, 0xFF, (exposure >> 8) & 0xFF);
    s->set_reg(s, 0x3016, 0xFF, exposure & 0xFF);

    // Ручна фіксація аналогового підсилення
    s->set_reg(s, 0x3010, 0xFF, 0x10);
  }
}

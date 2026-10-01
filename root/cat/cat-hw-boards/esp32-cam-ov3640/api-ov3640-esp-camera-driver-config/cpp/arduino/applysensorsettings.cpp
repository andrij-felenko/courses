#include "esp_camera.h"

// Застосування налаштувань сенсора в середовищі Arduino IDE
void applySensorSettings() {
  sensor_t *s = esp_camera_sensor_get();
  if (s != nullptr) {
    s->set_vflip(s, 1);        // Вертикальний розворот
    s->set_hmirror(s, 1);      // Горизонтальне дзеркалювання
    s->set_brightness(s, 1);   // Підвищення яскравості
    s->set_contrast(s, 0);     // Базовий контраст
    s->set_whitebal(s, 1);     // Автобаланс білого
    s->set_exposure_ctrl(s, 1);// Автоекспозиція
    s->set_gain_ctrl(s, 1);    // Автопідсилення
  }
}

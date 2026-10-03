#include "esp_camera.h"

void applySensorSettings() {
  sensor_t *s = esp_camera_sensor_get();
  if (!s) {
    Serial.println("Помилка отримання вказівника sensor_t");
    return;
  }

  // Адаптація параметрів під умови освітлення
  s->set_exposure_ctrl(s, 1);
  s->set_gain_ctrl(s, 1);
  s->set_gainceiling(s, GAINCEILING_8X);
  s->set_whitebal(s, 1);

  // Орієнтація кадру
  s->set_hmirror(s, 0);
  s->set_vflip(s, 0);
}

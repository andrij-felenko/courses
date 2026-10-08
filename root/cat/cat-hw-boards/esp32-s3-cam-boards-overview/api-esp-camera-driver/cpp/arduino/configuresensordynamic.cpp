#include "esp_camera.h"

void configureSensorDynamic() {
  sensor_t *s = esp_camera_sensor_get();
  if (s == nullptr) {
    Serial.println("Сенсор не виявлено!");
    return;
  }

  s->set_brightness(s, 1);
  s->set_contrast(s, 0);
  s->set_saturation(s, -1);
  s->set_hmirror(s, 1);
  s->set_vflip(s, 1);
}

#include "esp_camera.h"

bool recoverCamera(const camera_config_t *config) {
  Serial.println("Перезапуск драйвера камери...");
  esp_camera_deinit();

  if (config->pin_pwdn >= 0) {
    digitalWrite(config->pin_pwdn, HIGH);
    delay(100);
    digitalWrite(config->pin_pwdn, LOW);
    delay(100);
  }

  esp_err_t err = esp_camera_init(config);
  if (err == ESP_OK) {
    Serial.println("Драйвер камери відновлено успішно");
    return true;
  }
  Serial.printf("Спроба відновлення завершилася помилкою: 0x%x\n", err);
  return false;
}

#include "esp_camera.h"

// Безаварійна обробка помилок ініціалізації в середовищі Arduino IDE
bool initCameraSafe(const camera_config_t &config) {
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Помилка ініціалізації драйвера: 0x%X\n", err);
    if (err == ESP_ERR_NOT_FOUND) {
      Serial.println("Помилка: Сенсор OV3640 не відповідає по SCCB. Перевірте лінії живлення та XCLK");
    } else if (err == ESP_ERR_NO_MEM) {
      Serial.println("Помилка: Вичерпано оперативну пам'ять. Увімкніть PSRAM або виберіть JPEG");
    }
    return false;
  }
  Serial.println("Камеру успішно ініціалізовано");
  return true;
}

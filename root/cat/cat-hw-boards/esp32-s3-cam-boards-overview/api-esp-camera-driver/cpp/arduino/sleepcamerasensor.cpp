#include "esp_camera.h"
#include "driver/gpio.h"

#define PWDN_GPIO_NUM 32

void sleepCameraSensor() {
  esp_camera_deinit();
  pinMode(PWDN_GPIO_NUM, OUTPUT);
  digitalWrite(PWDN_GPIO_NUM, HIGH);
}

void wakeupCameraSensor() {
  digitalWrite(PWDN_GPIO_NUM, LOW);
  delay(10);
}

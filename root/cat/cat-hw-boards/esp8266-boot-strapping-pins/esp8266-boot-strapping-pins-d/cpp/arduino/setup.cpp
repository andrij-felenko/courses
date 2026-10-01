#include <Arduino.h>

const int SHARED_BOOT_PIN = 0; // GPIO0 використовується як завантажувальний вивід та вхід кнопки

void setup() {
  // Невелика пауза для стабілізації станів виводів після завантаження SoC
  delay(100);
  
  // Конфігуруємо GPIO0 як вхід із внутрішньою підтяжкою лише після старту
  pinMode(SHARED_BOOT_PIN, INPUT_PULLUP);
}

void loop() {
  if (digitalRead(SHARED_BOOT_PIN) == LOW) {
    // Обробка натискання кнопки без ризику збою режиму старту
  }
}

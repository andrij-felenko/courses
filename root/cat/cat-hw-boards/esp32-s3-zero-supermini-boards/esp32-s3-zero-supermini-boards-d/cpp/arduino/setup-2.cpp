#include "USB.h"
#include "USBHIDKeyboard.h"

// Створення об'єкта емулятора клавіатури USB HID
USBHIDKeyboard Keyboard;

void setup() {
  // Ініціалізація програмного стека USB
  Keyboard.begin();
  USB.begin();
}

void loop() {
  // Перевірка готовності USB з'єднання
  delay(5000);
  
  // Емуляція натискання клавіші та відправка символу
  Keyboard.press('a');
  delay(100);
  Keyboard.releaseAll();
}

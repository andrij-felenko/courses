#include "USB.h"
#include "USBHIDKeyboard.h"

USBHIDKeyboard keyboard;

void setup() {
  keyboard.begin();
  USB.begin();
  delay(2000);                 // час хостові розпізнати пристрій
  keyboard.println("Привіт від ESP32-S3");   // ніби надрукували з клавіатури
}

void loop() {}

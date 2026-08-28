#include "BluetoothSerial.h"
BluetoothSerial SerialBT;

char    line[64];        // буфер для одного рядка-команди
uint8_t len = 0;         // скільки символів уже зібрано

void setup() {
  SerialBT.begin("ESP32-robot");
}

void loop() {
  // 1. Забрати все, що ВЖЕ прийшло, не чекаючи решти
  while (SerialBT.available()) {
    char c = SerialBT.read();

    if (c == '\n' || c == '\r') {        // кінець рядка → команда готова
      if (len > 0) {
        line[len] = '\0';                // завершити С-рядок
        handleCommand(line);             // розібрати її
        len = 0;                         // і почати збирати наступну
      }
    } else if (len < sizeof(line) - 1) { // звичайний символ — у буфер
      line[len++] = c;
    } else {
      len = 0;                           // переповнення: скинути сміття, не зависнути
    }
  }

  // 2. Решта циклу біжить ЩОтакту, бо ми ніде не блокувалися
  updateMotors();
  checkFailsafe();
}

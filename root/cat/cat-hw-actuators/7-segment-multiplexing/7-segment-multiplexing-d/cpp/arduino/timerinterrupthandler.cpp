// Приклад неблокуючого обробника сканування (Arduino / C++)
#include <Arduino.h>

const uint8_t NUM_DIGITS = 4;
uint8_t displayBuffer[NUM_DIGITS] = {0x3F, 0x06, 0x5B, 0x4F}; // "0123"
volatile uint8_t currentDigit = 0;

void timerInterruptHandler() {
  // Крок 1: Гасіння — вимикаємо всі ключі розрядів
  for (uint8_t i = 0; i < NUM_DIGITS; i++) {
    digitalWrite(digitPins[i], DIGIT_OFF);
  }

  // Крок 2: Оновлення шини сегментів
  uint8_t mask = displayBuffer[currentDigit];
  for (uint8_t seg = 0; seg < 8; seg++) {
    digitalWrite(segmentPins[seg], (mask & (1 << seg)) ? SEGMENT_ON : SEGMENT_OFF);
  }

  // Крок 3: Активація поточного розряду
  digitalWrite(digitPins[currentDigit], DIGIT_ON);

  // Крок 4: Інкремент індексу розряду
  currentDigit = (currentDigit + 1) % NUM_DIGITS;
}

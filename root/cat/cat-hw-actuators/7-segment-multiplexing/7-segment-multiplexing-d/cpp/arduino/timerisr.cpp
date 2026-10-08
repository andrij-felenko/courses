// Приклад неблокуючого драйвера фонового сканування (Arduino / C++)
#include <Arduino.h>

const uint8_t NUM_DIGITS = 4;
uint8_t bufferA[NUM_DIGITS] = {0};
uint8_t bufferB[NUM_DIGITS] = {0};

uint8_t* volatile frontBuffer = bufferA;
uint8_t* volatile backBuffer = bufferB;
volatile uint8_t currentDigit = 0;

void setupTimerInterrupt();

void timerISR() {
  // 1. Blanking: гасіння розрядів
  for (uint8_t i = 0; i < NUM_DIGITS; i++) {
    digitalWrite(digitPins[i], LOW);
  }

  // 2. Завантаження маски з frontBuffer
  uint8_t mask = frontBuffer[currentDigit];
  for (uint8_t seg = 0; seg < 8; seg++) {
    digitalWrite(segmentPins[seg], (mask & (1 << seg)) ? HIGH : LOW);
  }

  // 3. Увімкнення поточного розряду
  digitalWrite(digitPins[currentDigit], HIGH);

  // 4. Інкремент позиції
  currentDigit = (currentDigit + 1) % NUM_DIGITS;
}

void updateDisplayData(const uint8_t* newSegmentData) {
  // Запис у фоновий буфер
  for (uint8_t i = 0; i < NUM_DIGITS; i++) {
    backBuffer[i] = newSegmentData[i];
  }

  // Критична секція підміни буферів
  noInterrupts();
  uint8_t* temp = frontBuffer;
  frontBuffer = backBuffer;
  backBuffer = temp;
  interrupts();
}

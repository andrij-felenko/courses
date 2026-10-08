#include <Arduino.h>

const uint8_t PIN_ZERO_CROSS = 2; // Переривання INT0
const uint8_t PIN_MOC3021    = 3; // Керування світлодіодом оптопари

volatile uint16_t delayMicros = 5000; // Затримка 5 мс (50% потужності)
volatile bool timerTriggered  = false;

void IRAM_ATTR zeroCrossISR() {
  // При переході мережі через 0 В скидаємо таймер
  timerTriggered = true;
}

void setup() {
  pinMode(PIN_MOC3021, OUTPUT);
  digitalWrite(PIN_MOC3021, LOW);
  
  pinMode(PIN_ZERO_CROSS, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_ZERO_CROSS), zeroCrossISR, RISING);
}

void loop() {
  if (timerTriggered) {
    timerTriggered = false;
    // Затримка фазового кута відносно нульової точки
    delayMicroseconds(delayMicros);
    
    // Формуємо імпульс тривалості 30 мкс для вмикання MOC3021
    digitalWrite(PIN_MOC3021, HIGH);
    delayMicroseconds(30);
    digitalWrite(PIN_MOC3021, LOW);
  }
}

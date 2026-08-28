// ESP32: підрахунок обертів через переривання по фронту
#include <Arduino.h>

const int TACH_PIN = 27;                 // вхід із зовнішньою або внутрішньою підтяжкою
volatile uint32_t tachEdges = 0;         // лічильник фронтів — його чіпає ISR

void IRAM_ATTR onTachEdge() {            // ISR має жити в IRAM на ESP32
  tachEdges++;                           // тільки інкремент — нічого важкого в ISR
}

void setup() {
  Serial.begin(115200);
  pinMode(TACH_PIN, INPUT_PULLUP);       // підтяжка до 3.3 В — тахо це відкритий колектор
  attachInterrupt(digitalPinToInterrupt(TACH_PIN), onTachEdge, RISING);  // фронт
}

uint32_t lastMs = 0;
void loop() {
  uint32_t now = millis();
  if (now - lastMs >= 1000) {            // раз на секунду
    lastMs = now;
    noInterrupts();                      // атомарно зняти й скинути
    uint32_t edges = tachEdges;
    tachEdges = 0;
    interrupts();

    uint32_t rpm = (edges / 2) * 60;     // ÷2 (2 імпульси/оберт) ×60 (у хвилини)
    Serial.printf("TACH: %u імп/с  →  %u об/хв\n", edges, rpm);
  }
}

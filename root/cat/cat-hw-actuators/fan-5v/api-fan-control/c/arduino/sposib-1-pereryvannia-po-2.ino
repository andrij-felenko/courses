// ATmega328 (Uno/Nano): підрахунок обертів через переривання по фронту
#include <Arduino.h>
#include <util/atomic.h>                 // ATOMIC_BLOCK — атомарне зчитування long

const uint8_t TACH_PIN = 2;              // пін 2 або 3 — апаратні переривання ATmega328
volatile uint32_t tachEdges = 0;

void onTachEdge() { tachEdges++; }       // ISR: тільки інкремент

void setup() {
  Serial.begin(115200);
  pinMode(TACH_PIN, INPUT_PULLUP);       // внутрішня підтяжка ~30 кОм до +5 В
  attachInterrupt(digitalPinToInterrupt(TACH_PIN), onTachEdge, RISING);
}

uint32_t lastMs = 0;
void loop() {
  uint32_t now = millis();
  if (now - lastMs >= 1000) {
    lastMs = now;
    uint32_t edges;
    ATOMIC_BLOCK(ATOMIC_RESTORESTATE) {  // читання 4-байтового long без розриву ISR
      edges = tachEdges;
      tachEdges = 0;
    }
    uint32_t rpm = (edges / 2UL) * 60UL; // ÷2 ×60
    Serial.print(F("TACH: ")); Serial.print(edges);
    Serial.print(F(" імп/с  ->  ")); Serial.print(rpm); Serial.println(F(" об/хв"));
  }
}

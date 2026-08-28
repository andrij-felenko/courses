#include "KY040.h"

KY040 knob(2, 3, 4);         // CLK=D2, DT=D3, SW=D4
long  value = 0;

void setup() {
  knob.begin();
  Serial.begin(9600);
  // Надійно: CLK і DT на перериванні (обидва пінии Uno — з апаратним INT).
  attachInterrupt(digitalPinToInterrupt(2), []{ knob.tick(); }, CHANGE);
  attachInterrupt(digitalPinToInterrupt(3), []{ knob.tick(); }, CHANGE);
}

void loop() {
  long now = knob.position();
  if (now != value) { value = now; Serial.println(value); }
  if (knob.pressed()) { knob.setPosition(0); Serial.println("reset"); }
}

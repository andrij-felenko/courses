const uint8_t BLOCKED = HIGH;     // ← що показав калібратор на ЦІЙ платі

// «зубець зайшов у щілину» — це перехід у стан BLOCKED:
//   BLOCKED==HIGH → фронт RISING; BLOCKED==LOW → фронт FALLING.
const int EDGE = (BLOCKED == HIGH) ? RISING : FALLING;

void setup() {
  pinMode(PIN_S, INPUT);
  attachInterrupt(digitalPinToInterrupt(PIN_S), onEdge, EDGE);
}

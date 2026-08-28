// 5161AS через один 74HC595: 3 ноги МК замість 8.
// Виходи регістра Q0..Q7 розведені на сегменти a..g,DP відповідно.
const uint8_t PIN_DATA  = 2;   // DS   (SER)   → пін 14 регістра
const uint8_t PIN_CLOCK = 3;   // SHCP (SRCLK) → пін 11 регістра
const uint8_t PIN_LATCH = 4;   // STCP (RCLK)  → пін 12 регістра

void setup() {
  pinMode(PIN_DATA, OUTPUT);
  pinMode(PIN_CLOCK, OUTPUT);
  pinMode(PIN_LATCH, OUTPUT);
}

void showMask595(uint8_t mask) {
  digitalWrite(PIN_LATCH, LOW);                  // закрити засувку на час засування
  shiftOut(PIN_DATA, PIN_CLOCK, MSBFIRST, mask); // 8 бітів у регістр
  digitalWrite(PIN_LATCH, HIGH);                 // клац → усі 8 виходів разом
}

void loop() {
  static const uint8_t THREE = SA|SB|SC|SD|SG;   // «3»
  showMask595(THREE);
  delay(500);
}

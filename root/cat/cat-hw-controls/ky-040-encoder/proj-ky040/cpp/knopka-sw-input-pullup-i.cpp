const uint8_t PIN_SW = 4;

bool          swPrev      = HIGH;      // попередній стан кнопки
unsigned long swLastMs    = 0;         // час останньої зміни
const unsigned long SW_DEBOUNCE = 30;  // мс глухоти після краю

bool buttonPressed() {                 // повертає true РАЗ на кожен натиск
  bool now = digitalRead(PIN_SW);
  if (now != swPrev && (millis() - swLastMs) > SW_DEBOUNCE) {
    swLastMs = millis();
    swPrev   = now;
    if (now == LOW) return true;       // край «відпущено → натиснуто»
  }
  return false;
}

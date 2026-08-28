const uint8_t PIN_CLK = 2;        // мусить бути пін із перериванням (Uno: D2 або D3)
const uint8_t PIN_DT  = 3;

volatile long counter = 0;

void onEncoderEdge() {
  uint8_t result = processEncoder(digitalRead(PIN_CLK), digitalRead(PIN_DT));
  if      (result == DIR_CW)  counter++;
  else if (result == DIR_CCW) counter--;
}

void setup() {
  pinMode(PIN_CLK, INPUT);
  pinMode(PIN_DT,  INPUT);
  // ловимо ОБИДВА фронти CLK: автомат сам розбереться, брязкіт відсіється таблицею
  attachInterrupt(digitalPinToInterrupt(PIN_CLK), onEncoderEdge, CHANGE);
  Serial.begin(9600);
}

void loop() {
  static long shown = 0;
  noInterrupts();
  long now = counter;             // читаємо volatile-лічильник атомарно
  interrupts();
  if (now != shown) { shown = now; Serial.println(now); }
}

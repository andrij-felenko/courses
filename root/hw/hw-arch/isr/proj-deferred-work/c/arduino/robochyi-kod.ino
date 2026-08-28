volatile bool fired = false;      // спільний прапорець — тому volatile

void IRAM_ATTR onEvent() {        // верхня половина: коротка, у RAM
  fired = true;                   // лише відмітити — і вийти
}

void setup() {
  pinMode(PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN), onEvent, FALLING);
  Serial.begin(115200);
}

void loop() {                     // нижня половина: тут можна все
  if (fired) {
    fired = false;                // скинути ПЕРЕД роботою
    Serial.println("подія!");     // друк, обчислення — будь-що
  }
}

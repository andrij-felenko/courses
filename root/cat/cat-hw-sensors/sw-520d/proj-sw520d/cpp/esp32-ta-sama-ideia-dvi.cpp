// ── варіант під ESP32 ──
const uint8_t PIN_SW = 4;              // на ESP32 годиться майже будь-який GPIO

volatile bool shockFlag = false;

void IRAM_ATTR isrShock() {             // IRAM_ATTR — обробник у швидкій RAM, обов'язково
  shockFlag = true;
}

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_SW), isrShock, FALLING);
  Serial.begin(115200);
}

void loop() {
  if (shockFlag) {
    shockFlag = false;
    Serial.println("ESP32 прокинувся від струсу!");
  }
}

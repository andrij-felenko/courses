const uint8_t PIN_SW  = 2;         // вивід давача (другий — на GND)
const uint8_t PIN_LED = 13;        // вбудований світлодіод

const uint8_t ACTIVE = LOW;        // активний нуль: подія = LOW

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);   // спокій = HIGH, замикання кульки = LOW
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  bool tilted = (digitalRead(PIN_SW) == ACTIVE);   // читаємо «чи замкнено»
  digitalWrite(PIN_LED, tilted ? HIGH : LOW);
}

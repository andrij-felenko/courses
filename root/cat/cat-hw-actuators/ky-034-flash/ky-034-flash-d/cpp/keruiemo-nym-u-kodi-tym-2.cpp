const uint8_t PIN_LED = 8;
const uint8_t PIN_IN  = 2;

void setup() {
  pinMode(PIN_LED, OUTPUT);
  pinMode(PIN_IN, INPUT);
}

void loop() {
  bool active = digitalRead(PIN_IN);        // є сигнал на вході?
  digitalWrite(PIN_LED, active ? HIGH : LOW); // так → живимо вогник; ні → гасимо
}

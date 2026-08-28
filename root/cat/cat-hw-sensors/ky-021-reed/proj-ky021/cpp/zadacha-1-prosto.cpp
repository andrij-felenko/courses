const uint8_t PIN_REED = 2;    // S давача KY-021
const uint8_t PIN_LED  = 13;   // вбудований світлодіод

inline bool magnetPresent(uint8_t pin) { return digitalRead(pin) == LOW; }

void setup() {
  pinMode(PIN_REED, INPUT);    // підтяжка вже на платі — INPUT достатньо
  pinMode(PIN_LED,  OUTPUT);
  Serial.begin(9600);
}

void loop() {
  bool magnet = magnetPresent(PIN_REED);
  digitalWrite(PIN_LED, magnet ? HIGH : LOW);
  Serial.println(magnet ? "магніт поряд" : "магніту немає");
  delay(100);
}

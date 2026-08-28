const uint8_t PIN_REED = 2;      // S давача
const uint8_t PIN_LED  = 13;     // вбудований світлодіод

void setup() {
  pinMode(PIN_REED, INPUT);      // підтяжка вже на платі KY-021
  pinMode(PIN_LED,  OUTPUT);
  Serial.begin(9600);
}

void loop() {
  // LOW = геркон замкнений = магніт поряд;  HIGH = магніту немає
  bool magnet = (digitalRead(PIN_REED) == LOW);
  digitalWrite(PIN_LED, magnet ? HIGH : LOW);
  Serial.println(magnet ? "магніт поряд" : "магніту немає");
  delay(50);
}

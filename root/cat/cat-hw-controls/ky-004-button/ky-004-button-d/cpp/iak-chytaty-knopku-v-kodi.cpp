const uint8_t PIN_BTN = 2;       // сигнал KY-004
const uint8_t PIN_LED = 13;      // вбудований світлодіод

void setup() {
  pinMode(PIN_BTN, INPUT);       // підтяжка вже на платі — INPUT, не INPUT_PULLUP
  pinMode(PIN_LED, OUTPUT);
}

void loop() {
  if (digitalRead(PIN_BTN) == HIGH)   // pull-down: натиск = «1»
    digitalWrite(PIN_LED, HIGH);
  else
    digitalWrite(PIN_LED, LOW);
}

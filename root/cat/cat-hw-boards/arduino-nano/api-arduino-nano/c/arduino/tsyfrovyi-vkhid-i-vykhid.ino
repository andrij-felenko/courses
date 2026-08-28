const uint8_t PIN_BTN = 2;      // кнопка між D2 і GND
const uint8_t PIN_LED = 13;     // вбудований світлодіод

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);   // вільний стан = HIGH, натиск = LOW
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    bool pressed = (digitalRead(PIN_BTN) == LOW);  // натиснуто = замкнуто на GND
    digitalWrite(PIN_LED, pressed ? HIGH : LOW);
}

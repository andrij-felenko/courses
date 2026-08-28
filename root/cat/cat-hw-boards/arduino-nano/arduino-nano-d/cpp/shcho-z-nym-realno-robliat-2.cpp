const uint8_t PIN_BTN = 2;    // кнопка між D2 і GND
const uint8_t PIN_POT = A0;   // середній вивід потенціометра
const uint8_t PIN_LED = 9;    // світлодіод на ШІМ-виводі ~D9

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);  // внутрішня підтяжка: вільний стан = HIGH
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    bool pressed = (digitalRead(PIN_BTN) == LOW);  // натиснуто = замкнуто на GND
    if (pressed) {
        int raw = analogRead(PIN_POT);      // 0..1023 (десятибітний АЦП)
        int duty = raw / 4;                 // звести до 0..255 для ШІМ
        analogWrite(PIN_LED, duty);         // яскравість за положенням ручки
    } else {
        analogWrite(PIN_LED, 0);            // відпущено — згасити
    }
}

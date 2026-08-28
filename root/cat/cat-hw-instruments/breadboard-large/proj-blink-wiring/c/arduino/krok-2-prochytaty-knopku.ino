const uint8_t PIN_LED = 8;
const uint8_t PIN_BTN = 3;   // ніжка IN зі схеми: сюди одна нога кнопки, друга — на «−»

void setup() {
    pinMode(PIN_LED, OUTPUT);
    pinMode(PIN_BTN, INPUT_PULLUP); // вхід + внутрішня підтяжка до «+»
}

void loop() {
    // active-low: натиснуто = LOW. Тож "світло є" ⇔ "на вході LOW".
    if (digitalRead(PIN_BTN) == LOW) {
        digitalWrite(PIN_LED, HIGH); // кнопку тримають → світимо
    } else {
        digitalWrite(PIN_LED, LOW);  // відпущено → гасимо
    }
}

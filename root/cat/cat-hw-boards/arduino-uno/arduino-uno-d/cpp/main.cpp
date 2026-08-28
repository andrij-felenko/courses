const uint8_t PIN_BTN = 2;    // кнопка (між виводом і землею)
const uint8_t PIN_LED = 13;   // вбудований світлодіод

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);  // вхід із вбудованою підтяжкою до 5 В
    pinMode(PIN_LED, OUTPUT);        // вихід на світлодіод
}

void loop() {
    // Кнопка притягує вивід до землі → натиснуто = LOW.
    bool pressed = (digitalRead(PIN_BTN) == LOW);
    digitalWrite(PIN_LED, pressed ? HIGH : LOW);  // тиснемо — світить
}

const uint8_t PIN_BTN = 2;    // кнопка між виводом і землею
const uint8_t PIN_LED = 13;

void setup() {
    pinMode(PIN_BTN, INPUT_PULLUP);  // вхід + вбудована підтяжка до 5 В
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    // Підтяжка тримає «1»; кнопка замикає вивід на землю → натиснуто = LOW.
    bool pressed = (digitalRead(PIN_BTN) == LOW);
    digitalWrite(PIN_LED, pressed ? HIGH : LOW);
}

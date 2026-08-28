const int BTN = 0;   // вивід, до якого підключена кнопка
const int LED = 2;   // вивід зі світлодіодом

void setup() {
    pinMode(BTN, INPUT_PULLUP);   // підтяжка тримає вхід у «1»
    pinMode(LED, OUTPUT);
}

void loop() {
    // кнопка притискає вхід до «0» → натиск = LOW
    bool pressed = (digitalRead(BTN) == LOW);
    digitalWrite(LED, pressed ? HIGH : LOW);
}

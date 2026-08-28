const uint8_t PIN_LED = 13;
unsigned long lastToggle = 0;      // коли перемикали востаннє
const unsigned long PERIOD = 500;  // період блимання, мс
bool ledOn = false;

void setup() {
    pinMode(PIN_LED, OUTPUT);
}

void loop() {
    unsigned long now = millis();
    if (now - lastToggle >= PERIOD) {   // час перемкнути?
        lastToggle = now;
        ledOn = !ledOn;
        digitalWrite(PIN_LED, ledOn ? HIGH : LOW);
    }
    // тут loop() крутиться вільно — можна ще й кнопку читати, і давач опитувати
}

#define LED_PIN  2                   // той самий GPIO2, що й у першому блимачі
#define INTERVAL 200                 // період перемикання, мілісекунди

void setup() {
    pinMode(LED_PIN, OUTPUT);        // ніжка на вихід — як і раніше, один раз
}

void loop() {
    static uint32_t lastToggle = 0;  // мітка часу останнього перемикання
    static bool ledOn = false;       // нинішній стан світлодіода

    uint32_t now = millis();         // «зиркнули на годинник» — один раз за оберт

    if (now - lastToggle >= INTERVAL) {
        lastToggle = now;            // ПЕРЕСУНУЛИ мітку на теперішній час
        ledOn = !ledOn;              // перемкнули логічний стан
        digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
    }

    // сюди керування доходить ЩОРАЗУ — і між перемиканнями теж.
    // тут можна робити будь-що інше: читати кнопку, опитувати давач…
}

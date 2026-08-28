#define LED_PIN     2
#define LED_INT     200              // блимати кожні 200 мс
#define SENSOR_INT  1000             // читати давач кожну 1000 мс

void loop() {
    static uint32_t lastBlink = 0;
    static uint32_t lastSensor = 0;
    static bool ledOn = false;

    uint32_t now = millis();

    // справа 1: блимання світлодіодом
    if (now - lastBlink >= LED_INT) {
        lastBlink = now;
        ledOn = !ledOn;
        digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
    }

    // справа 2: опитування давача — СВОЯ мітка, СВІЙ інтервал
    if (now - lastSensor >= SENSOR_INT) {
        lastSensor = now;
        float t = readTemperature();
        sendTemperature(t);
    }

    // обидві гілки бачать один і той самий `now`;
    // жодна не блокує іншу; loop() пролітає тисячі разів на секунду
}

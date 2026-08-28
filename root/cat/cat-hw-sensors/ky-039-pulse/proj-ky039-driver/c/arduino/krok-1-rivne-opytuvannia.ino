const uint8_t  PULSE     = A0;      // вихід S давача — на аналоговий вхід
const uint32_t SAMPLE_MS = 20;      // період опитування: 20 мс = 50 Гц

uint32_t g_lastSample = 0;

void loop() {
    uint32_t now = millis();
    if (now - g_lastSample >= SAMPLE_MS) {
        g_lastSample += SAMPLE_MS;          // НЕ '= now' — так період не «повзе»
        int raw = analogRead(PULSE);
        process(raw);                        // уся обробка — тут
    }
    // ...цикл вільний робити будь-що інше...
}

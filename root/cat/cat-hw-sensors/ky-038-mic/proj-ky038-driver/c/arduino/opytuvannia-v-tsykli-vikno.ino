unsigned long lastEvent = 0;       // millis() останньої зарахованої події
unsigned long soundCount = 0;      // лічильник гучних подій
bool wasSound = false;             // чи був звук у попередній ітерації
const unsigned long WINDOW_MS = 300;   // мертва зона після події

void loop() {
    bool isSound = (digitalRead(PIN_DO) != idleLevel);   // звук = «не спокій»

    // цікавить саме ФРОНТ: тиша щойно змінилася на звук
    if (isSound && !wasSound) {
        if (millis() - lastEvent > WINDOW_MS) {          // і вікно вже минуло
            lastEvent = millis();
            soundCount++;
            Serial.print("подія #");
            Serial.println(soundCount);
        }
    }
    wasSound = isSound;

    // ... тут головна програма вільна робити будь-що, бо ми не блокуємось ...
}

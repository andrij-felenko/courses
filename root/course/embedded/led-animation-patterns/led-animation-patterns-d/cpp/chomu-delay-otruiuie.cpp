unsigned long lastStep = 0;
bool ledOn = false;

void loop() {
    unsigned long now = millis();
    if (now - lastStep >= 500) {   // настав час кроку?
        lastStep = now;            // запам'ятали момент
        ledOn = !ledOn;
        digitalWrite(LED, ledOn ? HIGH : LOW);
    }
    // ↓ цикл вільний — тут читаємо кнопки, ведемо зв'язок, рухаємо інші ефекти
}

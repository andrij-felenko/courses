uint32_t lastTick = 0;
uint32_t uptimeSec = 0;

void loop() {
    uint32_t now = millis();
    if (now - lastTick >= 1000) {    // раз на секунду
        lastTick += 1000;
        uptimeSec++;

        float t = readTemperature();  // ваш давач: повертає °C як float
        showTemp(t);
        showUptime(uptimeSec);
    }

    // ...тут решта роботи приладу крутиться вільно, дисплей нікого не блокує...
}

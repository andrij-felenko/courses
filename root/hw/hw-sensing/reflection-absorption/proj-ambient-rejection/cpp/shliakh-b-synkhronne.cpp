const int CYCLES   = 8;          // скільки пар «увімк/вимк» накопичити
const int PHASE_US = 300;        // тривалість півперіоду (встановлення + вимір)

// Синхронний детектор: сума «світлих» мінус сума «темних» фаз.
int32_t readSync() {
    int32_t acc = 0;
    for (int i = 0; i < CYCLES; i++) {
        digitalWrite(LED_PIN, HIGH);                 // плюс-фаза
        delayMicroseconds(PHASE_US);
        acc += analogRead(SENSOR_PIN);

        digitalWrite(LED_PIN, LOW);                  // мінус-фаза
        delayMicroseconds(PHASE_US);
        acc -= analogRead(SENSOR_PIN);
    }
    return acc;                                      // рівне тло зникло, відбиток × CYCLES
}

void loopSync() {
    int32_t signal = readSync();
    bool obstacle = signal > 8 * 120;                // поріг масштабується на CYCLES
    Serial.printf("сигнал=%ld  перешкода=%d\n", (long)signal, obstacle);
    delay(20);
}

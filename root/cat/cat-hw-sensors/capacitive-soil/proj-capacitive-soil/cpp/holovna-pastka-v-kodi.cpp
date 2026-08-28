// груба перевірка «живий сигнал», щоб зловити мертвий таймер / обрив
bool sensorSane(int raw, int adcMax) {
    // якщо raw прилип до самого низу чи самого верху шкали — це підозріло:
    // або таймер не гойдається (NE555 на 3.3 В), або обрив/КЗ дроту
    if (raw <= 2)          return false;   // мертвий нуль
    if (raw >= adcMax - 2) return false;   // прилип до стелі
    return true;
}

// у loop() ESP32 (12 біт → adcMax = 4095):
int raw = readAvg(SOIL);
if (!sensorSane(raw, 4095)) {
    Serial.println("щуп мовчить: перевір таймер (NE555 vs TLC555?), живлення, дроти");
    // не приймаємо рішень поливу на битому сигналі!
} else {
    int pct = toPercent(raw);
    // ... нормальна логіка
}

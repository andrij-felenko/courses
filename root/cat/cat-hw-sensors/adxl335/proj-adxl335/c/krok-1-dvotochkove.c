const int PIN[3] = { A0, A1, A2 };   // X, Y, Z
const char* AXIS[3] = { "X", "Y", "Z" };

// Знімає один усереднений код для осі axis і напряму (+1g або -1g),
// коли користувач підтвердив, що поставив плату правильно.
int capturePoint(int axis, const char* dir) {
    Serial.print("Постав вiсь "); Serial.print(AXIS[axis]);
    Serial.print(" строго "); Serial.print(dir);
    Serial.println(" (+1g угору / -1g униз), потiм натисни Enter...");
    while (Serial.available() == 0) { /* чекаємо */ }
    while (Serial.available() > 0) Serial.read();   // з'їсти рядок
    int raw = readAvg(PIN[axis], 64);               // тихий, точний знімок
    Serial.print("  знято: "); Serial.println(raw);
    return raw;
}

void calibrate() {
    for (int ax = 0; ax < 3; ax++) {
        int up   = capturePoint(ax, "вгору");
        int down = capturePoint(ax, "вниз");
        biasRaw[ax]  = (up + down) / 2;
        scaleRaw[ax] = (up - down) / 2.0f;
        Serial.print("Вiсь "); Serial.print(AXIS[ax]);
        Serial.print(": bias="); Serial.print(biasRaw[ax]);
        Serial.print("  scale="); Serial.println(scaleRaw[ax], 1);
    }
    Serial.println("Калiбрування завершено. Впиши цi числа в код як стартовi.");
}

// Детектор поштовху: спрацьовує, коли модуль прискорення
// відбіг від 1g далі за поріг THRESH (у g).
const float THRESH = 0.35f;      // 0.35g понад тяжіння — впевнений струс
bool wasQuiet = true;            // щоб не сипати подіями, поки трясе

void loop() {
    float ax = readG(A0, 0);
    float ay = readG(A1, 1);
    float az = readG(A2, 2);

    float mag = sqrtf(ax*ax + ay*ay + az*az);   // модуль вектора, g
    float dev = fabsf(mag - 1.0f);              // відхилення від спокою

    if (dev > THRESH && wasQuiet) {
        Serial.print("ПОШТОВХ! |a|="); Serial.println(mag, 2);
        wasQuiet = false;                       // подія вже видана
    }
    if (dev < THRESH * 0.5f) {
        wasQuiet = true;                        // затихло — готові до наступного
    }
    delay(10);
}

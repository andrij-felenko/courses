const uint8_t MIC = A0;           // аналоговий вихід KY-037
const unsigned long WINDOW = 50;  // вікно вимірювання, мс

int measureLoudness() {
    unsigned long t0 = millis();
    int hi = 0, lo = 1023;        // межі діапазону АЦП (10-біт)
    while (millis() - t0 < WINDOW) {
        int v = analogRead(MIC);  // миттєва точка хвилі
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;               // РОЗМАХ: тиша ≈ мало, гучно ≈ багато
}

void setup() { Serial.begin(9600); }

void loop() {
    int loud = measureLoudness();
    Serial.println(loud);         // спробуй у тиші й під оплеск — числа різні
}

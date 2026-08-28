const uint8_t MIC = A0;              // AO давача
const unsigned long WINDOW = 50;     // вікно вимірювання, мс

int measurePeakToPeak() {
    unsigned long t0 = millis();
    int hi = 0, lo = 1023;           // межі 10-бітного АЦП Arduino
    while (millis() - t0 < WINDOW) {
        int v = analogRead(MIC);     // миттєва точка хвилі
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;                  // РОЗМАХ: тиша ≈ мало, гучно ≈ багато
}

void setup() { Serial.begin(9600); }

void loop() {
    Serial.println(measurePeakToPeak());   // спробуй у тиші й під оплеск — числа різні
}

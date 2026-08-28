const uint8_t AO = A0;                    // аналоговий вихід давача на A0
const unsigned long WIN = 50;             // вікно вимірювання, мс

int measurePeakToPeak() {
    unsigned long start = millis();
    int lo = 1023, hi = 0;                // межі для 10-бітного АЦП Uno
    while (millis() - start < WIN) {
        int v = analogRead(AO);
        if (v < lo) lo = v;
        if (v > hi) hi = v;
    }
    return hi - lo;                       // розмах у відліках АЦП
}

void setup() {
    Serial.begin(9600);
}

void loop() {
    int amp = measurePeakToPeak();
    Serial.print("розмах: ");
    Serial.println(amp);                  // мале — тихо, велике — гучно
    // поріг гучності ТЕПЕР число: наприклад
    if (amp > 60) Serial.println("  → гучно!");
}

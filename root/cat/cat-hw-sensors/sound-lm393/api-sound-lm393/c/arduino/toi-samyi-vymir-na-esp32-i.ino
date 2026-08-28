const uint8_t AO = 34;                    // ADC1! GPIO34 безпечний при Wi-Fi
const unsigned long WIN = 50;

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);             // 0..4095
    // за замовчуванням послаблення 11 dB → діапазон ~0.15..2.45 В;
    // за потреби ширший діапазон — analogSetPinAttenuation(AO, ADC_11db)
}

int measurePeakToPeak() {
    unsigned long start = millis();
    int lo = 4095, hi = 0;                // межі для 12-бітного АЦП ESP32
    while (millis() - start < WIN) {
        int v = analogRead(AO);
        if (v < lo) lo = v;
        if (v > hi) hi = v;
    }
    return hi - lo;
}

void loop() {
    int amp = measurePeakToPeak();
    Serial.print("розмах: ");
    Serial.println(amp);
    if (amp > 250) Serial.println("  → гучно!");   // поріг під 12-бітну шкалу
}

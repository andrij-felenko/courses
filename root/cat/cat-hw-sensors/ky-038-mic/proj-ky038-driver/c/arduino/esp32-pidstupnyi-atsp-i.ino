const uint8_t PIN_AO = 34;             // ADC1! (GPIO32..39) — щоб дружити з Wi-Fi
const uint16_t WINDOW_MS = 50;
const int ADC_MAX = 4095;              // стеля 12-бітного АЦП ESP32 (0..4095)

int  center  = 2048;                    // де стоїть центр сигналу (контроль країв)
bool clipped = false;

int measureAmplitude() {
    int lo = ADC_MAX, hi = 0;
    unsigned long t0 = millis();
    while (millis() - t0 < WINDOW_MS) {
        int v = analogRead(PIN_AO);     // на ESP32 analogRead повертає 0..4095
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    center  = (hi + lo) / 2;
    clipped = (hi >= ADC_MAX) || (lo <= 0);
    return hi - lo;
}

const char* loudnessLevel(int amp) {    // пороги інші — АЦП 12-бітний, шкала ширша
    if (amp < 40)   return "тиша";
    if (amp < 150)  return "чутно";
    if (amp < 500)  return "голосно";
    return "дуже голосно";
}

void setup() {
    Serial.begin(115200);
    analogSetAttenuation(ADC_11db);     // ОБОВ'ЯЗКОВО: діапазон до ~3.3 В
    // analogReadResolution(12);        // 12 біт — і так усталено, можна лишити
    delay(300);                         // дати мікрофону встановити зсув
}

void loop() {
    int amp = measureAmplitude();
    Serial.printf("розмах = %4d  →  %s", amp, loudnessLevel(amp));
    if (clipped) Serial.printf("   [!] обрізання, центр=%d — постав гвинтик у середину", center);
    Serial.println();
    delay(30);
}

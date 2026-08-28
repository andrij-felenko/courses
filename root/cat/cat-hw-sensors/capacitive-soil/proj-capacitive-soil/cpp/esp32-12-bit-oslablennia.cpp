// ESP32: читати ємнісний щуп правильним аналоговим трактом.
const uint8_t POWER = 25;              // живлення щупа з GPIO25
const uint8_t SOIL  = 34;              // AOUT на GPIO34 — це ADC1 (важливо, див. нижче)

// калібрування для ESP32 — інші числа, бо 12 біт! зняти на самому ESP32:
const int AIR   = 2600;                // сухо (щуп у повітрі)
const int WATER = 1300;                // мокро (щуп у воді)

int readAvg(uint8_t pin, uint8_t n = 16) {
    long sum = 0;
    for (uint8_t i = 0; i < n; i++) { sum += analogRead(pin); delay(2); }
    return (int)(sum / n);
}

int toPercent(int raw) {
    int pct = map(raw, AIR, WATER, 0, 100);
    return constrain(pct, 0, 100);
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);          // 0…4095
    analogSetAttenuation(ADC_11db);    // діапазон входу ≈ 0…3.1 В
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);
}

void loop() {
    digitalWrite(POWER, HIGH);         // ожив генератор
    delay(50);                          // усталення
    int raw = readAvg(SOIL);
    digitalWrite(POWER, LOW);          // знеструмили

    int pct = toPercent(raw);
    Serial.printf("raw=%d  moisture=%d%%\n", raw, pct);
    delay(2000);
}

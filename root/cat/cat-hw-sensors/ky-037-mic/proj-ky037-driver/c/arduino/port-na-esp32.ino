const uint8_t SOUND = 27;          // DO — будь-який GPIO (digitalRead, не АЦП)
const uint8_t MIC   = 34;          // AO — ТІЛЬКИ пін АЦП1 (32..39), щоб пережити Wi-Fi
const uint32_t DEAF_MS = 250;
const uint32_t WINDOW  = 50;

int      g_idle;
bool     g_wasLoud  = false;
uint32_t g_lastClap = 0;
bool     g_lightOn  = false;

inline bool isLoud() { return digitalRead(SOUND) != g_idle; }

int measurePeakToPeak() {
    uint32_t t0 = millis();
    int hi = 0, lo = 4095;         // 12-бітний АЦП ESP32: діапазон 0..4095
    while (millis() - t0 < WINDOW) {
        int v = analogRead(MIC);
        if (v > hi) hi = v;
        if (v < lo) lo = v;
    }
    return hi - lo;
}

void setup() {
    Serial.begin(115200);
    delay(100);
    pinMode(SOUND, INPUT);
    // analogReadResolution(12);   // 12 біт — типово, рядок для явності
    delay(50);
    g_idle = digitalRead(SOUND);
    Serial.printf("Спокій DO = %s\n", g_idle == HIGH ? "HIGH" : "LOW");
    Serial.println("Плесни для перемикання; заодно друкую рівень гучності.");
}

void loop() {
    // --- подія оплеску (фронт + гістерезис) ---
    bool loud = isLoud();
    bool rising = loud && !g_wasLoud;
    g_wasLoud = loud;
    if (rising && millis() - g_lastClap >= DEAF_MS) {
        g_lastClap = millis();
        g_lightOn = !g_lightOn;
        Serial.println(g_lightOn ? "оплеск → УВІМКНЕНО" : "оплеск → вимкнено");
    }

    // --- рівень гучності вікном (нечасто, щоб не забивати монітор) ---
    static uint32_t lastPrint = 0;
    if (millis() - lastPrint >= 300) {
        lastPrint = millis();
        Serial.printf("рівень = %d\n", measurePeakToPeak());
    }
}

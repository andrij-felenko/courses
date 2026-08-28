// ── KY-039 на ESP32: той самий тракт, 12-бітний АЦП, пін ТІЛЬКИ з АЦП1 ──

const uint8_t  PULSE     = 34;      // вихід S — ТІЛЬКИ пін АЦП1 (32..39), щоб пережити Wi-Fi
const uint32_t SAMPLE_MS = 20;      // 50 Гц

float g_baseline = 0;
const float BASE_ALPHA = 0.01;

float g_smooth = 0;
const float SMOOTH_ALPHA = 0.35;

float    g_prev     = 0;
float    g_peak     = 0;
uint32_t g_lastBeat = 0;
const float    MIN_AMP = 30.0;      // ~×4 від Arduino: 12-бітний АЦП дає більший розмах
const uint32_t MIN_GAP = 250;

const uint8_t N = 5;
uint32_t g_intervals[N] = {0};
uint8_t  g_idx = 0;
uint32_t g_prevBeat = 0;
bool     g_haveFirst = false;

uint32_t g_lastSample = 0;

void setup() {
    Serial.begin(115200);
    delay(100);
    // analogReadResolution(12);      // 12 біт — типово; рядок для явності
    Serial.println("KY-039 на ESP32: палець у щілину, нерухомо.");
    g_baseline = analogRead(PULSE);
}

void loop() {
    uint32_t now = millis();
    if (now - g_lastSample < SAMPLE_MS) return;
    g_lastSample += SAMPLE_MS;

    int raw = analogRead(PULSE);                       // 0..4095 на ESP32

    g_baseline += (raw - g_baseline) * BASE_ALPHA;
    float centered = raw - g_baseline;
    g_smooth += (centered - g_smooth) * SMOOTH_ALPHA;

    if (g_smooth > g_peak) g_peak = g_smooth;
    if (g_prev < 0 && g_smooth >= 0) {
        if (g_peak >= MIN_AMP && now - g_lastBeat >= MIN_GAP) {
            g_lastBeat = now;
            reportBeat(now);
        }
        g_peak = 0;
    }
    g_prev = g_smooth;
}

void reportBeat(uint32_t now) {
    if (!g_haveFirst) { g_prevBeat = now; g_haveFirst = true; return; }
    uint32_t beatMs = now - g_prevBeat;
    g_prevBeat = now;
    if (beatMs < 250 || beatMs > 2000) return;

    g_intervals[g_idx] = beatMs;
    g_idx = (g_idx + 1) % N;

    uint32_t sum = 0; uint8_t cnt = 0;
    for (uint8_t i = 0; i < N; i++)
        if (g_intervals[i] > 0) { sum += g_intervals[i]; cnt++; }
    if (cnt == 0) return;
    int bpm = 60000UL / (sum / cnt);

    Serial.printf("♥ BPM ≈ %d\n", bpm);
}

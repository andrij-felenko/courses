// ── KY-039: читання пульсу з аналогового виходу (Arduino, 10-бітний АЦП) ──

const uint8_t  PULSE     = A0;      // вихід S давача
const uint32_t SAMPLE_MS = 20;      // 50 Гц опитування

// -- крок 2: повільний нуль --
float g_baseline = 0;
const float BASE_ALPHA = 0.01;

// -- крок 3: згладжування --
float g_smooth = 0;
const float SMOOTH_ALPHA = 0.35;

// -- крок 4: пошук піків --
float    g_prev     = 0;
float    g_peak     = 0;
uint32_t g_lastBeat = 0;
const float    MIN_AMP = 8.0;       // мін. висота удару (одиниці АЦП; підбери!)
const uint32_t MIN_GAP = 250;       // глухе вікно, мс

// -- крок 5: усереднення BPM --
const uint8_t N = 5;
uint32_t g_intervals[N] = {0};
uint8_t  g_idx = 0;
uint32_t g_prevBeat = 0;
bool     g_haveFirst = false;

uint32_t g_lastSample = 0;

void setup() {
    Serial.begin(9600);
    Serial.println("KY-039: поклади палець у щілину, тримай нерухомо.");
    delay(50);
    g_baseline = analogRead(PULSE);   // старт нуля з першого відліку — швидше усталюється
}

void loop() {
    uint32_t now = millis();
    if (now - g_lastSample < SAMPLE_MS) return;   // ще не час читати
    g_lastSample += SAMPLE_MS;                     // рівна сітка, не «= now»

    // -- крок 1: рівний відлік --
    int raw = analogRead(PULSE);

    // -- крок 2: відняти повільний нуль --
    g_baseline += (raw - g_baseline) * BASE_ALPHA;
    float centered = raw - g_baseline;

    // -- крок 3: згладити --
    g_smooth += (centered - g_smooth) * SMOOTH_ALPHA;

    // -- крок 4: зловити удар --
    if (g_smooth > g_peak) g_peak = g_smooth;
    if (g_prev < 0 && g_smooth >= 0) {
        if (g_peak >= MIN_AMP && now - g_lastBeat >= MIN_GAP) {
            g_lastBeat = now;
            reportBeat(now);            // -- крок 5 усередині --
        }
        g_peak = 0;
    }
    g_prev = g_smooth;
}

// Викликається в мить кожного зарахованого удару.
void reportBeat(uint32_t now) {
    if (!g_haveFirst) { g_prevBeat = now; g_haveFirst = true; return; }
    uint32_t beatMs = now - g_prevBeat;
    g_prevBeat = now;
    if (beatMs < 250 || beatMs > 2000) return;     // явно хибний інтервал — пропускаємо

    g_intervals[g_idx] = beatMs;
    g_idx = (g_idx + 1) % N;

    uint32_t sum = 0; uint8_t cnt = 0;
    for (uint8_t i = 0; i < N; i++)
        if (g_intervals[i] > 0) { sum += g_intervals[i]; cnt++; }
    if (cnt == 0) return;
    int bpm = 60000UL / (sum / cnt);

    Serial.print("♥ удар   BPM ≈ ");
    Serial.println(bpm);
}

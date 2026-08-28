const uint8_t KNOCK = 2;
const uint8_t LED   = 13;             // «замок»: HIGH = відчинено
const unsigned long LOCKOUT = 60;
const unsigned long GAP_END = 800;
const uint8_t MAXN  = 12;
const float   TOL   = 0.25;           // допуск на частку (безрозмірний)

volatile bool knockFlag = false;
void onKnock() { knockFlag = true; }

unsigned long lastKnock = 0;
unsigned long gaps[MAXN];
uint8_t nGaps = 0, nHits = 0;
bool inSeries = false;

// еталон
unsigned long secretGaps[MAXN];
uint8_t secretN = 0;                  // 0 = ще не навчено
bool learning = true;                 // перша серія стане еталоном

// нормувати проміжки в частки від найдовшого; кладе результат у out[]
void normalize(unsigned long *src, uint8_t n, float *out) {
    unsigned long mx = 1;             // не ділимо на 0
    for (uint8_t i = 0; i < n; i++) if (src[i] > mx) mx = src[i];
    for (uint8_t i = 0; i < n; i++) out[i] = (float)src[i] / (float)mx;
}

// чи збігаються два ритми (однакова к-сть проміжків і кожна частка в допуску)
bool rhythmMatches(unsigned long *a, uint8_t na, unsigned long *b, uint8_t nb) {
    if (na != nb) return false;       // різна кількість стуків — точно не те
    if (na == 0)  return false;       // один стук ритму не має
    float fa[MAXN], fb[MAXN];
    normalize(a, na, fa);
    normalize(b, nb, fb);
    for (uint8_t i = 0; i < na; i++)
        if (fabs(fa[i] - fb[i]) > TOL) return false;   // хоч одна пара вибилась
    return true;
}

void setup() {
    pinMode(KNOCK, INPUT_PULLUP);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    attachInterrupt(digitalPinToInterrupt(KNOCK), onKnock, FALLING);
    Serial.println("Відстукайте секретний ритм — він стане ключем.");
}

void loop() {
    unsigned long now = millis();

    if (knockFlag) {
        knockFlag = false;
        if (now - lastKnock > LOCKOUT) {
            if (inSeries && nGaps < MAXN) gaps[nGaps++] = now - lastKnock;
            lastKnock = now;
            nHits++;
            inSeries = true;
        }
    }

    if (inSeries && now - lastKnock > GAP_END) {
        if (learning) {                        // перша серія → запам'ятати як ключ
            for (uint8_t i = 0; i < nGaps; i++) secretGaps[i] = gaps[i];
            secretN  = nGaps;
            learning = false;
            Serial.print("Ключ записано: ");
            Serial.print(nHits);
            Serial.println(" стук(и). Тепер відстукайте його, щоб відчинити.");
        } else {                               // наступні серії → звіряти з ключем
            if (rhythmMatches(gaps, nGaps, secretGaps, secretN)) {
                Serial.println(">>> ВІРНО — відчинено");
                digitalWrite(LED, HIGH);
            } else {
                Serial.println("... не той ритм");
                digitalWrite(LED, LOW);
            }
        }
        nGaps = 0; nHits = 0; inSeries = false;
    }
}

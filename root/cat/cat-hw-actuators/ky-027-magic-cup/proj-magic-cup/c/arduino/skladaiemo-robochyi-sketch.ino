// ── «Магічна чаша» на парі KY-027 (Arduino UNO / Nano, ATmega328P) ──
// S обох плат — на будь-які цифрові ноги; L обох — ТІЛЬКИ на ~ШІМ-ноги.

const uint8_t PIN_S_A = 8;    // вихід вимикача чаші A (цифровий вхід)
const uint8_t PIN_L_A = 9;    // світлодіод чаші A — ШІМ (~D9)
const uint8_t PIN_S_B = 7;    // вихід вимикача чаші B (цифровий вхід)
const uint8_t PIN_L_B = 6;    // світлодіод чаші B — ШІМ (~D6)

// Який рівень на піні S означає «нахилено». Залежить від того, яким боком
// стоїть трубка вимикача: замкнений вимикач тягне S до землі → LOW.
const bool TILTED = LOW;

// ── згасання брязкоту (див. вище) ──
struct Debounced { uint8_t pin; bool stable; bool lastRaw; uint32_t changedAt; };
const uint16_t DEBOUNCE_MS = 25;

void debounceBegin(Debounced &d, uint8_t pin) {
    d.pin = pin; pinMode(pin, INPUT);
    d.stable = digitalRead(pin); d.lastRaw = d.stable; d.changedAt = millis();
}
bool debounceRead(Debounced &d) {
    bool raw = digitalRead(d.pin);
    if (raw != d.lastRaw) { d.lastRaw = raw; d.changedAt = millis(); }
    if (raw != d.stable && (millis() - d.changedAt) >= DEBOUNCE_MS) d.stable = raw;
    return d.stable;
}

// ── спільний рівень переливу ──
uint8_t level = 128;
const uint8_t STEP = 3;
void nudge(int8_t dir) {
    int next = (int)level + dir * STEP;
    if (next < 0) next = 0;
    if (next > 255) next = 255;
    level = (uint8_t)next;
}

Debounced swA, swB;

void setup() {
    debounceBegin(swA, PIN_S_A);
    debounceBegin(swB, PIN_S_B);
    pinMode(PIN_L_A, OUTPUT);
    pinMode(PIN_L_B, OUTPUT);
}

void loop() {
    // 1. Чисті стани обох вимикачів (уже без брязкоту).
    bool tiltA = (debounceRead(swA) == TILTED);
    bool tiltB = (debounceRead(swB) == TILTED);

    // 2. Посунути спільний рівень за нахилом.
    //    A нахилена → до A (+); B нахилена → до B (−); обидві або жодна → стоїмо.
    if (tiltA && !tiltB)       nudge(+1);
    else if (tiltB && !tiltA)  nudge(-1);
    // (tiltA && tiltB) чи (!tiltA && !tiltB) → рівень не рухаємо

    // 3. Вивести рівень на світлодіоди: сума яскравостей завжди 255.
    analogWrite(PIN_L_A, level);
    analogWrite(PIN_L_B, 255 - level);

    delay(4);   // такт ≈4 мс → повний перелив за ~340 мс утримання (STEP=3)
}

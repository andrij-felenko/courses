// ── «Магічна чаша» на парі KY-027, ESP32 (Arduino-ESP32 core 3.x) ──
// Живлення плат — 3V3. ШІМ через LEDC; на ESP32 майже будь-який GPIO — вихід.

const uint8_t PIN_S_A = 4;    // вимикач A — цифровий вхід
const uint8_t PIN_L_A = 18;   // світлодіод A — ШІМ через LEDC
const uint8_t PIN_S_B = 5;    // вимикач B — цифровий вхід
const uint8_t PIN_L_B = 19;   // світлодіод B — ШІМ через LEDC
const bool    TILTED  = LOW;

const uint32_t PWM_FREQ = 5000;   // 5 кГц — оку не видно блимання
const uint8_t  PWM_BITS = 8;      // 8 біт → шпаруватість 0..255, як analogWrite

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
    ledcAttach(PIN_L_A, PWM_FREQ, PWM_BITS);   // ШІМ на ніжці A
    ledcAttach(PIN_L_B, PWM_FREQ, PWM_BITS);   // ШІМ на ніжці B
}

void loop() {
    bool tiltA = (debounceRead(swA) == TILTED);
    bool tiltB = (debounceRead(swB) == TILTED);

    if (tiltA && !tiltB)       nudge(+1);
    else if (tiltB && !tiltA)  nudge(-1);

    ledcWrite(PIN_L_A, level);          // замість analogWrite(...)
    ledcWrite(PIN_L_B, 255 - level);
    delay(4);
}

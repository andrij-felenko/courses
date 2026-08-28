// ── Одна KY-027 як плавний індикатор нахилу (Arduino) ──
const uint8_t PIN_S = 8;      // вихід вимикача (цифровий вхід)
const uint8_t PIN_L = 9;      // світлодіод — ШІМ (~D9)
const bool    TILTED = LOW;   // рівень S, що означає «нахилено»

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

Debounced sw;
uint8_t bright = 0;           // поточна яскравість 0..255
const uint8_t STEP = 4;

void setup() {
    debounceBegin(sw, PIN_S);
    pinMode(PIN_L, OUTPUT);
}

void loop() {
    bool tilted = (debounceRead(sw) == TILTED);
    // Нахилено → повземо до 255; рівно → сповзаємо до 0. Обидва — з упором.
    int next = (int)bright + (tilted ? +STEP : -STEP);
    if (next < 0) next = 0;
    if (next > 255) next = 255;
    bright = (uint8_t)next;

    analogWrite(PIN_L, bright);
    delay(6);                 // темп наростання/згасання
}

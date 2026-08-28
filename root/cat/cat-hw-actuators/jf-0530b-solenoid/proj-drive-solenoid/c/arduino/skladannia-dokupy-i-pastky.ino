// ── Повний драйвер JF-0530B: клацання АБО «втягнути-й-тримати» ──────────────
const uint8_t  SOL_PIN    = 5;      // ШІМ-здатна ніжка → затвор MOSFET / вхід INx ULN2003
const uint16_t PEAK_MS    = 60;     // повний струм на втягування
const uint8_t  HOLD_DUTY  = 90;     // ШІМ-утримання (0..255), добрати під примірник
const uint16_t REARM_MS   = 200;    // мертвий час між клацаннями (дребезг + фізика + тепло)
const uint32_t MAX_ON_MS  = 30000;  // абсолютна стеля утримання (страхувальник від бага)

enum SolState { SOL_IDLE, SOL_PEAK, SOL_HOLD };
SolState solState   = SOL_IDLE;
uint32_t solStart   = 0;            // мить старту поточного вмикання
uint32_t solLastEnd = 0;            // мить кінця останнього вмикання
bool     holdMode   = false;        // true → після PEAK лишаємось у HOLD; false → одиночний клац

void solenoidSetup() {
    pinMode(SOL_PIN, OUTPUT);
    digitalWrite(SOL_PIN, LOW);
}

// одиночне клацання (клац і сам відпустив за PEAK_MS)
bool solenoidPulse() {
    if (solState != SOL_IDLE) return false;
    if (millis() - solLastEnd < REARM_MS) return false;
    digitalWrite(SOL_PIN, HIGH);
    solState = SOL_PEAK; holdMode = false; solStart = millis();
    return true;
}

// втягнути й ТРИМАТИ (повний кидок → знижений ШІМ), поки не покличемо release
bool solenoidHold() {
    if (solState != SOL_IDLE) return false;
    if (millis() - solLastEnd < REARM_MS) return false;
    digitalWrite(SOL_PIN, HIGH);
    solState = SOL_PEAK; holdMode = true; solStart = millis();
    return true;
}

void solenoidRelease() {
    analogWrite(SOL_PIN, 0);
    digitalWrite(SOL_PIN, LOW);
    if (solState != SOL_IDLE) solLastEnd = millis();
    solState = SOL_IDLE;
}

// кликати щоразу в loop()
void solenoidUpdate() {
    switch (solState) {
        case SOL_PEAK:
            if (millis() - solStart >= PEAK_MS) {
                if (holdMode) { analogWrite(SOL_PIN, HOLD_DUTY); solState = SOL_HOLD; }
                else          { solenoidRelease(); }        // одиночний клац завершено
            }
            break;
        case SOL_HOLD:
            if (millis() - solStart >= MAX_ON_MS)           // стеля: тримають задовго — рубаємо
                solenoidRelease();
            break;
        default: break;
    }
}

const int TRIG_PIN = 5, ECHO_PIN = 18;
const uint32_t ECHO_TIMEOUT_US = 30000;   // ~5 м межі дальності
RangeFilter rf;

// Один відлік: відстань за часом луни + сила (тут — проксі; реальну дає давач).
Sample readRanger() {
    Sample s; s.t_ms = millis();
    digitalWrite(TRIG_PIN, LOW);  delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    uint32_t us = pulseIn(ECHO_PIN, HIGH, ECHO_TIMEOUT_US);
    if (us == 0) { s.valid = false; s.dist_mm = 0; s.strength = 0; return s; }
    s.dist_mm  = (uint16_t)(us * 343UL / 2000UL);   // мкс → мм за c = 343 м/с, шлях туди-й-назад
    s.strength = readEchoStrength();                // АЦП піка луни / signal-rate ToF-давача
    s.valid    = true;
    return s;
}

void setup() {
    Serial.begin(115200);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    rf_init(&rf, 1500, 200, 800);   // зближення ≤1.5 м/с; підлога/стеля сили — за калібруванням
}

void loop() {
    RangeResult r = rf_update(&rf, readRanger());
    switch (r.status) {
        case RF_FRESH:
            // r.med_mm → керування (край), r.mm → показ (гладко)
            Serial.printf("d=%u мм | гладко %u | довіра %.2f\n", r.med_mm, r.mm, r.conf);
            break;
        case RF_HELD:
            Serial.printf("тримаю %u мм (пропуск/викид)\n", r.mm);
            break;
        case RF_LOST:
            Serial.println("ВІДСТАНЬ НЕВІДОМА -> стоп/обережно");
            break;
    }
    delay(20);   // ~50 Гц; сам крок входить у ворота через мітку часу відліку
}

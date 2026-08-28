const uint8_t TILT  = 2;
const uint8_t BUZZ  = 8;               // зумер / реле (окрема нога, не S!)
const unsigned long SETTLE   = 30;     // мс: гасіння брязкоту
const unsigned long ALARM_MS = 800;    // мс: скільки НАХИЛ має триматися до тривоги

bool lastRaw = HIGH, stableState = HIGH;
unsigned long lastChangeMs = 0;
unsigned long tiltedSinceMs = 0;       // коли розпочався ПОТОЧНИЙ усталений нахил
bool alarmOn = false;

void setup() {
    pinMode(TILT, INPUT_PULLUP);
    pinMode(BUZZ, OUTPUT);
    Serial.begin(9600);
    lastRaw = stableState = digitalRead(TILT);
}

void loop() {
    // 1) гасіння брязкоту → чистий stableState
    bool raw = digitalRead(TILT);
    if (raw != lastRaw) { lastChangeMs = millis(); lastRaw = raw; }
    if ((millis() - lastChangeMs) > SETTLE && raw != stableState) {
        stableState = raw;
        if (stableState == LOW) tiltedSinceMs = millis();  // нахил тільки-но став усталеним
    }

    // 2) тривога — лише якщо усталений нахил тримається довше за ALARM_MS
    bool longTilt = (stableState == LOW) &&
                    ((millis() - tiltedSinceMs) > ALARM_MS);
    if (longTilt && !alarmOn) {
        alarmOn = true;
        digitalWrite(BUZZ, HIGH);
        Serial.println("ТРИВОГА: пристрій лежить набік!");
    } else if (!longTilt && alarmOn && stableState == HIGH) {
        alarmOn = false;                                   // підняли назад — знімаємо тривогу
        digitalWrite(BUZZ, LOW);
        Serial.println("норма: пристрій вирівняно");
    }
}

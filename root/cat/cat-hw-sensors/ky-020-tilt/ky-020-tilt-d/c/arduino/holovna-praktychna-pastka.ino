const uint8_t TILT = 2;
const unsigned long SETTLE = 30;   // мс: скільки рівень має протриматися

bool  stable   = HIGH;             // усталений стан (HIGH = рівно)
bool  lastRaw  = HIGH;             // попереднє СИРЕ читання
unsigned long lastChange = 0;      // коли сире читання востаннє смикнулось
unsigned long tilts = 0;           // лічильник справжніх нахилів

void setup() {
    pinMode(TILT, INPUT);
    Serial.begin(9600);
}

void loop() {
    bool raw = digitalRead(TILT);          // сире, брязкуче
    if (raw != lastRaw) {                  // рівень щойно смикнувся —
        lastChange = millis();             // перезапускаємо відлік «тиші»
        lastRaw = raw;
    }
    // рівень протримався сталим довше за SETTLE → приймаємо його
    if (millis() - lastChange > SETTLE && raw != stable) {
        stable = raw;
        if (stable == LOW) {               // перейшли саме в «нахил»
            tilts++;
            Serial.print("нахилів: ");
            Serial.println(tilts);
        }
    }
}

const uint8_t TILT  = 2;
const unsigned long SETTLE = 30;   // мс: скільки рівень має протриматися, щоб повірити

bool lastRaw       = HIGH;         // попереднє СИРЕ читання (HIGH = рівно)
bool stableState   = HIGH;         // усталений, «прийнятий» стан
unsigned long lastChangeMs = 0;    // коли сире читання востаннє смикнулось
unsigned long tiltCount = 0;       // лічильник СПРАВЖНІХ нахилів

void setup() {
    pinMode(TILT, INPUT_PULLUP);
    Serial.begin(9600);
    lastRaw = stableState = digitalRead(TILT);
}

// Повертає true рівно в ту ітерацію, коли усталений стан перейшов у «нахил».
bool tiltEdge() {
    bool raw = digitalRead(TILT);
    if (raw != lastRaw) {              // сире читання щойно смикнулось —
        lastChangeMs = millis();       // перезапускаємо відлік «тиші»
        lastRaw = raw;
    }
    // рівень протримався сталим довше за SETTLE і відрізняється від прийнятого?
    if ((millis() - lastChangeMs) > SETTLE && raw != stableState) {
        stableState = raw;             // приймаємо новий усталений стан
        return (stableState == LOW);   // true, лише якщо перейшли САМЕ в нахил
    }
    return false;
}

void loop() {
    if (tiltEdge()) {
        tiltCount++;
        Serial.print("нахилів: ");
        Serial.println(tiltCount);
    }
    // тут може крутитися решта програми — tiltEdge() нічого не блокує
}

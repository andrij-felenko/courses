// --- Ручний декодер NEC на Arduino / AVR ---
// OUT приймача → вивід 2 (на Uno/Nano вивід 2 і 3 уміють зовнішні переривання)
const uint8_t PIN_IR = 2;

volatile uint32_t gaps[70];        // кільце тривалостей між спадами (кадр = 1 преамбула + 32 біти ≈ 33 спади)
volatile uint8_t  head = 0, tail = 0;
volatile uint32_t lastFall = 0;

// ISR: коротко! зняти час, покласти інтервал у кільце, вийти
void onFall() {
    uint32_t now = micros();
    uint32_t gap = now - lastFall;
    lastFall = now;
    uint8_t nextHead = (head + 1) % 70;
    if (nextHead != tail) {        // не переповнити кільце
        gaps[head] = gap;
        head = nextHead;
    }
}

// стани автомата
enum { IDLE, DATA } state = IDLE;
uint32_t bits = 0;                 // сюди складаємо 32 біти (молодшим уперед)
uint8_t  nbits = 0;
uint32_t lastValue = 0;            // останній повний кадр (для повтору)

void setup() {
    Serial.begin(115200);
    pinMode(PIN_IR, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_IR), onFall, FALLING);
    Serial.println(F("Ручний NEC-декодер готовий."));
}

void loop() {
    // забрати з кільця всі нові інтервали (poll-and-drain)
    while (tail != head) {
        uint32_t gap = gaps[tail];
        tail = (tail + 1) % 70;
        handleGap(gap);
    }
}

// одна порція логіки автомата на один інтервал між спадами
void handleGap(uint32_t gap) {
    // допуск ±30% — дешеві пульти сильно «пливуть» за таймінгом
    if (within(gap, 13500)) {          // преамбула повного кадру
        state = DATA; bits = 0; nbits = 0;
        return;
    }
    if (within(gap, 11250)) {          // код-повтор: кнопку тримають
        Serial.print(F("ПОВТОР (тримають): addr=0x"));
        Serial.print((lastValue) & 0xFF, HEX);
        Serial.print(F(" cmd=0x"));
        Serial.println((lastValue >> 16) & 0xFF, HEX);
        state = IDLE;
        return;
    }
    if (state == DATA) {
        uint8_t bit = (gap > 1200) ? 1 : 0;    // поріг посередині між ~1.1 і ~2.2 мс
        bits |= ((uint32_t)bit << nbits);       // молодший біт уперед
        nbits++;
        if (nbits == 32) {
            decodeFrame(bits);
            state = IDLE;
        }
    }
}

bool within(uint32_t v, uint32_t target) {
    return v > (uint32_t)(target * 0.7) && v < (uint32_t)(target * 1.3);
}

void decodeFrame(uint32_t raw) {
    uint8_t addr  =  raw        & 0xFF;
    uint8_t addrN = (raw >> 8)  & 0xFF;
    uint8_t cmd   = (raw >> 16) & 0xFF;
    uint8_t cmdN  = (raw >> 24) & 0xFF;

    // перевірка інверсних байтів (для звичайного NEC)
    bool ok = ((uint8_t)(addr ^ addrN) == 0xFF) && ((uint8_t)(cmd ^ cmdN) == 0xFF);
    lastValue = raw;

    Serial.print(F("addr=0x")); Serial.print(addr, HEX);
    Serial.print(F(" cmd=0x"));  Serial.print(cmd, HEX);
    Serial.println(ok ? F("  [XOR ok]") : F("  [XOR BAD або extended-NEC]"));
}

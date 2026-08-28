const uint8_t PIN_PIR   = 2;      // OUT давача
const uint8_t PIN_RELAY = 8;      // вхід релейного модуля (активний "1")

const uint32_t WARMUP_MS   = 60000UL;  // прогрів: перша хвилина — не вірити
const uint32_t DEBOUNCE_MS = 40;       // скільки тримати рівень, щоб повірити
const uint32_t HOLD_MS     = 5000UL;   // власний "хвіст" після зникнення руху

uint32_t t_boot;          // мить старту (для гасіння прогріву)
uint32_t t_last_motion;   // коли востаннє бачили надійну "1"
uint32_t t_edge;          // коли рівень востаннє змінився (для дебаунсу)
int      raw_prev;        // попередній сирий рівень OUT
int      stable;          // згладжений рівень, якому вже віримо
bool     light_on;        // поточний стан світла

void setup() {
    pinMode(PIN_PIR, INPUT);      // OUT сам штовхає рівень — підтяжка не потрібна
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW); // почати з вимкненого світла
    Serial.begin(9600);

    t_boot = millis();
    raw_prev = digitalRead(PIN_PIR);
    stable   = 0;
    t_edge   = t_boot;
    light_on = false;
}

void loop() {
    uint32_t now = millis();

    // --- Шар 1: гасіння прогріву. Першу хвилину виходу не віримо. ---
    if (now - t_boot < WARMUP_MS) {
        digitalWrite(PIN_RELAY, LOW);
        return;                   // нічого не робимо, даємо давачу вгамуватися
    }

    // --- Шар 2: дебаунс. Рівень мусить протриматися DEBOUNCE_MS. ---
    int raw = digitalRead(PIN_PIR);
    if (raw != raw_prev) {        // рівень щойно смикнувся — перезапустити відлік
        t_edge = now;
        raw_prev = raw;
    }
    if (now - t_edge >= DEBOUNCE_MS) {   // протримався досить довго — вірити
        stable = raw;
    }

    if (stable == HIGH) {
        t_last_motion = now;      // бачимо надійний рух — оновити мітку
    }

    // --- Шар 3: рішення про світло з власним "хвостом" HOLD_MS. ---
    bool want_on = (now - t_last_motion < HOLD_MS);
    if (want_on != light_on) {
        light_on = want_on;
        digitalWrite(PIN_RELAY, light_on ? HIGH : LOW);
        Serial.println(light_on ? "світло УВІМК" : "світло вимк");
    }
}

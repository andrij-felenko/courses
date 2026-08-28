const uint8_t DO_PIN  = 2;
const uint8_t LOAD    = 13;         // реле/вентилятор (тут — вбудований LED)

const unsigned long LOCKOUT_MS = 2000;   // «карантин» після зміни стану

int  restLevel = HIGH;
bool state     = false;              // поточний стан термостата: true = «гаряче»
unsigned long lastFlip = 0;          // коли востаннє перемкнулися

int readRestLevel() {
    int highs = 0; const int N = 15;
    for (int i = 0; i < N; i++) { if (digitalRead(DO_PIN) == HIGH) highs++; delay(5); }
    return (highs > N / 2) ? HIGH : LOW;
}

bool rawHot() { return digitalRead(DO_PIN) != restLevel; }

void setup() {
    pinMode(DO_PIN, INPUT);
    pinMode(LOAD, OUTPUT);
    Serial.begin(9600);
    delay(300);
    restLevel = readRestLevel();
    state = rawHot();                          // початковий стан — від реальності
    digitalWrite(LOAD, state ? HIGH : LOW);
    lastFlip = millis();
}

void loop() {
    bool hot = rawHot();

    // Приймаємо зміну стану, ЛИШЕ якщо минув карантин від минулого перемикання.
    if (hot != state && (millis() - lastFlip) >= LOCKOUT_MS) {
        state = hot;
        lastFlip = millis();
        digitalWrite(LOAD, state ? HIGH : LOW);
        Serial.println(state ? ">> увімкнув навантаження (ГАРЯЧЕ)"
                             : "<< вимкнув навантаження (норма)");
    }

    // ... тут цикл вільний робити будь-що інше, він не заблокований ...
}

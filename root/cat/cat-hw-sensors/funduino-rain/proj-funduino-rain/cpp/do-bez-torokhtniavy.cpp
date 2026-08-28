const uint8_t RAIN = 2;             // цифровий вихід DO давача
const uint8_t LED  = 13;            // вбудований світлодіод плати
const unsigned long SETTLE = 400;   // скільки стан має протриматися, мс

bool raining   = false;             // поточний ПІДТВЕРДЖЕНИЙ стан
bool candidate = false;             // стан, який щойно побачили на нозі
unsigned long changedAt = 0;        // коли кандидат уперше з'явився

void setup() {
    pinMode(RAIN, INPUT);           // push-pull-вихід LM358 → підтяжка не потрібна
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() {
    // DO: 0 = дощ, 1 = сухо. Робимо булеве «зараз дощить?»
    bool now = (digitalRead(RAIN) == LOW);

    // показ змінився — запам'ятовуємо як кандидата й засікаємо час
    if (now != candidate) {
        candidate = now;
        changedAt = millis();
    }

    // приймаємо новий стан, ЛИШЕ коли кандидат протримався SETTLE мс —
    // це програмний гістерезис проти торохтняви межі
    if (candidate != raining && millis() - changedAt > SETTLE) {
        raining = candidate;
        digitalWrite(LED, raining);
        Serial.println(raining ? "дощ почався" : "дощ скінчився");
    }
    // програма НЕ спить: сюди можна вставити будь-яку іншу роботу
}

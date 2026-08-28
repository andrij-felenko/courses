const uint8_t  LASER      = 4;     // KY-008 S
const uint8_t  LDR        = A0;    // KY-018 -> аналоговий вхід
const uint32_t STABLE_MS  = 8;     // скільки стан має протриматись, щоб повірити

int  baseLight = 0;                // опорна освітленість «цілого» бар'єра
int  loThresh  = 0;                // нижче -> точно перекрито
int  hiThresh  = 0;                // вище  -> точно цілий

bool broken       = false;         // поточний підтверджений стан
bool candidate    = false;         // куди стан «хоче» перейти
uint32_t sinceChange = 0;          // відколи кандидат тримається

void calibrate() {
    // промінь уже горить; беремо середнє з кількох відліків як опору
    long sum = 0;
    const int N = 32;
    for (int i = 0; i < N; i++) { sum += analogRead(LDR); delay(3); }
    baseLight = sum / N;

    // пороги: перекрито, якщо світло впало >25%; повернення — при >85% опори
    loThresh = (baseLight * 3) / 4;    // 75% опори
    hiThresh = (baseLight * 85) / 100; // 85% опори (вище -> знову цілий)
}

void setup() {
    pinMode(LASER, OUTPUT);
    digitalWrite(LASER, HIGH);   // промінь тримає бар'єр
    Serial.begin(115200);
    delay(50);                   // дати променю й давачу вгамуватися
    calibrate();
    Serial.print("опора="); Serial.print(baseLight);
    Serial.print("  lo=");   Serial.print(loThresh);
    Serial.print("  hi=");   Serial.println(hiThresh);
}

void loop() {
    int light = analogRead(LDR);

    // 1) гістерезис: куди сигнал показує ПРЯМО ЗАРАЗ
    bool wantBroken = broken;                 // за замовчуванням не міняємо
    if (light < loThresh) wantBroken = true;  // впало глибоко -> перекрито
    if (light > hiThresh) wantBroken = false; // піднялось -> цілий
    // між lo і hi (мертва зона) стан лишається як був

    // 2) антидребезг: віримо новому стану, лише коли він протримався STABLE_MS
    uint32_t now = millis();
    if (wantBroken != candidate) {            // кандидат щойно змінився
        candidate   = wantBroken;
        sinceChange = now;
    } else if (candidate != broken && now - sinceChange >= STABLE_MS) {
        broken = candidate;                   // підтверджуємо перехід
        Serial.println(broken ? "ПЕРЕТИН!" : "бар'єр цілий");
    }
}

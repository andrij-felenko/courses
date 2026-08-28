const uint8_t SOUND = 3;           // DO давача
const uint8_t LED   = 13;          // світло / реле, яким керуємо

const uint32_t DEAF_MS = 250;      // «глухе» вікно після оплеску, мс (гістерезис у часі)

int      g_idle;                   // рівень спокою DO (автовизначення)
bool     g_wasLoud   = false;      // чи було «гучно» на попередньому оберті (для фронту)
uint32_t g_lastClap  = 0;          // час останнього ЗАРАХОВАНОГО оплеску
bool     g_lightOn   = false;      // поточний стан світла

inline bool isLoud() { return digitalRead(SOUND) != g_idle; }

void setup() {
    pinMode(SOUND, INPUT);
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
    delay(50);
    g_idle = digitalRead(SOUND);   // тиша = спокій цієї плати
    Serial.print("Спокій DO = ");
    Serial.println(g_idle == HIGH ? "HIGH" : "LOW");
    Serial.println("Плесни, щоб перемкнути світло.");
}

void loop() {
    bool loud = isLoud();

    // Фронт «тихо → гучно»: цього оберту гучно, а минулого було тихо.
    bool rising = loud && !g_wasLoud;
    g_wasLoud = loud;

    if (rising) {
        // Зараховуємо оплеск, лише якщо минуло «глухе» вікно від попереднього.
        if (millis() - g_lastClap >= DEAF_MS) {
            g_lastClap = millis();
            g_lightOn = !g_lightOn;              // ПЕРЕКИДАЄМО стан
            digitalWrite(LED, g_lightOn);
            Serial.println(g_lightOn ? "оплеск → УВІМКНЕНО" : "оплеск → вимкнено");
        }
        // інакше це хвіст/відлуння того самого оплеску — мовчки ігноруємо
    }
    // ...головний цикл вільний робити будь-що інше...
}

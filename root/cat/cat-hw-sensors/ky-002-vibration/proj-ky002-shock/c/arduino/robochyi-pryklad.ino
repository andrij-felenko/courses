#include <Arduino.h>

const uint8_t PIN_SHOCK = 2;    // S давача — на ногу з апаратним перериванням (D2)
const uint8_t PIN_LED   = 13;   // вбудований світлодіод

const uint32_t DEBOUNCE_MS = 60;   // вікно придушення брязкоту: одна подія на струс

// --- те, що ISR передає головному циклу; усе volatile ---
volatile uint32_t g_lastEdgeMs = 0;   // час останнього фронту (для головного циклу)
volatile uint32_t g_edgeCount  = 0;   // скільки фронтів прилетіло всього (сирих)
volatile bool     g_newEdge    = false;

int      g_idleLevel;      // рівень спокою, визначений на старті (HIGH або LOW)
uint32_t g_shocks   = 0;   // зараховані струси (після придушення брязкоту)
uint32_t g_lastShock = 0;  // час останнього ЗАРАХОВАНОГО струсу

// ISR: якнайкоротша. Жодного Serial, digitalRead-логіки чи обчислень.
void onShockEdge() {
    g_edgeCount++;
    g_lastEdgeMs = millis();   // millis() в ISR читати можна: лічильник не зупинений
    g_newEdge = true;
}

void setup() {
    pinMode(PIN_SHOCK, INPUT_PULLUP);   // підтяжка вгору — безпечний типовий випадок
    pinMode(PIN_LED, OUTPUT);
    Serial.begin(9600);
    delay(50);                          // дати входу усталитися перед зчитуванням спокою

    // --- Автовизначення полярності: що плата тримає у спокої? ---
    g_idleLevel = digitalRead(PIN_SHOCK);
    Serial.print("Рівень спокою = ");
    Serial.println(g_idleLevel == HIGH ? "HIGH (pull-up варіант)"
                                       : "LOW (pull-down варіант)");

    // Реагуємо на фронт, що ВІДХОДИТЬ від спокою:
    //   спокій HIGH → струс тягне вниз → ловимо FALLING;
    //   спокій LOW  → струс тягне вгору → ловимо RISING.
    int mode = (g_idleLevel == HIGH) ? FALLING : RISING;
    attachInterrupt(digitalPinToInterrupt(PIN_SHOCK), onShockEdge, mode);

    Serial.println("Готовий. Струсіть давач.");
}

void loop() {
    // Забрати з ISR свіжий фронт (коротко вимикаємо переривання, щоб читати цілісно).
    bool newEdge;
    uint32_t lastEdge;
    noInterrupts();
    newEdge  = g_newEdge;
    lastEdge = g_lastEdgeMs;
    g_newEdge = false;
    interrupts();

    if (newEdge) {
        // Придушення брязкоту без delay: зараховуємо струс,
        // лише якщо від попереднього зарахованого минуло DEBOUNCE_MS.
        if (lastEdge - g_lastShock >= DEBOUNCE_MS) {
            g_lastShock = lastEdge;
            g_shocks++;
            Serial.print("СТРУС #");
            Serial.println(g_shocks);
            digitalWrite(PIN_LED, HIGH);   // коротко засвітити (гасимо нижче, без delay)
        }
        // якщо не дотягло до вікна — це відскок пружини, мовчки ігноруємо
    }

    // Погасити світлодіод через 30 мс після засвічення — теж без delay.
    if (digitalRead(PIN_LED) == HIGH && millis() - g_lastShock >= 30) {
        digitalWrite(PIN_LED, LOW);
    }

    // ...тут головний цикл вільний робити будь-що інше: дисплей, інші давачі...
}

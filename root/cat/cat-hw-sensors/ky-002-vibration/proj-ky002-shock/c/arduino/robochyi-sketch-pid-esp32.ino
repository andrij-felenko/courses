const uint8_t PIN_SHOCK = 4;        // S давача (звичайна GPIO з підтяжкою)
const uint32_t DEBOUNCE_MS = 60;

volatile uint32_t g_edgeCount = 0;      // сирі фронти (нарощує ISR)
volatile uint32_t g_lastEdgeMs = 0;

uint32_t g_shocks = 0;
uint32_t g_lastShock = 0;
uint32_t g_seen = 0;                     // скільки фронтів головний цикл уже бачив

// ISR обов'язково в IRAM і максимально коротка.
void IRAM_ATTR onShockEdge() {
    g_edgeCount++;
    g_lastEdgeMs = millis();
}

void setup() {
    Serial.begin(115200);
    delay(100);
    pinMode(PIN_SHOCK, INPUT_PULLUP);
    delay(50);

    int idle = digitalRead(PIN_SHOCK);
    Serial.printf("Рівень спокою = %s\n",
                  idle == HIGH ? "HIGH (pull-up)" : "LOW (pull-down)");

    // Той самий принцип автополярності, що й на Arduino:
    int mode = (idle == HIGH) ? FALLING : RISING;
    attachInterrupt(digitalPinToInterrupt(PIN_SHOCK), onShockEdge, mode);

    Serial.println("Готовий. Струсіть давач.");
}

void loop() {
    // Читання uint32_t на 32-бітному ESP32 атомарне — захист не потрібен.
    uint32_t edges   = g_edgeCount;
    uint32_t lastEdge = g_lastEdgeMs;

    if (edges != g_seen) {          // прилетіли нові фронти від ISR
        g_seen = edges;
        if (lastEdge - g_lastShock >= DEBOUNCE_MS) {   // придушення брязкоту
            g_lastShock = lastEdge;
            g_shocks++;
            Serial.printf("СТРУС #%u\n", g_shocks);
        }
    }
    // головний цикл вільний: Wi-Fi, дисплей, інші давачі...
}

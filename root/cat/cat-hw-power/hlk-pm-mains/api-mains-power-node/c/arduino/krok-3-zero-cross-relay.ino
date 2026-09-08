/* ============================================================================
   krok-3-zero-cross-relay.ino — Arduino: синхронна комутація в нулі фази
   ========================================================================== */

const uint8_t PIN_ZERO_CROSS = 2;
const uint8_t PIN_RELAY      = 7;

const unsigned long RELAY_PULLIN_LAG_US = 6000; // 6 мс на рух якоря реле
const unsigned long HALF_CYCLE_US       = 10000; // 10 мс (50 Гц)

volatile bool g_switchScheduled = false;
volatile bool g_targetState     = false;

void IRAM_ATTR onZeroCross() {
    if (g_switchScheduled) {
        // Щоб якір торкнувся контакту в момент нуля фази,
        // подаємо струм на котушку із затримкою 4 мс після поточного нуля
        delayMicroseconds(HALF_CYCLE_US - RELAY_PULLIN_LAG_US);
        digitalWrite(PIN_RELAY, g_targetState ? HIGH : LOW);
        g_switchScheduled = false;
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_ZERO_CROSS, INPUT_PULLUP);
    pinMode(PIN_RELAY, OUTPUT);
    digitalWrite(PIN_RELAY, LOW);

    attachInterrupt(digitalPinToInterrupt(PIN_ZERO_CROSS), onZeroCross, FALLING);
    Serial.println(F("Zero-Cross Relay Synchronizer готовий"));
}

void switchRelaySynchronously(bool state) {
    g_targetState = state;
    g_switchScheduled = true;
}

void loop() {
    if (Serial.available() > 0) {
        char c = Serial.read();
        if (c == '1') switchRelaySynchronously(true);
        if (c == '0') switchRelaySynchronously(false);
    }
}

/* ============================================================================
   krok-3-load-switch-sequencing.ino — Поетапне підключення навантаження
   ========================================================================== */

const uint8_t PIN_PERIPH_1_EN = 6;  // Сенсори й логіка (етап 1)
const uint8_t PIN_PERIPH_2_EN = 7;  // Силові модулі: радіо / реле / серво (етап 2)
const uint8_t PIN_STATUS_LED  = 13;

enum BootStage {
    STAGE_INIT_POWER,
    STAGE_ENABLE_SENSORS,
    STAGE_ENABLE_HEAVY_LOAD,
    STAGE_SYSTEM_READY
};

static BootStage s_stage = STAGE_INIT_POWER;
static unsigned long s_stage_timer_ms = 0;

void setup() {
    Serial.begin(115200);

    digitalWrite(PIN_PERIPH_1_EN, HIGH); // P-MOSFET вимкнено
    digitalWrite(PIN_PERIPH_2_EN, HIGH);
    pinMode(PIN_PERIPH_1_EN, OUTPUT);
    pinMode(PIN_PERIPH_2_EN, OUTPUT);
    pinMode(PIN_STATUS_LED, OUTPUT);

    s_stage_timer_ms = millis();
    Serial.println(F("[Power Sequence] Початок двоетапного запуску живлення..."));
}

void loop() {
    unsigned long now = millis();

    switch (s_stage) {
        case STAGE_INIT_POWER:
            if (now - s_stage_timer_ms >= 150) {
                s_stage = STAGE_ENABLE_SENSORS;
                s_stage_timer_ms = now;
                digitalWrite(PIN_PERIPH_1_EN, LOW); // Вмикаємо сенсори
                Serial.println(F("[Stage 1] Первинні сенсори підключено до шини"));
            }
            break;

        case STAGE_ENABLE_SENSORS:
            if (now - s_stage_timer_ms >= 80) {
                s_stage = STAGE_ENABLE_HEAVY_LOAD;
                s_stage_timer_ms = now;
                digitalWrite(PIN_PERIPH_2_EN, LOW); // Вмикаємо силове навантаження
                Serial.println(F("[Stage 2] Силове навантаження підключено (радіо/серво)"));
            }
            break;

        case STAGE_ENABLE_HEAVY_LOAD:
            if (now - s_stage_timer_ms >= 50) {
                s_stage = STAGE_SYSTEM_READY;
                digitalWrite(PIN_STATUS_LED, HIGH);
                Serial.println(F("[Ready] Усі шини активні, живлення стабільне!"));
            }
            break;

        case STAGE_SYSTEM_READY:
            break;
    }
}

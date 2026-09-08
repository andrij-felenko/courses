/* ============================================================================
   krok-2-brownout-supervisor.ino — Неблокувальний супервізор Brown-out
   ========================================================================== */

const uint8_t  PIN_RAIL_ADC     = A0;
const uint8_t  PIN_LOAD_GATE    = 7;      // Керування P-MOSFET (LOW = ON)
const uint8_t  PIN_ALERT_LED    = 13;

const float    DIVIDER_RATIO    = 3.00f;
const float    ADC_VREF_V       = 5.00f;
const uint16_t ADC_MAX_COUNTS   = 1023;

const uint16_t V_WARN_TRIP_MV   = 4650;   // Поріг тривоги просідання (4.65 В)
const uint16_t V_WARN_CLEAR_MV  = 4800;   // Поріг повернення до норми (4.80 В)

enum RailState {
    RAIL_OK,
    RAIL_WARNING
};

static RailState s_rail_state = RAIL_OK;
static float s_smoothed_mv = 5000.0f;

uint16_t getVoltageMV() {
    uint16_t raw = analogRead(PIN_RAIL_ADC);
    float v_pin = (raw * ADC_VREF_V) / (float)ADC_MAX_COUNTS;
    float v_rail = v_pin * DIVIDER_RATIO * 1000.0f;
    s_smoothed_mv = 0.25f * v_rail + 0.75f * s_smoothed_mv;
    return (uint16_t)s_smoothed_mv;
}

void emergencyShedLoad() {
    digitalWrite(PIN_LOAD_GATE, HIGH);  // Розмикаємо P-MOSFET (відключаємо споживач)
    digitalWrite(PIN_ALERT_LED, HIGH);
    Serial.println(F("⚠ [ALARM] Brown-out попередження! Навантаження екстрено вимкнено!"));
}

void restoreLoad() {
    digitalWrite(PIN_LOAD_GATE, LOW);   // Замикаємо ключ назад
    digitalWrite(PIN_ALERT_LED, LOW);
    Serial.println(F("✓ [OK] Напруга шини MB102 стабілізувалася. Навантаження відновлено."));
}

void supervisorTick() {
    uint16_t v = getVoltageMV();

    switch (s_rail_state) {
        case RAIL_OK:
            if (v < V_WARN_TRIP_MV) {
                s_rail_state = RAIL_WARNING;
                emergencyShedLoad();
            }
            break;

        case RAIL_WARNING:
            if (v >= V_WARN_CLEAR_MV) {
                s_rail_state = RAIL_OK;
                restoreLoad();
            }
            break;
    }
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_RAIL_ADC, INPUT);
    pinMode(PIN_LOAD_GATE, OUTPUT);
    pinMode(PIN_ALERT_LED, OUTPUT);

    digitalWrite(PIN_LOAD_GATE, HIGH); // Старт у вимкненому стані
    digitalWrite(PIN_ALERT_LED, LOW);

    delay(200); // Очікування виходу LDO на режим
    Serial.println(F("[MB102 Supervisor] Запуск контролю стабільності шини"));
    
    digitalWrite(PIN_LOAD_GATE, LOW);  // Вмикаємо навантаження
}

void loop() {
    static unsigned long last_check_ms = 0;

    if (millis() - last_check_ms >= 10) {
        last_check_ms = millis();
        supervisorTick();
    }
}

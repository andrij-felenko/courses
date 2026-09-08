/* ============================================================================
   krok-1-rail-monitor.ino — Моніторинг напруги шини MB102 через АЦП
   
   Схема підключення:
     Шина MB102 (5V) ──[ R1: 20 кОм ]──┬──[ R2: 10 кОм ]── GND
                                       │
                                     Пін A0 (MCU, ліміт 0..5 В / 0..3.3 В)
   
   Коефіцієнт дільника: K = (R1 + R2) / R2 = (20 + 10) / 10 = 3.0
   ========================================================================== */

const uint8_t  PIN_RAIL_ADC     = A0;
const float    DIVIDER_RATIO    = 3.00f;   // (20k + 10k) / 10k
const float    ADC_VREF_V       = 5.00f;   // Опорна напруга АЦП
const uint16_t ADC_MAX_COUNTS   = 1023;    // 10-бітний АЦП

// Експоненційне згладжування (EMA) для придушення шумів макетної плати
static float s_smoothed_voltage_mv = 5000.0f;
const float  EMA_ALPHA             = 0.20f;  // Вага нового заміру (20%)

/**
 * Читання напруги шини у мілівольтах з апаратним усередненням
 */
uint16_t readRailVoltageMilliVolts() {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < 4; ++i) {
        sum += analogRead(PIN_RAIL_ADC);
    }
    float raw_avg = (float)sum / 4.0f;

    float v_pin_v = (raw_avg * ADC_VREF_V) / (float)ADC_MAX_COUNTS;
    float v_rail_v = v_pin_v * DIVIDER_RATIO;
    float v_rail_mv = v_rail_v * 1000.0f;

    // Фільтр EMA: V_new = alpha * V_raw + (1 - alpha) * V_old
    s_smoothed_voltage_mv = (EMA_ALPHA * v_rail_mv) + ((1.0f - EMA_ALPHA) * s_smoothed_voltage_mv);

    return (uint16_t)(s_smoothed_voltage_mv + 0.5f);
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_RAIL_ADC, INPUT);
    delay(100);
    Serial.println(F("[MB102 API] Ініціалізація моніторингу шин живлення..."));
}

void loop() {
    static unsigned long last_sample_ms = 0;
    
    if (millis() - last_sample_ms >= 50) {
        last_sample_ms = millis();
        uint16_t v_rail = readRailVoltageMilliVolts();
        
        Serial.print(F("Шина MB102: "));
        Serial.print(v_rail);
        Serial.println(F(" мВ"));
    }
}

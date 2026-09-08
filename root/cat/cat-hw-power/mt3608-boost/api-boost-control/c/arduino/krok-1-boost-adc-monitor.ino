/* ============================================================================
   krok-1-boost-adc-monitor.ino — Читання напруги підвищувача до 28 В
   ========================================================================== */

const uint8_t  PIN_BOOST_ADC  = A0;
const float    DIVIDER_RATIO  = 11.0f; // (100k + 10k) / 10k
const float    ADC_VREF_V     = 5.0f;

uint16_t readBoostVoltageMilliVolts() {
    uint32_t sum = 0;
    for (uint8_t i = 0; i < 4; ++i) {
        sum += analogRead(PIN_BOOST_ADC);
    }
    float raw = (float)sum / 4.0f;
    float v_pin = (raw * ADC_VREF_V) / 1023.0f;
    float v_out = v_pin * DIVIDER_RATIO * 1000.0f;
    return (uint16_t)v_out;
}

void setup() {
    Serial.begin(115200);
}

void loop() {
    delay(100);
    uint16_t mv = readBoostVoltageMilliVolts();
    Serial.print(F("MT3608 Vout: "));
    Serial.print(mv / 1000.0f, 2);
    Serial.println(F(" В"));
}

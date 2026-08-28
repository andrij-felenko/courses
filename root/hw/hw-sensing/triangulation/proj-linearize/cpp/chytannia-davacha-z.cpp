const int   SENSOR_PIN = 34;
const float ADC_VREF   = 3.3f;
const int   ADC_MAX    = 4095;

float readSensorVolts(int pin, int n = 16) {
    long acc = 0;
    for (int k = 0; k < n; k++) acc += analogRead(pin);
    return (float(acc) / n) * (ADC_VREF / ADC_MAX);
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);                       // 0..4095
    analogSetPinAttenuation(SENSOR_PIN, ADC_11db);  // вхід ~0..3.3 В
}

void loop() {
    float v = readSensorVolts(SENSOR_PIN);
    float d = voltageToDistance(v);
    Serial.printf("U=%.3f В  d=%.1f см\n", v, d);
    delay(50);
}

const int   LED_PIN    = 25;     // ІЧ-світлодіод через струмообмежувальний резистор
const int   SENSOR_PIN = 34;     // фотоприймач на вхід АЦП
const int   SETTLE_US  = 200;    // пауза на встановлення світлодіода й приймача, мкс

void setup() {
    Serial.begin(115200);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);
    analogReadResolution(12);                        // 0..4095
    analogSetPinAttenuation(SENSOR_PIN, ADC_11db);   // вхід ~0..3.3 В
}

// Повертає очищений від тла відбиток (коди АЦП; може бути від'ємним за шуму).
int readReflection() {
    digitalWrite(LED_PIN, LOW);                      // 1) тло без власного світла
    delayMicroseconds(SETTLE_US);
    int dark = analogRead(SENSOR_PIN);

    digitalWrite(LED_PIN, HIGH);                     // 2) тло + відбиток
    delayMicroseconds(SETTLE_US);
    int lit  = analogRead(SENSOR_PIN);

    digitalWrite(LED_PIN, LOW);                      // лишаємо світлодіод вимкненим
    return lit - dark;                               // тло скорочується
}

void loop() {
    int signal = readReflection();
    bool obstacle = signal > 120;                    // поріг — за калібруванням, див. нижче
    Serial.printf("відбиток=%d  перешкода=%d\n", signal, obstacle);
    delay(20);
}

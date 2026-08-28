// Повний вимірювальний цикл: рівний крок (таймер) → чисте читання → вольти → регулятору.
const int PIN_SENSOR = 34;    // ADC1 (GPIO34) — стабільний за Wi-Fi
const int N_AVG      = 16;    // √16 = 4× тихіше; +2 «ефективні» біти

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);        // рідні 12 біт ESP32
    setupSampler(1000);              // fs = 1 кГц: надвибірка над повільним давачем
}

void loop() {
    if (!tick) return;               // ще не час знімка — не робимо НІЧОГО тут
    tick = false;

    uint32_t code = readClean(PIN_SENSOR, N_AVG);          // чисте усереднене читання
    uint32_t mv   = analogReadMilliVolts(PIN_SENSOR);      // калібровані мВ (зсув+нелінійність)
    // (для строгості mv теж можна усереднити тим самим readClean-підходом)

    controlStep(mv);                 // готове число — регулятору (наступний крок модуля)
}

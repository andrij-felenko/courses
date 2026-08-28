// ADC1, 12 біт; PIN_RAW — вузол подільника напряму,
// PIN_BUF — вихід повторювача → той самий вузол
const int PIN_RAW = 34;   // ADC1 (GPIO34), напряму до МОм-подільника
const int PIN_BUF = 35;   // ADC1 (GPIO35), вихід ОП-буфера

static uint32_t avg_mv(int pin, int n) {
    uint32_t s = 0;
    for (int i = 0; i < n; i++) s += analogReadMilliVolts(pin);
    return s / n;
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);       // рідні 12 біт ESP32
    // analogSetPinAttenuation(PIN_RAW, ADC_11db); // якщо Vin > 1 В
    // analogSetPinAttenuation(PIN_BUF, ADC_11db);
}

void loop() {
    uint32_t raw = avg_mv(PIN_RAW, 16);  // високий опір джерела — занижує
    uint32_t buf = avg_mv(PIN_BUF, 16); // через буфер — істина
    // Очікуваний вивід:
    //   raw=945 mV  buf=1670 mV  dif=+725 mV   (джерело ~1.72 В, 1 МОм подільник)
    //   або raw≈buf (джерело й так низькоомне — буфер зайвий)
    Serial.printf("raw=%u mV  buf=%u mV  dif=%d mV\n",
                  raw, buf, (int)buf - (int)raw);
    delay(200);
}

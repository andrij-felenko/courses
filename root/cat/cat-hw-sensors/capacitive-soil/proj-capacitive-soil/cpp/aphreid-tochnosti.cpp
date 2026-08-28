// ESP32 + ADS1115: читати ємнісний щуп через зовнішній 16-бітний АЦП по I2C.
#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;                  // об'єкт АЦП на шині I2C

// щуп живимо з GPIO, як і раніше; AOUT ідемо на вхід A0 самого ADS1115
const uint8_t POWER = 25;

// калібрування у СИРИХ відліках ADS1115 (16 біт зі своїм PGA) — зняти окремо:
const int AIR   = 17000;               // сухо
const int WATER = 9000;                // мокро

void setup() {
    Serial.begin(115200);
    Wire.begin();                      // I2C: SDA/SCL за замовчуванням плати
    if (!ads.begin(0x48)) {            // адреса модуля; 0x48 — типова
        Serial.println("ADS1115 не знайдено — перевір I2C та живлення");
        while (1) delay(10);
    }
    ads.setGain(GAIN_ONE);             // PGA: діапазон входу ±4.096 В під наш сигнал
    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, LOW);
}

int readAvgADS(uint8_t ch, uint8_t n = 16) {
    long sum = 0;
    for (uint8_t i = 0; i < n; i++) {
        sum += ads.readADC_SingleEnded(ch);   // сирий 16-бітний відлік з каналу
        delay(2);
    }
    return (int)(sum / n);
}

void loop() {
    digitalWrite(POWER, HIGH);
    delay(50);                          // усталення генератора щупа
    int raw = readAvgADS(0);            // AOUT щупа на каналі A0 модуля ADS1115
    digitalWrite(POWER, LOW);

    int pct = constrain(map(raw, AIR, WATER, 0, 100), 0, 100);
    Serial.printf("ADS raw=%d  moisture=%d%%\n", raw, pct);
    delay(2000);
}

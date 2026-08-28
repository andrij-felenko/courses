// ESP32: заміряти вологість раз на 30 хв і спати між замірами.
#include <Arduino.h>

const uint8_t POWER = 25;                 // живлення щупа з GPIO25
const uint8_t SOIL  = 34;                 // AO на GPIO34 — це ADC1, безпечно
const uint64_t SLEEP_US = 30ULL * 60 * 1000000;   // 30 хв у мікросекундах

RTC_DATA_ATTR int wakeCount = 0;          // переживає глибокий сон (RTC-пам'ять)

int median9() {
    int a[9];
    for (int i = 0; i < 9; i++) { a[i] = analogRead(SOIL); delay(2); }
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8 - i; j++)
            if (a[j] > a[j+1]) { int t=a[j]; a[j]=a[j+1]; a[j+1]=t; }
    return a[4];
}

void setup() {
    Serial.begin(115200);
    analogReadResolution(12);             // 12-бітний АЦП ESP32: 0..4095

    pinMode(POWER, OUTPUT);
    digitalWrite(POWER, HIGH);            // подали живлення на щуп
    delay(10);
    int v = median9();                    // зняли
    digitalWrite(POWER, LOW);            // знеструмили щуп

    wakeCount++;
    Serial.printf("замір #%d: вологість(АЦП)=%d\n", wakeCount, v);
    Serial.flush();                       // дочекатись, поки друк дійде до порту

    // тут — рішення (полити/тривога/надіслати по мережі), поки ми ще не спимо
    esp_sleep_enable_timer_wakeup(SLEEP_US);   // збудитись через 30 хв
    esp_deep_sleep_start();               // заснути; прокинемось у setup() заново
}

void loop() {
    // порожній: уся робота в setup(), бо після сну код стартує спочатку
}

#include <DHT.h>

#define DHT_PIN   2         // ніжка МК, куди прийшла лінія DATA
#define DHT_TYPE  DHT11     // саме DHT11 — НЕ DHT22 і не AM2302

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();            // налаштувати ніжку в потрібний режим
    delay(1500);            // дати давачу очуняти після подачі живлення
}

void loop() {
    delay(2000);            // ≥ 1 с між читаннями; беремо 2 с із запасом

    float h = dht.readHumidity();      // % RH
    float t = dht.readTemperature();   // °C (без аргументу — Цельсій)

    // Давач міг не відповісти — тоді бібліотека повертає NAN.
    // Це не виняток, а звичайний робочий випадок: перевіряти ОБОВ'ЯЗКОВО.
    if (isnan(h) || isnan(t)) {
        Serial.println(F("DHT11 не відповів — пропускаю це читання"));
        return;             // просто чекаємо наступного проходу циклу
    }

    Serial.print(F("Вологість: "));
    Serial.print(h, 0);                // 0 знаків після крапки: DHT11 і так цілі
    Serial.print(F(" %   Температура: "));
    Serial.print(t, 0);
    Serial.println(F(" C"));
}

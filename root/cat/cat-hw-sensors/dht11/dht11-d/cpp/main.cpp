#include <DHT.h>

#define DHT_PIN   2         // ніжка МК, куди прийшла лінія DATA
#define DHT_TYPE  DHT11     // саме DHT11 (не DHT22)

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
    Serial.begin(9600);
    dht.begin();            // налаштувати ніжку й давач
}

void loop() {
    delay(2000);            // ≥ 1 с між читаннями; беремо 2 с із запасом

    float t = dht.readTemperature();   // °C
    float h = dht.readHumidity();       // % RH

    // Давач міг не відповісти — бібліотека поверне NAN. Перевіряймо!
    if (isnan(t) || isnan(h)) {
        Serial.println("DHT11 не відповів — пропускаю читання");
        return;
    }

    Serial.print("Temp: ");  Serial.print(t, 0);   // 0 знаків: DHT11 і так цілі
    Serial.print(" C   Hum: ");  Serial.print(h, 0);
    Serial.println(" %");
}

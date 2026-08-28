#define LED_PIN 2            // ніжка, до якої під'єднано світлодіод

void setup() {
    pinMode(LED_PIN, OUTPUT);        // налаштувати ніжку на вихід — один раз
}

void loop() {
    digitalWrite(LED_PIN, HIGH);     // увімкнути світлодіод
    delay(200);                      // зачекати 200 мілісекунд (світить)
    digitalWrite(LED_PIN, LOW);      // вимкнути світлодіод
    delay(200);                      // зачекати 200 мілісекунд (темно)
}

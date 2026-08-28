const uint8_t A_PIN = A0;        // аналоговий вихід 49E → A0
const uint8_t D_PIN = 3;         // цифровий вихід компаратора (поріг гвинтика)

int baseline = 512;              // нульова лінія — уточнимо на старті
const int DEADBAND = 4;          // мертва зона: |delta| нижче цього → «нема поля»

int readAveraged(uint8_t pin, uint8_t n) {
    long acc = 0;
    for (uint8_t i = 0; i < n; i++) { acc += analogRead(pin); delayMicroseconds(200); }
    return acc / n;
}

void setup() {
    pinMode(D_PIN, INPUT);
    Serial.begin(115200);
    delay(50);                        // хай живлення й вихід 49E устояться
    baseline = readAveraged(A_PIN, 64);   // калібрування нуля (біля давача НЕ має бути магніту!)
    Serial.print("baseline = ");
    Serial.println(baseline);
}

void loop() {
    int raw   = readAveraged(A_PIN, 8);   // трохи усереднити проти шуму
    int delta = raw - baseline;

    Serial.print("поле: ");
    if (delta > DEADBAND) {
        Serial.print(delta);  Serial.print("  (N-бік)");
    } else if (delta < -DEADBAND) {
        Serial.print(delta);  Serial.print("  (S-бік)");
    } else {
        Serial.print("~0    (нема)");
    }

    // цифровий вихід D0: клацає на порозі, заданому гвинтиком (зазвичай активний у нулі)
    if (digitalRead(D_PIN) == LOW) Serial.print("   [поріг!]");
    Serial.println();
    delay(100);
}

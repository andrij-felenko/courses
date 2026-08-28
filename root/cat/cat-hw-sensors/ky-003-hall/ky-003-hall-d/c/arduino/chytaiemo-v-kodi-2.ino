const uint8_t A_PIN = A0;   // аналоговий вихід 49E
const uint8_t D_PIN = 3;    // цифровий вихід компаратора

int baseline = 512;         // нульова лінія (≈ половина шкали)

void setup() {
    pinMode(D_PIN, INPUT);
    Serial.begin(9600);
    // за 200 мс без магніту запамʼятовуємо реальний спокій
    long acc = 0;
    for (int i = 0; i < 64; i++) { acc += analogRead(A_PIN); delay(3); }
    baseline = acc / 64;
}

void loop() {
    int raw   = analogRead(A_PIN);   // 0..1023
    int delta = raw - baseline;      // >0 один полюс, <0 протилежний

    Serial.print("поле: ");
    Serial.print(delta);
    Serial.print(delta > 0 ? " (N-бік) " : (delta < 0 ? " (S-бік) " : " (нема) "));
    // цифровий вихід: клацає на порозі гвинтика (типово активний у нулі)
    Serial.println(digitalRead(D_PIN) == LOW ? " [поріг!]" : "");
    delay(100);
}

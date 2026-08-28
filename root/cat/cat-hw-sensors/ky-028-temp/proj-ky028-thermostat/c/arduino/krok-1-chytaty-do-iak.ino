const uint8_t DO_PIN = 2;      // цифровий вихід модуля (поріг компаратора)

void setup() {
    pinMode(DO_PIN, INPUT);    // DO вже підтягнутий на платі — просто INPUT
    Serial.begin(9600);
}

void loop() {
    int level = digitalRead(DO_PIN);           // 0 або 1 — сирий рівень
    Serial.println(level == HIGH ? "DO = HIGH" : "DO = LOW");
    delay(300);
}

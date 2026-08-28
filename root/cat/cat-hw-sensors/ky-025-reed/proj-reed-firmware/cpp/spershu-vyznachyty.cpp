const uint8_t REED = 2;        // D0 давача на вивід D2

void setup() {
    pinMode(REED, INPUT);      // на платі KY-025 підтяжка Rp вже є — зовнішня не потрібна
    Serial.begin(9600);
    Serial.println("Підносьте й прибирайте магніт, стежте за рівнем D0:");
}

void loop() {
    int level = digitalRead(REED);
    Serial.println(level == HIGH ? "D0 = HIGH (високий)" : "D0 = LOW (низький)");
    delay(300);
}

const uint8_t RAIN = 2;
bool dryLevel;                      // рівень DO у спокої — визначимо на старті

void setup() {
    pinMode(RAIN, INPUT);
    Serial.begin(9600);
    delay(50);
    dryLevel = digitalRead(RAIN);   // ПРИПУСКАЄМО: на старті пластина суха
    Serial.print("рівень 'сухо' на цій платі = ");
    Serial.println(dryLevel ? "HIGH" : "LOW");
}

void loop() {
    bool nowWet = (digitalRead(RAIN) != dryLevel);   // мокро = НЕ як у спокої
    // ... далі звична логіка гістерезису/відсіву на булевому nowWet ...
}

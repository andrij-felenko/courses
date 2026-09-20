// Arduino C++ (ESP8266 Core)
void setup() {
    // Спочатку записуємо HIGH у регістр виходу, щоб при зміні режиму pin не просів у 0
    digitalWrite(0, HIGH);
    // Тепер перемикаємо напрямок виводу на вихід без хибного клацання Active-LOW ключа
    pinMode(0, OUTPUT);
}

void loop() {
    // Увімкнення реле (Active-LOW: низький рівень відкриває ключ)
    digitalWrite(0, LOW);
    delay(1000);

    // Вимкнення реле (високий рівень замикає керувальний ключ)
    digitalWrite(0, HIGH);
    delay(1000);
}

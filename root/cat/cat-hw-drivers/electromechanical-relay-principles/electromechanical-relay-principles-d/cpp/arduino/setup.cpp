const int RELAY_PIN = 7;

void setup() {
    // Ініціалізація виводу керування реле як виходу
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW); // Початковий стан: реле знеструмлене
}

void loop() {
    // Подача сигналу на ввімкнення котушки реле
    digitalWrite(RELAY_PIN, HIGH);
    delay(2000); // Реле замкнене протягом 2 секунд

    // Зняття сигналу керування (гасіння ЕРС забезпечується зворотним діодом)
    digitalWrite(RELAY_PIN, LOW);
    delay(2000); // Пауза для стабілізації механічної системи
}

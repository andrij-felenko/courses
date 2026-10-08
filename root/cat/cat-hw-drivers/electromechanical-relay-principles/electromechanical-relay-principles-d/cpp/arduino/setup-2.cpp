// Приклад керування силовим реле в середовищі Arduino (C++)
const int RELAY_PIN = 4; // Вивід GPIO для керування MOSFET-ключем

void setup() {
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW); // Початковий безпечний стан
}

void loop() {
    // Вмикання силового навантаження
    digitalWrite(RELAY_PIN, HIGH);
    // Пауза на завершення спрацьовування якоря та згасання брязкіту контактів
    delay(20);

    // Активна фаза роботи навантаження
    delay(5000);

    // Вимкнення силового навантаження
    digitalWrite(RELAY_PIN, LOW);
    // Пауза на згасання струму в котушці та повернення якоря пружиною
    delay(20);

    delay(5000);
}

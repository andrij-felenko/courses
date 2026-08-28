// HC-SR04-подібний модуль: trigger і echo на двох виводах.
// pulseIn-стиль: повертає відстань у см або -1, якщо відлуння не прийшло.
float ping_blocking(int trigPin, int echoPin) {
    // 1) короткий імпульс «пни» — 10 мкс
    digitalWrite(trigPin, LOW);  delayMicroseconds(2);
    digitalWrite(trigPin, HIGH); delayMicroseconds(10);
    digitalWrite(trigPin, LOW);

    // 2) чекаємо фронт echo (з тайм-аутом, щоб не зависнути назавжди)
    uint32_t t0 = micros();
    while (digitalRead(echoPin) == LOW)
        if (micros() - t0 > 30000UL) return -1.0f;   // давач не відповів

    // 3) міряємо ширину імпульсу echo
    uint32_t start = micros();
    while (digitalRead(echoPin) == HIGH)
        if (micros() - start > 25000UL) return -1.0f; // ціль поза діапазоном

    uint32_t dt = micros() - start;   // повний час польоту, мкс
    return dt / 58.0f;                // см  (правило: см ≈ мкс / 58)
}

const uint8_t PIN_DO = 2;          // вивід DO давача
uint8_t idleLevel;                 // рівень DO у тиші (визначимо самі)

// Прочитати рівень, що переважає в тиші: беремо більшість із багатьох відліків.
uint8_t detectIdleLevel(uint8_t pin, uint16_t samples = 200) {
    uint16_t highs = 0;
    for (uint16_t i = 0; i < samples; i++) {
        if (digitalRead(pin) == HIGH) highs++;
        delayMicroseconds(200);    // короткі паузи; загалом ~40 мс на всю оцінку
    }
    // Якщо більшість відліків були HIGH — спокій це HIGH, інакше LOW.
    return (highs > samples / 2) ? HIGH : LOW;
}

void setup() {
    pinMode(PIN_DO, INPUT);        // на платі є підтяжка; лишаємо звичайний вхід
    Serial.begin(9600);
    delay(300);                    // дати мікрофону встановити зсув після ввімкнення
    idleLevel = detectIdleLevel(PIN_DO);
    Serial.print("Рівень спокою DO = ");
    Serial.println(idleLevel == HIGH ? "HIGH (звук → LOW)" : "LOW (звук → HIGH)");
}

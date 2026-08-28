const int HOLD_PIN = 4;   // утримує P-MOSFET відкритим
const int KEY_PIN  = 5;   // читає стан кнопки

void setup() {
    // ПЕРШИМ — утримати живлення, поки кнопку ще тримають
    pinMode(HOLD_PIN, OUTPUT);
    digitalWrite(HOLD_PIN, HIGH);  // latch on

    pinMode(KEY_PIN, INPUT_PULLUP);

    // ... решта ініціалізації ...
}

void power_off() {
    // Самовимкнення: знімаємо утримання — живлення рветься
    digitalWrite(HOLD_PIN, LOW);
    // Цей рядок вже не виконається — МК мертвий
}

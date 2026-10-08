// Керування апаратним напівпровідниковим тригером блокування (Arduino C++)
// Мікроконтролер зчитує статус апаратної засувки та генерує безпечний імпульс скидання.

constexpr uint8_t LATCH_STATUS_PIN = 4; // Вхід зчитування стану RS-тригера (HIGH = Норма, LOW = Блокування)
constexpr uint8_t INTERLOCK_OK_PIN = 5; // Вхід стану апаратних вимикачів (HIGH = Замкнено)
constexpr uint8_t HW_RESET_TRIG_PIN= 6; // Вихід подачі імпульсу скидання (Set) на RS-тригер

bool tryHardwareReset() {
    // Скидання тригера дозволено ТІЛЬКИ якщо фізичний інтерлок повністю замкнений
    if (digitalRead(INTERLOCK_OK_PIN) == HIGH) {
        // Генерація калиброваного імпульсу тривалістю 50 мс на вхід Set RS-тригера
        digitalWrite(HW_RESET_TRIG_PIN, HIGH);
        delay(50);
        digitalWrite(HW_RESET_TRIG_PIN, LOW);
        
        // Перевірка, чи перейшов тригер у робочий стан
        return (digitalRead(LATCH_STATUS_PIN) == HIGH);
    }
    return false;
}

void setup() {
    pinMode(LATCH_STATUS_PIN, INPUT);
    pinMode(INTERLOCK_OK_PIN, INPUT);
    pinMode(HW_RESET_TRIG_PIN, OUTPUT);
    
    digitalWrite(HW_RESET_TRIG_PIN, LOW);
}

void loop() {
    bool isLatchOk = (digitalRead(LATCH_STATUS_PIN) == HIGH);
    
    if (!isLatchOk) {
        // Якщо тригер у стані блокування, спробувати безпечне відновлення
        // (наприклад, після натискання оператором програмної кнопки пуску)
        tryHardwareReset();
    }
    
    delay(100);
}

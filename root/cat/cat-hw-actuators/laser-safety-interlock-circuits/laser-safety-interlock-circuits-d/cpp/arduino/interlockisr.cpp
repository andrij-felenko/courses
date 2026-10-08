// Програмний моніторинг апаратного інтерлоку (Arduino C++)
// Мікроконтролер НЕ керує живленням лазера, а лише контролює статус безпеки.

constexpr uint8_t INTERLOCK_FB_PIN = 2; // Вхід моніторингу інтерлоку (через оптопару)
constexpr uint8_t LASER_ENABLE_PIN = 3; // Сигнал дозволу модуляції (PWM/Enable)
constexpr uint8_t STATUS_LED_PIN   = 13; // Індикатор стану системи

volatile bool g_interlock_ok = false;

void IRAM_ATTR interlockIsr() {
    // Негайна реакція на зміну стану апаратного інтерлоку
    g_interlock_ok = (digitalRead(INTERLOCK_FB_PIN) == HIGH);
}

void setup() {
    pinMode(INTERLOCK_FB_PIN, INPUT_PULLUP);
    pinMode(LASER_ENABLE_PIN, OUTPUT);
    pinMode(STATUS_LED_PIN, OUTPUT);
    
    // Блокуємо програмний дозвіл за замовчуванням
    digitalWrite(LASER_ENABLE_PIN, LOW);
    
    // Початкове зчитування стану контуру безпеки
    g_interlock_ok = (digitalRead(INTERLOCK_FB_PIN) == HIGH);
    
    // Реєстрація переривання для оперативного моніторингу
    attachInterrupt(digitalPinToInterrupt(INTERLOCK_FB_PIN), interlockIsr, CHANGE);
}

void loop() {
    // Пасивний моніторинг: програмний сигнал дозволу видається ТІЛЬКИ якщо апаратний контур замкнений.
    // Якщо апаратний контур розімкнено, лазер фізично знеструмлений реле безпеки,
    // незалежно від того, який рівень встановлено на LASER_ENABLE_PIN.
    if (g_interlock_ok) {
        digitalWrite(STATUS_LED_PIN, HIGH);
        // Дозволено програмне стробування
        digitalWrite(LASER_ENABLE_PIN, HIGH);
    } else {
        digitalWrite(STATUS_LED_PIN, LOW);
        // Негайно знімаємо програмний дозвіл
        digitalWrite(LASER_ENABLE_PIN, LOW);
    }
    
    delay(10);
}

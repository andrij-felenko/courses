#include <Arduino.h>

constexpr uint8_t PIN_INTERLOCK_FB = 4;   // Оптопара моніторингу інтерлоку
constexpr uint8_t PIN_EDM_FB       = 5;   // Зворотний контакт реле EDM
constexpr uint8_t PIN_MCU_ENABLE   = 18;  // Вихід стробування на вентиль І
constexpr uint8_t PIN_RESET_BTN    = 19;  // Кнопка ручного скидання

enum class SafetyState {
    Disabled,
    Ready,
    Active,
    Fault
};

SafetyState currentState = SafetyState::Disabled;

void setupSafetyHardware() {
    pinMode(PIN_INTERLOCK_FB, INPUT_PULLUP);
    pinMode(PIN_EDM_FB, INPUT_PULLUP);
    pinMode(PIN_RESET_BTN, INPUT_PULLUP);
    
    pinMode(PIN_MCU_ENABLE, OUTPUT);
    digitalWrite(PIN_MCU_ENABLE, LOW);
}

void processSafetyLogic() {
    bool interlockOk   = (digitalRead(PIN_INTERLOCK_FB) == LOW);
    bool edmOk         = (digitalRead(PIN_EDM_FB) == HIGH);
    bool resetPressed  = (digitalRead(PIN_RESET_BTN) == LOW);

    switch (currentState) {
        case SafetyState::Disabled:
            digitalWrite(PIN_MCU_ENABLE, LOW);
            if (interlockOk && edmOk) {
                currentState = SafetyState::Ready;
                Serial.println(F("[SAFETY] Контур відновлено. Натисніть скидання."));
            }
            break;

        case SafetyState::Ready:
            if (!interlockOk) {
                currentState = SafetyState::Disabled;
            } else if (resetPressed) {
                currentState = SafetyState::Active;
                digitalWrite(PIN_MCU_ENABLE, HIGH);
                Serial.println(F("[SAFETY] Апаратне стробування активовано."));
            }
            break;

        case SafetyState::Active:
            if (!interlockOk) {
                digitalWrite(PIN_MCU_ENABLE, LOW);
                currentState = SafetyState::Disabled;
                Serial.println(F("[SAFETY] Аварійне розмикання інтерлоку!"));
            }
            break;

        case SafetyState::Fault:
        default:
            digitalWrite(PIN_MCU_ENABLE, LOW);
            break;
    }
}

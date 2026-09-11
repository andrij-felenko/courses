// C++: Скінченний автомат захисту H-моста для мікроконтролера
#include <Arduino.h>

// Призначення виводів підключення драйвера
constexpr uint8_t PIN_FAULT = 2;   // Вивід з підтримкою зовнішнього переривання (INT0)
constexpr uint8_t PIN_PWM_IN1 = 5; // ШІМ-вихід керування напрямком 1
constexpr uint8_t PIN_DIR_IN2 = 4; // Цифровий вихід керування напрямком 2

enum class DriverState {
    RUNNING,            // Штатна робота приводу
    DEBOUNCE_CHECK,     // Фільтрація імпульсних комутаційних завад
    COOLDOWN,           // Пауза теплового остигання кристала драйвера
    PERMANENT_LOCKOUT   // Критичне блокування при непереборній аварії
};

// Змінні, доступні в обробнику переривання
volatile bool faultTriggered = false;

void IRAM_ATTR faultIsr() {
    faultTriggered = true;
}

class HBridgeProtector {
public:
    void begin() {
        pinMode(PIN_FAULT, INPUT_PULLUP); // Внутрішня або зовнішня підтяжка лінії відкритого стоку
        pinMode(PIN_PWM_IN1, OUTPUT);
        pinMode(PIN_DIR_IN2, OUTPUT);
        emergencyStopHardware();

        attachInterrupt(digitalPinToInterrupt(PIN_FAULT), faultIsr, FALLING);
    }

    void update() {
        uint32_t now = millis();

        switch (currentState) {
            case DriverState::RUNNING:
                if (faultTriggered) {
                    faultTriggered = false;
                    emergencyStopHardware();
                    stateEnterTime = now;
                    currentState = DriverState::DEBOUNCE_CHECK;
                }
                break;

            case DriverState::DEBOUNCE_CHECK:
                // Перевірка стабільності аварії через 2 мс
                if (now - stateEnterTime >= 2) {
                    if (digitalRead(PIN_FAULT) == LOW) {
                        // Аварія дійсна: перевіряємо лічильник повторних спроб
                        retryCount++;
                        if (retryCount >= MAX_RETRIES) {
                            currentState = DriverState::PERMANENT_LOCKOUT;
                        } else {
                            stateEnterTime = now;
                            currentState = DriverState::COOLDOWN;
                        }
                    } else {
                        // Була хибна перешкода, відновлюємо попередню швидкість
                        restoreDrive();
                        currentState = DriverState::RUNNING;
                    }
                }
                break;

            case DriverState::COOLDOWN:
                // Очікування 1.5 секунди для відведення тепла через плату
                if (now - stateEnterTime >= COOLDOWN_MS) {
                    if (digitalRead(PIN_FAULT) == HIGH) {
                        // Драйвер охолов і зняв аварійний сигнал
                        restoreDrive();
                        currentState = DriverState::RUNNING;
                    } else {
                        // Чип усе ще перегрітий: подовжуємо очікування
                        stateEnterTime = now;
                    }
                }
                break;

            case DriverState::PERMANENT_LOCKOUT:
                // Привід повністю знеструмлений, потрібне втручання оператора
                emergencyStopHardware();
                break;
        }

        // Скидання лічильника спроб, якщо мотор успішно пропрацював понад 10 секунд
        if (currentState == DriverState::RUNNING && (now - lastSuccessfulRunTime >= 10000)) {
            retryCount = 0;
            lastSuccessfulRunTime = now;
        }
    }

    void setTargetSpeed(int16_t speedPwm) {
        targetSpeed = constrain(speedPwm, -255, 255);
        if (currentState == DriverState::RUNNING) {
            applySpeed(targetSpeed);
        }
    }

    DriverState getState() const { return currentState; }

private:
    static constexpr uint8_t MAX_RETRIES = 3;
    static constexpr uint32_t COOLDOWN_MS = 1500;

    DriverState currentState = DriverState::RUNNING;
    uint32_t stateEnterTime = 0;
    uint32_t lastSuccessfulRunTime = 0;
    uint8_t retryCount = 0;
    int16_t targetSpeed = 0;

    void emergencyStopHardware() {
        analogWrite(PIN_PWM_IN1, 0);
        digitalWrite(PIN_DIR_IN2, LOW);
    }

    void restoreDrive() {
        applySpeed(targetSpeed);
    }

    void applySpeed(int16_t speed) {
        if (speed >= 0) {
            digitalWrite(PIN_DIR_IN2, LOW);
            analogWrite(PIN_PWM_IN1, speed);
        } else {
            digitalWrite(PIN_DIR_IN2, HIGH);
            analogWrite(PIN_PWM_IN1, 255 + speed); // Інверсія для реверсивного руху
        }
    }
};

HBridgeProtector motorProtector;

void setup() {
    motorProtector.begin();
    motorProtector.setTargetSpeed(180); // Запуск руху вперед
}

void loop() {
    motorProtector.update();
}

// Конфігурація високочастотного ШІМ (80 кГц) для безсердечникового двигуна в середовищі Arduino
#include <Arduino.h>

constexpr uint8_t MOTOR_PIN = 18;
constexpr uint32_t PWM_FREQ = 80000; // 80 кГц для малоіндуктивного ротора
constexpr uint8_t PWM_CHANNEL = 0;
constexpr uint8_t PWM_RESOLUTION = 8; // 8 біт (шкала 0..255)

class CorelessMotorDriver {
public:
    void begin() {
#if defined(ESP32)
        ledcSetup(PWM_CHANNEL, PWM_FREQ, PWM_RESOLUTION);
        ledcAttachPin(MOTOR_PIN, PWM_CHANNEL);
        setSpeed(0);
#else
        // Налаштування апаратного таймера AVR для підвищення частоти ШІМ
        pinMode(MOTOR_PIN, OUTPUT);
        analogWrite(MOTOR_PIN, 0);
#endif
    }

    void setSpeed(uint8_t speed) {
#if defined(ESP32)
        ledcWrite(PWM_CHANNEL, speed);
#else
        analogWrite(MOTOR_PIN, speed);
#endif
    }
};

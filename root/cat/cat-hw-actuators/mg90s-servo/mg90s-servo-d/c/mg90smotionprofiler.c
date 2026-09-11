#include <Arduino.h>
#include <Servo.h>

// Генератор плавного руху вала MG90S за квінтичною S-кривою
class MG90SMotionProfiler {
public:
    MG90SMotionProfiler(Servo& servoRef) : servo(servoRef) {}

    void begin(float initialAngle) {
        currentAngle = initialAngle;
        targetAngle = initialAngle;
        startAngle = initialAngle;
        isMoving = false;
        servo.write(static_cast<int>(currentAngle + 0.5f));
    }

    // Запуск маневру переміщення до нового кута за заданий час
    void moveTo(float newTargetAngle, unsigned long durationMs) {
        if (durationMs < 20) durationMs = 20; // Мінімальна тривалість — один період ШІМ
        startAngle = currentAngle;
        targetAngle = newTargetAngle;
        totalDurationMs = durationMs;
        startTimeMs = millis();
        isMoving = true;
    }

    // Оновлення координати (викликається в loop з інтервалом 20 мс)
    void update() {
        if (!isMoving) return;

        unsigned long now = millis();
        if (now - lastUpdateMs < 20) return; // Синхронізація з кадрами 50 Гц ШІМ
        lastUpdateMs = now;

        unsigned long elapsed = now - startTimeMs;
        if (elapsed >= totalDurationMs) {
            currentAngle = targetAngle;
            isMoving = false;
        } else {
            // Нормований часовий параметр tau від 0.0 до 1.0
            float tau = static_cast<float>(elapsed) / static_cast<float>(totalDurationMs);
            
            // Квінтичний поліном s(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5
            float tau3 = tau * tau * tau;
            float tau4 = tau3 * tau;
            float tau5 = tau4 * tau;
            float s = 10.0f * tau3 - 15.0f * tau4 + 6.0f * tau5;

            currentAngle = startAngle + (targetAngle - startAngle) * s;
        }

        servo.write(static_cast<int>(currentAngle + 0.5f));
    }

    bool busy() const { return isMoving; }
    float getAngle() const { return currentAngle; }

private:
    Servo& servo;
    float currentAngle = 90.0f;
    float startAngle = 90.0f;
    float targetAngle = 90.0f;
    unsigned long totalDurationMs = 1000;
    unsigned long startTimeMs = 0;
    unsigned long lastUpdateMs = 0;
    bool isMoving = false;
};

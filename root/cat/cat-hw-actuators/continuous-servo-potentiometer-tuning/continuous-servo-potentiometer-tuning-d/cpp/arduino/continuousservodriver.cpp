#include <Arduino.h>
#include <ESP32Servo.h>

class ContinuousServoDriver {
private:
    Servo m_servo;
    int m_pin;
    int m_neutral_offset_us;
    int m_deadband_us;
    const int m_base_neutral_us = 1500;
    const int m_min_pulse_us = 1000;
    const int m_max_pulse_us = 2000;

public:
    ContinuousServoDriver(int pin, int offset_us = 0, int deadband_us = 10)
        : m_pin(pin), m_neutral_offset_us(offset_us), m_deadband_us(deadband_us) {}

    void begin() {
        m_servo.attach(m_pin, m_min_pulse_us, m_max_pulse_us);
        stop();
    }

    void setNeutralOffset(int offset_us) {
        m_neutral_offset_us = offset_us;
    }

    void stop() {
        int calibrated_neutral = m_base_neutral_us + m_neutral_offset_us;
        m_servo.writeMicroseconds(calibrated_neutral);
    }

    void setSpeed(float speed_pct) {
        speed_pct = constrain(speed_pct, -100.0f, 100.0f);
        int calibrated_neutral = m_base_neutral_us + m_neutral_offset_us;
        int target_pulse = calibrated_neutral;

        if (speed_pct > 0.0f) {
            int range = m_max_pulse_us - calibrated_neutral;
            target_pulse = calibrated_neutral + static_cast<int>((speed_pct / 100.0f) * range);
        } else if (speed_pct < 0.0f) {
            int range = calibrated_neutral - m_min_pulse_us;
            target_pulse = calibrated_neutral - static_cast<int>((-speed_pct / 100.0f) * range);
        }

        // Перевірка зони нечутливості для запобігання паразитарному повзанню
        if (abs(target_pulse - calibrated_neutral) < m_deadband_us) {
            target_pulse = calibrated_neutral;
        }

        m_servo.writeMicroseconds(target_pulse);
    }
};

ContinuousServoDriver leftWheelServo(18, 12, 10);

void setup() {
    Serial.begin(115200);
    leftWheelServo.begin();
    Serial.println("Каліброване керування сервоприводом постійного обертання запущено.");
}

void loop() {
    // Демонстрація симетричного руху та повної зупинки
    leftWheelServo.setSpeed(50.0f);   // 50% вперед
    delay(2000);
    leftWheelServo.stop();             // Гарантована зупинка без повзання
    delay(1000);
    leftWheelServo.setSpeed(-50.0f);  // 50% назад
    delay(2000);
    leftWheelServo.stop();             // Гарантована зупинка
    delay(3000);
}

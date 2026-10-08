// C++ (Arduino / Embedded C++) - Захищене керування та detach
class SafeServoDriver {
private:
    bool attached_ = false;
    uint8_t pin_ = 0;
    uint16_t currentUs_ = 1500;

public:
    ServoError setAngle(float angle) {
        if (!attached_) {
            attach();
        }

        ServoError status = ServoError::Ok;
        if (angle < 0.0f || angle > 180.0f) {
            angle = (angle < 0.0f) ? 0.0f : 180.0f;
            status = ServoError::InvalidArg;
        }

        // Обчислення імпульсу та оновлення таймера
        currentUs_ = 500 + static_cast<uint16_t>(angle * (2000.0f / 180.0f));
        // hardware_pwm_write_us(pin_, currentUs_);

        return status;
    }

    void detach() {
        if (attached_) {
            // hardware_pwm_disable(pin_);
            attached_ = false;
        }
    }

    void attach() {
        if (!attached_) {
            // hardware_pwm_enable(pin_, currentUs_);
            attached_ = true;
        }
    }
};

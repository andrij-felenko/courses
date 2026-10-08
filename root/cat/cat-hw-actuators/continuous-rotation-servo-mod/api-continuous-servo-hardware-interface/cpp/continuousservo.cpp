// Клас апаратного інтерфейсу сервопривода постійного обертання на мові C++
#include <algorithm>
#include <cstdint>

class ContinuousServo {
private:
    uint8_t pin_;
    uint16_t current_pulse_us_;
    static constexpr uint16_t kNeutralUs = 1500;
    static constexpr uint16_t kMinUs = 1000;
    static constexpr uint16_t kMaxUs = 2000;

public:
    explicit ContinuousServo(uint8_t pin) 
        : pin_(pin), current_pulse_us_(kNeutralUs) {}

    void setSpeed(float speed) {
        // speed від -1.0f (максимальний реверс) до +1.0f (максимальний вперед)
        speed = std::clamp(speed, -1.0f, 1.0f);
        current_pulse_us_ = static_cast<uint16_t>(kNeutralUs + (speed * 500.0f));
    }

    void stop() {
        current_pulse_us_ = kNeutralUs;
    }

    uint16_t getPulseWidthUs() const { return current_pulse_us_; }
};

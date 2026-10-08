// Реєстрація callback та обробка аварійних подій (C++)
#include <functional>

class LiquidLevelSensorAdv {
public:
    using EventCallback = std::function<void(SensorStatus status, float levelPercent)>;

    void setEventCallback(EventCallback cb) {
        callback_ = cb;
    }

    void update() {
        uint16_t rawAdc = readAdcHw();
        if (rawAdc < 50) {
            if (callback_) callback_(SensorStatus::LineBreak, 0.0f);
            return;
        }
        if (rawAdc > 4045) {
            if (callback_) callback_(SensorStatus::ShortCircuit, 0.0f);
            return;
        }

        float percent = getPercent();
        if (percent < 5.0f && callback_) {
            callback_(SensorStatus::Ok, percent);
        }
    }

private:
    EventCallback callback_;
    uint16_t readAdcHw();
    float getPercent();
};

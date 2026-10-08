// Клас автокалібрування положення ротора BLDC-сервоконтролера
#include <cmath>
#include <cstdint>

class FocCalibrator {
public:
    struct Config {
        uint8_t polePairs;
        float alignCurrent;
    };

    FocCalibrator(const Config& cfg) : config_(cfg), thetaOffset_(0.0f), isCalibrated_(false) {}

    template <typename EncoderReadFn, typename SetFocFn>
    bool calibrate(EncoderReadFn&& readEncoder, SetFocFn&& setFoc) {
        setFoc(config_.alignCurrent, 0.0f, 0.0f);
        delayMs(300);

        // Підхід з позитивного зміщення
        setFoc(config_.alignCurrent, 0.0f, 0.15f);
        delayMs(200);
        setFoc(config_.alignCurrent, 0.0f, 0.0f);
        delayMs(200);
        float posMech = readEncoder();

        // Підхід з негативного зміщення
        setFoc(config_.alignCurrent, 0.0f, -0.15f);
        delayMs(200);
        setFoc(config_.alignCurrent, 0.0f, 0.0f);
        delayMs(200);
        float negMech = readEncoder();

        float avgMech = (posMech + negMech) * 0.5f;
        thetaOffset_ = std::fmod(config_.polePairs * avgMech, 2.0f * M_PI);
        if (thetaOffset_ < 0.0f) thetaOffset_ += 2.0f * M_PI;

        setFoc(0.0f, 0.0f, 0.0f);
        isCalibrated_ = true;
        return isCalibrated_;
    }

    float getOffset() const { return thetaOffset_; }

private:
    void delayMs(uint32_t ms) {
        for (volatile uint32_t i = 0; i < ms * 10000; ++i);
    }

    Config config_;
    float thetaOffset_;
    bool isCalibrated_;
};

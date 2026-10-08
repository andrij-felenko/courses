class AdaptiveCalibrator {
private:
    uint16_t minVal_ = 0xFFFF;
    uint16_t maxVal_ = 0;
    uint16_t threshold_ = 0;
    uint16_t hysteresis_ = 0;

public:
    void updateSample(uint16_t val) {
        if (val < minVal_) minVal_ = val;
        if (val > maxVal_) maxVal_ = val;
    }

    bool finalize(float ratio = 0.5f) {
        if (maxVal_ <= minVal_ || (maxVal_ - minVal_) < 30) {
            return false;
        }
        threshold_ = minVal_ + static_cast<uint16_t>((maxVal_ - minVal_) * ratio);
        hysteresis_ = static_cast<uint16_t>((maxVal_ - minVal_) * 0.05f);
        return true;
    }

    bool getState(uint16_t val, bool prevState) const {
        if (prevState) {
            return val >= (threshold_ - hysteresis_);
        } else {
            return val > (threshold_ + hysteresis_);
        }
    }
};

#include <Arduino.h>

enum class RvdtStatus {
    Ok,
    SignalLowError,
    SignalHighError,
    PhaseSyncError
};

struct RvdtConfig {
    uint32_t sampleRateHz;
    uint32_t carrierFreqHz;
    float lpfCutoffHz;
    float scaleFactor;
};

class RvdtDriver {
private:
    RvdtConfig config;
    float demodV1{0.0f};
    float demodV2{0.0f};
    RvdtStatus currentStatus{RvdtStatus::Ok};

public:
    explicit RvdtDriver(const RvdtConfig& cfg) : config(cfg) {}

    bool begin() {
        // Налаштування таймерів та АЦП
        return true;
    }

    void processSamples(float excSample, float s1Sample, float s2Sample) {
        // Синхронна обробка вибірок
    }

    float getAngle() const { return demodV1; }
    RvdtStatus getStatus() const { return currentStatus; }
};

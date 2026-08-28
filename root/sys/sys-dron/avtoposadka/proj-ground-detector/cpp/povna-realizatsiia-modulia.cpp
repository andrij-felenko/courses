#include <cstdint>
#include <cmath>
#include <array>
#include <algorithm>
#include <span>
#include <chrono>

enum class GroundModuleState : uint8_t {
    InAir = 0,
    ContactMaybe,
    ContactConfirmed,
    Landed,
    Disarmed
};

struct GroundDetectorParams {
    float maxVzAbs{0.15f};              // Гранична вертикальна швидкість контакту (м/с)
    float maxGyroAbs{0.20f};            // Гранична кутова швидкість (рад/с)
    float hoverThrRatio{0.30f};         // Максимальний поріг газу від висіння
    float confThresholdLand{0.85f};     // Поріг довіри для фіксації посадки
    float confThresholdDrop{0.20f};     // Поріг скидання в політ при відриві
    float timeRiseSec{0.50f};           // Постійна часу наростання довіри (с)
    float timeDecaySec{0.25f};          // Постійна часу витоку довіри (с)
    float disarmRampTimeSec{0.40f};     // Час лінійного зняття тяги (с)
};

class GroundDetectorModule {
public:
    static constexpr size_t AccelBufferSize = 32;

    explicit GroundDetectorModule(const GroundDetectorParams& params) noexcept
        : params_(params) {}

    void update(float vzEkf,
                float gyroNormRadS,
                float accelZMPS2,
                float currentThrottle,
                float hoverThrottle,
                float dtSec) noexcept {
        
        if (dtSec <= 0.0001f || dtSec > 0.2f) {
            dtSec = 0.02f;
        }

        // 1. Оновлення кільцевого буфера
        accelBuffer_[accelBufferIdx_] = accelZMPS2;
        accelBufferIdx_ = (accelBufferIdx_ + 1) % AccelBufferSize;
        if (accelBufferCount_ < AccelBufferSize) {
            accelBufferCount_++;
        }

        // 2. Детектування ударного імпульсу
        const float jerkIndicator = std::abs(accelZMPS2 - 2.0f * prevAccelZ_ + prevAccelZ2_);
        prevAccelZ2_ = prevAccelZ_;
        prevAccelZ_ = accelZMPS2;
        const float pImpact = (jerkIndicator > 6.0f) ? 1.0f : 0.0f;

        // 3. Часткові ймовірності
        const float maxAllowedThr = hoverThrottle * params_.hoverThrRatio;
        float pThrust{0.0f};
        if (currentThrottle <= maxAllowedThr && maxAllowedThr > 0.001f) {
            pThrust = 1.0f - (currentThrottle / maxAllowedThr) * 0.5f;
        }

        const float absVz = std::abs(vzEkf);
        float pVel{0.0f};
        if (absVz <= params_.maxVzAbs && params_.maxVzAbs > 0.001f) {
            pVel = 1.0f - (absVz / params_.maxVzAbs) * 0.4f;
        }

        const float pGyro = (gyroNormRadS <= params_.maxGyroAbs) ? 1.0f : 0.0f;

        // 4. Миттєва зважена впевненість
        const float sRaw = 0.40f * pThrust + 0.35f * pVel + 0.15f * pGyro + 0.10f * pImpact;

        // 5. Витікаючий інтегратор
        if (sRaw >= 0.60f) {
            float alphaRise = dtSec / params_.timeRiseSec;
            alphaRise = std::clamp(alphaRise, 0.0f, 1.0f);
            confidence_ += (1.0f - confidence_) * alphaRise;
        } else {
            const float decayFactor = std::exp(-dtSec / params_.timeDecaySec);
            confidence_ *= decayFactor;
        }
        confidence_ = std::clamp(confidence_, 0.0f, 1.0f);

        // 6. Кінцевий автомат станів
        switch (state_) {
            case GroundModuleState::InAir: {
                freezeITerms_ = false;
                disarmRequested_ = false;
                throttleOutputScale_ = 1.0f;
                landedTimeAccum_ = 0.0f;

                if (confidence_ >= 0.35f) {
                    state_ = GroundModuleState::ContactMaybe;
                }
                break;
            }

            case GroundModuleState::ContactMaybe: {
                if (confidence_ < params_.confThresholdDrop) {
                    state_ = GroundModuleState::InAir;
                    break;
                }

                if (confidence_ >= 0.60f) {
                    state_ = GroundModuleState::ContactConfirmed;
                    freezeITerms_ = true;
                }
                break;
            }

            case GroundModuleState::ContactConfirmed: {
                if (confidence_ < params_.confThresholdDrop) {
                    state_ = GroundModuleState::InAir;
                    freezeITerms_ = false;
                    break;
                }

                if (confidence_ >= params_.confThresholdLand) {
                    state_ = GroundModuleState::Landed;
                    landedTimeAccum_ = 0.0f;
                }
                break;
            }

            case GroundModuleState::Landed: {
                freezeITerms_ = true;
                landedTimeAccum_ += dtSec;

                if (landedTimeAccum_ < params_.disarmRampTimeSec) {
                    const float ramp = 1.0f - (landedTimeAccum_ / params_.disarmRampTimeSec);
                    throttleOutputScale_ = std::max(0.0f, ramp);
                } else {
                    throttleOutputScale_ = 0.0f;
                    disarmRequested_ = true;
                    state_ = GroundModuleState::Disarmed;
                }
                break;
            }

            case GroundModuleState::Disarmed:
            default: {
                throttleOutputScale_ = 0.0f;
                disarmRequested_ = true;
                freezeITerms_ = true;
                break;
            }
        }
    }

    [[nodiscard]] GroundModuleState state() const noexcept { return state_; }
    [[nodiscard]] float confidence() const noexcept { return confidence_; }
    [[nodiscard]] float throttleScale() const noexcept { return throttleOutputScale_; }
    [[nodiscard]] bool areITermsFrozen() const noexcept { return freezeITerms_; }
    [[nodiscard]] bool isDisarmRequested() const noexcept { return disarmRequested_; }

private:
    GroundDetectorParams params_;
    GroundModuleState state_{GroundModuleState::InAir};
    float confidence_{0.0f};
    float throttleOutputScale_{1.0f};
    bool  freezeITerms_{false};
    bool  disarmRequested_{false};

    std::array<float, AccelBufferSize> accelBuffer_{};
    size_t accelBufferIdx_{0};
    size_t accelBufferCount_{0};

    float prevAccelZ_{0.0f};
    float prevAccelZ2_{0.0f};
    float landedTimeAccum_{0.0f};
};

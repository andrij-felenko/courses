#include <cstdint>
#include <cmath>
#include <algorithm>
#include <chrono>

enum class GroundDetectorState : uint8_t {
    InAir = 0,
    GroundContact,
    MaybeLanded,
    Landed,
    Disarmed
};

struct GroundDetectorConfig {
    float maxVelocityZ{0.15f};          // Поріг вертикальної швидкості (м/с)
    float maxAngularRateRad{0.25f};     // Поріг кутової швидкості (~14 град/с)
    float throttleHoverRatio{0.30f};    // Поріг газу (30% від газу зависання)
    float groundEffectAltM{1.50f};      // Висота зони екранного ефекту (м)
    std::chrono::milliseconds contactDuration{500};
    std::chrono::milliseconds landedDuration{1000};
    std::chrono::milliseconds disarmTimeout{500};
};

class GroundDetector {
public:
    using Milliseconds = std::chrono::milliseconds;

    explicit GroundDetector(const GroundDetectorConfig& config) noexcept
        : config_(config) {}

    void update(float vzActual,
                float gyroNormRad,
                float currentThrottle,
                float hoverThrottle,
                float altitudeM,
                Milliseconds now) noexcept {
        
        const float throttleThreshold = hoverThrottle * config_.throttleHoverRatio;
        const bool lowThrust = (currentThrottle <= throttleThreshold);
        const bool nearZeroVz = (std::abs(vzActual) <= config_.maxVelocityZ);
        const bool gyroQuiet = (gyroNormRad <= config_.maxAngularRateRad);
        const bool physicalContact = lowThrust && nearZeroVz && gyroQuiet;

        switch (state_) {
            case GroundDetectorState::InAir: {
                iTermsFrozen_ = false;
                disarmCommanded_ = false;

                if (physicalContact) {
                    state_ = GroundDetectorState::GroundContact;
                    contactStart_ = now;
                }
                break;
            }

            case GroundDetectorState::GroundContact: {
                if (!physicalContact) {
                    state_ = GroundDetectorState::InAir;
                    break;
                }

                if ((now - contactStart_) >= config_.contactDuration) {
                    state_ = GroundDetectorState::MaybeLanded;
                    maybeLandedStart_ = now;
                    iTermsFrozen_ = true;
                }
                break;
            }

            case GroundDetectorState::MaybeLanded: {
                if (!physicalContact) {
                    state_ = GroundDetectorState::InAir;
                    iTermsFrozen_ = false;
                    break;
                }

                if ((now - maybeLandedStart_) >= config_.landedDuration) {
                    state_ = GroundDetectorState::Landed;
                    landedStart_ = now;
                }
                break;
            }

            case GroundDetectorState::Landed: {
                const auto elapsed = now - landedStart_;
                if (elapsed < config_.disarmTimeout) {
                    const float rampFactor = 1.0f - (static_cast<float>(elapsed.count()) /
                                                     static_cast<float>(config_.disarmTimeout.count()));
                    throttleOutput_ = currentThrottle * rampFactor;
                } else {
                    throttleOutput_ = 0.0f;
                    disarmCommanded_ = true;
                    state_ = GroundDetectorState::Disarmed;
                }
                break;
            }

            case GroundDetectorState::Disarmed:
            default: {
                throttleOutput_ = 0.0f;
                disarmCommanded_ = true;
                iTermsFrozen_ = true;
                break;
            }
        }
    }

    [[nodiscard]] GroundDetectorState state() const noexcept { return state_; }
    [[nodiscard]] bool areITermsFrozen() const noexcept { return iTermsFrozen_; }
    [[nodiscard]] bool isDisarmCommanded() const noexcept { return disarmCommanded_; }
    [[nodiscard]] float throttleOutput() const noexcept { return throttleOutput_; }

private:
    GroundDetectorConfig config_;
    GroundDetectorState state_{GroundDetectorState::InAir};
    Milliseconds contactStart_{0};
    Milliseconds maybeLandedStart_{0};
    Milliseconds landedStart_{0};
    float throttleOutput_{1.0f};
    bool iTermsFrozen_{false};
    bool disarmCommanded_{false};
};

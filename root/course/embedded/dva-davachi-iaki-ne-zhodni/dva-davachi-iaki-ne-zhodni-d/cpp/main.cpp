#include <array>
#include <optional>
#include <cmath>
#include <cstdint>
#include <algorithm>

enum class VoterBiasPolicy : uint8_t {
    FailsafeDefault = 0,
    PessimisticMax  = 1,
    PessimisticMin  = 2
};

enum class VoterState : uint8_t {
    HealthyConsensus   = 0,
    DegradedTmr        = 1,
    DegradedAnalytical = 2,
    BiasedFailsafe     = 3,
    CriticalFault      = 4
};

struct VoterConfig {
    float tolerance{0.5f};
    float modelTolerance{1.0f};
    uint16_t tripDebounce{3};
    uint16_t healDebounce{10};
    VoterBiasPolicy biasPolicy{VoterBiasPolicy::FailsafeDefault};
    float failsafeDefault{0.0f};
};

struct VoterResult {
    float value;
    VoterState state;
    uint8_t healthyMask;
    bool isValid;
};

class SensorVoter {
public:
    explicit SensorVoter(const VoterConfig& config) noexcept
        : cfg_(config),
          state_(VoterState::HealthyConsensus),
          lastValidOutput_(config.failsafeDefault) {}

    template <size_t N>
    VoterResult process(const std::array<float, N>& readings,
                        std::optional<float> modelVal = std::nullopt) noexcept {
        static_assert(N == 2 || N == 3, "SensorVoter підтримує конфігурації з 2 або 3 давачами");

        if constexpr (N == 2) {
            return processDual(readings, modelVal);
        } else {
            return processTriple(readings);
        }
    }

    [[nodiscard]] VoterState state() const noexcept { return state_; }
    [[nodiscard]] uint8_t healthyMask() const noexcept { return healthyMask_; }

private:
    VoterConfig cfg_;
    VoterState state_{VoterState::HealthyConsensus};
    uint16_t faultCounter_{0};
    uint16_t healCounter_{0};
    uint8_t healthyMask_{0x07};
    float lastValidOutput_{0.0f};

    [[nodiscard]] float applyBias(float v0, float v1) const noexcept {
        switch (cfg_.biasPolicy) {
            case VoterBiasPolicy::PessimisticMax: return std::max(v0, v1);
            case VoterBiasPolicy::PessimisticMin: return std::min(v0, v1);
            case VoterBiasPolicy::FailsafeDefault:
            default:
                return cfg_.failsafeDefault;
        }
    }

    VoterResult processDual(const std::array<float, 2>& r, 
                            std::optional<float> modelVal) noexcept {
        const float diff = std::abs(r[0] - r[1]);

        if (diff <= cfg_.tolerance) {
            if (faultCounter_ > 0) --faultCounter_;
            if (healCounter_ < cfg_.healDebounce) ++healCounter_;

            if (healCounter_ >= cfg_.healDebounce) {
                state_ = VoterState::HealthyConsensus;
                healthyMask_ = 0x03;
            }

            lastValidOutput_ = (r[0] + r[1]) * 0.5f;
            return {lastValidOutput_, state_, healthyMask_, true};
        }

        healCounter_ = 0;
        if (faultCounter_ < cfg_.tripDebounce) {
            ++faultCounter_;
            return {lastValidOutput_, state_, healthyMask_, true};
        }

        if (modelVal.has_value()) {
            const float err0 = std::abs(r[0] - *modelVal);
            const float err1 = std::abs(r[1] - *modelVal);

            if (err0 <= cfg_.modelTolerance && err1 > cfg_.modelTolerance) {
                state_ = VoterState::DegradedAnalytical;
                healthyMask_ = 0x01;
                lastValidOutput_ = r[0];
                return {lastValidOutput_, state_, healthyMask_, true};
            }
            if (err1 <= cfg_.modelTolerance && err0 > cfg_.modelTolerance) {
                state_ = VoterState::DegradedAnalytical;
                healthyMask_ = 0x02;
                lastValidOutput_ = r[1];
                return {lastValidOutput_, state_, healthyMask_, true};
            }
        }

        state_ = VoterState::BiasedFailsafe;
        healthyMask_ = 0x00;
        lastValidOutput_ = applyBias(r[0], r[1]);
        const bool valid = (cfg_.biasPolicy != VoterBiasPolicy::FailsafeDefault);
        return {lastValidOutput_, state_, healthyMask_, valid};
    }

    VoterResult processTriple(const std::array<float, 3>& r) noexcept {
        const float d01 = std::abs(r[0] - r[1]);
        const float d12 = std::abs(r[1] - r[2]);
        const float d20 = std::abs(r[2] - r[0]);

        const bool p01 = (d01 <= cfg_.tolerance);
        const bool p12 = (d12 <= cfg_.tolerance);
        const bool p20 = (d20 <= cfg_.tolerance);

        if (p01 && p12 && p20) {
            state_ = VoterState::HealthyConsensus;
            healthyMask_ = 0x07;
            faultCounter_ = 0;
            lastValidOutput_ = (r[0] + r[1] + r[2]) / 3.0f;
            return {lastValidOutput_, state_, healthyMask_, true};
        }

        if (p01) {
            state_ = VoterState::DegradedTmr;
            healthyMask_ = 0x03;
            lastValidOutput_ = (r[0] + r[1]) * 0.5f;
            return {lastValidOutput_, state_, healthyMask_, true};
        }
        if (p12) {
            state_ = VoterState::DegradedTmr;
            healthyMask_ = 0x06;
            lastValidOutput_ = (r[1] + r[2]) * 0.5f;
            return {lastValidOutput_, state_, healthyMask_, true};
        }
        if (p20) {
            state_ = VoterState::DegradedTmr;
            healthyMask_ = 0x05;
            lastValidOutput_ = (r[2] + r[0]) * 0.5f;
            return {lastValidOutput_, state_, healthyMask_, true};
        }

        state_ = VoterState::CriticalFault;
        healthyMask_ = 0x00;
        return {cfg_.failsafeDefault, state_, healthyMask_, false};
    }
};

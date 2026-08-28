#include <cstdint>
#include <cmath>
#include <array>
#include <span>
#include <algorithm>

class PirDspProcessor {
public:
    enum class State : uint8_t {
        Idle,
        PosPeakDetected,
        NegPeakDetected,
        DeadTime
    };

    explicit constexpr PirDspProcessor(float sensitivityMultiplier = 4.0f) noexcept
        : thresholdMultiplier_{sensitivityMultiplier} {}

    [[nodiscard]] bool processSample(float rawAdcSample) noexcept {
        bool triggered = false;

        // 1. Пряма фільтрація (Direct Form II Transposed)
        const float filtered = filterStep(rawAdcSample);

        // 2. Адаптивне оновлення фонового шуму в стані спокою
        if (state_ == State::Idle) {
            const float absVal = std::fabs(filtered);
            noiseSigma_ = 0.995f * noiseSigma_ + 0.005f * absVal;
            noiseSigma_ = std::max(noiseSigma_, 5.0f);
        }

        const float threshold = noiseSigma_ * thresholdMultiplier_;

        // 3. Автомат розпізнавання чергування фаз
        switch (state_) {
            case State::Idle:
                if (filtered > threshold) {
                    state_ = State::PosPeakDetected;
                    timerTicks_ = 0;
                } else if (filtered < -threshold) {
                    state_ = State::NegPeakDetected;
                    timerTicks_ = 0;
                }
                break;

            case State::PosPeakDetected:
                ++timerTicks_;
                if (filtered < -threshold && timerTicks_ >= kMinWindowTicks) {
                    triggered = true;
                    state_ = State::DeadTime;
                    timerTicks_ = 0;
                } else if (timerTicks_ > kMaxWindowTicks) {
                    state_ = State::Idle;
                }
                break;

            case State::NegPeakDetected:
                ++timerTicks_;
                if (filtered > threshold && timerTicks_ >= kMinWindowTicks) {
                    triggered = true;
                    state_ = State::DeadTime;
                    timerTicks_ = 0;
                } else if (timerTicks_ > kMaxWindowTicks) {
                    state_ = State::Idle;
                }
                break;

            case State::DeadTime:
                ++timerTicks_;
                if (timerTicks_ >= kDeadTimeTicks) {
                    state_ = State::Idle;
                }
                break;
        }

        return triggered;
    }

    void processBlock(std::span<const float> inputBuffer, std::span<bool> outputEvents) noexcept {
        const size_t count = std::min(inputBuffer.size(), outputEvents.size());
        for (size_t i = 0; i < count; ++i) {
            outputEvents[i] = processSample(inputBuffer[i]);
        }
    }

    [[nodiscard]] State currentState() const noexcept { return state_; }
    [[nodiscard]] float currentNoiseFloor() const noexcept { return noiseSigma_; }

    void reset() noexcept {
        d1_ = 0.0f;
        d2_ = 0.0f;
        noiseSigma_ = 15.0f;
        timerTicks_ = 0;
        state_ = State::Idle;
    }

private:
    static constexpr uint32_t kSampleRateHz    = 50;
    static constexpr uint32_t kMinWindowTicks  = static_cast<uint32_t>(kSampleRateHz * 0.15f);
    static constexpr uint32_t kMaxWindowTicks  = static_cast<uint32_t>(kSampleRateHz * 1.50f);
    static constexpr uint32_t kDeadTimeTicks   = static_cast<uint32_t>(kSampleRateHz * 1.00f);

    // Коефіцієнти фільтра Butterworth Bandpass (0.5–4.0 Гц, Fs = 50 Гц)
    static constexpr float kB0 =  0.1983f;
    static constexpr float kB1 =  0.0000f;
    static constexpr float kB2 = -0.1983f;
    static constexpr float kA1 = -1.5422f;
    static constexpr float kA2 =  0.6034f;

    float d1_{0.0f};
    float d2_{0.0f};
    float noiseSigma_{15.0f};
    float thresholdMultiplier_{4.0f};

    uint32_t timerTicks_{0};
    State state_{State::Idle};

    [[nodiscard]] float filterStep(float x) noexcept {
        const float y = kB0 * x + d1_;
        d1_ = kB1 * x - kA1 * y + d2_;
        d2_ = kB2 * x - kA2 * y;
        return y;
    }
};
